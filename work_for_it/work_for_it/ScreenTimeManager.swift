//
//  ScreenTimeManager.swift
//  work_for_it
//
//  Created by jason daniel umana on 9/18/26.
//

import Foundation
import Combine
import FamilyControls
import ManagedSettings

@MainActor
final class ScreenTimeManager: ObservableObject {

    static let shared = ScreenTimeManager()

    // MARK: - Published Properties

    @Published var selection = FamilyActivitySelection()

    @Published var message: String?


    // MARK: - Private Properties

    private let store = ManagedSettingsStore()

    private let selectionStorageKey =
        "work_for_it.FamilyActivitySelection"


    // MARK: - Initialization

    private init() {
        loadSelection()
    }


    // MARK: - Authorization

    func requestAuthorization() async -> Bool {

        // If the user already gave permission,
        // don't ask again.
        if AuthorizationCenter.shared.authorizationStatus == .approved {
            return true
        }

        do {

            try await AuthorizationCenter.shared
                .requestAuthorization(for: .individual)

            return AuthorizationCenter.shared.authorizationStatus == .approved

        } catch {

            let nsError = error as NSError

            print("FAMILY CONTROLS ERROR")
            print("Domain:", nsError.domain)
            print("Code:", nsError.code)
            print("Description:", nsError.localizedDescription)
            print("UserInfo:", nsError.userInfo)

            message = """
            Could not request Screen Time access.

            \(nsError.localizedDescription)
            """

            return false
        }
    }


    // MARK: - Block Apps

    func blockSelectedApps() {

        guard
            AuthorizationCenter.shared.authorizationStatus == .approved
        else {

            message =
                "Screen Time permission is required before apps can be locked."

            return
        }


        let applications =
            selection.applicationTokens


        guard !applications.isEmpty else {

            message =
                "Choose at least one app first."

            return
        }


        /*
         Work For It currently works with
         individual applications only.

         We do not want the user selecting an
         entire category such as all Games.
         */

        guard selection.categoryTokens.isEmpty else {

            message =
                "Choose individual apps instead of entire categories."

            return
        }


        /*
         THIS LINE ACTUALLY BLOCKS
         THE SELECTED APPLICATIONS.
         */

        store.shield.applications =
            applications


        let count =
            applications.count

        message =
            "\(count) app\(count == 1 ? "" : "s") locked."
    }


    // MARK: - Unlock Apps

    func unblockAllApps() {

        store.shield.applications = nil

        message =
            "All apps have been unlocked."
    }


    // MARK: - Save Selection

    func saveSelection() {

        do {

            let encodedSelection =
                try JSONEncoder()
                    .encode(selection)

            UserDefaults.standard.set(
                encodedSelection,
                forKey: selectionStorageKey
            )

        } catch {

            print(
                "Failed to save selection:",
                error.localizedDescription
            )

            message =
                "Could not save your selected apps."
        }
    }


    // MARK: - Load Selection

    private func loadSelection() {

        guard
            let savedData =
                UserDefaults.standard.data(
                    forKey: selectionStorageKey
                )
        else {
            return
        }


        do {

            selection =
                try JSONDecoder()
                    .decode(
                        FamilyActivitySelection.self,
                        from: savedData
                    )

        } catch {

            print(
                "Failed to load selection:",
                error.localizedDescription
            )

            UserDefaults.standard.removeObject(
                forKey: selectionStorageKey
            )
        }
    }
}
