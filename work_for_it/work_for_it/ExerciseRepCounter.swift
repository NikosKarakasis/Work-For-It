//
//  ExerciseRepCounter.swift
//  work_for_it
//
//  Created by jason daniel umana on 9/18/26.
//

import SwiftUI
import Vision

final class ExerciseRepCounter: ObservableObject {

    // MARK: - Exercise Types

    enum Exercise: String, CaseIterable, Identifiable {
        case squat = "Squat"
        case pushUp = "Push-Up"

        var id: String {
            rawValue
        }
    }

    // MARK: - Rep State

    private enum MovementPhase {
        case ready
        case down
    }

    // MARK: - Published Properties

    @Published var exercise: Exercise = .squat {
        didSet {
            if exercise != oldValue {
                reset()
            }
        }
    }

    @Published var reps: Int = 0

    @Published var feedback: String = "Move into position"

    private var phase: MovementPhase = .ready

    // MARK: - Update From Camera

    func update(
        with joints: [VNHumanBodyPoseObservation.JointName: CGPoint]
    ) {

        switch exercise {

        case .squat:
            detectSquat(using: joints)

        case .pushUp:
            detectPushUp(using: joints)
        }
    }

    // MARK: - Squat Detection

    private func detectSquat(
        using joints: [VNHumanBodyPoseObservation.JointName: CGPoint]
    ) {

        var kneeAngles: [Double] = []

        // Left leg
        if let hip = joints[.leftHip],
           let knee = joints[.leftKnee],
           let ankle = joints[.leftAnkle] {

            let angle = calculateAngle(
                first: hip,
                middle: knee,
                last: ankle
            )

            kneeAngles.append(angle)
        }

        // Right leg
        if let hip = joints[.rightHip],
           let knee = joints[.rightKnee],
           let ankle = joints[.rightAnkle] {

            let angle = calculateAngle(
                first: hip,
                middle: knee,
                last: ankle
            )

            kneeAngles.append(angle)
        }

        guard !kneeAngles.isEmpty else {
            feedback = "Make sure your full legs are visible"
            return
        }

        let kneeAngle =
            kneeAngles.reduce(0, +)
            / Double(kneeAngles.count)

        // Standing
        if kneeAngle > 155 {

            if phase == .down {

                reps += 1
                phase = .ready
                feedback = "Rep counted!"
            } else {

                feedback = "Squat down"
            }

            return
        }

        // Bottom of squat
        if kneeAngle < 100 {

            phase = .down
            feedback = "Good depth — stand up"

            return
        }

        // Between standing and bottom position
        if phase == .down {

            feedback = "Stand all the way up"

        } else {

            feedback = "Go lower"
        }
    }

    // MARK: - Push-Up Detection

    private func detectPushUp(
        using joints: [VNHumanBodyPoseObservation.JointName: CGPoint]
    ) {

        var elbowAngles: [Double] = []

        // Left arm
        if let shoulder = joints[.leftShoulder],
           let elbow = joints[.leftElbow],
           let wrist = joints[.leftWrist] {

            let angle = calculateAngle(
                first: shoulder,
                middle: elbow,
                last: wrist
            )

            elbowAngles.append(angle)
        }

        // Right arm
        if let shoulder = joints[.rightShoulder],
           let elbow = joints[.rightElbow],
           let wrist = joints[.rightWrist] {

            let angle = calculateAngle(
                first: shoulder,
                middle: elbow,
                last: wrist
            )

            elbowAngles.append(angle)
        }

        guard !elbowAngles.isEmpty else {
            feedback = "Make sure your arms are visible"
            return
        }

        let elbowAngle =
            elbowAngles.reduce(0, +)
            / Double(elbowAngles.count)

        // Arms extended
        if elbowAngle > 155 {

            if phase == .down {

                reps += 1
                phase = .ready
                feedback = "Rep counted!"
            } else {

                feedback = "Lower yourself"
            }

            return
        }

        // Bottom of push-up
        if elbowAngle < 90 {

            phase = .down
            feedback = "Good depth — push up"

            return
        }

        if phase == .down {

            feedback = "Push all the way up"

        } else {

            feedback = "Go lower"
        }
    }

    // MARK: - Joint Angle Calculation

    private func calculateAngle(
        first: CGPoint,
        middle: CGPoint,
        last: CGPoint
    ) -> Double {

        let firstAngle = atan2(
            Double(first.y - middle.y),
            Double(first.x - middle.x)
        )

        let secondAngle = atan2(
            Double(last.y - middle.y),
            Double(last.x - middle.x)
        )

        var angle = abs(
            (secondAngle - firstAngle)
            * 180
            / .pi
        )

        if angle > 180 {
            angle = 360 - angle
        }

        return angle
    }

    // MARK: - Reset

    func reset() {

        reps = 0
        phase = .ready

        switch exercise {

        case .squat:
            feedback = "Stand tall to begin"

        case .pushUp:
            feedback = "Get into push-up position"
        }
    }
}
