# RepLock

**Pay in reps, not in scroll time.**

RepLock is a browser extension (with a companion web dashboard) that blocks short-form video feeds — TikTok, Instagram Reels, YouTube Shorts — behind a live, camera-verified workout. To open the feed, you have to actually do the exercise. Your webcam watches your form and counts real reps using on-device pose detection; no video ever leaves your machine.

Built at [Hackathon Name] by [Team Name].

---

## The Problem

Short-form video is engineered to be nearly impossible to self-regulate. App-level screen time limits and site blockers are trivial to bypass ("Remind Me in 15 Minutes," disabling the extension, etc.) because they only cost a click. RepLock raises the cost of unlocking to something that has to be *physically earned* — and turns doomscrolling into an accidental workout habit.

## How It Works

1. **Detect** — A browser extension watches for short-form video domains/URL patterns (`tiktok.com`, `instagram.com/reels/*`, `youtube.com/shorts/*`).
2. **Block** — Before the feed renders, a full-screen overlay takes over the tab.
3. **Verify** — The overlay requests camera access and starts a pose-estimation model. The user performs an exercise (e.g., squats) in view of the camera.
4. **Count** — A rep-counting state machine tracks joint angles frame-by-frame to count valid, full-range reps (no half-reps, no gaming the counter).
5. **Unlock** — Once the target rep count is hit, the overlay dismisses and the feed is unlocked for a configurable session window (e.g., 10 minutes) before re-locking.

## Features

- **Real-time pose detection** — client-side pose estimation (e.g., MediaPipe Pose / TensorFlow.js MoveNet) run entirely in-browser; no frames are uploaded or stored.
- **Rep counting, not timers** — an angle-threshold state machine counts genuine up/down repetitions per exercise, so users can't just "wait out" a timer.
- **Skeleton overlay feedback** — a live joint overlay on the camera feed shows the user they're being tracked correctly and helps with form.
- **Configurable difficulty** — rep count and unlock duration are adjustable; difficulty can scale up with usage (e.g., more reps required per unlock over time).
- **Multi-exercise support** — squats, push-ups, jumping jacks, and plank holds (stability-based rather than rep-based).
- **Site blocklist** — user-configurable list of domains/URL patterns to gate.
- **Stats dashboard** — tracks reps completed, sessions blocked, and streaks over time.
- **Privacy-first by design** — all camera processing happens on-device; the app never transmits or persists video.

## Architecture

| Layer | Responsibility |
|---|---|
| Browser extension (content script) | Detects target URLs, injects the blocking overlay before feed content loads |
| Pose engine | Runs pose estimation on the live camera feed and emits joint landmark coordinates per frame |
| Rep-counter module | Consumes landmarks, applies per-exercise angle thresholds, and emits verified rep/hold events |
| Unlock manager | Grants a timed unlock once the rep target is met; re-locks on session expiry |
| Web dashboard | Marketing/landing page + stats view + settings (blocklist, difficulty, exercise selection) |
| Local storage | Persists streaks, stats, and settings on-device (no backend required for MVP) |

## Tech Stack (proposed)

- **Extension:** Manifest V3 (content scripts + `declarativeNetRequest`)
- **Pose detection:** MediaPipe Pose or TensorFlow.js MoveNet (WASM/WebGL, runs client-side)
- **Web dashboard:** React/Vite (or plain HTML/CSS/JS for hackathon speed)
- **Storage:** LocalStorage/IndexedDB (no backend needed for MVP)

## Privacy

RepLock requires camera access to function, which is a deliberately sensitive permission — the app is transparent about it:

- Pose detection runs **entirely on-device**; camera frames are never uploaded, streamed, or stored.
- No account or sign-in is required for the core blocking/unlock flow.
- Users can revoke camera permission at any time, which simply disables unlocking (the block stays in place).

## Team & Roles

- **Landing page / Web hero (this repo's web dashboard entry point):** [Your name] — owns the marketing landing page that introduces RepLock, communicates the camera + workout mechanic, and drives install/demo conversion.
- *(Add other team members and roles here — pose detection, extension/blocking logic, rep-counting algorithm, dashboard/stats, etc.)*

## Status

Hackathon MVP — targeting one platform (browser extension) and one exercise (squats) fully working end-to-end for the demo, with additional exercises and the stats dashboard as stretch goals.

## Getting Started

```bash
# clone and install
git clone <repo-url>
cd replock
npm install

# run the web dashboard locally
npm run dev

# load the extension unpacked (Chrome)
# chrome://extensions -> Developer mode -> Load unpacked -> /extension
```
