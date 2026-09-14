import UIKit

final class PathInputView: UIView {

    enum InputType {
        case executable
        case metadata
    }

    let textField = UITextField()

    private let iconView = UIImageView()

    private let titleLabel = UILabel()

    private let browseButton = UIButton(
        type: .system
    )

    private let selectedIndicator = UIView()

    private let type: InputType

    var browseAction: (() -> Void)?

    init(type: InputType) {

        self.type = type

        super.init(frame: .zero)

        setup()
    }

    required init?(coder: NSCoder) {

        self.type = .executable

        super.init(coder: coder)

        setup()
    }

    private func setup() {

        backgroundColor =
            AppTheme.secondaryCard

        layer.cornerRadius =
            AppTheme.smallCornerRadius

        layer.borderWidth = 1

        layer.borderColor =
            UIColor.black.withAlphaComponent(
                0.06
            ).cgColor

        setupIcon()

        setupTitle()

        setupTextField()

        setupBrowseButton()

        setupIndicator()

        setupConstraints()
    }

    private func setupIcon() {

        iconView.translatesAutoresizingMaskIntoConstraints = false

        switch type {

        case .executable:

            iconView.image =
                AppTheme.symbol(
                    "terminal.fill",
                    size: 17,
                    weight: .semibold
                )

        case .metadata:

            iconView.image =
                AppTheme.symbol(
                    "doc.text.fill",
                    size: 17,
                    weight: .semibold
                )
        }

        iconView.tintColor =
            AppTheme.accent

        iconView.contentMode =
            .scaleAspectFit

        addSubview(iconView)
    }

    private func setupTitle() {

        titleLabel.translatesAutoresizingMaskIntoConstraints = false

        switch type {

        case .executable:
            titleLabel.text = "EXECUTABLE"

        case .metadata:
            titleLabel.text = "GLOBAL METADATA"
        }

        titleLabel.font =
            UIFont.systemFont(
                ofSize: 10,
                weight: .bold
            )

        titleLabel.textColor =
            AppTheme.secondaryText

        addSubview(titleLabel)
    }

    private func setupTextField() {

        textField.translatesAutoresizingMaskIntoConstraints = false

        switch type {

        case .executable:

            textField.placeholder =
                "Select executable..."

        case .metadata:

            textField.placeholder =
                "Select global-metadata.dat..."
        }

        textField.font =
            UIFont.systemFont(
                ofSize: 14,
                weight: .medium
            )

        textField.textColor =
            AppTheme.primaryText

        textField.tintColor =
            AppTheme.accent

        textField.autocapitalizationType =
            .none

        textField.autocorrectionType =
            .no

        textField.spellCheckingType =
            .no

        textField.clearButtonMode =
            .whileEditing

        addSubview(textField)
    }

    private func setupBrowseButton() {

        browseButton.translatesAutoresizingMaskIntoConstraints = false

        browseButton.backgroundColor =
            AppTheme.accent.withAlphaComponent(
                0.10
            )

        browseButton.layer.cornerRadius = 11

        browseButton.setImage(
            AppTheme.symbol(
                "folder.fill",
                size: 17,
                weight: .semibold
            ),
            for: .normal
        )

        browseButton.tintColor =
            AppTheme.accent

        browseButton.addTarget(
            self,
            action: #selector(browsePressed),
            for: .touchUpInside
        )

        addSubview(browseButton)
    }

    private func setupIndicator() {

        selectedIndicator.translatesAutoresizingMaskIntoConstraints = false

        selectedIndicator.backgroundColor =
            AppTheme.success

        selectedIndicator.layer.cornerRadius = 3

        selectedIndicator.alpha = 0

        addSubview(selectedIndicator)
    }

    private func setupConstraints() {

        NSLayoutConstraint.activate([

            iconView.leadingAnchor.constraint(
                equalTo: leadingAnchor,
                constant: 14
            ),

            iconView.centerYAnchor.constraint(
                equalTo: centerYAnchor
            ),

            iconView.widthAnchor.constraint(
                equalToConstant: 23
            ),

            iconView.heightAnchor.constraint(
                equalToConstant: 23
            ),

            titleLabel.leadingAnchor.constraint(
                equalTo: iconView.trailingAnchor,
                constant: 10
            ),

            titleLabel.topAnchor.constraint(
                equalTo: topAnchor,
                constant: 8
            ),

            titleLabel.trailingAnchor.constraint(
                lessThanOrEqualTo:
                    browseButton.leadingAnchor,
                constant: -10
            ),

            textField.leadingAnchor.constraint(
                equalTo: titleLabel.leadingAnchor
            ),

            textField.trailingAnchor.constraint(
                equalTo: browseButton.leadingAnchor,
                constant: -10
            ),

            textField.topAnchor.constraint(
                equalTo: titleLabel.bottomAnchor,
                constant: 1
            ),

            textField.bottomAnchor.constraint(
                equalTo: bottomAnchor,
                constant: -7
            ),

            browseButton.trailingAnchor.constraint(
                equalTo: trailingAnchor,
                constant: -10
            ),

            browseButton.centerYAnchor.constraint(
                equalTo: centerYAnchor
            ),

            browseButton.widthAnchor.constraint(
                equalToConstant: 44
            ),

            browseButton.heightAnchor.constraint(
                equalToConstant: 44
            ),

            selectedIndicator.trailingAnchor.constraint(
                equalTo: trailingAnchor,
                constant: -5
            ),

            selectedIndicator.topAnchor.constraint(
                equalTo: topAnchor,
                constant: 5
            ),

            selectedIndicator.bottomAnchor.constraint(
                equalTo: bottomAnchor,
                constant: -5
            ),

            selectedIndicator.widthAnchor.constraint(
                equalToConstant: 4
            )
        ])
    }

    func setSelected(
        _ selected: Bool
    ) {

        UIView.animate(
            withDuration: 0.25
        ) {

            self.selectedIndicator.alpha =
                selected ? 1.0 : 0.0
        }
    }

    @objc
    private func browsePressed() {

        browseAction?()
    }
}
