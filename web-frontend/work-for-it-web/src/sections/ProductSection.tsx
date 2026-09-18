import "./Sections.css";

const FEATURES = [
  {
    title: "On-device pose tracking",
    body: "Every rep is verified locally. No camera frame ever leaves your machine.",
  },
  {
    title: "Real reps, not timers",
    body: "A knee-angle state machine counts full-range reps, so half-reps don't count.",
  },
  {
    title: "No account needed",
    body: "Nothing to sign up for. Install it and it just works.",
  },
];

export default function ProductSection() {
  return (
    <section className="product-section">
      <div className="wrap">
        <span className="eyebrow">Camera-verified workout lock</span>
        <h2>No reps, no Shorts.</h2>
        <p className="product-lede">
          Work For It blocks YouTube Shorts until your camera sees you finish a real set.
          On-device pose tracking counts your reps — nothing is ever recorded or uploaded.
        </p>

        <button type="button" className="btn btn-primary">
          Add to Chrome
        </button>

        <div className="product-features">
          {FEATURES.map((feature) => (
            <div className="product-feature" key={feature.title}>
              <h3>{feature.title}</h3>
              <p>{feature.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
