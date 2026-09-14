import UIKit

final class MainViewController:
    UIViewController {

    // MARK: Services

    private let filePicker =
        FilePickerService()

    private let dumpManager =
        DumpManager()

    // MARK: Scroll

    private let scrollView =
        UIScrollView()

    private let contentView =
        UIView()

    // MARK: Header

    private let headerView =
        UIView()

    private let logoView =
        UIView()

    private let logoImageView =
        UIImageView()

    private let titleLabel =
        UILabel()

    private let subtitleLabel =
        UILabel()

    private let infoButton =
        UIButton(
            type: .system
        )

    // MARK: Hero

    private let heroCard =
        ModernCardView()

    private let heroIconContainer =
        UIView()

    private let heroIcon =
        UIImageView()

    private let heroTitle =
        UILabel()

    private let heroSubtitle =
        UILabel()

    private let readyBadge =
        UIView()

    private let readyDot =
        UIView()

    private let readyLabel =
        UILabel()

    // MARK: Files

    private let pathsCard =
        ModernCardView()

    private let pathsTitle =
        UILabel()

    private let pathsSubtitle =
        UILabel()

    private let executableInput =
        PathInputView(
            type: .executable
        )

    private let metadataInput =
        PathInputView(
            type: .metadata
        )

    // MARK: Output

    private let outputConsole =
        OutputConsoleView()

    // MARK: Bottom

    private let bottomCard =
        ModernCardView()

    private let dumpButton =
        UIButton(
            type: .system
        )

    private let dumpTitleLabel =
        UILabel()

    private let dumpIcon =
        UIImageView()

    private let dumpSpinner =
        UIActivityIndicatorView(
            style: .medium
        )

    private let settingsButton =
        UIButton(
            type: .system
        )

    private let engineLabel =
        UILabel()

    private let engineValue =
        UILabel()

    // MARK: Animation

    private var dumpTimer:
        Timer?

    private var dumpAnimationStep =
        0

    private var isDumping =
        false

    // MARK: Lifecycle

    override func viewDidLoad() {

        super.viewDidLoad()

        view.backgroundColor =
            AppTheme.background

        navigationController?
            .setNavigationBarHidden(
                true,
                animated: false
            )

        setupFilePicker()

        setupDumpManager()

        setupScrollView()

        setupHeader()

        setupHero()

        setupPaths()

        setupOutput()

        setupBottom()

        setupConstraints()
    }

    // MARK: File Picker

    private func setupFilePicker() {

        filePicker.completion = {
            [weak self]
            url,
            type in

            self?.handleSelectedFile(
                url: url,
                type: type
            )
        }

        executableInput.browseAction = {
            [weak self] in

            guard let self = self else {
                return
            }

            self.filePicker.present(
                from: self,
                type: .executable
            )
        }

        metadataInput.browseAction = {
            [weak self] in

            guard let self = self else {
                return
            }

            self.filePicker.present(
                from: self,
                type: .metadata
            )
        }
    }

    // MARK: Dump Manager

    private func setupDumpManager() {

        dumpManager.onLog = {
            [weak self]
            message in

            DispatchQueue.main.async {

                self?.outputConsole.append(
                    message
                )
            }
        }

        dumpManager.onProgress = {
            [weak self]
            progress in

            DispatchQueue.main.async {

                self?.outputConsole.setProgress(
                    progress
                )
            }
        }

        dumpManager.onStateChanged = {
            [weak self]
            state in

            DispatchQueue.main.async {

                self?.handleDumpState(
                    state
                )
            }
        }
    }

    // MARK: Scroll

    private func setupScrollView() {

        scrollView.translatesAutoresizingMaskIntoConstraints =
            false

        scrollView.showsVerticalScrollIndicator =
            false

        scrollView.alwaysBounceVertical =
            true

        scrollView.contentInsetAdjustmentBehavior =
            .never

        view.addSubview(
            scrollView
        )

        contentView.translatesAutoresizingMaskIntoConstraints =
            false

        scrollView.addSubview(
            contentView
        )
    }

    // MARK: Header

    private func setupHeader() {

        headerView.translatesAutoresizingMaskIntoConstraints =
            false

        contentView.addSubview(
            headerView
        )

        logoView.translatesAutoresizingMaskIntoConstraints =
            false

        logoView.backgroundColor =
            AppTheme.accent

        logoView.layer.cornerRadius =
            15

        headerView.addSubview(
            logoView
        )

        logoImageView.translatesAutoresizingMaskIntoConstraints =
            false

        logoImageView.image =
            AppTheme.symbol(
                "cube.box.fill",
                size: 21,
                weight: .bold
            )

        logoImageView.tintColor =
            .white

        logoView.addSubview(
            logoImageView
        )

        titleLabel.translatesAutoresizingMaskIntoConstraints =
            false

        titleLabel.text =
            "ASASEC"

        titleLabel.font =
            UIFont.systemFont(
                ofSize: 20,
                weight: .bold
            )

        titleLabel.textColor =
            AppTheme.primaryText

        headerView.addSubview(
            titleLabel
        )

        subtitleLabel.translatesAutoresizingMaskIntoConstraints =
            false

        subtitleLabel.text =
            "IL2CPP DUMPER"

        subtitleLabel.font =
            UIFont.monospacedSystemFont(
                ofSize: 9,
                weight: .bold
            )

        subtitleLabel.textColor =
            AppTheme.accent

        headerView.addSubview(
            subtitleLabel
        )

        infoButton.translatesAutoresizingMaskIntoConstraints =
            false

        infoButton.setImage(
            AppTheme.symbol(
                "info.circle.fill",
                size: 25,
                weight: .medium
            ),
            for: .normal
        )

        infoButton.tintColor =
            AppTheme.secondaryText

        infoButton.addTarget(
            self,
            action: #selector(infoPressed),
            for: .touchUpInside
        )

        headerView.addSubview(
            infoButton
        )
    }

    // MARK: Hero

    private func setupHero() {

        contentView.addSubview(
            heroCard
        )

        heroIconContainer.translatesAutoresizingMaskIntoConstraints =
            false

        heroIconContainer.backgroundColor =
            AppTheme.accent.withAlphaComponent(
                0.11
            )

        heroIconContainer.layer.cornerRadius =
            20

        heroCard.addSubview(
            heroIconContainer
        )

        heroIcon.translatesAutoresizingMaskIntoConstraints =
            false

        heroIcon.image =
            AppTheme.symbol(
                "cube.fill",
                size: 28,
                weight: .medium
            )

        heroIcon.tintColor =
            AppTheme.accent

        heroIconContainer.addSubview(
            heroIcon
        )

        heroTitle.translatesAutoresizingMaskIntoConstraints =
            false

        heroTitle.text =
            "IL2CPP Workspace"

        heroTitle.font =
            UIFont.systemFont(
                ofSize: 21,
                weight: .bold
            )

        heroTitle.textColor =
            AppTheme.primaryText

        heroCard.addSubview(
            heroTitle
        )

        heroSubtitle.translatesAutoresizingMaskIntoConstraints =
            false

        heroSubtitle.text =
            "Analyze Unity IL2CPP applications\nwith the Perfare dump engine."

        heroSubtitle.font =
            UIFont.systemFont(
                ofSize: 12.5,
                weight: .regular
            )

        heroSubtitle.textColor =
            AppTheme.secondaryText

        heroSubtitle.numberOfLines =
            2

        heroCard.addSubview(
            heroSubtitle
        )

        readyBadge.translatesAutoresizingMaskIntoConstraints =
            false

        readyBadge.backgroundColor =
            AppTheme.success.withAlphaComponent(
                0.10
            )

        readyBadge.layer.cornerRadius =
            12

        heroCard.addSubview(
            readyBadge
        )

        readyDot.translatesAutoresizingMaskIntoConstraints =
            false

        readyDot.backgroundColor =
            AppTheme.success

        readyDot.layer.cornerRadius =
            4

        readyBadge.addSubview(
            readyDot
        )

        readyLabel.translatesAutoresizingMaskIntoConstraints =
            false

        readyLabel.text =
            "READY"

        readyLabel.font =
            UIFont.monospacedSystemFont(
                ofSize: 9,
                weight: .bold
            )

        readyLabel.textColor =
            AppTheme.success

        readyBadge.addSubview(
            readyLabel
        )
    }

    // MARK: Paths

    private func setupPaths() {

        contentView.addSubview(
            pathsCard
        )

        pathsTitle.translatesAutoresizingMaskIntoConstraints =
            false

        pathsTitle.text =
            "Input Files"

        pathsTitle.font =
            UIFont.systemFont(
                ofSize: 19,
                weight: .bold
            )

        pathsTitle.textColor =
            AppTheme.primaryText

        pathsCard.addSubview(
            pathsTitle
        )

        pathsSubtitle.translatesAutoresizingMaskIntoConstraints =
            false

        pathsSubtitle.text =
            "Provide the executable and global metadata."

        pathsSubtitle.font =
            UIFont.systemFont(
                ofSize: 12,
                weight: .regular
            )

        pathsSubtitle.textColor =
            AppTheme.secondaryText

        pathsCard.addSubview(
            pathsSubtitle
        )

        pathsCard.addSubview(
            executableInput
        )

        pathsCard.addSubview(
            metadataInput
        )
    }

    // MARK: Output

    private func setupOutput() {

        outputConsole.translatesAutoresizingMaskIntoConstraints =
            false

        contentView.addSubview(
            outputConsole
        )
    }

    // MARK: Bottom

    private func setupBottom() {

        contentView.addSubview(
            bottomCard
        )

        dumpButton.translatesAutoresizingMaskIntoConstraints =
            false

        dumpButton.backgroundColor =
            AppTheme.accent

        dumpButton.layer.cornerRadius =
            17

        dumpButton.layer.shadowColor =
            AppTheme.accent.cgColor

        dumpButton.layer.shadowOpacity =
            0.28

        dumpButton.layer.shadowRadius =
            14

        dumpButton.layer.shadowOffset =
            CGSize(
                width: 0,
                height: 6
            )

        dumpButton.addTarget(
            self,
            action: #selector(dumpPressed),
            for: .touchUpInside
        )

        bottomCard.addSubview(
            dumpButton
        )

        dumpIcon.translatesAutoresizingMaskIntoConstraints =
            false

        dumpIcon.image =
            AppTheme.symbol(
                "play.fill",
                size: 13,
                weight: .bold
            )

        dumpIcon.tintColor =
            .white

        dumpButton.addSubview(
            dumpIcon
        )

        dumpTitleLabel.translatesAutoresizingMaskIntoConstraints =
            false

        dumpTitleLabel.text =
            "START DUMP"

        dumpTitleLabel.font =
            UIFont.systemFont(
                ofSize: 14,
                weight: .bold
            )

        dumpTitleLabel.textColor =
            .white

        dumpButton.addSubview(
            dumpTitleLabel
        )

        dumpSpinner.translatesAutoresizingMaskIntoConstraints =
            false

        dumpSpinner.color =
            .white

        dumpSpinner.hidesWhenStopped =
            true

        dumpButton.addSubview(
            dumpSpinner
        )

        settingsButton.translatesAutoresizingMaskIntoConstraints =
            false

        settingsButton.backgroundColor =
            AppTheme.secondaryCard

        settingsButton.layer.cornerRadius =
            17

        settingsButton.setImage(
            AppTheme.symbol(
                "gearshape.fill",
                size: 20,
                weight: .medium
            ),
            for: .normal
        )

        settingsButton.tintColor =
            AppTheme.primaryText

        settingsButton.addTarget(
            self,
            action: #selector(settingsPressed),
            for: .touchUpInside
        )

        bottomCard.addSubview(
            settingsButton
        )

        engineLabel.translatesAutoresizingMaskIntoConstraints =
            false

        engineLabel.text =
            "ENGINE"

        engineLabel.font =
            UIFont.monospacedSystemFont(
                ofSize: 9,
                weight: .bold
            )

        engineLabel.textColor =
            AppTheme.secondaryText

        bottomCard.addSubview(
            engineLabel
        )

        engineValue.translatesAutoresizingMaskIntoConstraints =
            false

        engineValue.text =
            "PERFARE"

        engineValue.font =
            UIFont.monospacedSystemFont(
                ofSize: 10,
                weight: .bold
            )

        engineValue.textColor =
            AppTheme.accent

        bottomCard.addSubview(
            engineValue
        )
    }

    // MARK: Constraints

    private func setupConstraints() {

        NSLayoutConstraint.activate([

            // Scroll

            scrollView.topAnchor.constraint(
                equalTo: view.topAnchor
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

            // Content

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

            // Header

            headerView.topAnchor.constraint(
                equalTo:
                    contentView.topAnchor,
                constant: 12
            ),

            headerView.leadingAnchor.constraint(
                equalTo:
                    contentView.leadingAnchor,
                constant: 20
            ),

            headerView.trailingAnchor.constraint(
                equalTo:
                    contentView.trailingAnchor,
                constant: -20
            ),

            headerView.heightAnchor.constraint(
                equalToConstant: 58
            ),

            logoView.leadingAnchor.constraint(
                equalTo:
                    headerView.leadingAnchor
            ),

            logoView.centerYAnchor.constraint(
                equalTo:
                    headerView.centerYAnchor
            ),

            logoView.widthAnchor.constraint(
                equalToConstant: 48
            ),

            logoView.heightAnchor.constraint(
                equalToConstant: 48
            ),

            logoImageView.centerXAnchor.constraint(
                equalTo:
                    logoView.centerXAnchor
            ),

            logoImageView.centerYAnchor.constraint(
                equalTo:
                    logoView.centerYAnchor
            ),

            logoImageView.widthAnchor.constraint(
                equalToConstant: 28
            ),

            logoImageView.heightAnchor.constraint(
                equalToConstant: 28
            ),

            titleLabel.leadingAnchor.constraint(
                equalTo:
                    logoView.trailingAnchor,
                constant: 12
            ),

            titleLabel.topAnchor.constraint(
                equalTo:
                    headerView.topAnchor,
                constant: 8
            ),

            subtitleLabel.leadingAnchor.constraint(
                equalTo:
                    titleLabel.leadingAnchor
            ),

            subtitleLabel.topAnchor.constraint(
                equalTo:
                    titleLabel.bottomAnchor,
                constant: 1
            ),

            infoButton.trailingAnchor.constraint(
                equalTo:
                    headerView.trailingAnchor
            ),

            infoButton.centerYAnchor.constraint(
                equalTo:
                    headerView.centerYAnchor
            ),

            infoButton.widthAnchor.constraint(
                equalToConstant: 44
            ),

            infoButton.heightAnchor.constraint(
                equalToConstant: 44
            ),

            // Hero

            heroCard.topAnchor.constraint(
                equalTo:
                    headerView.bottomAnchor,
                constant: 16
            ),

            heroCard.leadingAnchor.constraint(
                equalTo:
                    contentView.leadingAnchor,
                constant: 16
            ),

            heroCard.trailingAnchor.constraint(
                equalTo:
                    contentView.trailingAnchor,
                constant: -16
            ),

            heroCard.heightAnchor.constraint(
                equalToConstant: 132
            ),

            heroIconContainer.leadingAnchor.constraint(
                equalTo:
                    heroCard.leadingAnchor,
                constant: 18
            ),

            heroIconContainer.centerYAnchor.constraint(
                equalTo:
                    heroCard.centerYAnchor
            ),

            heroIconContainer.widthAnchor.constraint(
                equalToConstant: 64
            ),

            heroIconContainer.heightAnchor.constraint(
                equalToConstant: 64
            ),

            heroIcon.centerXAnchor.constraint(
                equalTo:
                    heroIconContainer.centerXAnchor
            ),

            heroIcon.centerYAnchor.constraint(
                equalTo:
                    heroIconContainer.centerYAnchor
            ),

            heroIcon.widthAnchor.constraint(
                equalToConstant: 36
            ),

            heroIcon.heightAnchor.constraint(
                equalToConstant: 36
            ),

            heroTitle.leadingAnchor.constraint(
                equalTo:
                    heroIconContainer.trailingAnchor,
                constant: 15
            ),

            heroTitle.topAnchor.constraint(
                equalTo:
                    heroCard.topAnchor,
                constant: 26
            ),

            heroTitle.trailingAnchor.constraint(
                lessThanOrEqualTo:
                    readyBadge.leadingAnchor,
                constant: -8
            ),

            heroSubtitle.leadingAnchor.constraint(
                equalTo:
                    heroTitle.leadingAnchor
            ),

            heroSubtitle.topAnchor.constraint(
                equalTo:
                    heroTitle.bottomAnchor,
                constant: 5
            ),

            heroSubtitle.trailingAnchor.constraint(
                equalTo:
                    heroCard.trailingAnchor,
                constant: -18
            ),

            readyBadge.trailingAnchor.constraint(
                equalTo:
                    heroCard.trailingAnchor,
                constant: -16
            ),

            readyBadge.topAnchor.constraint(
                equalTo:
                    heroCard.topAnchor,
                constant: 16
            ),

            readyBadge.widthAnchor.constraint(
                equalToConstant: 65
            ),

            readyBadge.heightAnchor.constraint(
                equalToConstant: 25
            ),

            readyDot.leadingAnchor.constraint(
                equalTo:
                    readyBadge.leadingAnchor,
                constant: 9
            ),

            readyDot.centerYAnchor.constraint(
                equalTo:
                    readyBadge.centerYAnchor
            ),

            readyDot.widthAnchor.constraint(
                equalToConstant: 8
            ),

            readyDot.heightAnchor.constraint(
                equalToConstant: 8
            ),

            readyLabel.leadingAnchor.constraint(
                equalTo:
                    readyDot.trailingAnchor,
                constant: 5
            ),

            readyLabel.centerYAnchor.constraint(
                equalTo:
                    readyBadge.centerYAnchor
            ),

            // Paths

            pathsCard.topAnchor.constraint(
                equalTo:
                    heroCard.bottomAnchor,
                constant: 16
            ),

            pathsCard.leadingAnchor.constraint(
                equalTo:
                    contentView.leadingAnchor,
                constant: 16
            ),

            pathsCard.trailingAnchor.constraint(
                equalTo:
                    contentView.trailingAnchor,
                constant: -16
            ),

            pathsCard.heightAnchor.constraint(
                equalToConstant: 226
            ),

            pathsTitle.leadingAnchor.constraint(
                equalTo:
                    pathsCard.leadingAnchor,
                constant: 18
            ),

            pathsTitle.topAnchor.constraint(
                equalTo:
                    pathsCard.topAnchor,
                constant: 17
            ),

            pathsSubtitle.leadingAnchor.constraint(
                equalTo:
                    pathsTitle.leadingAnchor
            ),

            pathsSubtitle.topAnchor.constraint(
                equalTo:
                    pathsTitle.bottomAnchor,
                constant: 3
            ),

            executableInput.leadingAnchor.constraint(
                equalTo:
                    pathsCard.leadingAnchor,
                constant: 14
            ),

            executableInput.trailingAnchor.constraint(
                equalTo:
                    pathsCard.trailingAnchor,
                constant: -14
            ),

            executableInput.topAnchor.constraint(
                equalTo:
                    pathsSubtitle.bottomAnchor,
                constant: 12
            ),

            executableInput.heightAnchor.constraint(
                equalToConstant: 67
            ),

            metadataInput.leadingAnchor.constraint(
                equalTo:
                    executableInput.leadingAnchor
            ),

            metadataInput.trailingAnchor.constraint(
                equalTo:
                    executableInput.trailingAnchor
            ),

            metadataInput.topAnchor.constraint(
                equalTo:
                    executableInput.bottomAnchor,
                constant: 8
            ),

            metadataInput.heightAnchor.constraint(
                equalToConstant: 67
            ),

            // Output

            outputConsole.topAnchor.constraint(
                equalTo:
                    pathsCard.bottomAnchor,
                constant: 16
            ),

            outputConsole.leadingAnchor.constraint(
                equalTo:
                    contentView.leadingAnchor,
                constant: 16
            ),

            outputConsole.trailingAnchor.constraint(
                equalTo:
                    contentView.trailingAnchor,
                constant: -16
            ),

            outputConsole.heightAnchor.constraint(
                equalToConstant: 390
            ),

            // Bottom

            bottomCard.topAnchor.constraint(
                equalTo:
                    outputConsole.bottomAnchor,
                constant: 16
            ),

            bottomCard.leadingAnchor.constraint(
                equalTo:
                    contentView.leadingAnchor,
                constant: 16
            ),

            bottomCard.trailingAnchor.constraint(
                equalTo:
                    contentView.trailingAnchor,
                constant: -16
            ),

            bottomCard.heightAnchor.constraint(
                equalToConstant: 128
            ),

            dumpButton.leadingAnchor.constraint(
                equalTo:
                    bottomCard.leadingAnchor,
                constant: 15
            ),

            dumpButton.topAnchor.constraint(
                equalTo:
                    bottomCard.topAnchor,
                constant: 15
            ),

            dumpButton.trailingAnchor.constraint(
                equalTo:
                    settingsButton.leadingAnchor,
                constant: -10
            ),

            dumpButton.heightAnchor.constraint(
                equalToConstant: 57
            ),

            settingsButton.trailingAnchor.constraint(
                equalTo:
                    bottomCard.trailingAnchor,
                constant: -15
            ),

            settingsButton.topAnchor.constraint(
                equalTo:
                    dumpButton.topAnchor
            ),

            settingsButton.widthAnchor.constraint(
                equalToConstant: 57
            ),

            settingsButton.heightAnchor.constraint(
                equalToConstant: 57
            ),

            dumpIcon.leadingAnchor.constraint(
                equalTo:
                    dumpButton.leadingAnchor,
                constant: 24
            ),

            dumpIcon.centerYAnchor.constraint(
                equalTo:
                    dumpButton.centerYAnchor
            ),

            dumpIcon.widthAnchor.constraint(
                equalToConstant: 18
            ),

            dumpIcon.heightAnchor.constraint(
                equalToConstant: 18
            ),

            dumpTitleLabel.leadingAnchor.constraint(
                equalTo:
                    dumpIcon.trailingAnchor,
                constant: 8
            ),

            dumpTitleLabel.centerYAnchor.constraint(
                equalTo:
                    dumpButton.centerYAnchor
            ),

            dumpSpinner.centerXAnchor.constraint(
                equalTo:
                    dumpButton.centerXAnchor
            ),

            dumpSpinner.centerYAnchor.constraint(
                equalTo:
                    dumpButton.centerYAnchor
            ),

            dumpSpinner.widthAnchor.constraint(
                equalToConstant: 22
            ),

            dumpSpinner.heightAnchor.constraint(
                equalToConstant: 22
            ),

            engineLabel.leadingAnchor.constraint(
                equalTo:
                    bottomCard.leadingAnchor,
                constant: 18
            ),

            engineLabel.bottomAnchor.constraint(
                equalTo:
                    bottomCard.bottomAnchor,
                constant: -15
            ),

            engineValue.leadingAnchor.constraint(
                equalTo:
                    engineLabel.trailingAnchor,
                constant: 7
            ),

            engineValue.centerYAnchor.constraint(
                equalTo:
                    engineLabel.centerYAnchor
            ),

            bottomCard.bottomAnchor.constraint(
                equalTo:
                    contentView.bottomAnchor,
                constant: -25
            )
        ])
    }

    // MARK: File Selected

    private func handleSelectedFile(
        url: URL,
        type: FilePickerService.SelectionType
    ) {

        let path =
            url.path

        switch type {

        case .executable:

            executableInput.textField.text =
                path

            executableInput.setSelected(
                true
            )

            outputConsole.append(
                "[FILE] Executable selected."
            )

            outputConsole.append(
                "[PATH] \(path)"
            )

        case .metadata:

            metadataInput.textField.text =
                path

            metadataInput.setSelected(
                true
            )

            outputConsole.append(
                "[FILE] Metadata selected."
            )

            outputConsole.append(
                "[PATH] \(path)"
            )
        }
    }

    // MARK: Dump

    @objc
    private func dumpPressed() {

        guard isDumping == false else {
            return
        }

        view.endEditing(
            true
        )

        let executable =
            executableInput.textField.text?
            .trimmingCharacters(
                in: .whitespacesAndNewlines
            ) ?? ""

        let metadata =
            metadataInput.textField.text?
            .trimmingCharacters(
                in: .whitespacesAndNewlines
            ) ?? ""

        guard executable.isEmpty == false else {

            showAlert(
                title: "Executable Missing",
                message:
                    "Select the executable file before starting the dump."
            )

            return
        }

        guard metadata.isEmpty == false else {

            showAlert(
                title: "Metadata Missing",
                message:
                    "Select global-metadata.dat before starting the dump."
            )

            return
        }

        outputConsole.clear()

        startDumpAnimation()

        dumpManager.start(
            executable: executable,
            metadata: metadata
        )
    }

    // MARK: Dump Animation

    private func startDumpAnimation() {

        isDumping = true

        dumpButton.isEnabled =
            false

        settingsButton.isEnabled =
            false

        dumpIcon.isHidden =
            true

        dumpSpinner.isHidden =
            false

        dumpSpinner.startAnimating()

        dumpTitleLabel.text =
            "DUMPING"

        dumpAnimationStep =
            0

        dumpTimer?.invalidate()

        dumpTimer =
            Timer.scheduledTimer(
                withTimeInterval: 0.42,
                repeats: true
            ) {
                [weak self] timer in

                guard let self = self else {

                    timer.invalidate()

                    return
                }

                self.dumpAnimationStep += 1

                let dots =
                    String(
                        repeating: ".",
                        count:
                            self.dumpAnimationStep % 4
                    )

                UIView.transition(
                    with:
                        self.dumpTitleLabel,
                    duration: 0.16,
                    options:
                        .transitionCrossDissolve,
                    animations: {

                        self.dumpTitleLabel.text =
                            "DUMPING" + dots
                    }
                )
            }
    }

    private func stopDumpAnimation(
        success: Bool
    ) {

        dumpTimer?.invalidate()

        dumpTimer = nil

        dumpSpinner.stopAnimating()

        dumpSpinner.isHidden =
            true

        dumpIcon.isHidden =
            false

        isDumping =
            false

        dumpButton.isEnabled =
            true

        settingsButton.isEnabled =
            true

        if success {

            dumpIcon.image =
                AppTheme.symbol(
                    "checkmark",
                    size: 14,
                    weight: .bold
                )

            dumpButton.backgroundColor =
                AppTheme.success

            dumpTitleLabel.text =
                "DUMP COMPLETE"

            dumpButton.layer.shadowColor =
                AppTheme.success.cgColor

        } else {

            dumpIcon.image =
                AppTheme.symbol(
                    "exclamationmark",
                    size: 14,
                    weight: .bold
                )

            dumpButton.backgroundColor =
                AppTheme.danger

            dumpTitleLabel.text =
                "DUMP FAILED"

            dumpButton.layer.shadowColor =
                AppTheme.danger.cgColor
        }

        UIView.animate(
            withDuration: 0.25
        ) {

            self.dumpButton.transform =
                CGAffineTransform(
                    scaleX: 1.03,
                    y: 1.03
                )
        } completion: {
            _ in

            UIView.animate(
                withDuration: 0.25
            ) {

                self.dumpButton.transform =
                    .identity
            }
        }

        DispatchQueue.main.asyncAfter(
            deadline: .now() + 2.0
        ) {
            [weak self] in

            self?.resetDumpButton()
        }
    }

    private func resetDumpButton() {

        UIView.transition(
            with:
                dumpButton,
            duration: 0.25,
            options:
                .transitionCrossDissolve,
            animations: {

                self.dumpButton.backgroundColor =
                    AppTheme.accent

                self.dumpButton.layer.shadowColor =
                    AppTheme.accent.cgColor

                self.dumpIcon.image =
                    AppTheme.symbol(
                        "play.fill",
                        size: 13,
                        weight: .bold
                    )

                self.dumpTitleLabel.text =
                    "START DUMP"
            }
        )
    }

    // MARK: State

    private func handleDumpState(
        _ state: DumpManager.State
    ) {

        switch state {

        case .idle:

            outputConsole.setStatus(
                "READY",
                color: AppTheme.success
            )

        case .running:

            outputConsole.setStatus(
                "DUMPING",
                color: AppTheme.accent
            )

        case .completed:

            outputConsole.setStatus(
                "COMPLETE",
                color: AppTheme.success
            )

            outputConsole.append(
                "[SYSTEM] All operations completed successfully."
            )

            stopDumpAnimation(
                success: true
            )

        case .failed:

            outputConsole.setStatus(
                "FAILED",
                color: AppTheme.danger
            )

            outputConsole.append(
                "[ERROR] Dump process failed."
            )

            stopDumpAnimation(
                success: false
            )
        }
    }

    // MARK: Settings

    @objc
    private func settingsPressed() {

        guard isDumping == false else {
            return
        }

        let settings =
            SettingsViewController()

        settings.modalPresentationStyle =
            .pageSheet

        if #available(iOS 15.0, *) {

            if let sheet =
                settings.sheetPresentationController {

                sheet.detents = [
                    .medium(),
                    .large()
                ]

                sheet.prefersGrabberVisible =
                    true

                sheet.preferredCornerRadius =
                    26
            }
        }

        present(
            settings,
            animated: true
        )
    }

    // MARK: Info

    @objc
    private func infoPressed() {

        let alert =
            UIAlertController(
                title:
                    "ASASEC IL2CPP DUMPER",
                message:
                    """
                    Modern IL2CPP analysis interface.

                    Engine
                    Perfare

                    GUI
                    Asasec

                    Minimum iOS
                    13.0
                    """,
                preferredStyle:
                    .alert
            )

        alert.addAction(
            UIAlertAction(
                title: "OK",
                style: .default
            )
        )

        present(
            alert,
            animated: true
        )
    }

    // MARK: Alert

    private func showAlert(
        title: String,
        message: String
    ) {

        let alert =
            UIAlertController(
                title: title,
                message: message,
                preferredStyle: .alert
            )

        alert.addAction(
            UIAlertAction(
                title: "OK",
                style: .default
            )
        )

        present(
            alert,
            animated: true
        )
    }

    deinit {

        dumpTimer?.invalidate()

        dumpManager.stop()
    }
}
