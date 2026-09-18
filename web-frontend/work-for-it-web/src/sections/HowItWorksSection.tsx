import "./Sections.css";

const STEPS = [
  {
    n: "01",
    title: "Detect",
    body: "Work For It watches for YouTube Shorts as you browse.",
  },
  {
    n: "02",
    title: "Block",
    body: "Before the video plays, a full-screen lock takes over the tab.",
  },
  {
    n: "03",
    title: "Verify",
    body: "Your camera turns on and watches you perform the exercise.",
  },
  {
    n: "04",
    title: "Count",
    body: "On-device pose tracking counts real, full-range reps — no half-reps.",
  },
  {
    n: "05",
    title: "Unlock",
    body: "Hit the target rep count and the feed opens for a set window of time.",
  },
];

export default function HowItWorksSection() {
  return (
    <section className="how-it-works-section">
      <div className="wrap">
        <span className="eyebrow">How it works</span>
        <h2>Five steps between you and your feed.</h2>

        <ol className="steps-list">
          {STEPS.map((step) => (
            <li className="steps-item" key={step.n}>
              <span className="steps-num">{step.n}</span>
              <div>
                <h3>{step.title}</h3>
                <p>{step.body}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
