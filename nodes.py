import importlib.util
import json
import os
import tempfile

import torch
import soundfile as sf
import folder_paths

from transformers import (
    AutoModelForMultimodalLM,
    AutoModelForTokenClassification,
    AutoProcessor,
)


# =========================
# 模型缓存
# =========================

_MODEL_CACHE = {}
_ALIGNER_CACHE = {}

QWEN_MODEL_CATEGORY = "qwen3_asr"
QWEN_MODEL_ROOT = os.path.join(folder_paths.models_dir, QWEN_MODEL_CATEGORY)
folder_paths.add_model_folder_path(
    QWEN_MODEL_CATEGORY,
    QWEN_MODEL_ROOT,
    is_default=True,
)

AUDIO_EXTENSIONS = {
    ".wav", ".mp3", ".flac", ".m4a", ".ogg",
    ".opus", ".aac", ".wma", ".webm",
}

LANGUAGE_OPTIONS = {
    "自动检测": None,
    "中文（zh）": "zh",
    "英语（en）": "en",
    "粤语（yue）": "yue",
    "阿拉伯语（ar）": "ar",
    "德语（de）": "de",
    "法语（fr）": "fr",
    "西班牙语（es）": "es",
    "葡萄牙语（pt）": "pt",
    "印度尼西亚语（id）": "id",
    "意大利语（it）": "it",
    "韩语（ko）": "ko",
    "俄语（ru）": "ru",
    "泰语（th）": "th",
    "越南语（vi）": "vi",
    "日语（ja）": "ja",
    "土耳其语（tr）": "tr",
    "印地语（hi）": "hi",
    "马来语（ms）": "ms",
    "荷兰语（nl）": "nl",
    "瑞典语（sv）": "sv",
    "丹麦语（da）": "da",
    "芬兰语（fi）": "fi",
    "波兰语（pl）": "pl",
    "捷克语（cs）": "cs",
    "菲律宾语（fil）": "fil",
    "波斯语（fa）": "fa",
    "希腊语（el）": "el",
    "匈牙利语（hu）": "hu",
    "马其顿语（mk）": "mk",
    "罗马尼亚语（ro）": "ro",
}

ALIGNER_LANGUAGE_ALIASES = {
    "zh": "zh", "chinese": "zh",
    "en": "en", "english": "en",
    "yue": "yue", "cantonese": "yue",
    "fr": "fr", "french": "fr",
    "de": "de", "german": "de",
    "it": "it", "italian": "it",
    "ja": "ja", "japanese": "ja",
    "ko": "ko", "korean": "ko",
    "pt": "pt", "portuguese": "pt",
    "ru": "ru", "russian": "ru",
    "es": "es", "spanish": "es",
}
ALIGNER_DEPENDENCIES = {
    "ja": ("nagisa", "pip install nagisa"),
    "ko": ("soynlp", "pip install soynlp"),
}
MAX_ALIGNER_SECONDS = 300


def discover_comfyui_models(architecture):
    models = {}

    for root in folder_paths.get_folder_paths(QWEN_MODEL_CATEGORY):
        if not os.path.isdir(root):
            continue

        for current, dirs, files in os.walk(root):
            dirs[:] = [name for name in dirs if not name.startswith(".")]

            if "config.json" not in files:
                continue

            try:
                with open(
                    os.path.join(current, "config.json"),
                    "r",
                    encoding="utf-8",
                ) as config_file:
                    config = json.load(config_file)
            except (OSError, ValueError):
                continue

            if architecture not in config.get("architectures", []):
                continue

            label = os.path.relpath(current, root)
            if label == ".":
                label = os.path.basename(current)

            original = label
            number = 2
            while label in models:
                label = f"{original} ({number})"
                number += 1

            models[label] = os.path.abspath(current)
            dirs[:] = []

    return models


