import AppKit
import ServiceManagement
import SwiftUI

struct SettingsView: View {
    @AppStorage(KitSettingsKeys.kitBinaryPath) private var kitBinaryPath = KitSettings.defaultKitBinaryPath()
    @AppStorage(KitSettingsKeys.automaticallyCheckForUpdates) private var automaticallyCheckForUpdates = true
    @State private var launchAtLogin = LoginItemService.isEnabled
    @State private var loginItemError: String?

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

            Toggle("Launch at Login", isOn: $launchAtLogin)
                .onChange(of: launchAtLogin) { _, newValue in
                    updateLaunchAtLogin(newValue)
                }

            Toggle("Automatically Check for Updates", isOn: $automaticallyCheckForUpdates)

            if let loginItemError {
                Text(loginItemError)
                    .font(.callout)
                    .foregroundStyle(.red)
            }

            Text("The companion app is optional. It only runs read-only kit commands in-app; mutating commands stay in Terminal.")
                .font(.callout)
                .foregroundStyle(.secondary)
        }
        .formStyle(.grouped)
        .padding(20)
        .frame(width: 520)
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
            try LoginItemService.setEnabled(enabled)
            loginItemError = nil
        } catch {
            launchAtLogin = LoginItemService.isEnabled
            loginItemError = error.localizedDescription
        }
    }
}
