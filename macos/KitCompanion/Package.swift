// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "KitCompanion",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "KitCompanion", targets: ["KitCompanion"])
    ],
    dependencies: [
        .package(url: "https://github.com/sparkle-project/Sparkle.git", from: "2.9.3")
    ],
    targets: [
        .executableTarget(
            name: "KitCompanion",
            dependencies: [
                .product(name: "Sparkle", package: "Sparkle")
            ],
            path: "Sources/KitCompanion"
        )
    ]
)
