# Manim Animation Workflow

Generate programmatic math/animation explainer videos with [Manim](https://www.manim.community/) (the 3Blue1Brown animation engine).

## Pipeline

1. **Ingest** (optional) – `yt-dlp` downloads a YouTube source and extracts auto-captions.
2. **Script** – `tools/edu_script_tools.py` builds a kid-friendly scene list via Ollama or a fallback template.
3. **Narration** – `tools/tts_tools.py` renders each scene to a WAV using pyttsx3 or Windows SAPI.
4. **Manim scene** – `tools/manim_tools.py` writes a `Scene` class and calls `manim` to render it.
5. **Assembly** – `tools/edu_visual_tools.py` mixes narration and optional background music.

The visual Manim scene currently shows one slide per segment: a colored circle + burned-in text. This is the simplest way to keep rendering reliable while the script/LLM improves.

## Installation

```cmd
pip install manim
```

On Windows you may also need a LaTeX distribution (MiKTeX/TinyTeX) if you want `MathTex` formulas. Plain `Text` objects work without LaTeX.

## Usage

```cmd
# Render a Manim explainer from a topic (works without Ollama/YouTube)
python -m agents.orchestrator --manim --idea "fractions" --audience kids

# From a YouTube URL (requires yt-dlp and a local Ollama for script generation)
python -m agents.orchestrator --manim --youtube "https://www.youtube.com/watch?v=..." --audience kids
```

Output: `projects/<project_id>/final_manim_video.mp4`

## Why Manim?

- **Programmatic**: every frame is Python code, so the agent can generate scenes from a script.
- **Math-first**: built-in `MathTex`, `Axes`, `FunctionGraph`, `Vector`, `Transform`, etc.
- **Smooth animations**: fades, morphs, camera moves, 3D support.
- **Two versions**: the 3b1b fork (`manimgl`) is Grant Sanderson's bespoke version; the Community edition (`manim`) is well-documented and easier to install. This repo uses the Community edition.

## Limitations & next steps

- The auto-generated scene is intentionally simple (text slides). For richer math visuals, pipe the script into an LLM prompt that writes Manim code directly, or call `tools/manim_tools.write_scene_file` with custom Manim source.
- Text-only labels avoid the LaTeX dependency. For formulas, install MiKTeX/TinyTeX and use `MathTex`.
- `manim` can be slow on CPU; 480p15 (`-q l`) is the default for fast iteration.
