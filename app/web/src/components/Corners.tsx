// Graphify's frame corner: one 20px L, rotated into each corner by the .corner classes in globals.css.
function Corner({ at }: { at: "tl" | "tr" | "bl" | "br" }) {
  return (
    <i className={`corner ${at}`} aria-hidden="true">
      <svg viewBox="0 0 20 20" width="20" height="20">
        <path d="M.75.75V19.25H19.25" fill="none" stroke="currentColor" />
      </svg>
    </i>
  );
}

export function Corners() {
  return (
    <>
      <Corner at="tl" />
      <Corner at="tr" />
      <Corner at="bl" />
      <Corner at="br" />
    </>
  );
}
