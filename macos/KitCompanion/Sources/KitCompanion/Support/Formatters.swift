import Foundation

enum KitDisplay {
    static func shortPath(_ path: String, maxLength: Int = 58) -> String {
        var value = path.replacingOccurrences(of: NSHomeDirectory(), with: "~")
        guard value.count > maxLength else {
            return value
        }
        let head = value.prefix(maxLength / 2)
        let tail = value.suffix(maxLength / 2)
        value = "\(head)...\(tail)"
        return value
    }

    static func relativeDate(_ value: Date?) -> String {
        guard let value else {
            return "Never"
        }
        return RelativeDateTimeFormatter().localizedString(for: value, relativeTo: Date())
    }
}