def resolve_model_path(model_name, model_path, architecture):
    if model_name != "自定义路径":
        models = discover_comfyui_models(architecture)
        if model_name not in models:
            raise FileNotFoundError(
                f"ComfyUI 模型目录中找不到：{model_name}"
            )
        return models[model_name]

    model_path = model_path.strip()
    if not model_path:
        raise ValueError(
            "请选择 ComfyUI 模型，或填写自定义模型路径。\n"
            f"推荐模型目录：{QWEN_MODEL_ROOT}"
        )

    model_path = os.path.abspath(
        os.path.expandvars(os.path.expanduser(model_path))
    )

    config_path = os.path.join(model_path, "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            architectures = json.load(config_file).get("architectures", [])
    except (OSError, ValueError) as error:
        raise FileNotFoundError(f"模型配置不可用：\n{config_path}") from error

    if architecture not in architectures:
        raise ValueError(f"模型类型不匹配，需要：{architecture}")

    return model_path


def collect_audio_files(input_dir):
    input_dir = input_dir.strip()
    if not input_dir:
        return []

    input_dir = os.path.abspath(
        os.path.expandvars(os.path.expanduser(input_dir))
    )
    if not os.path.isdir(input_dir):
        raise FileNotFoundError(f"音频文件夹不存在：\n{input_dir}")

    return sorted(
        os.path.join(input_dir, name)
        for name in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, name))
        and os.path.splitext(name)[1].lower() in AUDIO_EXTENSIONS
    )


def validate_aligner_language(language):
    language_key = str(language or "").strip().lower()
    language_code = ALIGNER_LANGUAGE_ALIASES.get(language_key)
    if not language_code:
        raise ValueError(
            f"Forced Aligner 不支持词级时间戳语言：{language or '未知'}。\n"
            "支持：中文、英语、粤语、法语、德语、意大利语、日语、韩语、"
            "葡萄牙语、俄语、西班牙语。"
        )

    dependency = ALIGNER_DEPENDENCIES.get(language_code)
    if dependency and importlib.util.find_spec(dependency[0]) is None:
        raise ImportError(
            f"{language or language_code} 词级时间戳需要额外依赖：\n"
            f"{dependency[1]}"
        )

    return language_code


def get_audio_duration(audio_path):
    try:
        return float(sf.info(audio_path).duration)
    except (OSError, RuntimeError):
        try:
            import librosa
            return float(librosa.get_duration(path=audio_path))
        except Exception as error:
            raise ValueError(f"无法读取音频时长：\n{audio_path}") from error


def validate_aligner_duration(duration_seconds, source_name):
    if duration_seconds > MAX_ALIGNER_SECONDS:
        raise ValueError(
            f"Forced Aligner 最多支持 5 分钟音频：{source_name}\n"
            f"当前时长：{duration_seconds:.1f} 秒"
        )


def iter_audio_batches(audio_items):
    if not audio_items:
        return

    batch_size = min(len(audio_items), 3)
    for start in range(0, len(audio_items), batch_size):
        yield audio_items[start:start + batch_size]


def resolve_device(device):
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device


def resolve_dtype(precision, device):
    if device == "cpu":
        return torch.float32

    if precision == "bf16":
        return torch.bfloat16
    if precision == "fp16":
        return torch.float16
    if precision == "fp32":
        return torch.float32

    # auto
    if torch.cuda.is_available() and torch.cuda.is_bf16_supported():
        return torch.bfloat16

    return torch.float16


def load_model(model_path, device, precision):
    device = resolve_device(device)
    dtype = resolve_dtype(precision, device)

    cache_key = (model_path, device, str(dtype))

    if cache_key in _MODEL_CACHE:
        return _MODEL_CACHE[cache_key]

    if not os.path.isdir(model_path):
        raise FileNotFoundError(
            f"Qwen3-ASR-HF 模型目录不存在：\n{model_path}"
        )

    print("[Qwen3-ASR-HF] 加载 Processor...")
    processor = AutoProcessor.from_pretrained(
        model_path,
        local_files_only=True,
    )

    print(
        f"[Qwen3-ASR-HF] 加载模型：{model_path}\n"
        f"[Qwen3-ASR-HF] device={device}, dtype={dtype}"
    )

    model = AutoModelForMultimodalLM.from_pretrained(
        model_path,
        dtype=dtype,
        local_files_only=True,
    )

    model = model.to(device)
    model.eval()

    _MODEL_CACHE[cache_key] = (processor, model)

    print("[Qwen3-ASR-HF] 模型加载完成")

    return processor, model


def load_aligner(model_path, device, precision):
    device = resolve_device(device)
    dtype = resolve_dtype(precision, device)
    cache_key = (model_path, device, str(dtype))

    if cache_key in _ALIGNER_CACHE:
        return _ALIGNER_CACHE[cache_key]

    processor = AutoProcessor.from_pretrained(
        model_path,
        local_files_only=True,
    )
    model = AutoModelForTokenClassification.from_pretrained(
        model_path,
        dtype=dtype,
        local_files_only=True,
    ).to(device)
    model.eval()
    _ALIGNER_CACHE[cache_key] = (processor, model)
    return processor, model


