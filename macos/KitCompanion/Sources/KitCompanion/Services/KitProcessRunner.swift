import Foundation

private struct CloseoutFixStreamSnapshot {
    let stdout: String
    let stderr: String
    let finalPayload: CloseoutFixPayload?
}

private final class CloseoutFixJSONLStream {
    private let decoder = JSONDecoder()
    private let lock = NSLock()
    private var stdoutBuffer = ""
    private var stdoutText = ""
    private var stderrText = ""
    private var finalPayload: CloseoutFixPayload?

    func appendStdout(_ data: Data, onEvent: @escaping (CloseoutFixEvent) -> Void) {
        let chunk = String(decoding: data, as: UTF8.self)
        guard !chunk.isEmpty else {
            return
        }
        let lines = appendStdoutChunk(chunk)
        for line in lines {
            handleLine(line, onEvent: onEvent)
        }
    }

    func appendStderr(_ data: Data) {
        let chunk = String(decoding: data, as: UTF8.self)
        guard !chunk.isEmpty else {
            return
        }
        lock.lock()
        stderrText += chunk
        lock.unlock()
    }

    func finishStdout(onEvent: @escaping (CloseoutFixEvent) -> Void) {
        let line: String?
        lock.lock()
        if stdoutBuffer.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            line = nil
        } else {
            line = stdoutBuffer
        }
        stdoutBuffer = ""
        lock.unlock()

        if let line {
            handleLine(line, onEvent: onEvent)
        }
    }

    func snapshot() -> CloseoutFixStreamSnapshot {
        lock.lock()
        defer { lock.unlock() }
        return CloseoutFixStreamSnapshot(stdout: stdoutText, stderr: stderrText, finalPayload: finalPayload)
    }

    private func appendStdoutChunk(_ chunk: String) -> [String] {
        lock.lock()
        defer { lock.unlock() }

        stdoutText += chunk
        stdoutBuffer += chunk

        var lines: [String] = []
        while let newline = stdoutBuffer.firstIndex(of: "\n") {
            var line = String(stdoutBuffer[..<newline])
            if line.last == "\r" {
                line.removeLast()
            }
            stdoutBuffer.removeSubrange(...newline)
            if !line.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                lines.append(line)
            }
        }
        return lines
    }

    private func handleLine(_ line: String, onEvent: @escaping (CloseoutFixEvent) -> Void) {
        let data = Data(line.utf8)
        if let finalLine = try? decoder.decode(CloseoutFixFinalPayloadLine.self, from: data),
           finalLine.event == "final-payload",
           let payload = finalLine.payload {
            lock.lock()
            finalPayload = payload
            lock.unlock()
            return
        }
        if let event = try? decoder.decode(CloseoutFixEvent.self, from: data) {
            onEvent(event)
        }
    }
}

private final class CloseoutFixContinuationBox: @unchecked Sendable {
    private let lock = NSLock()
    private var didResume = false
    private let stdoutHandle: FileHandle
    private let stderrHandle: FileHandle
    private let continuation: CheckedContinuation<CloseoutFixPayload, Error>

    init(
        stdoutHandle: FileHandle,
        stderrHandle: FileHandle,
        continuation: CheckedContinuation<CloseoutFixPayload, Error>
    ) {
        self.stdoutHandle = stdoutHandle
        self.stderrHandle = stderrHandle
        self.continuation = continuation
    }

    func finish(_ result: Result<CloseoutFixPayload, Error>) {
        lock.lock()
        if didResume {
            lock.unlock()
            return
        }
        didResume = true
        lock.unlock()

        stdoutHandle.readabilityHandler = nil
        stderrHandle.readabilityHandler = nil

        switch result {
        case .success(let payload):
            continuation.resume(returning: payload)
        case .failure(let error):
            continuation.resume(throwing: error)
        }
    }
}

final class KitProcessRunner {
    enum RunnerError: LocalizedError {
        case missingBinary
        case blockedMutatingCommand(String)
        case commandFailed(String, Int32, String)
        case invalidJSON(String, String)
        case decodingFailed(String, String)

        var errorDescription: String? {
            switch self {
            case .missingBinary:
                return "Could not find the kit binary. Set it in Settings."
            case .blockedMutatingCommand(let command):
                return "Refusing to run mutating command in the app: \(command)"
            case .commandFailed(let command, let code, let stderr):
                let detail = stderr.isEmpty ? "No diagnostic output." : stderr
                return "Command failed (\(code)): \(command). \(detail)"
            case .invalidJSON(let command, let excerpt):
                return "Command did not return valid JSON: \(command). Output: \(excerpt)"
            case .decodingFailed(let command, let message):
                return "Command JSON did not match the app model: \(command). \(message)"
            }
        }
    }

