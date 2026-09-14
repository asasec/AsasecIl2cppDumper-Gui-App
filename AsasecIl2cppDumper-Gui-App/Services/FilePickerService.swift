import UIKit
import UniformTypeIdentifiers

final class FilePickerService: NSObject {

    enum SelectionType {
        case executable
        case metadata
    }

    private var selectionType:
        SelectionType?

    var completion:
        ((URL, SelectionType) -> Void)?

    func present(
        from viewController: UIViewController,
        type: SelectionType
    ) {

        selectionType = type

        let picker =
            UIDocumentPickerViewController(
                forOpeningContentTypes: [
                    .data
                ]
            )

        picker.delegate = self

        picker.allowsMultipleSelection = false

        picker.modalPresentationStyle =
            .formSheet

        viewController.present(
            picker,
            animated: true
        )
    }
}

extension FilePickerService:
    UIDocumentPickerDelegate {

    func documentPicker(
        _ controller: UIDocumentPickerViewController,
        didPickDocumentsAt urls: [URL]
    ) {

        guard let url = urls.first else {
            return
        }

        guard let type = selectionType else {
            return
        }

        completion?(
            url,
            type
        )
    }

    func documentPickerWasCancelled(
        _ controller: UIDocumentPickerViewController
    ) {
    }
}
