import UIKit

final class SettingsViewController:
    UIViewController {

    private let scrollView =
        UIScrollView()

    private let contentView =
        UIView()

    private let titleLabel =
        UILabel()

    private let subtitleLabel =
        UILabel()

    private let engineCard =
        UIView()

    private let engineIcon =
        UIImageView()

    private let engineTitle =
        UILabel()

    private let engineSubtitle =
        UILabel()

    private let engineValue =
        UILabel()

    private let appearanceCard =
        UIView()

    private let appearanceIcon =
        UIImageView()

    private let appearanceTitle =
        UILabel()

    private let appearanceSubtitle =
        UILabel()

    private let closeButton =
        UIButton(
            type: .system
        )

    override func viewDidLoad() {

        super.viewDidLoad()

        view.backgroundColor =
            AppTheme.background

        setupUI()

        setupConstraints()
    }

    private func setupUI() {

        scrollView.translatesAutoresizingMaskIntoConstraints =
            false

        scrollView.showsVerticalScrollIndicator =
            false

        view.addSubview(scrollView)

        contentView.translatesAutoresizingMaskIntoConstraints =
            false

        scrollView.addSubview(
            contentView
        )

        titleLabel.translatesAutoresizingMaskIntoConstraints =
            false

        titleLabel.text =
            "Settings"

        titleLabel.font =
            UIFont.systemFont(
                ofSize: 30,
                weight: .bold
            )

        titleLabel.textColor =
            AppTheme.primaryText

        contentView.addSubview(
            titleLabel
        )

        subtitleLabel.translatesAutoresizingMaskIntoConstraints =
            false

        subtitleLabel.text =
            "Configure your dumping environment."

        subtitleLabel.font =
            UIFont.systemFont(
                ofSize: 14,
                weight: .regular
            )

        subtitleLabel.textColor =
            AppTheme.secondaryText

        contentView.addSubview(
            subtitleLabel
        )

        createEngineCard()

        createAppearanceCard()

        closeButton.translatesAutoresizingMaskIntoConstraints =
            false

        closeButton.setTitle(
            "Done",
            for: .normal
        )

        closeButton.setTitleColor(
            .white,
            for: .normal
        )

        closeButton.titleLabel?.font =
            UIFont.systemFont(
                ofSize: 16,
                weight: .bold
            )

        closeButton.backgroundColor =
            AppTheme.accent

        closeButton.layer.cornerRadius =
            16

        closeButton.addTarget(
            self,
            action: #selector(closePressed),
            for: .touchUpInside
        )

        contentView.addSubview(
            closeButton
        )
    }

    private func createEngineCard() {

        engineCard.translatesAutoresizingMaskIntoConstraints =
            false

        engineCard.backgroundColor =
            AppTheme.card

        engineCard.layer.cornerRadius =
            18

        contentView.addSubview(
            engineCard
        )

        engineIcon.translatesAutoresizingMaskIntoConstraints =
            false

        engineIcon.image =
            AppTheme.symbol(
                "cpu",
                size: 20,
                weight: .semibold
            )

        engineIcon.tintColor =
            AppTheme.accent

        engineCard.addSubview(
            engineIcon
        )

        engineTitle.translatesAutoresizingMaskIntoConstraints =
            false

        engineTitle.text =
            "Dump Engine"

        engineTitle.font =
            UIFont.systemFont(
                ofSize: 16,
                weight: .semibold
            )

        engineTitle.textColor =
            AppTheme.primaryText

        engineCard.addSubview(
            engineTitle
        )

        engineSubtitle.translatesAutoresizingMaskIntoConstraints =
            false

        engineSubtitle.text =
            "IL2CPP analysis engine"

        engineSubtitle.font =
            UIFont.systemFont(
                ofSize: 12,
                weight: .regular
            )

        engineSubtitle.textColor =
            AppTheme.secondaryText

        engineCard.addSubview(
            engineSubtitle
        )

        engineValue.translatesAutoresizingMaskIntoConstraints =
            false

        engineValue.text =
            "PERFARE"

        engineValue.font =
            UIFont.monospacedSystemFont(
                ofSize: 11,
                weight: .bold
            )

        engineValue.textColor =
            AppTheme.accent

        engineCard.addSubview(
            engineValue
        )
    }

    private func createAppearanceCard() {

        appearanceCard.translatesAutoresizingMaskIntoConstraints =
            false

        appearanceCard.backgroundColor =
            AppTheme.card

        appearanceCard.layer.cornerRadius =
            18

        contentView.addSubview(
            appearanceCard
        )

        appearanceIcon.translatesAutoresizingMaskIntoConstraints =
            false

        appearanceIcon.image =
            AppTheme.symbol(
                "circle.lefthalf.fill",
                size: 20,
                weight: .medium
            )

        appearanceIcon.tintColor =
            AppTheme.accent

        appearanceCard.addSubview(
            appearanceIcon
        )

        appearanceTitle.translatesAutoresizingMaskIntoConstraints =
            false

        appearanceTitle.text =
            "Appearance"

        appearanceTitle.font =
            UIFont.systemFont(
                ofSize: 16,
                weight: .semibold
            )

        appearanceTitle.textColor =
            AppTheme.primaryText

        appearanceCard.addSubview(
            appearanceTitle
        )

        appearanceSubtitle.translatesAutoresizingMaskIntoConstraints =
            false

        appearanceSubtitle.text =
            "Automatically follows iOS appearance."

        appearanceSubtitle.font =
            UIFont.systemFont(
                ofSize: 12,
                weight: .regular
            )

        appearanceSubtitle.textColor =
            AppTheme.secondaryText

        appearanceCard.addSubview(
            appearanceSubtitle
        )
    }

    private func setupConstraints() {

        NSLayoutConstraint.activate([

            scrollView.topAnchor.constraint(
                equalTo:
                    view.safeAreaLayoutGuide.topAnchor
            ),

            scrollView.leadingAnchor.constraint(
                equalTo: view.leadingAnchor
            ),

            scrollView.trailingAnchor.constraint(
                equalTo: view.trailingAnchor
            ),

            scrollView.bottomAnchor.constraint(
                equalTo: view.bottomAnchor
            ),

            contentView.topAnchor.constraint(
                equalTo:
                    scrollView.contentLayoutGuide.topAnchor
            ),

            contentView.leadingAnchor.constraint(
                equalTo:
                    scrollView.contentLayoutGuide.leadingAnchor
            ),

            contentView.trailingAnchor.constraint(
                equalTo:
                    scrollView.contentLayoutGuide.trailingAnchor
            ),

            contentView.bottomAnchor.constraint(
                equalTo:
                    scrollView.contentLayoutGuide.bottomAnchor
            ),

            contentView.widthAnchor.constraint(
                equalTo:
                    scrollView.frameLayoutGuide.widthAnchor
            ),

            titleLabel.topAnchor.constraint(
                equalTo: contentView.topAnchor,
                constant: 25
            ),

            titleLabel.leadingAnchor.constraint(
                equalTo: contentView.leadingAnchor,
                constant: 22
            ),

            subtitleLabel.topAnchor.constraint(
                equalTo: titleLabel.bottomAnchor,
                constant: 4
            ),

            subtitleLabel.leadingAnchor.constraint(
                equalTo: titleLabel.leadingAnchor
            ),

            engineCard.topAnchor.constraint(
                equalTo: subtitleLabel.bottomAnchor,
                constant: 25
            ),

            engineCard.leadingAnchor.constraint(
                equalTo: contentView.leadingAnchor,
                constant: 18
            ),

            engineCard.trailingAnchor.constraint(
                equalTo: contentView.trailingAnchor,
                constant: -18
            ),

            engineCard.heightAnchor.constraint(
                equalToConstant: 78
            ),

            engineIcon.leadingAnchor.constraint(
                equalTo: engineCard.leadingAnchor,
                constant: 17
            ),

            engineIcon.centerYAnchor.constraint(
                equalTo: engineCard.centerYAnchor
            ),

            engineIcon.widthAnchor.constraint(
                equalToConstant: 27
            ),

            engineIcon.heightAnchor.constraint(
                equalToConstant: 27
            ),

            engineTitle.leadingAnchor.constraint(
                equalTo: engineIcon.trailingAnchor,
                constant: 14
            ),

            engineTitle.topAnchor.constraint(
                equalTo: engineCard.topAnchor,
                constant: 17
            ),

            engineSubtitle.leadingAnchor.constraint(
                equalTo: engineTitle.leadingAnchor
            ),

            engineSubtitle.topAnchor.constraint(
                equalTo: engineTitle.bottomAnchor,
                constant: 3
            ),

            engineValue.trailingAnchor.constraint(
                equalTo: engineCard.trailingAnchor,
                constant: -17
            ),

            engineValue.centerYAnchor.constraint(
                equalTo: engineCard.centerYAnchor
            ),

            appearanceCard.topAnchor.constraint(
                equalTo: engineCard.bottomAnchor,
                constant: 12
            ),

            appearanceCard.leadingAnchor.constraint(
                equalTo: engineCard.leadingAnchor
            ),

            appearanceCard.trailingAnchor.constraint(
                equalTo: engineCard.trailingAnchor
            ),

            appearanceCard.heightAnchor.constraint(
                equalToConstant: 78
            ),

            appearanceIcon.leadingAnchor.constraint(
                equalTo: appearanceCard.leadingAnchor,
                constant: 17
            ),

            appearanceIcon.centerYAnchor.constraint(
                equalTo: appearanceCard.centerYAnchor
            ),

            appearanceIcon.widthAnchor.constraint(
                equalToConstant: 27
            ),

            appearanceIcon.heightAnchor.constraint(
                equalToConstant: 27
            ),

            appearanceTitle.leadingAnchor.constraint(
                equalTo: appearanceIcon.trailingAnchor,
                constant: 14
            ),

            appearanceTitle.topAnchor.constraint(
                equalTo: appearanceCard.topAnchor,
                constant: 17
            ),

            appearanceSubtitle.leadingAnchor.constraint(
                equalTo: appearanceTitle.leadingAnchor
            ),

            appearanceSubtitle.topAnchor.constraint(
                equalTo: appearanceTitle.bottomAnchor,
                constant: 3
            ),

            closeButton.topAnchor.constraint(
                equalTo: appearanceCard.bottomAnchor,
                constant: 25
            ),

            closeButton.leadingAnchor.constraint(
                equalTo: appearanceCard.leadingAnchor
            ),

            closeButton.trailingAnchor.constraint(
                equalTo: appearanceCard.trailingAnchor
            ),

            closeButton.heightAnchor.constraint(
                equalToConstant: 55
            ),

            closeButton.bottomAnchor.constraint(
                equalTo: contentView.bottomAnchor,
                constant: -30
            )
        ])
    }

    @objc
    private func closePressed() {

        dismiss(
            animated: true
        )
    }
}
