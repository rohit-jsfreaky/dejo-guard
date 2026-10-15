// Where the hero's website thumbnails sit: two staggered columns per side, sizes in px, so nothing overlaps or upscales.
// Deterministic, so the server and the browser draw the same layout.

export type Tile = { side: "l" | "r"; x: number; y: number; w: number; depth: number; shot: string; delay: number; stop: number | null };

function seeded(seed: number) {
  let a = seed;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const SIZES = [132, 112, 144, 104, 124, 116, 140, 108, 128];
const SHOTS = Array.from({ length: 24 }, (_, i) => `t${String(i + 1).padStart(2, "0")}`);

function place() {
  const depth = seeded(23);
  const tiles: Omit<Tile, "shot" | "delay" | "stop">[] = [];
  for (const side of ["l", "r"] as const) {
    const cols: [number, number][] = [
      [14, 18],
      [166, 96],
    ];
    cols.forEach(([edge, startY], col) => {
      let i = col * 3 + (side === "l" ? 0 : 4);
      for (let y = startY; y < 1000; ) {
        const w = SIZES[i % SIZES.length];
        i++;
        tiles.push({ side, x: edge + (col === 0 ? 0 : Math.floor((144 - w) / 2)), y, w, depth: 0.55 + depth() * 0.45 });
        y += Math.floor(w * 0.99) + 26;
      }
    });
  }
  return tiles;
}

export function heroTiles(): Tile[] {
  const tiles = place();
  // the trail visits three tiles down the left, then three up the right
  const stopsOf = (side: "l" | "r", reverse: boolean) => {
    const pool = tiles.filter((t) => t.side === side && t.y >= 120 && t.y <= 720).sort((a, b) => (reverse ? b.y - a.y : a.y - b.y));
    return [pool[0], pool[Math.floor(pool.length / 2)], pool[pool.length - 1]];
  };
  const stops = [...stopsOf("l", false), ...stopsOf("r", true)];
  const shuffle = seeded(5);
  const order = [...SHOTS];
  for (let i = order.length - 1; i > 0; i--) {
    const j = Math.floor(shuffle() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }
  return tiles.map((t, i) => ({
    ...t,
    shot: order[i % order.length],
    delay: (i * 1.3) % 12,
    stop: stops.includes(t) ? stops.indexOf(t) : null,
  }));
}