    private let fileManager: FileManager
    private static let companionPath = [
        "/opt/homebrew/bin",
        "/usr/local/bin",
        "/Library/Frameworks/Python.framework/Versions/Current/bin",
        "/usr/bin",
        "/bin",
        "/usr/sbin",
        "/sbin"
    ].joined(separator: ":")

    init(fileManager: FileManager = .default) {
        self.fileManager = fileManager
    }

    func runJSON<T: Decodable>(
        _ type: T.Type,
        arguments: [String],
        kitPath: String,
        workingDirectory: String? = nil
    ) async throws -> T {
        try Self.validateReadOnlyCommand(arguments)
        let result = try await run(arguments: arguments, kitPath: kitPath, workingDirectory: workingDirectory)
        let command = renderedCommand(arguments)
        let jsonData: Data
        do {
            jsonData = try jsonObjectData(from: result.stdout, command: command)
        } catch {
            if !result.succeeded {
                let diagnostic = result.stderr.isEmpty ? Self.outputExcerpt(result.stdout) : result.stderr
                throw RunnerError.commandFailed(command, result.exitCode, diagnostic)
            }
            throw error
        }

        do {
            return try JSONDecoder().decode(T.self, from: jsonData)
        } catch {
            if !result.succeeded {
                let diagnostic = [
                    result.stderr,
                    Self.outputExcerpt(result.stdout)
                ]
                .filter { !$0.isEmpty }
                .joined(separator: " ")
                throw RunnerError.commandFailed(command, result.exitCode, diagnostic)
            }
            throw RunnerError.decodingFailed(command, error.localizedDescription)
        }
    }

    func runJSONText(arguments: [String], kitPath: String, workingDirectory: String? = nil) async throws -> String {
        try Self.validateReadOnlyCommand(arguments)
        let result = try await run(arguments: arguments, kitPath: kitPath, workingDirectory: workingDirectory)
        let command = renderedCommand(arguments)
        let jsonData: Data
        do {
            jsonData = try jsonObjectData(from: result.stdout, command: command)
        } catch {
            if !result.succeeded {
                let diagnostic = result.stderr.isEmpty ? Self.outputExcerpt(result.stdout) : result.stderr
                throw RunnerError.commandFailed(command, result.exitCode, diagnostic)
            }
            throw error
        }

        if !result.succeeded {
            let diagnostic = [
                result.stderr,
                Self.outputExcerpt(result.stdout)
            ]
            .filter { !$0.isEmpty }
            .joined(separator: " ")
            throw RunnerError.commandFailed(command, result.exitCode, diagnostic)
        }

        return Self.prettyPrintedJSON(jsonData)
    }

    func runCloseoutFix(
        arguments: [String],
        kitPath: String,
        workingDirectory: String? = nil,
        onEvent: @escaping (CloseoutFixEvent) -> Void
    ) async throws -> CloseoutFixPayload {
        try Self.validateCloseoutFixCommand(arguments)
        let binary = try resolvedBinaryURL(kitPath: kitPath)
        let command = renderedCommand(arguments)

        return try await withCheckedThrowingContinuation { continuation in
            let process = Process()
            process.executableURL = binary
            process.arguments = arguments
            process.environment = Self.processEnvironment()
            if let workingDirectory {
                process.currentDirectoryURL = URL(fileURLWithPath: workingDirectory, isDirectory: true)
            }

            let stdoutPipe = Pipe()
            let stderrPipe = Pipe()
            let stdoutHandle = stdoutPipe.fileHandleForReading
            let stderrHandle = stderrPipe.fileHandleForReading
            let stream = CloseoutFixJSONLStream()
            let finisher = CloseoutFixContinuationBox(
                stdoutHandle: stdoutHandle,
                stderrHandle: stderrHandle,
                continuation: continuation
            )

            stdoutHandle.readabilityHandler = { handle in
                let data = handle.availableData
                if !data.isEmpty {
                    stream.appendStdout(data, onEvent: onEvent)
                }
            }
            stderrHandle.readabilityHandler = { handle in
                let data = handle.availableData
                if !data.isEmpty {
                    stream.appendStderr(data)
                }
            }

            process.standardOutput = stdoutPipe
            process.standardError = stderrPipe
            process.terminationHandler = { terminated in
                stdoutHandle.readabilityHandler = nil
                stderrHandle.readabilityHandler = nil

                let remainingStdout = stdoutHandle.availableData
                if !remainingStdout.isEmpty {
                    stream.appendStdout(remainingStdout, onEvent: onEvent)
                }
                let remainingStderr = stderrHandle.availableData
                if !remainingStderr.isEmpty {
                    stream.appendStderr(remainingStderr)
                }
                stream.finishStdout(onEvent: onEvent)

                let snapshot = stream.snapshot()
                if let finalPayload = snapshot.finalPayload {
                    finisher.finish(.success(finalPayload))
                    return
                }

                let diagnostic = snapshot.stderr.isEmpty ? Self.outputExcerpt(snapshot.stdout) : snapshot.stderr
                if terminated.terminationStatus != 0 {
                    finisher.finish(.failure(RunnerError.commandFailed(command, terminated.terminationStatus, diagnostic)))
                    return
                }
                finisher.finish(.failure(RunnerError.invalidJSON(command, Self.outputExcerpt(snapshot.stdout))))
            }

            do {
                try process.run()
            } catch {
                finisher.finish(.failure(error))
            }
        }
    }

