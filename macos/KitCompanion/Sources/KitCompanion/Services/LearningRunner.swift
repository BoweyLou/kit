import Foundation
import Darwin

enum LearningRunnerError: LocalizedError {
    case missingBinary
    case commandFailed(String, Int32, String)
    case invalidJSON(String)
    case decodingFailed(String)
    case rejectedPayload(String)

    var errorDescription: String? {
        switch self {
        case .missingBinary: return "Could not find the kit binary. Set it in Settings."
        case .commandFailed(let command, let code, let detail): return "Learning command failed (\(code)): \(command). \(detail)"
        case .invalidJSON(let command): return "Learning command did not return one JSON object: \(command)"
        case .decodingFailed(let detail): return "Learning JSON did not match the typed app contract: \(detail)"
        case .rejectedPayload(let detail): return "Learning result was rejected before display: \(detail)"
        }
    }
}

protocol LearningRunning {
    func run<T: Decodable & LearningPayloadMetadata>(
        _ type: T.Type,
        command: LearningCommand,
        selectedRepo: String,
        kitPath: String
    ) async throws -> T
}

private actor LearningWriteSerializer {
    static let shared = LearningWriteSerializer()
    private var activeRepos = Set<String>()
    private struct Waiter {
        let id: UUID
        let continuation: CheckedContinuation<Void, Error>
    }
    private var waiters: [String: [Waiter]] = [:]

    func acquire(_ repo: String) async throws {
        try Task.checkCancellation()
        if activeRepos.insert(repo).inserted {
            do {
                try Task.checkCancellation()
            } catch {
                release(repo)
                throw error
            }
            return
        }

        let id = UUID()
        try await withTaskCancellationHandler {
            try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
                if Task.isCancelled {
                    continuation.resume(throwing: CancellationError())
                    return
                }
                waiters[repo, default: []].append(Waiter(id: id, continuation: continuation))
            }
        } onCancel: {
            Task { await self.cancelWaiter(repo, id: id) }
        }

        do {
            try Task.checkCancellation()
        } catch {
            release(repo)
            throw error
        }
    }

    func release(_ repo: String) {
        if var queued = waiters[repo], !queued.isEmpty {
            let next = queued.removeFirst()
            waiters[repo] = queued.isEmpty ? nil : queued
            next.continuation.resume()
        } else {
            activeRepos.remove(repo)
        }
    }

    private func cancelWaiter(_ repo: String, id: UUID) {
        guard var queued = waiters[repo], let index = queued.firstIndex(where: { $0.id == id }) else {
            return
        }
        let waiter = queued.remove(at: index)
        waiters[repo] = queued.isEmpty ? nil : queued
        waiter.continuation.resume(throwing: CancellationError())
    }
}

private final class LearningProcessState: @unchecked Sendable {
    private let lock = NSLock()
    private let fileManager: FileManager
    private var continuation: CheckedContinuation<KitCommandResult, Error>?
    private var process: Process?
    private var outputURLs = Set<URL>()
    private var outputHandles: [URL: FileHandle] = [:]
    private var launchInProgress = false
    private var cancelled = false
    private var completed = false

    init(fileManager: FileManager) {
        self.fileManager = fileManager
    }

    func install(
        continuation: CheckedContinuation<KitCommandResult, Error>,
        process: Process
    ) {
        lock.lock()
        guard !completed else {
            lock.unlock()
            continuation.resume(throwing: CancellationError())
            return
        }
        self.continuation = continuation
        self.process = process
        lock.unlock()
    }

    func registerOutput(url: URL, handle: FileHandle) {
        lock.lock()
        guard !completed else {
            lock.unlock()
            handle.closeFile()
            try? fileManager.removeItem(at: url)
            return
        }
        outputURLs.insert(url)
        outputHandles[url] = handle
        lock.unlock()
    }

    func run(_ process: Process) throws {
        lock.lock()
        if cancelled || completed {
            lock.unlock()
            finish(.failure(CancellationError()))
            throw CancellationError()
        }
        launchInProgress = true
        lock.unlock()

        do {
            try process.run()
        } catch {
            lock.lock()
            launchInProgress = false
            let wasCancelled = cancelled
            lock.unlock()
            finish(.failure(wasCancelled ? CancellationError() : error))
            throw wasCancelled ? CancellationError() : error
        }

        lock.lock()
        launchInProgress = false
        let shouldTerminate = cancelled
        lock.unlock()
        if shouldTerminate {
            process.terminate()
        }
    }

