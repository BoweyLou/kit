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
    targets: [
        .executableTarget(
            name: "KitCompanion",
            path: "Sources/KitCompanion"
        )
    ]
)
