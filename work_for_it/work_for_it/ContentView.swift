//
//  ContentView.swift
//  work_for_it
//
//  Created by jason daniel umana on 9/18/26.
//

import SwiftUI

struct ContentView: View {

    var body: some View {
        NavigationStack {

            ZStack {

                // MARK: - Background

                LinearGradient(
                    colors: [
                        Color.black,
                        Color.gray.opacity(0.8)
                    ],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()

                VStack(spacing: 30) {

                    Spacer()

                    // MARK: - Logo / Title

                    Image(systemName: "figure.strengthtraining.traditional")
                        .font(.system(size: 80))
                        .foregroundStyle(.white)

                    VStack(spacing: 10) {

                        Text("Work For It")
                            .font(
                                .system(
                                    size: 42,
                                    weight: .bold,
                                    design: .rounded
                                )
                            )
                            .foregroundStyle(.white)

                        Text(
                            "Earn your screen time."
                        )
                        .font(.title3)
                        .foregroundStyle(
                            .white.opacity(0.75)
                        )
                    }

                    // MARK: - Description

                    VStack(spacing: 12) {

                        Text(
                            "Complete an exercise challenge before accessing your social apps."
                        )
                        .font(.headline)
                        .multilineTextAlignment(.center)
                        .foregroundStyle(.white)

                        Text(
                            "Your camera tracks your movement and automatically counts your reps."
                        )
                        .font(.subheadline)
                        .multilineTextAlignment(.center)
                        .foregroundStyle(
                            .white.opacity(0.7)
                        )
                    }
                    .padding(.horizontal, 30)

                    Spacer()

                    // MARK: - Start Button

                    NavigationLink {

                        ExerciseChallengeView()

                    } label: {

                        HStack(spacing: 12) {

                            Image(
                                systemName:
                                    "camera.fill"
                            )

                            Text(
                                "Start Challenge"
                            )
                            .fontWeight(.bold)
                        }
                        .font(.title3)
                        .foregroundStyle(.black)
                        .frame(
                            maxWidth: .infinity
                        )
                        .padding()
                        .background(
                            Color.white
                        )
                        .clipShape(
                            RoundedRectangle(
                                cornerRadius: 18
                            )
                        )
                    }
                    .padding(.horizontal, 30)

                    Text(
                        "Choose Squat or Push-Up on the next screen"
                    )
                    .font(.caption)
                    .foregroundStyle(
                        .white.opacity(0.6)
                    )

                    Spacer()
                        .frame(height: 20)
                }
            }
            .toolbar(.hidden)
        }
    }
}

#Preview {
    ContentView()
}