    func cancel() {
        lock.lock()
        guard !completed else {
            lock.unlock()
            return
        }
        cancelled = true
        let process = self.process
        let launching = launchInProgress
        let running = process?.isRunning == true
        lock.unlock()

        if running {
            process?.terminate()
        } else if !launching {
            finish(.failure(CancellationError()))
        }
    }

    func processDidTerminate(_ process: Process, stdoutURL: URL, stderrURL: URL) {
        lock.lock()
        let wasCancelled = cancelled
        lock.unlock()
        if wasCancelled {
            finish(.failure(CancellationError()))
            return
        }
        finish(.success(KitCommandResult(
            stdout: readFile(at: stdoutURL),
            stderr: readFile(at: stderrURL),
            exitCode: process.terminationStatus
        )))
    }

    func fail(_ error: Error) {
        finish(.failure(error))
    }

    private func finish(_ result: Result<KitCommandResult, Error>) {
        lock.lock()
        guard !completed else {
            lock.unlock()
            return
        }
        completed = true
        let continuation = self.continuation
        self.continuation = nil
        let outputHandles = Array(self.outputHandles.values)
        self.outputHandles.removeAll()
        let outputURLs = self.outputURLs
        self.outputURLs.removeAll()
        lock.unlock()

        outputHandles.forEach { $0.closeFile() }
        outputURLs.forEach { try? fileManager.removeItem(at: $0) }
        continuation?.resume(with: result)
    }

    private func readFile(at url: URL) -> String {
        String(decoding: (try? Data(contentsOf: url)) ?? Data(), as: UTF8.self)
    }
}

final class LearningRunner: LearningRunning {
    private let fileManager: FileManager
    private static let companionPath = [
        "/opt/homebrew/bin", "/usr/local/bin", "/Library/Frameworks/Python.framework/Versions/Current/bin",
        "/usr/bin", "/bin", "/usr/sbin", "/sbin"
    ].joined(separator: ":")

    init(fileManager: FileManager = .default) {
        self.fileManager = fileManager
    }

    func run<T: Decodable & LearningPayloadMetadata>(
        _ type: T.Type,
        command: LearningCommand,
        selectedRepo: String,
        kitPath: String
    ) async throws -> T {
        try Task.checkCancellation()
        let validated = try LearningCommandValidator.validate(command.arguments, selectedRepo: selectedRepo)
        if validated.writesSidecar {
            try await LearningWriteSerializer.shared.acquire(selectedRepo)
            do {
                try Task.checkCancellation()
                let payload: T = try await execute(type, command: validated, selectedRepo: selectedRepo, kitPath: kitPath)
                await LearningWriteSerializer.shared.release(selectedRepo)
                return payload
            } catch {
                await LearningWriteSerializer.shared.release(selectedRepo)
                throw error
            }
        }
        return try await execute(type, command: validated, selectedRepo: selectedRepo, kitPath: kitPath)
    }

    private func execute<T: Decodable & LearningPayloadMetadata>(
        _ type: T.Type,
        command: LearningCommand,
        selectedRepo: String,
        kitPath: String
    ) async throws -> T {
        let environment = Self.processEnvironment()
        let result = try await runProcess(
            arguments: command.arguments,
            kitPath: kitPath,
            workingDirectory: selectedRepo,
            environment: environment
        )
        try Task.checkCancellation()
        let rendered = KitCommandLine.render(arguments: command.arguments)
        let data = try jsonData(from: result.stdout, command: rendered)

        if result.exitCode != 0 {
            if let errorPayload = try? JSONDecoder().decode(LearningErrorPayload.self, from: data) {
                let detail = errorPayload.gate?.reason
                    ?? errorPayload.errors?.joined(separator: "; ")
                    ?? result.stderr
                throw LearningRunnerError.commandFailed(rendered, result.exitCode, detail)
            }
            let detail = result.stderr.isEmpty ? excerpt(result.stdout) : result.stderr
            throw LearningRunnerError.commandFailed(rendered, result.exitCode, detail)
        }

        let payload: T
        do {
            payload = try JSONDecoder().decode(T.self, from: data)
        } catch {
            throw LearningRunnerError.decodingFailed(error.localizedDescription)
        }
        do {
            try LearningPayloadValidator.validate(
                payload,
                expectedCommand: command.route,
                selectedRepo: selectedRepo,
                environment: environment
            )
        } catch {
            throw LearningRunnerError.rejectedPayload(error.localizedDescription)
        }
        return payload
    }

