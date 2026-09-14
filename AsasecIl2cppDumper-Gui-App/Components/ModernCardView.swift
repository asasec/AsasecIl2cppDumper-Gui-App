import UIKit

final class ModernCardView: UIView {

    override init(frame: CGRect) {

        super.init(frame: frame)

        setup()
    }

    required init?(coder: NSCoder) {

        super.init(coder: coder)

        setup()
    }

    private func setup() {

        translatesAutoresizingMaskIntoConstraints = false

        backgroundColor = AppTheme.card

        layer.cornerRadius = AppTheme.cornerRadius

        layer.masksToBounds = false

        layer.shadowColor = UIColor.black.cgColor

        layer.shadowOpacity =
            AppTheme.shadowOpacity

        layer.shadowRadius =
            AppTheme.shadowRadius

        layer.shadowOffset =
            AppTheme.shadowOffset
    }

    override func layoutSubviews() {

        super.layoutSubviews()

        layer.shadowPath =
            UIBezierPath(
                roundedRect: bounds,
                cornerRadius: AppTheme.cornerRadius
            ).cgPath
    }
}
