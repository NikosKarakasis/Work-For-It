import "./Sections.css";

const POINTS = [
  {
    title: "Nothing leaves your device",
    body: "Pose detection runs entirely on-device. Camera frames are never uploaded, streamed, or stored.",
  },
  {
    title: "No account required",
    body: "There's nothing to sign up for. Install the extension and it just works.",
  },
  {
    title: "Camera access is yours to revoke",
    body: "Turn off camera permission any time — the app simply stays locked until you turn it back on.",
  },
];

export default function PrivacySection() {
  return (
    <section className="privacy-section">
      <div className="wrap">
        <span className="eyebrow">Privacy</span>
        <h2>Your camera never leaves your machine.</h2>

        <div className="privacy-points">
          {POINTS.map((point) => (
            <div className="privacy-point" key={point.title}>
              <h3>{point.title}</h3>
              <p>{point.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
