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
            showDashboard(section: .overview)
        } label: {
            Label("Open Dashboard", systemImage: "rectangle.3.group")
        }

        Button {
            store.loadCommandMap()
            showDashboard(section: .commands)
        } label: {
            Label("Command Browser", systemImage: "terminal")
        }

        Button {
            showDashboard(section: .learning)
        } label: {
            Label("Learning", systemImage: "graduationcap")
        }
        .accessibilityLabel("Open Learning Dashboard")

        Divider()

        if store.targets.isEmpty {
            Text("No targets loaded")
                .foregroundStyle(.secondary)
        } else {
            ForEach(store.targets.prefix(6)) { target in
                Button {
                    store.select(target)
                    showDashboard(section: .overview)
                } label: {
                    Label(target.name, systemImage: target.isDirty ? "exclamationmark.circle" : "checkmark.circle")
                }
            }
        }

        Divider()

        Button {
            store.previewBatchUpdate()
            showDashboard(section: .batch)
        } label: {
            Label("Preview Updates", systemImage: "doc.text.magnifyingglass")
        }

        Button {
            store.checkForUpdates()
            showDashboard()
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

    private func showDashboard(section: DashboardSection? = nil) {
        if let section {
            store.dashboardSection = section
        }
        openWindow(id: "dashboard")
        DashboardWindowPresenter.bringToFront()
    }
}
