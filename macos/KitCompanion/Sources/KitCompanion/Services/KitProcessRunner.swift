import Foundation

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
        let result = try await run(arguments: arguments, kitPath: kitPath, workingDirectory: workingDirectory)
        let command = renderedCommand(arguments)
        let decoder = JSONDecoder()
        var finalPayload: CloseoutFixPayload?

        for line in result.stdout.split(whereSeparator: \.isNewline) {
            let data = Data(String(line).utf8)
            if let finalLine = try? decoder.decode(CloseoutFixFinalPayloadLine.self, from: data),
               finalLine.event == "final-payload" {
                finalPayload = finalLine.payload
                continue
            }
            if let event = try? decoder.decode(CloseoutFixEvent.self, from: data) {
                onEvent(event)
            }
        }

        if let finalPayload {
            return finalPayload
        }

        let diagnostic = result.stderr.isEmpty ? Self.outputExcerpt(result.stdout) : result.stderr
        if !result.succeeded {
            throw RunnerError.commandFailed(command, result.exitCode, diagnostic)
        }
        throw RunnerError.invalidJSON(command, Self.outputExcerpt(result.stdout))
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

            let stdoutPipe = Pipe()
            let stderrPipe = Pipe()
            process.standardOutput = stdoutPipe
            process.standardError = stderrPipe

            do {
                try process.run()
            } catch {
                continuation.resume(throwing: error)
                return
            }

            process.terminationHandler = { terminated in
                let stdout = stdoutPipe.fileHandleForReading.readDataToEndOfFile()
                let stderr = stderrPipe.fileHandleForReading.readDataToEndOfFile()
                continuation.resume(
                    returning: KitCommandResult(
                        stdout: String(data: stdout, encoding: .utf8) ?? "",
                        stderr: String(data: stderr, encoding: .utf8) ?? "",
                        exitCode: terminated.terminationStatus
                    )
                )
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
