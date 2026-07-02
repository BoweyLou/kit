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

private enum DashboardWindowPresenter {
    private static var closeObserver: NSObjectProtocol?

    static func bringToFront() {
        NSApp.setActivationPolicy(.regular)
        focusWindow()
        DispatchQueue.main.async {
            focusWindow()
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.15) {
            focusWindow()
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) {
            focusWindow()
        }
    }

    private static func focusWindow() {
        NSRunningApplication.current.activate(options: [.activateAllWindows])
        NSApp.activate(ignoringOtherApps: true)

        guard let dashboardWindow = NSApp.windows.first(where: { $0.title == "Kit Dashboard" }) else {
            return
        }
        observeDashboardClose(dashboardWindow)
        dashboardWindow.deminiaturize(nil)
        dashboardWindow.makeKeyAndOrderFront(nil)
        dashboardWindow.orderFrontRegardless()
    }

    private static func observeDashboardClose(_ window: NSWindow) {
        guard closeObserver == nil else {
            return
        }
        closeObserver = NotificationCenter.default.addObserver(
            forName: NSWindow.willCloseNotification,
            object: window,
            queue: .main
        ) { _ in
            if let observer = closeObserver {
                NotificationCenter.default.removeObserver(observer)
            }
            closeObserver = nil
            NSApp.setActivationPolicy(.accessory)
        }
    }
}
