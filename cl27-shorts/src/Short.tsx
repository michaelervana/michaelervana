import { Audio, Video } from "@remotion/media";
import { loadFont } from "@remotion/fonts";
import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  Interactive,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import MEDIA from "./media.json";
import VO from "./vo.json";
import { Beat, PLANS, Plan } from "./plans";

// fonts are bundled locally (the game's own Barlow family), so rendering never waits on the network
const DISPLAY = "Barlow Condensed", BODY = "Barlow";
const FACES: [string, string, string, string][] = [
  [DISPLAY, "normal", "700", "BarlowCondensed-normal-700"], [DISPLAY, "normal", "800", "BarlowCondensed-normal-800"], [DISPLAY, "normal", "900", "BarlowCondensed-normal-900"],
  [DISPLAY, "italic", "800", "BarlowCondensed-italic-800"], [DISPLAY, "italic", "900", "BarlowCondensed-italic-900"],
  [BODY, "normal", "600", "Barlow-normal-600"], [BODY, "normal", "700", "Barlow-normal-700"],
];
for (const [family, style, weight, file] of FACES) loadFont({ family, style, weight, url: staticFile(`fonts/${file}-latin.woff2`), format: "woff2" });

export const FPS = 30;
const LEAD = 12; // frames of picture before the first word
const GAP = 7; // pause between lines
const OUTRO = 54; // end card
const NAVY = "#08112b";
const GOLD = "#ffd23d";

// layout (1080 x 1920, kept clear of TikTok's top bar and bottom caption/UI area)
const CARD = { x: 40, y: 470, w: 1000, h: 562 };
const BIG_Y = 1062;
const CAP_Y = 1345;

type Line = { src: string; dur: number; text: string };
type Voice = { name: string; lines: Line[] };

export const timeline = (id: string) => {
  const v = (VO as Record<string, Voice>)[id];
  let t = LEAD;
  const lines = v.lines.map((l) => {
    const from = t, len = Math.ceil(l.dur * FPS);
    t += len + GAP;
    return { ...l, from, len };
  });
  const end = t - GAP + 10;
  return { lines, end, total: end + OUTRO };
};

const mediaDur = (key: string) => {
  const k = key.split("@")[0];
  return (MEDIA as Record<string, number>)[k] ?? 5;
};
const mediaSrc = (key: string) => {
  const k = key.split("@")[0];
  return staticFile(`media/${k.startsWith("g:") ? "game" : "ref"}/${k.slice(2)}.mp4`);
};
const mediaStart = (key: string) => Number(key.split("@")[1] ?? 0);

