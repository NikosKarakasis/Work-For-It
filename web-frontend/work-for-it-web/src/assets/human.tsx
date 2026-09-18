export default function Human() {
  return (
    <div className="viewfinder">
      <div className="vf-bracket vf-tl" />
      <div className="vf-bracket vf-tr" />
      <div className="vf-bracket vf-bl" />
      <div className="vf-bracket vf-br" />
      <div className="vf-scan" />

      <div className="silhouette-box">
        <svg viewBox="0 0 100 140" className="silhouette" aria-hidden="true">
          <g className="sil-body">
            {/* torso */}
            <line x1="50" y1="25" x2="50" y2="62" strokeWidth="18">
              <animate attributeName="y1" values="25;31;25" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y2" values="62;66;62" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
            </line>

            {/* shoulders */}
            <line x1="32" y1="32" x2="68" y2="32" strokeWidth="16">
              <animate attributeName="y1" values="32;38;32" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y2" values="32;38;32" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
            </line>

            {/* hips */}
            <line x1="38" y1="58" x2="62" y2="58" strokeWidth="16">
              <animate attributeName="x1" values="38;34;38" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="x2" values="62;66;62" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y1" values="58;68;58" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y2" values="58;68;58" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
            </line>

            {/* head */}
            <circle cx="50" cy="16" r="11">
              <animate attributeName="cy" values="16;22;16" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
            </circle>

            {/* left arm */}
            <line x1="32" y1="32" x2="24" y2="50" strokeWidth="13">
              <animate attributeName="y1" values="32;38;32" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="x2" values="24;15;24" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y2" values="50;52;50" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
            </line>
            <line x1="24" y1="50" x2="20" y2="66" strokeWidth="11">
              <animate attributeName="x1" values="24;15;24" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y1" values="50;52;50" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="x2" values="20;8;20" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y2" values="66;64;66" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
            </line>

            {/* right arm */}
            <line x1="68" y1="32" x2="76" y2="50" strokeWidth="13">
              <animate attributeName="y1" values="32;38;32" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="x2" values="76;85;76" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y2" values="50;52;50" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
            </line>
            <line x1="76" y1="50" x2="80" y2="66" strokeWidth="11">
              <animate attributeName="x1" values="76;85;76" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y1" values="50;52;50" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="x2" values="80;92;80" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y2" values="66;64;66" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
            </line>

            {/* left leg */}
            <line x1="38" y1="58" x2="34" y2="90" strokeWidth="15">
              <animate attributeName="x1" values="38;34;38" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y1" values="58;68;58" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="x2" values="34;26;34" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y2" values="90;92;90" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
            </line>
            <line x1="34" y1="90" x2="32" y2="122" strokeWidth="12">
              <animate attributeName="x1" values="34;26;34" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y1" values="90;92;90" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="x2" values="32;30;32" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
            </line>
            <ellipse cx="32" cy="127" rx="9" ry="5">
              <animate attributeName="cx" values="32;30;32" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
            </ellipse>

            {/* right leg */}
            <line x1="62" y1="58" x2="66" y2="90" strokeWidth="15">
              <animate attributeName="x1" values="62;66;62" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y1" values="58;68;58" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="x2" values="66;74;66" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y2" values="90;92;90" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
            </line>
            <line x1="66" y1="90" x2="68" y2="122" strokeWidth="12">
              <animate attributeName="x1" values="66;74;66" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="y1" values="90;92;90" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
              <animate attributeName="x2" values="68;70;68" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
            </line>
            <ellipse cx="68" cy="127" rx="9" ry="5">
              <animate attributeName="cx" values="68;70;68" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.15 1;0.45 0 0.15 1" />
            </ellipse>
          </g>

        </svg>
      </div>

      <style>{`
        .viewfinder {
          position: relative;
          width: min(420px, 85vw);
          aspect-ratio: 1;
          margin: 0 auto;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .vf-bracket {
          position: absolute;
          width: 34px;
          height: 34px;
          border: 3px solid var(--cyan, #4DD9C0);
          z-index: 3;
        }
        .vf-tl { top: 0; left: 0; border-right: none; border-bottom: none; border-top-left-radius: 10px; }
        .vf-tr { top: 0; right: 0; border-left: none; border-bottom: none; border-top-right-radius: 10px; }
        .vf-bl { bottom: 0; left: 0; border-right: none; border-top: none; border-bottom-left-radius: 10px; }
        .vf-br { bottom: 0; right: 0; border-left: none; border-top: none; border-bottom-right-radius: 10px; }

        .vf-scan {
          position: absolute;
          left: 8%;
          right: 8%;
          height: 2px;
          background: linear-gradient(90deg, transparent, var(--cyan, #4DD9C0), transparent);
          top: 12%;
          z-index: 2;
          animation: vf-scan-move 2.6s ease-in-out infinite;
        }
        @keyframes vf-scan-move {
          0%, 100% { top: 12%; opacity: 0.3; }
          50% { top: 88%; opacity: 1; }
        }

        .silhouette-box {
          --sil-fill: var(--cyan, #4DD9C0);
          --sil-dot: var(--accent, #FF3D6E);
          width: 62%;
          aspect-ratio: 100 / 140;
          filter: drop-shadow(0 0 22px color-mix(in srgb, var(--sil-fill) 45%, transparent));
          z-index: 1;
        }
        .silhouette { width: 100%; height: 100%; overflow: visible; }
        .sil-body line, .sil-body ellipse { stroke: var(--sil-fill); stroke-linecap: round; fill: var(--sil-fill); }
        .sil-body circle { fill: var(--sil-fill); }
        .sil-joints .dot { fill: var(--sil-dot); animation: sil-pulse 1.6s ease-in-out infinite; }

        @keyframes sil-pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }

        @media (prefers-reduced-motion: reduce) {
          .vf-scan { animation: none; top: 50%; opacity: 0.5; }
          .sil-body animate, .sil-joints animate { display: none; }
          .sil-joints .dot { animation: none; }
        }
      `}</style>
    </div>
  );
}