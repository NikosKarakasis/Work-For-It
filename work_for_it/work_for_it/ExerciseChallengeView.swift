//
//  ExerciseChallengeView.swift
//  work_for_it
//
//  Created by jason daniel umana on 9/18/26.
//

import SwiftUI

struct ExerciseChallengeView: View {

    @StateObject private var camera = CameraManager()
    @StateObject private var counter = ExerciseRepCounter()

    var body: some View {
        ZStack {

            // MARK: - Camera Preview

            CameraPreview(
                session: camera.session
            )
            .ignoresSafeArea()

            // Slight dark overlay for text readability
            Color.black
                .opacity(0.15)
                .ignoresSafeArea()

            VStack {

                // MARK: - Exercise Picker

                Picker(
                    "Exercise",
                    selection: $counter.exercise
                ) {

                    ForEach(
                        ExerciseRepCounter.Exercise.allCases
                    ) { exercise in

                        Text(exercise.rawValue)
                            .tag(exercise)
                    }
                }
                .pickerStyle(.segmented)
                .padding()
                .background(.ultraThinMaterial)

                Spacer()

                // MARK: - Rep Counter Card

                VStack(spacing: 12) {

                    Text("\(counter.reps)")
                        .font(
                            .system(
                                size: 90,
                                weight: .bold,
                                design: .rounded
                            )
                        )

                    Text(counter.exercise.rawValue)
                        .font(.title2.bold())

                    Text(counter.feedback)
                        .font(.headline)
                        .multilineTextAlignment(.center)

                    // MARK: - Body Detection Status

                    HStack(spacing: 8) {

                        Circle()
                            .fill(
                                camera.bodyDetected
                                ? Color.green
                                : Color.red
                            )
                            .frame(
                                width: 12,
                                height: 12
                            )

                        Text(
                            camera.bodyDetected
                            ? "Body detected"
                            : "Move into frame"
                        )
                    }
                    .font(.subheadline)
                }
                .foregroundStyle(.white)
                .padding(30)
                .frame(maxWidth: .infinity)
                .background(
                    Color.black.opacity(0.55)
                )
                .clipShape(
                    RoundedRectangle(
                        cornerRadius: 30
                    )
                )
                .padding()

                // MARK: - Reset Button

                Button("Reset Reps") {
                    counter.reset()
                }
                .buttonStyle(.borderedProminent)
                .padding(.bottom, 30)
            }

            // MARK: - Camera Permission Message

            if !camera.permissionGranted {

                VStack(spacing: 16) {

                    Image(
                        systemName: "camera.fill"
                    )
                    .font(
                        .system(size: 50)
                    )

                    Text("Camera Access Required")
                        .font(.title2.bold())

                    Text(
                        "Work For It needs camera access to detect your body and count your exercise reps."
                    )
                    .multilineTextAlignment(.center)
                }
                .padding(30)
                .background(
                    .ultraThinMaterial
                )
                .clipShape(
                    RoundedRectangle(
                        cornerRadius: 24
                    )
                )
                .padding()
            }
        }

        // MARK: - Send Body Joints to Rep Counter

        .onReceive(camera.$joints) { joints in

            guard !joints.isEmpty else {
                return
            }

            counter.update(
                with: joints
            )
        }

        // MARK: - Camera Lifecycle

        .onAppear {
            camera.start()
        }

        .onDisappear {
            camera.stop()
        }
    }
}

#Preview {
    ExerciseChallengeView()
}
