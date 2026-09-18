# ComfyUI Qwen3-ASR HF

Windows ComfyUI custom node for local Qwen3-ASR Hugging Face models.

## Model folders

Place complete HF model directories under:

```text
ComfyUI/models/qwen3_asr/
├─ Qwen3-ASR-1.7B-hf/
└─ Qwen3-ForcedAligner-0.6B-hf/
```

The node also accepts an absolute custom model path. Model weights are not
included in this repository.

## Features

- Single audio input or folder batch transcription.
- Chinese interface and model/language selectors.
- Custom output directory and filename without overwriting existing files.
- Optional word-level timestamp JSON and SRT output.

Forced alignment supports up to five minutes of audio in Chinese, English,
Cantonese, French, German, Italian, Japanese, Korean, Portuguese, Russian and
Spanish. Japanese timestamps require `nagisa`; Korean timestamps require
`soynlp`.

## Installation

Copy this directory into `ComfyUI/custom_nodes`, install `requirements.txt`
with ComfyUI's Python, then restart ComfyUI.

## License

MIT. Model weights keep their original upstream licenses and are not included.
