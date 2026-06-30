# Kit Companion Configuration

Kit Companion is optional and stores app-only settings in macOS user defaults.
These settings do not change the required `kit` CLI setup.

| Setting | Default | Purpose |
| --- | --- | --- |
| `kitBinaryPath` | `~/.local/bin/kit` | Selects the launcher used for read-only kit commands in the app. |
| `automaticallyCheckForUpdates` | `true` | Controls whether Sparkle checks the Kit Companion appcast for app updates. |

Sparkle update metadata is embedded in the app bundle:

| Info.plist key | Value |
| --- | --- |
| `SUFeedURL` | `https://github.com/BoweyLou/kit/releases/latest/download/KitCompanion-appcast.xml` |
| `SUPublicEDKey` | Public EdDSA key used to verify Sparkle update archives. |

The private Sparkle signing key must stay outside the repository. Local release
builds use the `com.boweylou.KitCompanion` Keychain account by default, while
automation can pass the key through `SPARKLE_ED_PRIVATE_KEY`.
