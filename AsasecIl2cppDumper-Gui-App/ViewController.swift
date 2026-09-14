import UIKit

final class ViewController: UIViewController {

    private let titleLabel: UILabel = {
        let label = UILabel()

        label.text = "Asasec Il2cppDumper"

        label.font = UIFont.systemFont(
            ofSize: 30,
            weight: .bold
        )

        label.textAlignment = .center

        label.translatesAutoresizingMaskIntoConstraints = false

        return label
    }()

    private let messageLabel: UILabel = {
        let label = UILabel()

        label.text = "Il2cppDumper GUI"

        label.font = UIFont.systemFont(
            ofSize: 18,
            weight: .regular
        )

        label.textAlignment = .center

        label.numberOfLines = 0

        label.translatesAutoresizingMaskIntoConstraints = false

        return label
    }()

    private let continueButton: UIButton = {
        let button = UIButton(type: .system)

        button.setTitle(
            "Devam Et",
            for: .normal
        )

        button.titleLabel?.font = UIFont.systemFont(
            ofSize: 17,
            weight: .semibold
        )

        button.translatesAutoresizingMaskIntoConstraints = false

        return button
    }()

    override func viewDidLoad() {
        super.viewDidLoad()

        view.backgroundColor = .systemBackground

        title = "Asasec Il2cppDumper"

        view.addSubview(titleLabel)
        view.addSubview(messageLabel)
        view.addSubview(continueButton)

        continueButton.addTarget(
            self,
            action: #selector(continueTapped),
            for: .touchUpInside
        )

        NSLayoutConstraint.activate([

            titleLabel.centerXAnchor.constraint(
                equalTo: view.centerXAnchor
            ),

            titleLabel.centerYAnchor.constraint(
                equalTo: view.centerYAnchor,
                constant: -70
            ),

            titleLabel.leadingAnchor.constraint(
                greaterThanOrEqualTo: view.leadingAnchor,
                constant: 24
            ),

            titleLabel.trailingAnchor.constraint(
                lessThanOrEqualTo: view.trailingAnchor,
                constant: -24
            ),

            messageLabel.topAnchor.constraint(
                equalTo: titleLabel.bottomAnchor,
                constant: 18
            ),

            messageLabel.centerXAnchor.constraint(
                equalTo: view.centerXAnchor
            ),

            messageLabel.leadingAnchor.constraint(
                greaterThanOrEqualTo: view.leadingAnchor,
                constant: 24
            ),

            messageLabel.trailingAnchor.constraint(
                lessThanOrEqualTo: view.trailingAnchor,
                constant: -24
            ),

            continueButton.topAnchor.constraint(
                equalTo: messageLabel.bottomAnchor,
                constant: 28
            ),

            continueButton.centerXAnchor.constraint(
                equalTo: view.centerXAnchor
            ),

            continueButton.heightAnchor.constraint(
                equalToConstant: 44
            ),

            continueButton.widthAnchor.constraint(
                equalToConstant: 140
            )
        ])
    }

    @objc private func continueTapped() {

        let alert = UIAlertController(
            title: "Asasec Il2cppDumper",
            message: "Uygulama başarıyla çalışıyor.",
            preferredStyle: .alert
        )

        alert.addAction(
            UIAlertAction(
                title: "Tamam",
                style: .default
            )
        )

        present(
            alert,
            animated: true
        )
    }
}
