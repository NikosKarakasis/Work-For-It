//
//  AppSelectionView.swift
//  work_for_it
//
//  Created by jason daniel umana on 9/18/26.
//

import SwiftUI
import FamilyControls
import ManagedSettings

struct AppSelectionView: View {

    @StateObject private var screenTime =
        ScreenTimeManager.shared

    @State private var showingPicker =
        false


    // MARK: - Background

    private let backgroundColor =
        Color(
            red: 0.95,
            green: 0.97,
            blue: 0.99
        )


    var body: some View {

        ZStack {

            backgroundColor
                .ignoresSafeArea()


            VStack(
                alignment: .leading,
                spacing: 0
            ) {

                // Progress bar
                topBar


                // MARK: - Title

                Text(
                    "Which social apps\ndo you want\nto lock?"
                )
                .font(
                    .system(
                        size: 40,
                        weight: .bold,
                        design: .rounded
                    )
                )
                .foregroundStyle(.black)
                .padding(.top, 30)


                // MARK: - Subtitle

                Text(
                    "Choose apps like Instagram, TikTok, YouTube, Facebook, X, Reddit, or Snapchat."
                )
                .font(
                    .system(size: 17)
                )
                .foregroundStyle(.secondary)
                .padding(.top, 12)


                // MARK: - Main Content

                ScrollView {

                    VStack(spacing: 16) {

                        if screenTime
                            .selection
                            .applicationTokens
                            .isEmpty {

                            emptyState

                        } else {

                            selectedApps
                        }


                        chooseAppsButton


                        // Category warning
                        if !screenTime
                            .selection
                            .categoryTokens
                            .isEmpty {

                            warningCard(
                                text:
                                    "Choose individual apps instead of entire categories."
                            )
                        }


                        // Website warning
                        if !screenTime
                            .selection
                            .webDomainTokens
                            .isEmpty {

                            warningCard(
                                text:
                                    "Website selections are not used in this version."
                            )
                        }
                    }
                    .padding(.top, 30)
                    .padding(.bottom, 24)
                }


                // MARK: - Lock Button

                lockAppsButton


                // MARK: - Unlock Testing Button

                if !screenTime
                    .selection
                    .applicationTokens
                    .isEmpty {

                    unblockButton
                        .padding(.top, 10)
                }
            }
            .padding(.horizontal, 24)
            .padding(.top, 10)
            .padding(.bottom, 16)
        }


        // MARK: - Apple's App Picker

        .familyActivityPicker(
            isPresented: $showingPicker,
            selection: $screenTime.selection
        )


        // Save selection automatically
        .onChange(
            of: screenTime.selection
        ) { _, _ in

            screenTime.saveSelection()
        }


        // MARK: - Alert

        .alert(
            "Work For It",
            isPresented: Binding(

                get: {
                    screenTime.message != nil
                },

                set: { newValue in

                    if !newValue {
                        screenTime.message = nil
                    }
                }
            )
        ) {

            Button(
                "OK",
                role: .cancel
            ) {

                screenTime.message = nil
            }

        } message: {

            Text(
                screenTime.message ?? ""
            )
        }
    }


    // MARK: - Top Progress Bar

    private var topBar: some View {

        HStack(spacing: 18) {

            Button {

                // Back navigation will be
                // added later.

            } label: {

                Image(
                    systemName:
                        "chevron.left"
                )
                .font(
                    .system(
                        size: 22,
                        weight: .bold
                    )
                )
                .foregroundStyle(.black)
                .frame(
                    width: 52,
                    height: 52
                )
                .background(.white)
                .clipShape(Circle())
            }
            .buttonStyle(.plain)


            GeometryReader { geometry in

                ZStack(
                    alignment: .leading
                ) {

                    // Background progress bar
                    Capsule()
                        .fill(
                            Color.gray
                                .opacity(0.16)
                        )
                        .frame(height: 12)


                    // Current progress
                    Capsule()
                        .fill(Color.blue)
                        .frame(
                            width:
                                geometry
                                    .size
                                    .width
                                * 0.33,

                            height: 12
                        )
                }
            }
            .frame(height: 12)
        }
    }


    // MARK: - Selected Apps

    private var selectedApps: some View {

        VStack(spacing: 16) {

            HStack {

                Text(
                    "\(screenTime.selection.applicationTokens.count) selected"
                )
                .font(
                    .system(
                        size: 15,
                        weight: .semibold
                    )
                )
                .foregroundStyle(
                    .secondary
                )


                Spacer()
            }


            ForEach(
                Array(
                    screenTime
                        .selection
                        .applicationTokens
                ),
                id: \.self
            ) { token in

                SocialAppCard(
                    token: token
                )
            }
        }
    }


    // MARK: - Empty State

    private var emptyState: some View {

        VStack(spacing: 14) {

            Image(
                systemName:
                    "rectangle.stack.badge.plus"
            )
            .font(
                .system(size: 44)
            )
            .foregroundStyle(.blue)


            Text(
                "No social apps selected"
            )
            .font(
                .system(
                    size: 20,
                    weight: .bold
                )
            )


            Text(
                "Tap below and choose the social media apps you want to earn access to."
            )
            .font(
                .system(size: 15)
            )
            .foregroundStyle(
                .secondary
            )
            .multilineTextAlignment(
                .center
            )
            .padding(.horizontal)
        }
        .frame(
            maxWidth: .infinity
        )
        .padding(
            .vertical,
            34
        )
        .background(.white)
        .clipShape(
            RoundedRectangle(
                cornerRadius: 24,
                style: .continuous
            )
        )
        .shadow(
            color:
                .black.opacity(0.06),
            radius: 0,
            x: 0,
            y: 6
        )
    }


