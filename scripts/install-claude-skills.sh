#!/usr/bin/env bash
# Installs third-party Claude skills (from the "12 repo GitHub" list) into ~/.claude/skills.
# Run manually or via the SessionStart hook in .claude/settings.json. Idempotent.
set -u
CACHE="${HOME}/.cache/claude-skill-repos"
DEST="${HOME}/.claude/skills"
mkdir -p "$CACHE" "$DEST"

# repo|path-to-skills (dir containing SKILL.md, or a dir of skill folders)
REPOS=(
  "heygen-com/hyperframes|skills"
  "greensock/gsap-skills|skills"
  "Vincentwei1021/video-shotcraft|."
  "Tejashmakwana/motionmaxxing|."
  "arjun988/blender-skills|.claude/skills"
  "achimala/dream-loop|."
  "majidmanzarpour/threejs-game-skills|skills"
  "wheresryan22/anatomy|."
  "viettranx/3dviz-pro-max|skills"
)

for entry in "${REPOS[@]}"; do
  repo="${entry%%|*}"; sub="${entry#*|}"
  dir="$CACHE/${repo//\//__}"
  if [ ! -d "$dir/.git" ]; then
    git clone -q --depth 1 "https://github.com/$repo" "$dir" || { echo "skip $repo (clone failed)"; continue; }
  fi
  src="$dir/$sub"
  if [ -f "$src/SKILL.md" ]; then
    ln -sfn "$src" "$DEST/${repo##*/}"
  else
    for s in "$src"/*/; do
      [ -f "$s/SKILL.md" ] && ln -sfn "${s%/}" "$DEST/$(basename "$s")"
    done
  fi
done
echo "Claude skills installed: $(ls "$DEST" | wc -l)"