    func run(arguments: [String], kitPath: String, workingDirectory: String? = nil) async throws -> KitCommandResult {
        let binary = try resolvedBinaryURL(kitPath: kitPath)
        return try await withCheckedThrowingContinuation { continuation in
            let process = Process()
            process.executableURL = binary
            process.arguments = arguments
            process.environment = Self.processEnvironment()
            if let workingDirectory {
                process.currentDirectoryURL = URL(fileURLWithPath: workingDirectory, isDirectory: true)
            }

            let fileManager = self.fileManager
            let token = UUID().uuidString
            let stdoutURL = fileManager.temporaryDirectory.appendingPathComponent("KitCompanion-\(token)-stdout.txt")
            let stderrURL = fileManager.temporaryDirectory.appendingPathComponent("KitCompanion-\(token)-stderr.txt")
            _ = fileManager.createFile(atPath: stdoutURL.path, contents: nil)
            _ = fileManager.createFile(atPath: stderrURL.path, contents: nil)

            do {
                let stdoutHandle = try FileHandle(forWritingTo: stdoutURL)
                let stderrHandle = try FileHandle(forWritingTo: stderrURL)
                process.standardOutput = stdoutHandle
                process.standardError = stderrHandle

                process.terminationHandler = { terminated in
                    stdoutHandle.closeFile()
                    stderrHandle.closeFile()
                    let stdout = (try? Data(contentsOf: stdoutURL)) ?? Data()
                    let stderr = (try? Data(contentsOf: stderrURL)) ?? Data()
                    try? FileManager.default.removeItem(at: stdoutURL)
                    try? FileManager.default.removeItem(at: stderrURL)
                    continuation.resume(
                        returning: KitCommandResult(
                            stdout: String(data: stdout, encoding: .utf8) ?? "",
                            stderr: String(data: stderr, encoding: .utf8) ?? "",
                            exitCode: terminated.terminationStatus
                        )
                    )
                }

                do {
                    try process.run()
                } catch {
                    stdoutHandle.closeFile()
                    stderrHandle.closeFile()
                    throw error
                }
            } catch {
                try? fileManager.removeItem(at: stdoutURL)
                try? fileManager.removeItem(at: stderrURL)
                continuation.resume(throwing: error)
                return
            }
        }
    }

    func resolvedBinaryURL(kitPath: String) throws -> URL {
        let trimmed = kitPath.trimmingCharacters(in: .whitespacesAndNewlines)
        let candidates = [
            trimmed,
            ProcessInfo.processInfo.environment["KIT_COMPANION_KIT_PATH"] ?? "",
            NSHomeDirectory() + "/.local/bin/kit",
            "/opt/homebrew/bin/kit",
            "/usr/local/bin/kit"
        ].filter { !$0.isEmpty }

        for candidate in candidates where fileManager.isExecutableFile(atPath: candidate) {
            return URL(fileURLWithPath: candidate)
        }

        throw RunnerError.missingBinary
    }

