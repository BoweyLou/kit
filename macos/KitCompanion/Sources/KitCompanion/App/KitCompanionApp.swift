import AppKit
import SwiftUI

enum AppTermination {
    static var userRequestedQuit = false
    static var allowsUpdaterTermination = false
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        false
    }

    func applicationShouldTerminate(_ sender: NSApplication) -> NSApplication.TerminateReply {
        (AppTermination.userRequestedQuit || AppTermination.allowsUpdaterTermination) ? .terminateNow : .terminateCancel
    }
}

@main
struct KitCompanionApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    @StateObject private var store = KitCompanionStore()

    var body: some Scene {
        MenuBarExtra {
            MenuBarView(store: store)
        } label: {
            Label(store.menuTitle, systemImage: store.menuSymbolName)
                .accessibilityLabel(Text(store.menuTitle))
        }
        .menuBarExtraStyle(.menu)

        Window("Kit Dashboard", id: "dashboard") {
            DashboardView(store: store)
        }
        .defaultSize(width: 860, height: 520)

        Settings {
            SettingsView()
        }
    }
}
