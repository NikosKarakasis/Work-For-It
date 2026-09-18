//
//  CameraPreview.swift
//  work_for_it
//
//  Created by jason daniel umana on 9/18/26.
//

import SwiftUI
import AVFoundation

struct CameraPreview: UIViewRepresentable {

    let session: AVCaptureSession

    func makeUIView(context: Context) -> UIView {

        let view = CameraPreviewUIView()

        view.previewLayer.session = session
        view.previewLayer.videoGravity = .resizeAspectFill

        return view
    }

    func updateUIView(
        _ uiView: UIView,
        context: Context
    ) {
    }
}

final class CameraPreviewUIView: UIView {

    override class var layerClass: AnyClass {
        AVCaptureVideoPreviewLayer.self
    }

    var previewLayer: AVCaptureVideoPreviewLayer {
        layer as! AVCaptureVideoPreviewLayer
    }
}
