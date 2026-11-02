# Golazo Night Cup – credits

## Stadium model

`stadium.js` contains a simplified, repacked version of:

**"Al Wakrah Stadium Worldcup 2022"** by Ninh Phạm
(https://sketchfab.com/yu.gi_oh2011), from
https://sketchfab.com/3d-models/al-wakrah-stadium-worldcup-2022-d7452e247d55493e8e6a9c086a4eafe6

Licensed under CC BY-NC-SA 4.0 (http://creativecommons.org/licenses/by-nc-sa/4.0/).

These changes were made for the game:

- Mirrored, re-centred on the pitch, and simplified by vertex clustering.
- The seats, pitch, goals, boards and ground were removed. Spectator positions are sampled from the seat cushions and the dugout seats.
- The roof panels over the pitch and the hanging screen objects were removed.

Under the same license, the modified model is non-commercial, needs attribution, and must be shared alike.

## Goalkeeper model

`keeper.js` contains a repacked version of:

**"654230010 SHANNON GOALKEEPER BODY BLOCK"** by 654230010
(https://sketchfab.com/654230010), from
https://sketchfab.com/3d-models/654230010-shannon-goalkeeper-body-block-dcb2ecef5d3146b3af612ecaa4bea183

Licensed under CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/).

These changes were made for the game:

- The materials were converted to metal/rough.
- The textures were re-encoded and unused UV sets removed.
- Goalkeeper gloves were painted over the hands.
- In the game the kit is tinted in each team's goalkeeper colours, and the skeleton is driven by the game's own animation.
- The model's diving-save animation is baked into joint poses (in `index.html`) and drives the keepers' dives.

## Goalkeeper set position

The keepers' set position is baked from the animation of:

**"Goalkeeper Stylized - Rig and Animation"** by P-Vi.Art
(https://sketchfab.com/dpducphong), from
https://sketchfab.com/3d-models/goalkeeper-stylized-rig-and-animation-7de86f9c36f84152a777f27a73646ada

Licensed under CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/). Only the motion is used: the joint positions are resampled onto the game's skeleton.

## Not included in this public copy

The player-supplied competition intro video, the menu stadium-atmosphere recording and the Chelsea win film (with its soundtrack) are used only in the private build of the game. They are not stored in this repository.

## Trademarks

Club crests, competition marks, sponsor marks and broadcaster logos belong to their owners. This is a non-commercial fan project for personal use.
