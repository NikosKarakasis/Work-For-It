import AVFoundation
import Vision
import SwiftUI

final class CameraManager: NSObject, ObservableObject {

    // MARK: - Camera

    let session = AVCaptureSession()

    private let sessionQueue = DispatchQueue(
        label: "camera.session.queue"
    )

    private let videoOutput = AVCaptureVideoDataOutput()

    private var isConfigured = false

    // MARK: - Published State

    @Published var permissionGranted = false

    @Published var bodyDetected = false

    @Published var joints:
        [VNHumanBodyPoseObservation.JointName: CGPoint] = [:]

    // MARK: - Init

    override init() {
        super.init()
        requestCameraPermission()
    }

    // MARK: - Camera Permission

    private func requestCameraPermission() {

        switch AVCaptureDevice.authorizationStatus(for: .video) {

        case .authorized:

            DispatchQueue.main.async {
                self.permissionGranted = true
            }

            configureCamera()

        case .notDetermined:

            AVCaptureDevice.requestAccess(for: .video) { [weak self] granted in

                guard let self = self else {
                    return
                }

                DispatchQueue.main.async {
                    self.permissionGranted = granted
                }

                if granted {
                    self.configureCamera()
                } else {
                    print("Camera permission denied")
                }
            }

        case .denied:

            DispatchQueue.main.async {
                self.permissionGranted = false
            }

            print("Camera permission denied")

        case .restricted:

            DispatchQueue.main.async {
                self.permissionGranted = false
            }

            print("Camera permission restricted")

        @unknown default:

            DispatchQueue.main.async {
                self.permissionGranted = false
            }

            print("Unknown camera permission state")
        }
    }

    // MARK: - Configure Camera

    private func configureCamera() {

        sessionQueue.async { [weak self] in

            guard let self = self else {
                return
            }

            guard !self.isConfigured else {
                return
            }

            self.session.beginConfiguration()

            self.session.sessionPreset = .high

            // Remove old inputs if needed
            for input in self.session.inputs {
                self.session.removeInput(input)
            }

            // Front camera
            guard let camera =
                    AVCaptureDevice.default(
                        .builtInWideAngleCamera,
                        for: .video,
                        position: .front
                    )
            else {

                print("Front camera not found")

                self.session.commitConfiguration()

                return
            }

            // Camera input
            do {

                let input =
                    try AVCaptureDeviceInput(
                        device: camera
                    )

                if self.session.canAddInput(input) {

                    self.session.addInput(input)

                } else {

                    print("Could not add camera input")
                }

            } catch {

                print("Camera input error: \(error)")

                self.session.commitConfiguration()

                return
            }

            // Video output
            self.videoOutput.alwaysDiscardsLateVideoFrames = true

            self.videoOutput.setSampleBufferDelegate(
                self,
                queue: DispatchQueue(
                    label: "camera.frames.queue"
                )
            )

            self.videoOutput.videoSettings = [
                kCVPixelBufferPixelFormatTypeKey as String:
                    kCVPixelFormatType_32BGRA
            ]

            if self.session.canAddOutput(self.videoOutput) {

                self.session.addOutput(self.videoOutput)

            } else {

                print("Could not add video output")
            }

            self.session.commitConfiguration()

            self.isConfigured = true

            self.start()
        }
    }

    // MARK: - Start Camera

    func start() {

        sessionQueue.async { [weak self] in

            guard let self = self else {
                return
            }

            guard self.isConfigured else {
                return
            }

            guard !self.session.isRunning else {
                return
            }

            self.session.startRunning()
        }
    }

    // MARK: - Stop Camera

    func stop() {

        sessionQueue.async { [weak self] in

            guard let self = self else {
                return
            }

            guard self.session.isRunning else {
                return
            }

            self.session.stopRunning()
        }
    }

    // MARK: - Body Pose Detection

    private func detectBodyPose(
        pixelBuffer: CVPixelBuffer
    ) {

        let request = VNDetectHumanBodyPoseRequest()

        let handler = VNImageRequestHandler(
            cvPixelBuffer: pixelBuffer,
            orientation: .leftMirrored,
            options: [:]
        )

        do {

            try handler.perform([request])

            guard let observation =
                    request.results?.first
            else {

                DispatchQueue.main.async {
                    self.bodyDetected = false
                    self.joints = [:]
                }

                return
            }

            let recognizedPoints =
                try observation.recognizedPoints(.all)

            var detectedJoints:
                [VNHumanBodyPoseObservation.JointName: CGPoint] = [:]

            for (jointName, point) in recognizedPoints {

                guard point.confidence > 0.3 else {
                    continue
                }

                detectedJoints[jointName] = CGPoint(
                    x: point.location.x,
                    y: point.location.y
                )
            }

            DispatchQueue.main.async {

                self.joints = detectedJoints

                self.bodyDetected =
                    !detectedJoints.isEmpty
            }

        } catch {

            print("Body pose detection error: \(error)")
        }
    }
}

// MARK: - Camera Frame Delegate

extension CameraManager:
    AVCaptureVideoDataOutputSampleBufferDelegate {

    func captureOutput(
        _ output: AVCaptureOutput,
        didOutput sampleBuffer: CMSampleBuffer,
        from connection: AVCaptureConnection
    ) {

        guard let pixelBuffer =
                CMSampleBufferGetImageBuffer(
                    sampleBuffer
                )
        else {
            return
        }

        detectBodyPose(
            pixelBuffer: pixelBuffer
        )
    }
}
