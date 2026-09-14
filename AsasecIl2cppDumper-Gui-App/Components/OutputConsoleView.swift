import UIKit

final class OutputConsoleView: UIView {

    private let headerView = UIView()

    private let titleLabel = UILabel()

    private let statusDot = UIView()

    private let statusLabel = UILabel()

    private let clearButton = UIButton(
        type: .system
    )

    private let progressView = UIProgressView(
        progressViewStyle: .default
    )

    private let textView = UITextView()

    private let emptyLabel = UILabel()

    override init(frame: CGRect) {

        super.init(frame: frame)

        setup()
    }

    required init?(coder: NSCoder) {

        super.init(coder: coder)

        setup()
    }

    private func setup() {

        backgroundColor =
            AppTheme.consoleBackground

        layer.cornerRadius = 22

        clipsToBounds = true

        setupHeader()

        setupProgress()

        setupTextView()

        setupEmptyLabel()

        setupConstraints()
    }

    // MARK: Header

    private func setupHeader() {

        headerView.translatesAutoresizingMaskIntoConstraints =
            false

        addSubview(headerView)

        titleLabel.translatesAutoresizingMaskIntoConstraints =
            false

        titleLabel.text = "OUTPUT"

        titleLabel.font =
            UIFont.monospacedSystemFont(
                ofSize: 13,
                weight: .bold
            )

        titleLabel.textColor =
            AppTheme.accent

        headerView.addSubview(titleLabel)

        statusDot.translatesAutoresizingMaskIntoConstraints =
            false

        statusDot.backgroundColor =
            AppTheme.success

        statusDot.layer.cornerRadius = 4

        headerView.addSubview(statusDot)

        statusLabel.translatesAutoresizingMaskIntoConstraints =
            false

        statusLabel.text = "READY"

        statusLabel.font =
            UIFont.monospacedSystemFont(
                ofSize: 9,
                weight: .bold
            )

        statusLabel.textColor =
            AppTheme.secondaryText

        headerView.addSubview(statusLabel)

        clearButton.translatesAutoresizingMaskIntoConstraints =
            false

        clearButton.setImage(
            AppTheme.symbol(
                "trash",
                size: 13,
                weight: .medium
            ),
            for: .normal
        )

        clearButton.tintColor =
            AppTheme.secondaryText

        clearButton.addTarget(
            self,
            action: #selector(clearPressed),
            for: .touchUpInside
        )

        headerView.addSubview(clearButton)
    }

    // MARK: Progress

    private func setupProgress() {

        progressView.translatesAutoresizingMaskIntoConstraints =
            false

        progressView.progress = 0

        progressView.trackTintColor =
            UIColor.white.withAlphaComponent(
                0.08
            )

        progressView.progressTintColor =
            AppTheme.accent

        progressView.layer.cornerRadius = 2

        progressView.clipsToBounds = true

        addSubview(progressView)
    }

    // MARK: Text

    private func setupTextView() {

        textView.translatesAutoresizingMaskIntoConstraints =
            false

        textView.backgroundColor = .clear

        textView.isEditable = false

        textView.isSelectable = true

        textView.font =
            UIFont.monospacedSystemFont(
                ofSize: 11.5,
                weight: .regular
            )

        textView.textColor =
            AppTheme.consoleText

        textView.tintColor =
            AppTheme.accent

        textView.textContainerInset =
            UIEdgeInsets(
                top: 14,
                left: 14,
                bottom: 14,
                right: 14
            )

        textView.alpha = 0

        addSubview(textView)
    }

    private func setupEmptyLabel() {

        emptyLabel.translatesAutoresizingMaskIntoConstraints =
            false

        emptyLabel.text =
            "Waiting for dump process..."

        emptyLabel.font =
            UIFont.monospacedSystemFont(
                ofSize: 11,
                weight: .regular
            )

        emptyLabel.textColor =
            UIColor.white.withAlphaComponent(
                0.30
            )

        emptyLabel.textAlignment =
            .center

        addSubview(emptyLabel)
    }

    // MARK: Constraints

