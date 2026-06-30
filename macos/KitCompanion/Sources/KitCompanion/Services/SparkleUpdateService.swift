import Foundation
import Sparkle

@MainActor
final class SparkleUpdateService: NSObject, SPUUpdaterDelegate {
    static let shared = SparkleUpdateService()

    private var controller: SPUStandardUpdaterController!

    private override init() {
        super.init()
        controller = SPUStandardUpdaterController(
            startingUpdater: true,
            updaterDelegate: self,
            userDriverDelegate: nil
        )
    }

    func setAutomaticallyChecksForUpdates(_ enabled: Bool) {
        controller.updater.automaticallyChecksForUpdates = enabled
        UserDefaults.standard.set(enabled, forKey: KitSettingsKeys.automaticallyCheckForUpdates)
    }

    func checkForUpdates() {
        controller.checkForUpdates(nil)
    }

    func checkForUpdatesInBackground() {
        controller.updater.checkForUpdatesInBackground()
    }

    func updater(_ updater: SPUUpdater, willInstallUpdate item: SUAppcastItem) {
        AppTermination.allowsUpdaterTermination = true
    }

    func updaterWillRelaunchApplication(_ updater: SPUUpdater) {
        AppTermination.allowsUpdaterTermination = true
    }
}
