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
    private let launchOptions = KitCompanionLaunchOptions.parse(arguments: CommandLine.arguments)

    var body: some Scene {
        MenuBarExtra {
            MenuBarView(store: store)
        } label: {
            MenuBarLabelView(store: store, launchOptions: launchOptions)
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

private struct MenuBarLabelView: View {
    @ObservedObject var store: KitCompanionStore
    let launchOptions: KitCompanionLaunchOptions?

    var body: some View {
        Label(store.menuTitle, systemImage: store.menuSymbolName)
            .accessibilityLabel(Text(store.menuTitle))
            .background {
                LaunchRouteHandler(store: store, launchOptions: launchOptions)
            }
    }
}

private struct LaunchRouteHandler: View {
    @ObservedObject var store: KitCompanionStore
    let launchOptions: KitCompanionLaunchOptions?

    @Environment(\.openWindow) private var openWindow
    @State private var didHandleLaunchRoute = false

    var body: some View {
        Color.clear
            .frame(width: 0, height: 0)
            .allowsHitTesting(false)
            .task {
                guard !didHandleLaunchRoute, let launchOptions else {
                    return
                }
                didHandleLaunchRoute = true
                store.dashboardSection = launchOptions.dashboardSection
                openWindow(id: "dashboard")
                DashboardWindowPresenter.bringToFront()
            }
    }
}
