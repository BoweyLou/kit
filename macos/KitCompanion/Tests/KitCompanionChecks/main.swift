import Foundation

enum CheckFailure: Error, CustomStringConvertible {
    case failed(String)

    var description: String {
        switch self {
        case .failed(let message):
            return message
        }
    }
}

func check(_ condition: @autoclosure () -> Bool, _ message: String) throws {
    if !condition() {
        throw CheckFailure.failed(message)
    }
}

func expectThrows(_ message: String, _ body: () throws -> Void) throws {
    do {
        try body()
    } catch {
        return
    }
    throw CheckFailure.failed(message)
}

func makeCommand(
    name: String,
    path: [String]? = nil,
    mutation: String = "read-only",
    targetRepoWrite: String = "never",
    sidecarWrite: String = "never",
    jsonSupported: Bool = true,
    flags: [String] = ["--json"],
    examples: [String] = []
) -> CommandEntry {
    CommandEntry(
        name: name,
        path: path ?? name.split(separator: " ").map(String.init),
        summary: "Test command",
        audience: ["human", "agent"],
        mutation: mutation,
        targetRepoWrite: targetRepoWrite,
        sidecarWrite: sidecarWrite,
        jsonSupported: jsonSupported,
        routeRole: nil,
        canonicalCommand: name,
        aliasOf: nil,
        outputSchema: "test_payload",
        examples: examples,
        flags: flags.map { CommandFlag(option: $0, dest: nil, help: nil, required: false, choices: nil) },
        docs: []
    )
}

do {
    let start = makeCommand(name: "start", flags: ["--repo", "--json", "--no-update"])
    try check(start.appCoverage == .native, "start should use the native overview coverage")
    try check(
        start.safeArguments(selectedRepo: "/tmp/example repo") == ["start", "--repo", "/tmp/example repo", "--no-update", "--json"],
        "start preview should force --no-update and --json"
    )

    let update = makeCommand(
        name: "update",
        mutation: "writes-target-by-default",
        targetRepoWrite: "writes-target-by-default",
        flags: ["--repo", "--json", "--all", "--dry-run", "--apply"]
    )
    try check(
        update.safeArguments(selectedRepo: "/tmp/example") == ["update", "--repo", "/tmp/example", "--dry-run", "--json"],
        "update should use selected repo dry-run arguments"
    )

    let closeoutFix = makeCommand(
        name: "closeout-fix",
        mutation: "launches-write-agent",
        targetRepoWrite: "via launched agent in --apply mode",
        sidecarWrite: "with --apply",
        flags: ["--repo", "--json", "--apply", "--jsonl", "--agent", "--timeout-seconds"]
    )
    try check(closeoutFix.appCoverage == .native, "closeout-fix should have a native one-click app surface")
    try check(
        closeoutFix.safeArguments(selectedRepo: "/tmp/example") == ["closeout-fix", "--repo", "/tmp/example", "--json"],
        "command-browser closeout-fix should preview only"
    )

    let targetImport = makeCommand(
        name: "target import",
        path: ["target", "import"],
        mutation: "writes-local-kit-registry-with-apply",
        sidecarWrite: "with --apply",
        flags: ["--root", "--json", "--dry-run", "--apply"]
    )
    try check(targetImport.appCoverage == .previewInApp, "target import should be preview-only")
    try check(targetImport.safeArguments(selectedRepo: nil) == nil, "target import should need a selected root")
    try check(
        targetImport.safeArguments(selectedRepo: "/tmp/root") == ["target", "import", "--root", "/tmp/root", "--dry-run", "--json"],
        "target import should force --dry-run"
    )

    let doctor = makeCommand(name: "doctor", flags: ["--repo", "--json", "--write-sidecar"])
    try check(doctor.appCoverage == .runInApp, "doctor should run in app without optional write-sidecar")
    try check(
        doctor.safeArguments(selectedRepo: "/tmp/repo") == ["doctor", "--repo", "/tmp/repo", "--json"],
        "doctor should omit optional sidecar write flag"
    )

    try expectThrows("unsafe update should be blocked") {
        try KitProcessRunner.validateReadOnlyCommand(["update", "--repo", "/tmp/repo"])
    }
    try KitProcessRunner.validateReadOnlyCommand(["update", "--repo", "/tmp/repo", "--dry-run", "--json"])
    try expectThrows("automation handoff without dry-run should be blocked") {
        try KitProcessRunner.validateReadOnlyCommand(["automation-handoff", "--repo", "/tmp/repo", "--json"])
    }
    try KitProcessRunner.validateReadOnlyCommand(["automation-handoff", "--repo", "/tmp/repo", "--dry-run", "--json"])
    try expectThrows("generic closeout-fix apply should be blocked") {
        try KitProcessRunner.validateReadOnlyCommand(["closeout-fix", "--repo", "/tmp/repo", "--apply", "--jsonl"])
    }
    try KitProcessRunner.validateReadOnlyCommand(["closeout-fix", "--repo", "/tmp/repo", "--json"])
    try KitProcessRunner.validateCloseoutFixCommand(["closeout-fix", "--repo", "/tmp/repo", "--apply", "--jsonl"])
    try KitProcessRunner.validateCloseoutFixCommand(["closeout-fix", "--repo", "/tmp/repo", "--apply", "--jsonl", "--agent", "codex"])
    try expectThrows("closeout-fix dedicated runner should reject custom agent commands") {
        try KitProcessRunner.validateCloseoutFixCommand([
            "closeout-fix",
            "--repo",
            "/tmp/repo",
            "--apply",
            "--jsonl",
            "--agent-command",
            "danger"
        ])
    }
    let finalLine = """
    {"event":"final-payload","payload":{"command":"closeout-fix","result":"applied","commits":[{"short_sha":"abc123","subject":"Add lane"}],"receipts":[{"path":"/tmp/receipt.json","kind":"closeout-fix"}],"branches_pushed":[],"worktrees_pruned":[],"blockers":[],"exit_code":0}}
    """
    let finalPayload = try JSONDecoder().decode(CloseoutFixFinalPayloadLine.self, from: Data(finalLine.utf8))
    try check(finalPayload.payload?.result == "applied", "closeout-fix final JSONL payload should decode")
    try check(finalPayload.payload?.commits?.first?.subject == "Add lane", "closeout-fix commits should decode")

    let status = makeCommand(
        name: "status",
        flags: ["--repo", "--json"],
        examples: ["kit status --repo /path/to/repo --json"]
    )
    try check(
        status.terminalCommand(selectedRepo: "/tmp/example repo") == "kit status --repo '/tmp/example repo' --json",
        "terminal commands should shell-quote repo paths"
    )

    print("KitCompanionChecks passed")
} catch {
    fputs("KitCompanionChecks failed: \(error)\n", stderr)
    exit(1)
}