// One clip for one stretch of the timeline: ref clips sit in a card over a blurred copy of themselves,
// gameplay fills the frame. Both drift in slowly (Ken Burns) so nothing is ever static.
const Clip: React.FC<{ k: string; len: number; seed: number }> = ({ k, len, seed }) => {
  const frame = useCurrentFrame();
  const start = mediaStart(k), dur = mediaDur(k);
  const trimBefore = Math.round(Math.min(start, Math.max(0, dur - 1)) * FPS);
  const loop = dur - start < len / FPS + 0.2;
  const game = k.startsWith("g:");
  const zoom = interpolate(frame, [0, len], seed % 2 ? [1.04, 1.13] : [1.13, 1.04], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const pan = interpolate(frame, [0, len], seed % 3 === 0 ? [-18, 18] : [14, -14], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const enter = spring({ frame, fps: FPS, config: { damping: 200 }, durationInFrames: 12 });
  if (game) {
    return (
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <Video src={mediaSrc(k)} muted loop={loop} trimBefore={trimBefore} objectFit="cover"
          style={{ width: "100%", height: "100%", scale: String(zoom), translate: `0px ${pan}px` }} />
        <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(4,8,22,.5) 0%, rgba(4,8,22,0) 20%, rgba(4,8,22,0) 52%, rgba(4,8,22,.6) 72%, rgba(4,8,22,.85) 100%)" }} />
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Video src={mediaSrc(k)} muted loop={loop} trimBefore={trimBefore} objectFit="cover"
        style={{ width: "100%", height: "100%", scale: "1.35", filter: "blur(30px) brightness(.72) saturate(1.3)" }} />
      <AbsoluteFill style={{ background: `radial-gradient(120% 70% at 50% 38%, rgba(8,17,43,.05), rgba(8,17,43,.78))` }} />
      <Interactive.Div name="Card" style={{
        position: "absolute", left: CARD.x, top: CARD.y, width: CARD.w, height: CARD.h, overflow: "hidden", borderRadius: 26,
        boxShadow: "0 30px 80px rgba(0,0,0,.6), 0 0 0 3px rgba(255,255,255,.16)",
        opacity: enter, scale: String(interpolate(enter, [0, 1], [0.94, 1])),
      }}>
        <Video src={mediaSrc(k)} muted loop={loop} trimBefore={trimBefore} objectFit="cover"
          style={{ width: "100%", height: "100%", scale: String(zoom), translate: `${pan}px 0px` }} />
        <AbsoluteFill style={{ boxShadow: "inset 0 0 120px rgba(0,0,0,.45)" }} />
      </Interactive.Div>
    </AbsoluteFill>
  );
};

// Beats: each voiceover line gets its own picture(s), split evenly when there are two.
const Pictures: React.FC<{ plan: Plan; lines: ReturnType<typeof timeline>["lines"]; end: number }> = ({ plan, lines, end }) => {
  const out: React.ReactNode[] = [];
  lines.forEach((l, i) => {
    const b = plan.beats[i], from = i === 0 ? 0 : l.from - 3;
    const until = i + 1 < lines.length ? lines[i + 1].from - 3 : end;
    const n = b.media.length, part = Math.ceil((until - from) / n);
    b.media.forEach((k, j) => {
      const f = from + j * part, len = Math.min(part, until - f);
      out.push(
        <Sequence key={`${i}-${j}`} from={f} durationInFrames={len} premountFor={30} name={`Beat ${i + 1}${n > 1 ? String.fromCharCode(97 + j) : ""}: ${k}`}>
          <Clip k={k} len={len} seed={i * 3 + j} />
        </Sequence>,
      );
    });
  });
  return <>{out}</>;
};

const Stamp: React.FC<{ b: Beat }> = ({ b }) => {
  const frame = useCurrentFrame();
  const s = spring({ frame: frame - 4, fps: FPS, config: { damping: 13, stiffness: 170 } });
  const sub = spring({ frame: frame - 10, fps: FPS, config: { damping: 200 } });
  return (
    <AbsoluteFill style={{ alignItems: "center", pointerEvents: "none" }}>
      {b.big ? (
        <Interactive.Div name="Big" style={{
          position: "absolute", top: BIG_Y, maxWidth: 1000, textAlign: "center", fontFamily: DISPLAY, fontStyle: "italic", fontWeight: 900,
          fontSize: b.big.length > 14 ? 92 : b.big.length > 9 ? 118 : 150, lineHeight: 1, color: GOLD, letterSpacing: "-.01em",
          textShadow: "0 6px 0 rgba(0,0,0,.35), 0 10px 40px rgba(0,0,0,.65)",
          opacity: interpolate(s, [0, 1], [0, 1]), scale: String(interpolate(s, [0, 1], [1.7, 1])),
        }}>{b.big}</Interactive.Div>
      ) : null}
      {b.sub ? (
        <Interactive.Div name="Sub" style={{
          position: "absolute", top: b.big ? BIG_Y + (b.big.length > 14 ? 104 : b.big.length > 9 ? 128 : 160) : BIG_Y + 18, maxWidth: 960, textAlign: "center",
          fontFamily: DISPLAY, fontWeight: 800, fontSize: 44, letterSpacing: ".08em", color: "#fff", padding: "6px 18px",
          background: "rgba(8,17,43,.72)", borderLeft: `6px solid ${GOLD}`, borderRadius: 6,
          opacity: sub, translate: `0px ${interpolate(sub, [0, 1], [24, 0])}px`,
        }}>{b.sub}</Interactive.Div>
      ) : null}
    </AbsoluteFill>
  );
};

// Captions: the line in chunks of a few words, the word being said lit in gold.
const Caption: React.FC<{ text: string; len: number }> = ({ text, len }) => {
  const frame = useCurrentFrame();
  const words = text.split(/\s+/).filter(Boolean);
  const w = words.map((x) => x.length + 2), tot = w.reduce((a, b) => a + b, 0);
  let acc = 0;
  const at = words.map((_, i) => { const s = (acc / tot) * len; acc += w[i]; return s; });
  const chunks: number[][] = []; let cur: number[] = [], cl = 0;
  words.forEach((x, i) => { if (cur.length && (cur.length >= 4 || cl + x.length > 20)) { chunks.push(cur); cur = []; cl = 0; } cur.push(i); cl += x.length + 1; });
  if (cur.length) chunks.push(cur);
  let ci = chunks.findIndex((c, k) => frame < (k + 1 < chunks.length ? at[chunks[k + 1][0]] : len + 999));
  if (ci < 0) ci = chunks.length - 1;
  const chunk = chunks[ci], t0 = at[chunk[0]];
  const lit = chunk.filter((i) => frame >= at[i]).pop() ?? chunk[0];
  const pop = spring({ frame: frame - t0, fps: FPS, config: { damping: 14, stiffness: 220 }, durationInFrames: 10 });
  return (
    <AbsoluteFill style={{ alignItems: "center" }}>
      <Interactive.Div name="Caption" style={{
        position: "absolute", top: CAP_Y, width: 960, textAlign: "center", fontFamily: DISPLAY, fontWeight: 900, fontSize: 82, lineHeight: 1.04,
        textTransform: "uppercase", color: "#fff", WebkitTextStroke: "3px rgba(0,0,0,.55)", paintOrder: "stroke fill",
        textShadow: "0 5px 18px rgba(0,0,0,.8)", scale: String(interpolate(pop, [0, 1], [0.86, 1])), opacity: interpolate(pop, [0, 1], [0.3, 1]),
      }}>
        {chunk.map((i) => (
          <span key={i} style={{ color: i === lit ? GOLD : frame >= at[i] ? "#fff" : "rgba(255,255,255,.55)" }}>
            {words[i]}{" "}
          </span>
        ))}
      </Interactive.Div>
    </AbsoluteFill>
  );
};

const Brand: React.FC<{ size?: number }> = ({ size = 1 }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 18 * size, fontFamily: DISPLAY, fontStyle: "italic", fontWeight: 900 }}>
    <span style={{ fontSize: 112 * size, lineHeight: 0.85, background: "linear-gradient(180deg,#fff 0%,#fff 46%,#b9cdf5 54%,#e9f0ff 100%)", WebkitBackgroundClip: "text", color: "transparent", filter: "drop-shadow(0 6px 22px rgba(80,140,255,.45))" }}>
      CHAMPIONS LEAGUE
    </span>
    <span style={{ fontSize: 64 * size, letterSpacing: ".1em", color: "#fff", padding: `${6 * size}px ${18 * size}px`, borderRadius: 12 * size, border: "2px solid rgba(255,255,255,.5)", background: "linear-gradient(135deg,rgba(255,255,255,.3),rgba(255,255,255,.08))", transform: "skewX(-12deg)" }}>
      27
    </span>
  </div>
);

