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

        print("ASASEC: Scene başladı")

        let window = UIWindow(windowScene: windowScene)

        let controller = UIViewController()
        controller.view.backgroundColor = .systemBackground

        print("ASASEC: Basit UIViewController oluşturuldu")

        window.rootViewController = controller
        window.makeKeyAndVisible()

        self.window = window

        print("ASASEC: Window görünür")
    }
}
