import UIKit

final class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    func scene(
        _ scene: UIScene,
        willConnectTo session: UISceneSession,
        options connectionOptions: UIScene.ConnectionOptions
    ) {

        guard let windowScene = scene as? UIWindowScene else {
            return
        }

        let window = UIWindow(windowScene: windowScene)

        let viewController = UIViewController()

        viewController.view.backgroundColor = .systemRed

        let label = UILabel()

        label.text = """
        ASASEC DEBUG

        SCENE ÇALIŞIYOR

        UIWindow oluşturuldu
        UIViewController oluşturuldu
        """

        label.textColor = .white
        label.font = UIFont.systemFont(
            ofSize: 22,
            weight: .bold
        )
        label.textAlignment = .center
        label.numberOfLines = 0
        label.translatesAutoresizingMaskIntoConstraints = false

        viewController.view.addSubview(label)

        NSLayoutConstraint.activate([
            label.leadingAnchor.constraint(
                equalTo: viewController.view.leadingAnchor,
                constant: 20
            ),

            label.trailingAnchor.constraint(
                equalTo: viewController.view.trailingAnchor,
                constant: -20
            ),

            label.centerYAnchor.constraint(
                equalTo: viewController.view.centerYAnchor
            )
        ])

        window.rootViewController = viewController

        self.window = window

        window.makeKeyAndVisible()
    }
}