const Hook: React.FC<{ title: string; len: number }> = ({ title, len }) => {
  const frame = useCurrentFrame();
  const s = spring({ frame, fps: FPS, config: { damping: 15, stiffness: 140 } });
  const out = interpolate(frame, [len - 8, len], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ alignItems: "center" }}>
      <Interactive.Div name="Hook" style={{
        position: "absolute", top: 170, width: 980, textAlign: "center", fontFamily: DISPLAY, fontStyle: "italic", fontWeight: 900, fontSize: 112, lineHeight: 0.95,
        color: "#fff", textShadow: "0 8px 0 rgba(0,0,0,.3), 0 14px 50px rgba(0,0,0,.7)", textWrap: "balance",
        opacity: Math.min(s, out), translate: `0px ${interpolate(s, [0, 1], [-60, 0])}px`,
      }}>
        {title}
        <div style={{ height: 12, width: interpolate(s, [0, 1], [0, 340]), background: GOLD, margin: "22px auto 0", borderRadius: 6, transform: "skewX(-18deg)" }} />
      </Interactive.Div>
    </AbsoluteFill>
  );
};

const TopTag: React.FC<{ tag: string }> = ({ tag }) => {
  const frame = useCurrentFrame();
  const s = spring({ frame, fps: FPS, config: { damping: 200 } });
  return (
    <AbsoluteFill style={{ alignItems: "center" }}>
      <Interactive.Div name="Tag" style={{
        position: "absolute", top: 300, display: "flex", alignItems: "center", gap: 14, fontFamily: DISPLAY, fontWeight: 800, fontSize: 46, letterSpacing: ".14em",
        color: "#fff", padding: "10px 26px", borderRadius: 40, background: "rgba(8,17,43,.7)", border: "2px solid rgba(255,210,61,.55)",
        opacity: s, translate: `0px ${interpolate(s, [0, 1], [-20, 0])}px`,
      }}>
        <span style={{ width: 16, height: 16, borderRadius: 8, background: GOLD, boxShadow: `0 0 18px ${GOLD}` }} />
        {tag}
      </Interactive.Div>
    </AbsoluteFill>
  );
};