# =========================
# ComfyUI AUDIO → 临时 WAV
# =========================

def comfy_audio_to_wav(audio):
    if not isinstance(audio, dict):
        raise TypeError("AUDIO 输入格式错误。")

    waveform = audio.get("waveform")
    sample_rate = audio.get("sample_rate")

    if waveform is None:
        raise ValueError("AUDIO 中没有 waveform。")

    if sample_rate is None:
        raise ValueError("AUDIO 中没有 sample_rate。")

    if not isinstance(waveform, torch.Tensor):
        waveform = torch.as_tensor(waveform)

    waveform = waveform.detach().cpu()

    # ComfyUI 通常为：
    # [batch, channels, samples]
    if waveform.ndim == 3:
        waveform = waveform[0]

    # 转单声道
    if waveform.ndim == 2:
        waveform = waveform.mean(dim=0)

    if waveform.ndim != 1:
        raise ValueError(
            f"无法识别 AUDIO waveform 形状：{tuple(waveform.shape)}"
        )

    waveform = waveform.float().numpy()

    fd, temp_path = tempfile.mkstemp(
        prefix="qwen3_asr_",
        suffix=".wav",
    )
    os.close(fd)

    sf.write(
        temp_path,
        waveform,
        int(sample_rate),
    )

    return temp_path


# =========================
# 保存 TXT
# =========================

def resolve_output_directory(output_dir=""):
    output_dir = output_dir.strip()

    if output_dir:
        output_dir = os.path.abspath(
            os.path.expandvars(os.path.expanduser(output_dir))
        )
    else:
        output_dir = folder_paths.get_output_directory()

    os.makedirs(output_dir, exist_ok=True)

    return os.path.abspath(output_dir)


def select_output_directory(initial_dir="", title="选择转写文件保存目录"):
    import tkinter as tk
    from tkinter import filedialog

    initial_dir = initial_dir.strip()

    if not os.path.isdir(initial_dir):
        initial_dir = folder_paths.get_output_directory()

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    try:
        selected = filedialog.askdirectory(
            parent=root,
            initialdir=initial_dir,
            mustexist=True,
            title=title,
        )
    finally:
        root.destroy()

    return os.path.abspath(selected) if selected else ""


def open_output_directory(output_dir=""):
    output_dir = resolve_output_directory(output_dir)
    os.startfile(output_dir)
    return output_dir


def save_txt_file(text, filename, output_dir=""):
    output_dir = resolve_output_directory(output_dir)

    if not filename:
        filename = "qwen3_asr"

    filename = os.path.basename(filename)

    if filename.lower().endswith(".txt"):
        filename = filename[:-4]

    number = 0

    while True:
        suffix = "" if number == 0 else f"_{number:03d}"
        output_path = os.path.join(
            output_dir,
            f"{filename}{suffix}.txt",
        )

        try:
            with open(
                output_path,
                "x",
                encoding="utf-8",
            ) as f:
                f.write(text)
            break
        except FileExistsError:
            number += 1

    print(f"[Qwen3-ASR-HF] TXT 已保存：{output_path}")

    return output_path


def format_srt_time(seconds):
    milliseconds = max(0, round(float(seconds) * 1000))
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def timestamps_to_srt(timestamps):
    blocks = []
    for number, item in enumerate(timestamps, 1):
        blocks.append(
            f"{number}\n"
            f"{format_srt_time(item['start_time'])} --> "
            f"{format_srt_time(item['end_time'])}\n"
            f"{item['text']}"
        )
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def save_timestamp_files(timestamps, filename, output_dir=""):
    output_dir = resolve_output_directory(output_dir)
    filename = os.path.basename(filename or "qwen3_asr")
    for suffix in (".txt", ".srt", ".json"):
        if filename.lower().endswith(suffix):
            filename = filename[:-len(suffix)]
            break

    number = 0
    while True:
        suffix = "" if number == 0 else f"_{number:03d}"
        stem = os.path.join(output_dir, f"{filename}{suffix}")
        json_path = f"{stem}.timestamps.json"
        srt_path = f"{stem}.srt"
        if not os.path.exists(json_path) and not os.path.exists(srt_path):
            break
        number += 1

    with open(json_path, "x", encoding="utf-8") as file:
        json.dump(timestamps, file, ensure_ascii=False, indent=2)
    with open(srt_path, "x", encoding="utf-8") as file:
        file.write(timestamps_to_srt(timestamps))

    return json_path, srt_path


# =========================
# 节点
# =========================

