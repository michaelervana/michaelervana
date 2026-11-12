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

## Player model

`player.js` contains a repacked version of:

**"Animated Football Player Trips Loop"** by LasquetiSpice
(https://sketchfab.com/LasquetiSpice), from
https://sketchfab.com/3d-models/animated-football-player-trips-loop-d68b6101da814089a4dfcf012016283a

Licensed under CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/).

These changes were made for the game:

- The animation was removed and the skeleton reset to its bind pose; the game's own animation drives it.
- The mesh was simplified (about 48,000 to 23,000 triangles) and unused UV sets and tangents removed.
- The textures were re-encoded; the shirt number, crest and brand marks were painted out.
- In the game every defender and forward wears this model. A shader colours the kit per club (stripes and bands included), prints the player's name, number and club crest, and applies one of three skin tones.

## Match officials and midfielders model

`referee.js` contains a repacked version of:

**"Man Player"** by RiverofCreative
(https://sketchfab.com/RiverofCreative), from
https://sketchfab.com/3d-models/man-player-4c7133dbb06e4136891d59231372d818

Licensed under CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/).

These changes were made for the game:

- The static poses were removed and the skeleton flattened (helper nodes removed) in its rest pose.
- The tongue, teeth, nails, corneas and eyelashes were removed and the rest simplified (about 45,000 to 24,000 triangles).
- The colour textures were combined into one atlas; shirt, shorts and boots were turned neutral grey so they can be coloured in game.
- In the game the referee, both assistants and the midfielders of both teams wear this model. A shader colours the kit, draws socks on the shins, prints name, number and crest, and applies one of three skin tones.

## Match ball and pitch grass

`pitch.js` contains material derived from:

**"Soccer ball"** by Agisoft (https://sketchfab.com/agisoft), from
https://sketchfab.com/3d-models/soccer-ball-7aa17e963bc84f63ad665e5f8d8d17de

**"Green Grass"** by ROY (https://sketchfab.com/roy.gearloft.in), from
https://sketchfab.com/3d-models/green-grass-1b900e5cb8a84e0fa96b3a6df11c03d1

Both licensed under CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/).

These changes were made for the game:

- The ball scan was baked onto a sphere map (white-balanced) and is wrapped on the game's ball.
- The grass model is used three ways: its blade heights, baked from above into a seamless tile, drive the layered 3D grass over the whole pitch; the same bake gives the turf its fine detail; and 380 of its tufts, each simplified, form a tile of real blades planted around the camera for close views.

## Goal

`pitch.js` also contains the frame of the "Football goal" model supplied by the project owner (an FBX with rope textures; its archive carries no author or licence file, so none can be credited here).

- Used: posts and crossbar, ground frame, the three rear poles and the stay lines, with depths fitted to the game's net.
- Not used as geometry: the rope net (about 220,000 triangles). The game draws the net as a simulated cloth in the same honeycomb mesh, so the ball can spear and shake it.

## Commentary

`voice.js` holds 95 short commentary clips generated with Google AI Studio (Gemini speech, voice "Fenrir"): kick-offs, goals, scores nil to twenty, ball won back, goal kicks and free kicks, naming clubs only. They are played back to back to form each line. If the clips cannot load, the browser's own English speech voice (Web Speech API) reads the same lines.

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