    private func runProcess(
        arguments: [String],
        kitPath: String,
        workingDirectory: String,
        environment: [String: String]
    ) async throws -> KitCommandResult {
        let binary = try resolvedBinaryURL(kitPath: kitPath)
        try Task.checkCancellation()
        let token = UUID().uuidString
        let stdoutURL = fileManager.temporaryDirectory.appendingPathComponent("KitCompanion-Learning-\(token)-stdout.txt")
        let stderrURL = fileManager.temporaryDirectory.appendingPathComponent("KitCompanion-Learning-\(token)-stderr.txt")
        let state = LearningProcessState(fileManager: fileManager)

        do {
            let stdoutHandle = try createSecureTemporaryOutput(at: stdoutURL, state: state)
            let stderrHandle = try createSecureTemporaryOutput(at: stderrURL, state: state)
            return try await withTaskCancellationHandler {
                try Task.checkCancellation()
                return try await withCheckedThrowingContinuation { continuation in
                    let process = Process()
                    process.executableURL = binary
                    process.arguments = arguments
                    process.environment = environment
                    process.currentDirectoryURL = URL(fileURLWithPath: workingDirectory, isDirectory: true)
                    state.install(continuation: continuation, process: process)

                    do {
                process.standardOutput = stdoutHandle
                process.standardError = stderrHandle
                process.terminationHandler = { terminated in
                    state.processDidTerminate(terminated, stdoutURL: stdoutURL, stderrURL: stderrURL)
                }
                try state.run(process)
                    } catch {
                        state.fail(error)
                    }
                }
            } onCancel: {
                state.cancel()
            }
        } catch {
            state.fail(error)
            throw error
        }
    }

    private func createSecureTemporaryOutput(at url: URL, state: LearningProcessState) throws -> FileHandle {
        let descriptor = url.path.withCString { Darwin.open($0, O_WRONLY | O_CREAT | O_EXCL, 0o600) }
        guard descriptor >= 0 else {
            throw POSIXError(POSIXErrorCode(rawValue: errno) ?? .EIO)
        }
        let handle = FileHandle(fileDescriptor: descriptor, closeOnDealloc: true)
        state.registerOutput(url: url, handle: handle)
        return handle
    }

    private func resolvedBinaryURL(kitPath: String) throws -> URL {
        let candidates = [
            kitPath.trimmingCharacters(in: .whitespacesAndNewlines),
            ProcessInfo.processInfo.environment["KIT_COMPANION_KIT_PATH"] ?? "",
            NSHomeDirectory() + "/.local/bin/kit", "/opt/homebrew/bin/kit", "/usr/local/bin/kit"
        ].filter { !$0.isEmpty }
        for candidate in candidates where fileManager.isExecutableFile(atPath: candidate) {
            return URL(fileURLWithPath: candidate)
        }
        throw LearningRunnerError.missingBinary
    }

    private func jsonData(from output: String, command: String) throws -> Data {
        let trimmed = output.trimmingCharacters(in: .whitespacesAndNewlines)
        guard trimmed.hasPrefix("{"), trimmed.hasSuffix("}") else { throw LearningRunnerError.invalidJSON(command) }
        let data = Data(trimmed.utf8)
        guard (try? JSONSerialization.jsonObject(with: data)) is [String: Any] else { throw LearningRunnerError.invalidJSON(command) }
        return data
    }

    private func excerpt(_ text: String) -> String { text.count <= 240 ? text : String(text.prefix(240)) + "..." }

    private static func processEnvironment() -> [String: String] {
        var environment = ProcessInfo.processInfo.environment
        environment["PATH"] = companionPath + ":" + (environment["PATH"] ?? "")
        return environment
    }
}