class Qwen3ASRHFNode:

    @classmethod
    def INPUT_TYPES(cls):
        model_names = [
            "自定义路径",
            *discover_comfyui_models("Qwen3ASRForConditionalGeneration").keys(),
        ]
        aligner_names = [
            "自定义路径",
            *discover_comfyui_models("Qwen3ASRForTokenClassification").keys(),
        ]

        return {
            "required": {
                "input_dir": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                    },
                ),

                "model_name": (model_names,),

                "model_path": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                    },
                ),

                "language": (
                    list(LANGUAGE_OPTIONS),
                ),

                "prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                    },
                ),

                "max_new_tokens": (
                    "INT",
                    {
                        "default": 1024,
                        "min": 32,
                        "max": 8192,
                        "step": 32,
                    },
                ),

                "device": (
                    [
                        "auto",
                        "cuda",
                        "cpu",
                    ],
                ),

                "precision": (
                    [
                        "auto",
                        "bf16",
                        "fp16",
                        "fp32",
                    ],
                ),

                "save_txt": (
                    "BOOLEAN",
                    {
                        "default": False,
                    },
                ),

                "output_filename": (
                    "STRING",
                    {
                        "default": "qwen3_asr",
                        "multiline": False,
                    },
                ),

                "generate_timestamps": (
                    "BOOLEAN",
                    {"default": False},
                ),

                "aligner_model_name": (aligner_names,),

                "aligner_model_path": (
                    "STRING",
                    {
                        "default": os.path.join(
                            QWEN_MODEL_ROOT,
                            "Qwen3-ForcedAligner-0.6B-hf",
                        ),
                        "multiline": False,
                    },
                ),

                "output_dir": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                    },
                ),
            },
            "optional": {
                "audio": ("AUDIO",),
            },
        }

    RETURN_TYPES = (
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
    )

    RETURN_NAMES = (
        "text",
        "language",
        "txt_path",
        "timestamps_json",
        "srt_path",
    )

    FUNCTION = "transcribe"

    CATEGORY = "音频/Qwen3-ASR-HF"

    # 非常重要：
    # 让节点自己成为输出节点
    OUTPUT_NODE = True


    def transcribe(
        self,
        input_dir,
        model_name,
        model_path,
        generate_timestamps,
        aligner_model_name,
        aligner_model_path,
        language,
        prompt,
        max_new_tokens,
        device,
        precision,
        save_txt,
        output_filename,
        output_dir,
        audio=None,
    ):

        device = resolve_device(device)
        model_path = resolve_model_path(
            model_name,
            model_path,
            "Qwen3ASRForConditionalGeneration",
        )
        if generate_timestamps:
            aligner_model_path = resolve_model_path(
                aligner_model_name,
                aligner_model_path,
                "Qwen3ASRForTokenClassification",
            )

        temp_audio = None

        try:
            audio_items = []

            if audio is not None:
                temp_audio = comfy_audio_to_wav(audio)
                audio_items.append((output_filename or "qwen3_asr", temp_audio))

            for audio_path in collect_audio_files(input_dir):
                audio_items.append((
                    os.path.splitext(os.path.basename(audio_path))[0],
                    audio_path,
                ))

            if not audio_items:
                raise ValueError("请连接音频，或填写包含音频文件的输入文件夹。")

            language_arg = LANGUAGE_OPTIONS.get(language, language)
            if language_arg == "auto":
                language_arg = None

            prompt_arg = prompt.strip() or None

            if generate_timestamps:
                if language_arg is not None:
                    validate_aligner_language(language_arg)
                for source_name, audio_path in audio_items:
                    validate_aligner_duration(
                        get_audio_duration(audio_path),
                        source_name,
                    )

            processor, model = load_model(
                model_path=model_path,
                device=device,
                precision=precision,
            )
            aligner_processor = aligner_model = None
            if generate_timestamps:
                aligner_processor, aligner_model = load_aligner(
                    model_path=aligner_model_path,
                    device=device,
                    precision=precision,
                )

            print(
                f"[Qwen3-ASR-HF] 开始识别，共 {len(audio_items)} 个音频"
            )

            results = []
            for batch in iter_audio_batches(audio_items):
                paths = [item[1] for item in batch]
                languages = [language_arg] * len(batch)
                prompts = [prompt_arg] * len(batch)

                inputs = processor.apply_transcription_request(
                    audio=paths,
                    language=languages,
                    prompt=prompts,
                ).to(model.device, model.dtype)

                with torch.inference_mode():
                    output_ids = model.generate(
                        **inputs,
                        max_new_tokens=max_new_tokens,
                        do_sample=False,
                    )

                generated_ids = output_ids[
                    :,
                    inputs["input_ids"].shape[1]:
                ]
                parsed_batch = processor.decode(
                    generated_ids,
                    return_format="parsed",
                )
                if len(parsed_batch) != len(batch):
                    raise RuntimeError("模型返回数量与本批音频数量不一致。")

                timestamp_batch = [None] * len(batch)
                if generate_timestamps:
                    transcripts = [
                        str(parsed.get("transcription") or "").strip()
                        for parsed in parsed_batch
                    ]
                    if any(not transcript for transcript in transcripts):
                        raise ValueError("转写文本为空，无法生成词级时间戳。")
                    detected_languages = [
                        validate_aligner_language(
                            parsed.get("language") or language_arg
                        )
                        for parsed in parsed_batch
                    ]
                    aligner_inputs, word_lists = (
                        aligner_processor.prepare_forced_aligner_inputs(
                            audio=paths,
                            transcript=transcripts,
                            language=detected_languages,
                        )
                    )
                    aligner_inputs = aligner_inputs.to(
                        aligner_model.device,
                        aligner_model.dtype,
                    )
                    with torch.inference_mode():
                        aligner_outputs = aligner_model(**aligner_inputs)
                    timestamp_batch = aligner_processor.decode_forced_alignment(
                        logits=aligner_outputs.logits,
                        input_ids=aligner_inputs["input_ids"],
                        word_lists=word_lists,
                        timestamp_token_id=aligner_model.config.timestamp_token_id,
                    )

                for (source_name, _), parsed, timestamps in zip(
                    batch,
                    parsed_batch,
                    timestamp_batch,
                ):
                    text = str(parsed.get("transcription") or "").strip()
                    detected_language = str(parsed.get("language") or "").strip()
                    if len(audio_items) == 1:
                        filename = output_filename or source_name
                    elif output_filename:
                        filename = f"{output_filename}_{source_name}"
                    else:
                        filename = source_name
                    txt_path = ""
                    if save_txt:
                        txt_path = save_txt_file(
                            text,
                            filename,
                            output_dir,
                        )

                    timestamps_json = ""
                    srt_path = ""
                    if timestamps is not None:
                        timestamps_json = json.dumps(
                            timestamps,
                            ensure_ascii=False,
                        )
                        _, srt_path = save_timestamp_files(
                            timestamps,
                            filename,
                            output_dir,
                        )

                    results.append((
                        source_name,
                        text,
                        detected_language,
                        txt_path,
                        timestamps_json,
                        srt_path,
                    ))

                    print("")
                    print(f"========== {source_name} ==========")
                    print(f"语言：{detected_language}")
                    print("")
                    print(text)
                    print("==================================")
                    print("")

            if len(results) == 1:
                (
                    _, text, detected_language, txt_path,
                    timestamps_json, srt_path,
                ) = results[0]
            else:
                text = "\n\n".join(
                    f"[{name}]\n{item_text}"
                    for name, item_text, _, _, _, _ in results
                )
                detected_language = "\n".join(
                    f"{name}: {item_language}"
                    for name, _, item_language, _, _, _ in results
                )
                txt_path = "\n".join(
                    item_path
                    for _, _, _, item_path, _, _ in results
                    if item_path
                )
                timestamps_json = "\n".join(
                    item_json
                    for _, _, _, _, item_json, _ in results
                    if item_json
                )
                srt_path = "\n".join(
                    item_path
                    for _, _, _, _, _, item_path in results
                    if item_path
                )

            # -------------------------
            # 7. ComfyUI UI + 输出
            # -------------------------

            return {
                "ui": {
                    "text": [text],
                    "language": [
                        detected_language
                    ],
                },

                "result": (
                    text,
                    detected_language,
                    txt_path,
                    timestamps_json,
                    srt_path,
                ),
            }

        finally:
            if temp_audio:
                if os.path.exists(temp_audio):
                    try:
                        os.remove(temp_audio)
                    except Exception:
                        pass


# =========================
# ComfyUI 注册
# =========================

NODE_CLASS_MAPPINGS = {
    "Qwen3ASRHFNode":
        Qwen3ASRHFNode,
}


NODE_DISPLAY_NAME_MAPPINGS = {
    "Qwen3ASRHFNode":
        "Qwen3-ASR-HF 语音识别",
}
