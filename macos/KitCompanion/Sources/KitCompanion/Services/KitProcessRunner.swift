import Foundation

final class KitProcessRunner {
    enum RunnerError: LocalizedError {
        case missingBinary
        case blockedMutatingCommand(String)
        case invalidJSON(String)

        var errorDescription: String? {
            switch self {
            case .missingBinary:
                return "Could not find the kit binary. Set it in Settings."
            case .blockedMutatingCommand(let command):
                return "Refusing to run mutating command in the app: \(command)"
            case .invalidJSON(let command):
                return "Command did not return valid JSON: \(command)"
            }
        }
    }

    private let fileManager: FileManager

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
        do {
            return try JSONDecoder().decode(T.self, from: Data(result.stdout.utf8))
        } catch {
            throw RunnerError.invalidJSON(renderedCommand(arguments))
        }
    }

    func run(arguments: [String], kitPath: String, workingDirectory: String? = nil) async throws -> KitCommandResult {
        let binary = try resolvedBinaryURL(kitPath: kitPath)
        return try await withCheckedThrowingContinuation { continuation in
            let process = Process()
            process.executableURL = binary
            process.arguments = arguments
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
            if !readOnly && !dryRunAllowed {
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
        (["kit"] + arguments).joined(separator: " ")
    }
}
