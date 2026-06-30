import AppKit
import ServiceManagement
import SwiftUI

struct SettingsView: View {
    @AppStorage(KitSettingsKeys.kitBinaryPath) private var kitBinaryPath = KitSettings.defaultKitBinaryPath()
    @AppStorage(KitSettingsKeys.automaticallyCheckForUpdates) private var automaticallyCheckForUpdates = true
    @State private var launchAtLogin = LoginItemService.isEnabled
    @State private var loginItemState = LoginItemService.currentState()
    @State private var loginItemError: String?
    @State private var isSyncingLaunchAtLogin = false

    var body: some View {
        Form {
            LabeledContent("kit Binary") {
                HStack {
                    TextField("kit binary", text: $kitBinaryPath)
                        .textFieldStyle(.roundedBorder)
                    Button {
                        chooseKitBinary()
                    } label: {
                        Image(systemName: "folder")
                    }
                    .help("Choose kit binary")
                }
            }

            VStack(alignment: .leading, spacing: 8) {
                Toggle("Launch at Login", isOn: $launchAtLogin)
                    .onChange(of: launchAtLogin) { _, newValue in
                        guard !isSyncingLaunchAtLogin else {
                            return
                        }
                        updateLaunchAtLogin(newValue)
                    }

                HStack(spacing: 8) {
                    Label(loginItemState.label, systemImage: loginItemState.needsApproval ? "exclamationmark.triangle" : "power")
                        .font(.callout.weight(.medium))
                    Text(loginItemState.message)
                        .font(.callout)
                        .foregroundStyle(.secondary)
                }

                if !loginItemState.isInstalledInApplications {
                    Label("Install Kit Companion in /Applications before enabling login launch.", systemImage: "folder.badge.gearshape")
                        .font(.callout)
                        .foregroundStyle(.secondary)
                }

                if loginItemState.needsApproval {
                    Button {
                        LoginItemService.openSystemSettings()
                    } label: {
                        Label("Open Login Items", systemImage: "gearshape")
                    }
                }
            }

            Toggle("Automatically Check for Updates", isOn: $automaticallyCheckForUpdates)
                .onChange(of: automaticallyCheckForUpdates) { _, newValue in
                    SparkleUpdateService.shared.setAutomaticallyChecksForUpdates(newValue)
                }

            if let loginItemError {
                Text(loginItemError)
                    .font(.callout)
                    .foregroundStyle(.red)
            }

            Text("The companion app is optional. It only runs read-only kit commands in-app; mutating commands stay in Terminal. App updates are verified and installed by Sparkle.")
                .font(.callout)
                .foregroundStyle(.secondary)
        }
        .formStyle(.grouped)
        .padding(20)
        .frame(width: 520)
        .onAppear {
            refreshLaunchAtLogin()
        }
        .onReceive(NotificationCenter.default.publisher(for: NSApplication.didBecomeActiveNotification)) { _ in
            refreshLaunchAtLogin()
        }
    }

    private func chooseKitBinary() {
        let panel = NSOpenPanel()
        panel.canChooseFiles = true
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = false
        panel.directoryURL = URL(fileURLWithPath: (kitBinaryPath as NSString).deletingLastPathComponent, isDirectory: true)
        if panel.runModal() == .OK, let url = panel.url {
            kitBinaryPath = url.path
        }
    }

    private func updateLaunchAtLogin(_ enabled: Bool) {
        do {
            let state = try LoginItemService.setEnabled(enabled)
            loginItemState = state
            syncLaunchAtLoginToggle(state.isEnabled)
            loginItemError = nil
        } catch {
            refreshLaunchAtLogin()
            loginItemError = error.localizedDescription
        }
    }

    private func refreshLaunchAtLogin() {
        let state = LoginItemService.currentState()
        loginItemState = state
        syncLaunchAtLoginToggle(state.isEnabled)
    }

    private func syncLaunchAtLoginToggle(_ enabled: Bool) {
        isSyncingLaunchAtLogin = true
        launchAtLogin = enabled
        DispatchQueue.main.async {
            isSyncingLaunchAtLogin = false
        }
    }
}