    static func validateCloseoutFixCommand(_ arguments: [String]) throws {
        let command = arguments.joined(separator: " ")
        guard arguments.first == "closeout-fix" else {
            throw RunnerError.blockedMutatingCommand(command)
        }

        var sawRepo = false
        var sawApply = false
        var sawJSONL = false
        var index = 1
        while index < arguments.count {
            let argument = arguments[index]
            switch argument {
            case "--repo":
                guard index + 1 < arguments.count else {
                    throw RunnerError.blockedMutatingCommand(command)
                }
                sawRepo = true
                index += 2
            case "--apply":
                sawApply = true
                index += 1
            case "--jsonl":
                sawJSONL = true
                index += 1
            case "--agent":
                guard index + 1 < arguments.count, ["auto", "codex"].contains(arguments[index + 1]) else {
                    throw RunnerError.blockedMutatingCommand(command)
                }
                index += 2
            case "--timeout-seconds":
                guard index + 1 < arguments.count, Int(arguments[index + 1]) != nil else {
                    throw RunnerError.blockedMutatingCommand(command)
                }
                index += 2
            default:
                throw RunnerError.blockedMutatingCommand(command)
            }
        }

        if !sawRepo || !sawApply || !sawJSONL {
            throw RunnerError.blockedMutatingCommand(command)
        }
    }

    static func validateReadOnlyCommand(_ arguments: [String]) throws {
        let command = arguments.joined(separator: " ")
        let mutatingFlags = ["--apply", "--write", "--write-sidecar", "--global"]
        if mutatingFlags.contains(where: { arguments.contains($0) || command.contains($0) }) {
            throw RunnerError.blockedMutatingCommand(command)
        }

        guard let first = arguments.first else {
            return
        }

        switch first {
        case "install", "setup", "migrate-config":
            throw RunnerError.blockedMutatingCommand(command)
        case "sidecar-init", "docs-propose", "changelog-update":
            throw RunnerError.blockedMutatingCommand(command)
        case "automation-handoff":
            if !arguments.contains("--dry-run") {
                throw RunnerError.blockedMutatingCommand(command)
            }
        case "feedback":
            let readOnly = arguments.contains("--list") || arguments.contains("--export-json")
            if !readOnly {
                throw RunnerError.blockedMutatingCommand(command)
            }
        case "start":
            let checkOnly = arguments.contains("--no-update")
                || command.contains("--update-policy check-only")
                || command.contains("--update-policy=check-only")
            if !checkOnly {
                throw RunnerError.blockedMutatingCommand(command)
            }
        case "update":
            if !arguments.contains("--dry-run") {
                throw RunnerError.blockedMutatingCommand(command)
            }
        case "self":
            if arguments.dropFirst().first == "update" {
                throw RunnerError.blockedMutatingCommand(command)
            }
        case "target":
            let subcommand = arguments.dropFirst().first ?? ""
            let dryRunAllowed = arguments.contains("--dry-run") && ["import", "prune-missing", "update", "update-all"].contains(subcommand)
            let readOnly = ["list", "dirty-report", "doctor", "status"].contains(subcommand)
            let previewOnly = !arguments.contains("--apply") && subcommand == "repair-source-clone"
            if !readOnly && !dryRunAllowed && !previewOnly {
                throw RunnerError.blockedMutatingCommand(command)
            }
        case "worktree":
            if arguments.dropFirst().first == "prune", !arguments.contains("--dry-run") {
                throw RunnerError.blockedMutatingCommand(command)
            }
        default:
            return
        }
    }

    private func renderedCommand(_ arguments: [String]) -> String {
        KitCommandLine.render(arguments: arguments)
    }

    private static func processEnvironment() -> [String: String] {
        var environment = ProcessInfo.processInfo.environment
        if let existingPath = environment["PATH"], !existingPath.isEmpty {
            environment["PATH"] = companionPath + ":" + existingPath
        } else {
            environment["PATH"] = companionPath
        }
        return environment
    }

    private func jsonObjectData(from output: String, command: String) throws -> Data {
        let trimmed = output.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.hasPrefix("{"), trimmed.hasSuffix("}") {
            return Data(trimmed.utf8)
        }

        guard let start = trimmed.firstIndex(of: "{"),
              let end = trimmed.lastIndex(of: "}"),
              start <= end else {
            throw RunnerError.invalidJSON(command, Self.outputExcerpt(trimmed))
        }

        let json = String(trimmed[start...end])
        return Data(json.utf8)
    }

    private static func outputExcerpt(_ value: String) -> String {
        if value.isEmpty {
            return "(empty)"
        }
        if value.count <= 240 {
            return value
        }
        return String(value.prefix(240)) + "..."
    }

    private static func prettyPrintedJSON(_ data: Data) -> String {
        guard let object = try? JSONSerialization.jsonObject(with: data),
              JSONSerialization.isValidJSONObject(object),
              let prettyData = try? JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys]),
              let pretty = String(data: prettyData, encoding: .utf8) else {
            return String(data: data, encoding: .utf8) ?? ""
        }
        return pretty
    }
}
