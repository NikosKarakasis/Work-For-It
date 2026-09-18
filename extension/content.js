console.log("Work for it content script loaded")

const UNLOCK_DURATION_MS = 10 * 60 * 1000; // 10 minutes

let lastPath = location.pathname


window.addEventListener("message", (event) => {
    if (event.data.workForItUnlocked) {
        chrome.storage.local.set({ unlockedUntil: Date.now() + UNLOCK_DURATION_MS });

        const frame = document.getElementById("work-for-it-lock");

        if (frame) {
            frame.remove();
        }
    }
});

document.addEventListener("DOMContentLoaded", () => {
            checkIfShort();

// callback - function that runs every time a relevant DOM change occurs
const observer = new MutationObserver(() => {
    if(location.pathname !== lastPath) {
        lastPath = location.pathname;
        checkIfShort();
    }});

// targetNode - what part of the page to watch - we'll use document.body(whole page)
// options - an object describing what kinds of changes to watch for.
// we want { childList: true, subtree: true } - childList means elements being added/removed, subtree means not just direct children of document.body, but anywhere nested underneath it too
observer.observe(document.body, { childList: true, subtree: true });
})


async function checkIfShort() {

    if (location.pathname.startsWith("/shorts/")) {
        const stored = await chrome.storage.local.get("unlockedUntil");
        const unlockedUntil = stored.unlockedUntil || 0;

        if (Date.now() < unlockedUntil) {
            console.log("Still within unlock window, skipping lock");
            return;
        }

        console.log("LOCKED. This is a short")

        if (!document.getElementById("work-for-it-lock")) {
            const lockFrame = document.createElement("iframe");

            lockFrame.allow = "camera";

            lockFrame.id = "work-for-it-lock";
            lockFrame.src = chrome.runtime.getURL("lock.html");
            lockFrame.style.position = "fixed";
            lockFrame.style.top = "0";
            lockFrame.style.left = "0";
            lockFrame.style.width = "100%";
            lockFrame.style.height = "100%";
            lockFrame.style.border = "none";
            lockFrame.style.zIndex = "2147483647";
            document.body.appendChild(lockFrame);
        }
    } else {
        console.log("Not a short")

        const existingFrame = document.getElementById("work-for-it-lock");

        if (existingFrame) {
            existingFrame.remove();
        }
    }

}