    // MARK: - Choose Apps Button

    private var chooseAppsButton: some View {

        Button {

            Task {

                let approved =
                    await screenTime
                        .requestAuthorization()


                guard approved else {
                    return
                }


                showingPicker = true
            }

        } label: {

            HStack(spacing: 14) {

                Image(
                    systemName:
                        "plus.circle.fill"
                )
                .font(
                    .system(size: 22)
                )


                VStack(
                    alignment: .leading,
                    spacing: 2
                ) {

                    Text(
                        screenTime
                            .selection
                            .applicationTokens
                            .isEmpty

                        ? "Choose Social Apps"

                        : "Add or Remove Apps"
                    )
                    .font(
                        .system(
                            size: 18,
                            weight: .semibold
                        )
                    )


                    Text(
                        "Instagram, TikTok, YouTube and more"
                    )
                    .font(
                        .system(size: 13)
                    )
                    .foregroundStyle(
                        .secondary
                    )
                }


                Spacer()


                Image(
                    systemName:
                        "chevron.right"
                )
                .font(
                    .system(
                        size: 16,
                        weight: .semibold
                    )
                )
            }
            .foregroundStyle(.blue)
            .padding(
                .horizontal,
                22
            )
            .frame(height: 78)
            .background(.white)
            .clipShape(
                RoundedRectangle(
                    cornerRadius: 22,
                    style: .continuous
                )
            )
            .shadow(
                color:
                    .black.opacity(0.06),
                radius: 0,
                x: 0,
                y: 6
            )
        }
        .buttonStyle(.plain)
    }


    // MARK: - Lock Apps Button

    private var lockAppsButton: some View {

        let appCount =
            screenTime
                .selection
                .applicationTokens
                .count


        let hasApps =
            appCount > 0


        return Button {

            screenTime.saveSelection()

            screenTime
                .blockSelectedApps()

        } label: {

            HStack {

                Image(
                    systemName:
                        "lock.fill"
                )


                Text(
                    hasApps

                    ? "Lock \(appCount) App\(appCount == 1 ? "" : "s")"

                    : "Choose Apps First"
                )
            }
            .font(
                .system(
                    size: 18,
                    weight: .bold
                )
            )
            .frame(
                maxWidth: .infinity
            )
            .frame(height: 60)
            .background(

                hasApps
                ? Color.blue
                : Color.gray
                    .opacity(0.25)
            )
            .foregroundStyle(.white)
            .clipShape(
                RoundedRectangle(
                    cornerRadius: 18,
                    style: .continuous
                )
            )
        }
        .disabled(!hasApps)
    }


    // MARK: - Unlock Button

    private var unblockButton: some View {

        Button {

            screenTime
                .unblockAllApps()

        } label: {

            Text(
                "Unlock All Apps"
            )
            .font(
                .system(
                    size: 16,
                    weight: .semibold
                )
            )
            .frame(
                maxWidth: .infinity
            )
            .frame(height: 50)
        }
        .buttonStyle(.plain)
        .foregroundStyle(.blue)
    }


    // MARK: - Warning Card

    private func warningCard(
        text: String
    ) -> some View {

        HStack(spacing: 12) {

            Image(
                systemName:
                    "exclamationmark.triangle.fill"
            )
            .foregroundStyle(.orange)


            Text(text)
                .font(
                    .system(size: 14)
                )
                .foregroundStyle(
                    .secondary
                )


            Spacer()
        }
        .padding(16)
        .background(
            Color.orange
                .opacity(0.08)
        )
        .clipShape(
            RoundedRectangle(
                cornerRadius: 16
            )
        )
    }
}


// MARK: - Selected App Card

struct SocialAppCard: View {

    let token: ApplicationToken


    var body: some View {

        HStack(spacing: 16) {

            /*
             Apple displays the selected
             app's icon and name here.
             */

            Label(token)
                .labelStyle(
                    .titleAndIcon
                )
                .font(
                    .system(
                        size: 20,
                        weight: .semibold
                    )
                )


            Spacer()


            Image(
                systemName:
                    "checkmark.circle.fill"
            )
            .font(
                .system(size: 24)
            )
            .foregroundStyle(.blue)
        }
        .padding(
            .horizontal,
            22
        )
        .frame(height: 82)
        .background(.white)
        .clipShape(
            RoundedRectangle(
                cornerRadius: 22,
                style: .continuous
            )
        )
        .overlay {

            RoundedRectangle(
                cornerRadius: 22,
                style: .continuous
            )
            .stroke(
                Color.gray
                    .opacity(0.12),
                lineWidth: 1
            )
        }
        .shadow(
            color:
                .black.opacity(0.07),
            radius: 0,
            x: 0,
            y: 6
        )
    }
}


#Preview {
    AppSelectionView()
}
