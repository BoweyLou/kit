import AppKit
import SwiftUI

struct MenuBarView: View {
    @ObservedObject var store: KitCompanionStore
    @Environment(\.openWindow) private var openWindow

    var body: some View {
        Button {
            store.refreshTargets()
        } label: {
            Label("Refresh", systemImage: "arrow.clockwise")
        }

        Button {
            openWindow(id: "dashboard")
        } label: {
            Label("Open Dashboard", systemImage: "rectangle.3.group")
        }

        Divider()

        if store.targets.isEmpty {
            Text("No targets loaded")
                .foregroundStyle(.secondary)
        } else {
            ForEach(store.targets.prefix(6)) { target in
                Button {
                    store.select(target)
                    openWindow(id: "dashboard")
                } label: {
                    Label(target.name, systemImage: target.isDirty ? "exclamationmark.circle" : "checkmark.circle")
                }
            }
        }

        Divider()

        Button {
            store.previewBatchUpdate()
            openWindow(id: "dashboard")
        } label: {
            Label("Preview Updates", systemImage: "doc.text.magnifyingglass")
        }

        Button {
            store.checkForUpdates()
            openWindow(id: "dashboard")
        } label: {
            Label("Check for App Update", systemImage: "arrow.down.app")
        }

        SettingsLink {
            Label("Settings", systemImage: "gearshape")
        }

        Button {
            AppTermination.userRequestedQuit = true
            NSApplication.shared.terminate(nil)
        } label: {
            Label("Quit", systemImage: "power")
        }
    }
}
