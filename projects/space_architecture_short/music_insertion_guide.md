# Music Insertion Guide — Space Architecture Short

## Default
The build already mixes the royalty-free bed `assets/music/bensound-softvibes.mp3` at ~12 % volume, ducked under the Vietnamese voiceover and SFX.

## Reference / copyrighted track
If you provide a licensed music file (e.g. "METAMORPHOSIS — INTERWORLD") you can swap it in:

```cmd
python projects\space_architecture_short\build.py --with-music "path/to/licensed_track.mp3"
```

This produces `projects/space_architecture_short/space_architecture_reference_music_mix.mp4`.

## Cue-sheet workflow
1. Open `music_cue_sheet.json`.
2. Replace `"target_track"` with the actual song title and rights holder.
3. Adjust cue times to match the final rendered durations (run `build.py` first to get `config.json` timings).
4. Provide the licensed audio file and run `build.py --with-music <file>`.

## Do not commit copyrighted audio
Only commit `.wav`/`.mp3` files you own or that are explicitly royalty-free.