const Outro: React.FC<{ k: string }> = ({ k }) => {
  const frame = useCurrentFrame();
  const s = spring({ frame, fps: FPS, config: { damping: 16, stiffness: 120 } });
  return (
    <AbsoluteFill>
      <Clip k={k} len={OUTRO} seed={1} />
      <AbsoluteFill style={{ background: "rgba(4,8,22,.55)" }} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", gap: 46 }}>
        <div style={{ opacity: s, scale: String(interpolate(s, [0, 1], [0.8, 1])) }}><Brand size={0.82} /></div>
        <div style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 50, letterSpacing: ".12em", color: GOLD, opacity: interpolate(frame, [10, 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
          FOLLOW BUAT FAKTA BOLA LAINNYA
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// film grain and vignette on top of everything, for the documentary feel
const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ overflow: "hidden", opacity: 0.09, mixBlendMode: "overlay" }}>
        <Img src={staticFile("media/grain.png")} style={{ position: "absolute", width: 1340, height: 2180, left: -((frame * 137) % 260), top: -((frame * 91) % 260) }} />
      </AbsoluteFill>
      <AbsoluteFill style={{ boxShadow: "inset 0 0 220px rgba(0,0,0,.55)" }} />
    </AbsoluteFill>
  );
};

export const Short: React.FC<{ id: string }> = ({ id }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const plan = PLANS.find((p) => p.id === id)!;
  const { lines, end, total } = timeline(id);
  return (
    <AbsoluteFill style={{ backgroundColor: NAVY, fontFamily: BODY }}>
      <Pictures plan={plan} lines={lines} end={end} />
      {lines.map((l, i) => (
        <Sequence key={`t${i}`} from={l.from} durationInFrames={(i + 1 < lines.length ? lines[i + 1].from : end) - l.from} name={`Text ${i + 1}`}>
          {i > 0 ? <Stamp b={plan.beats[i]} /> : plan.beats[0].big ? <Sequence from={18}><Stamp b={plan.beats[0]} /></Sequence> : null}
          <Caption text={l.text} len={l.len} />
        </Sequence>
      ))}
      <Sequence durationInFrames={lines[0].from + lines[0].len + 4} name="Hook"><Hook title={plan.title} len={lines[0].from + lines[0].len + 4} /></Sequence>
      <Sequence from={lines[1].from} durationInFrames={end - lines[1].from} name="Tag"><TopTag tag={plan.tag} /></Sequence>
      <Sequence from={end} durationInFrames={OUTRO} name="Outro"><Outro k={plan.outro} /></Sequence>
      <Grain />
      <AbsoluteFill style={{ pointerEvents: "none" }}>
        <div style={{ position: "absolute", top: 0, left: 0, height: 8, width: `${(frame / durationInFrames) * 100}%`, background: GOLD }} />
      </AbsoluteFill>
      {/* sound: voice, the game's stadium music under it, a whoosh on every new picture and a hit on every number */}
      {lines.map((l, i) => (
        <Sequence key={`a${i}`} from={l.from} durationInFrames={l.len + 6} layout="none"><Audio src={staticFile(l.src)} volume={1} /></Sequence>
      ))}
      <Audio src={staticFile("media/menu.mp3")} loop volume={(f) => interpolate(f, [0, 20, end, total - 12, total], [0, 0.16, 0.16, 0.35, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.quad) })} />
      {lines.map((l, i) => (i > 0 ? (
        <Sequence key={`w${i}`} from={l.from - 6} durationInFrames={20} layout="none"><Audio src={staticFile("media/sfx/whoosh.wav")} volume={0.28} /></Sequence>
      ) : null))}
      {lines.map((l, i) => (plan.beats[i].big ? (
        <Sequence key={`h${i}`} from={l.from + (i === 0 ? 18 : 4)} durationInFrames={20} layout="none"><Audio src={staticFile("media/sfx/hit.wav")} volume={0.45} /></Sequence>
      ) : null))}
      <Sequence from={end} durationInFrames={20} layout="none"><Audio src={staticFile("media/sfx/whoosh.wav")} volume={0.4} /></Sequence>
    </AbsoluteFill>
  );
};
