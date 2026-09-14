import UIKit

enum AppTheme {

    // MARK: - Accent

    static let accent = UIColor(
        red: 0.08,
        green: 0.69,
        blue: 0.80,
        alpha: 1.0
    )

    static let accentDark = UIColor(
        red: 0.05,
        green: 0.55,
        blue: 0.66,
        alpha: 1.0
    )

    // MARK: - Status

    static let success = UIColor(
        red: 0.22,
        green: 0.82,
        blue: 0.48,
        alpha: 1.0
    )

    static let warning = UIColor(
        red: 1.00,
        green: 0.67,
        blue: 0.20,
        alpha: 1.0
    )

    static let danger = UIColor(
        red: 1.00,
        green: 0.29,
        blue: 0.32,
        alpha: 1.0
    )

    // MARK: - Background

    static let background = UIColor { trait in

        if trait.userInterfaceStyle == .dark {

            return UIColor(
                red: 0.035,
                green: 0.042,
                blue: 0.052,
                alpha: 1.0
            )
        }

        return UIColor(
            red: 0.95,
            green: 0.96,
            blue: 0.97,
            alpha: 1.0
        )
    }

    static let card = UIColor { trait in

        if trait.userInterfaceStyle == .dark {

            return UIColor(
                red: 0.075,
                green: 0.085,
                blue: 0.105,
                alpha: 1.0
            )
        }

        return UIColor.white
    }

    static let secondaryCard = UIColor { trait in

        if trait.userInterfaceStyle == .dark {

            return UIColor(
                red: 0.105,
                green: 0.118,
                blue: 0.14,
                alpha: 1.0
            )
        }

        return UIColor(
            red: 0.965,
            green: 0.972,
            blue: 0.98,
            alpha: 1.0
        )
    }

    // MARK: - Console

    static let consoleBackground = UIColor(
        red: 0.035,
        green: 0.040,
        blue: 0.047,
        alpha: 1.0
    )

    static let consoleText = UIColor(
        red: 0.78,
        green: 0.82,
        blue: 0.86,
        alpha: 1.0
    )

    // MARK: - Text

    static let primaryText = UIColor { trait in

        if trait.userInterfaceStyle == .dark {
            return UIColor.white
        }

        return UIColor(
            red: 0.07,
            green: 0.08,
            blue: 0.10,
            alpha: 1.0
        )
    }

    static let secondaryText = UIColor { trait in

        if trait.userInterfaceStyle == .dark {

            return UIColor(
                red: 0.60,
                green: 0.64,
                blue: 0.69,
                alpha: 1.0
            )
        }

        return UIColor(
            red: 0.42,
            green: 0.45,
            blue: 0.50,
            alpha: 1.0
        )
    }

    // MARK: - Common

    static let cornerRadius: CGFloat = 20.0

    static let smallCornerRadius: CGFloat = 14.0

    static let shadowOpacity: Float = 0.08

    static let shadowRadius: CGFloat = 18.0

    static let shadowOffset = CGSize(
        width: 0,
        height: 7
    )

    // MARK: - Symbols

    static func symbol(
        _ name: String,
        size: CGFloat = 18,
        weight: UIImage.SymbolWeight = .medium
    ) -> UIImage? {

        let configuration = UIImage.SymbolConfiguration(
            pointSize: size,
            weight: weight
        )

        return UIImage(
            systemName: name,
            withConfiguration: configuration
        )
    }
}
