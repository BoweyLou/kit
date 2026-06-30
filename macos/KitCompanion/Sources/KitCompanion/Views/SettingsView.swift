import AppKit
import SwiftUI

struct SettingsView: View {
    @AppStorage(KitSettingsKeys.kitBinaryPath) private var kitBinaryPath = KitSettings.defaultKitBinaryPath()

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
}
