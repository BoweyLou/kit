import AppKit
import Foundation

enum DashboardWindowPresenter {
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
