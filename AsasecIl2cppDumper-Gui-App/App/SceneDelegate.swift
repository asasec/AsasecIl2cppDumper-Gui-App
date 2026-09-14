import UIKit

final class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    func scene(
        _ scene: UIScene,
        willConnectTo session: UISceneSession,
        options connectionOptions: UIScene.ConnectionOptions
    ) {
        guard let windowScene = scene as? UIWindowScene else {
            print("ASASEC ERROR: UIWindowScene yok")
            return
        }

        print("ASASEC: Scene başladı")

        let window = UIWindow(windowScene: windowScene)

        let testViewController = UIViewController()
        testViewController.view.backgroundColor = .systemRed

        print("ASASEC: Test UIViewController oluşturuldu")

        window.rootViewController = testViewController
        window.makeKeyAndVisible()

        self.window = window

        print("ASASEC: Window makeKeyAndVisible yapıldı")
    }
}
