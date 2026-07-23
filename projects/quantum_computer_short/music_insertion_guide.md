# Music Insertion Guide

## Important copyright notice
The requested reference track **METAMORPHOSIS — INTERWORLD** is a copyrighted commercial release.
This repository **must not** contain the file unless you have a valid license for the project.
The default build therefore produces two outputs:

1. `quantum_short_voice_sfx.mp4` — narration, sound effects, and a generated ambient bed only.
2. `quantum_short_reference_music_mix.mp4` — **only produced if** you place a licensed audio file at `assets/audio/quantum_music.mp3` (or similar) and run the optional music mix step.

## How to add the reference track
1. Acquire a properly licensed copy of the track.
2. Place it at `assets/audio/quantum_music.mp3`.
3. Ensure it is trimmed to start at the first beat and is at least 60 seconds long.
4. Run:
   ```bash
   python projects/quantum_computer_short/build.py --with-music assets/audio/quantum_music.mp3
   ```
5. The build script will duck the music under voice using FFmpeg sidechain-style compression and align it to the cues in `music_cue_sheet.json`.

## If you do not have the track
Use the `voice_sfx` version and add music directly in YouTube Shorts editor, CapCut, or DaVinci Resolve using the cue sheet as a guide.

## Generated ambient bed
The build script synthesizes a dark ambient bed (soft electrical hum, risers, low-frequency hits) in `audio/ambient_bed.wav`. This is royalty-free and is safe to use as a placeholder or final background if no commercial track is available.

## SFX-only output
`quantum_short_voice_sfx.mp4` is the primary deliverable. It contains:
- Edge-TTS Vietnamese narration.
- Synthesized digital pulse, switch click, shutter snap, riser, and interference hit.
- Ducking applied so narration is always clear.
