import { Composition, Folder } from "remotion";
import { PLANS } from "./plans";
import { FPS, Short, timeline } from "./Short";

// Ten standalone TikTok shorts (1080 x 1920), each timed to its own voiceover.
export const RemotionRoot: React.FC = () => {
  return (
    <Folder name="CL27-Shorts">
      {PLANS.map((p) => (
        <Composition key={p.id} id={p.id} component={Short} durationInFrames={timeline(p.id).total} fps={FPS} width={1080} height={1920} defaultProps={{ id: p.id }} />
      ))}
    </Folder>
  );
};