    private func setupConstraints() {

        NSLayoutConstraint.activate([

            headerView.topAnchor.constraint(
                equalTo: topAnchor
            ),

            headerView.leadingAnchor.constraint(
                equalTo: leadingAnchor
            ),

            headerView.trailingAnchor.constraint(
                equalTo: trailingAnchor
            ),

            headerView.heightAnchor.constraint(
                equalToConstant: 46
            ),

            titleLabel.leadingAnchor.constraint(
                equalTo: headerView.leadingAnchor,
                constant: 15
            ),

            titleLabel.centerYAnchor.constraint(
                equalTo: headerView.centerYAnchor
            ),

            statusDot.leadingAnchor.constraint(
                equalTo: titleLabel.trailingAnchor,
                constant: 9
            ),

            statusDot.centerYAnchor.constraint(
                equalTo: titleLabel.centerYAnchor
            ),

            statusDot.widthAnchor.constraint(
                equalToConstant: 8
            ),

            statusDot.heightAnchor.constraint(
                equalToConstant: 8
            ),

            statusLabel.leadingAnchor.constraint(
                equalTo: statusDot.trailingAnchor,
                constant: 5
            ),

            statusLabel.centerYAnchor.constraint(
                equalTo: titleLabel.centerYAnchor
            ),

            clearButton.trailingAnchor.constraint(
                equalTo: headerView.trailingAnchor,
                constant: -8
            ),

            clearButton.centerYAnchor.constraint(
                equalTo: headerView.centerYAnchor
            ),

            clearButton.widthAnchor.constraint(
                equalToConstant: 38
            ),

            clearButton.heightAnchor.constraint(
                equalToConstant: 38
            ),

            progressView.topAnchor.constraint(
                equalTo: headerView.bottomAnchor
            ),

            progressView.leadingAnchor.constraint(
                equalTo: leadingAnchor
            ),

            progressView.trailingAnchor.constraint(
                equalTo: trailingAnchor
            ),

            progressView.heightAnchor.constraint(
                equalToConstant: 3
            ),

            textView.topAnchor.constraint(
                equalTo: progressView.bottomAnchor
            ),

            textView.leadingAnchor.constraint(
                equalTo: leadingAnchor
            ),

            textView.trailingAnchor.constraint(
                equalTo: trailingAnchor
            ),

            textView.bottomAnchor.constraint(
                equalTo: bottomAnchor
            ),

            emptyLabel.centerXAnchor.constraint(
                equalTo: centerXAnchor
            ),

            emptyLabel.centerYAnchor.constraint(
                equalTo: centerYAnchor
            )
        ])
    }

    // MARK: Public

    func append(
        _ message: String
    ) {

        if textView.alpha == 0 {

            textView.alpha = 1

            emptyLabel.alpha = 0
        }

        let oldText =
            textView.text ?? ""

        if oldText.isEmpty {

            textView.text = message

        } else {

            textView.text =
                oldText + "\n" + message
        }

        scrollToBottom()
    }

    func clear() {

        textView.text = ""

        textView.alpha = 0

        emptyLabel.alpha = 1

        setProgress(
            0,
            animated: false
        )

        setStatus(
            "READY",
            color: AppTheme.success
        )
    }

    func setStatus(
        _ status: String,
        color: UIColor
    ) {

        statusLabel.text =
            status.uppercased()

        UIView.animate(
            withDuration: 0.2
        ) {

            self.statusDot.backgroundColor =
                color
        }
    }

    func setProgress(
        _ value: Float,
        animated: Bool = true
    ) {

        let safeValue =
            max(
                0,
                min(
                    1,
                    value
                )
            )

        progressView.setProgress(
            safeValue,
            animated: animated
        )
    }

    private func scrollToBottom() {

        guard textView.text.isEmpty == false else {
            return
        }

        let position =
            max(
                0,
                textView.text.count - 1
            )

        textView.scrollRangeToVisible(
            NSRange(
                location: position,
                length: 1
            )
        )
    }

    @objc
    private func clearPressed() {

        clear()
    }
}
