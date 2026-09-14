import Foundation

final class DumpManager {

    enum State {
        case idle
        case running
        case completed
        case failed
    }

    var onLog:
        ((String) -> Void)?

    var onProgress:
        ((Float) -> Void)?

    var onStateChanged:
        ((State) -> Void)?

    private var timer: Timer?

    private var currentStep = 0

    private var steps: [
        (String, Float)
    ] = []

    private(set) var state:
        State = .idle

    // MARK: Start

    func start(
        executable: String,
        metadata: String
    ) {

        stop()

        state = .running

        onStateChanged?(
            .running
        )

        steps = [

            (
                "[INIT] Initializing dump engine...",
                0.05
            ),

            (
                "[FILE] Loading executable...",
                0.12
            ),

            (
                "[FILE] Loading global-metadata.dat...",
                0.20
            ),

            (
                "[IL2CPP] Detecting Unity version...",
                0.30
            ),

            (
                "[IL2CPP] Reading metadata tables...",
                0.42
            ),

            (
                "[IL2CPP] Resolving type definitions...",
                0.55
            ),

            (
                "[IL2CPP] Resolving method definitions...",
                0.67
            ),

            (
                "[IL2CPP] Processing fields...",
                0.76
            ),

            (
                "[IL2CPP] Processing properties...",
                0.84
            ),

            (
                "[DUMP] Generating output...",
                0.92
            ),

            (
                "[DUMP] Finalizing...",
                0.98
            ),

            (
                "[SUCCESS] Dump completed.",
                1.00
            )
        ]

        currentStep = 0

        onLog?(
            "[ENGINE] Perfare Dumper"
        )

        onLog?(
            "[INPUT] Executable: \(executable)"
        )

        onLog?(
            "[INPUT] Metadata: \(metadata)"
        )

        onLog?(
            "[SYSTEM] Dump process started."
        )

        onProgress?(
            0
        )

        timer = Timer.scheduledTimer(
            withTimeInterval: 0.55,
            repeats: true
        ) {
            [weak self] timer in

            guard let self = self else {
                timer.invalidate()
                return
            }

            self.processNextStep()
        }
    }

    // MARK: Process

    private func processNextStep() {

        guard currentStep < steps.count else {

            finish()

            return
        }

        let step =
            steps[currentStep]

        onLog?(
            step.0
        )

        onProgress?(
            step.1
        )

        currentStep += 1

        if currentStep >= steps.count {

            finish()
        }
    }

    // MARK: Finish

    private func finish() {

        timer?.invalidate()

        timer = nil

        state = .completed

        onProgress?(
            1.0
        )

        onStateChanged?(
            .completed
        )
    }

    // MARK: Stop

    func stop() {

        timer?.invalidate()

        timer = nil
    }

    deinit {

        timer?.invalidate()
    }
}
