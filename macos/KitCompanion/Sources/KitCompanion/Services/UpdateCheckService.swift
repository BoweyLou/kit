import Foundation

final class UpdateCheckService {
    struct GitHubRelease: Decodable {
        struct Asset: Decodable {
            let name: String
            let browserDownloadURL: URL

            enum CodingKeys: String, CodingKey {
                case name
                case browserDownloadURL = "browser_download_url"
            }
        }

        let tagName: String
        let htmlURL: URL
        let assets: [Asset]

        enum CodingKeys: String, CodingKey {
            case tagName = "tag_name"
            case htmlURL = "html_url"
            case assets
        }
    }

    private let latestReleaseURL = URL(string: "https://api.github.com/repos/BoweyLou/kit/releases/latest")!

    func check(currentVersion: String) async -> UpdateCheckResult {
        do {
            var request = URLRequest(url: latestReleaseURL)
            request.setValue("application/vnd.github+json", forHTTPHeaderField: "Accept")
            request.timeoutInterval = 15

            let (data, response) = try await URLSession.shared.data(for: request)
            if let http = response as? HTTPURLResponse, !(200..<300).contains(http.statusCode) {
                return failure(currentVersion: currentVersion, "Update check failed with HTTP \(http.statusCode)")
            }

            let release = try JSONDecoder().decode(GitHubRelease.self, from: data)
            let download = release.assets.first { asset in
                asset.name.hasSuffix(".dmg") && asset.name.contains("KitCompanion")
            }?.browserDownloadURL
            return UpdateCheckResult(
                currentVersion: currentVersion,
                latestVersion: release.tagName.trimmingCharacters(in: CharacterSet(charactersIn: "vV")),
                releaseURL: release.htmlURL,
                downloadURL: download,
                checkedAt: Date(),
                errorMessage: nil
            )
        } catch {
            return failure(currentVersion: currentVersion, error.localizedDescription)
        }
    }

    private func failure(currentVersion: String, _ message: String) -> UpdateCheckResult {
        UpdateCheckResult(
            currentVersion: currentVersion,
            latestVersion: nil,
            releaseURL: nil,
            downloadURL: nil,
            checkedAt: Date(),
            errorMessage: message
        )
    }
}
