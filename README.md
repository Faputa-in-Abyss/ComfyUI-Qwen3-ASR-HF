# ComfyUI Qwen3-ASR HF

[中文教程](#中文教程) | [English Guide](#english-guide)

Windows ComfyUI 本地语音识别节点，直接加载 Qwen3-ASR 的 Hugging Face（HF）原生模型。支持单个音频、文件夹批量识别、术语提示、自定义保存位置，以及可选的词级时间戳和 SRT 字幕。

A Windows ComfyUI custom node for local speech recognition with the native Hugging Face version of Qwen3-ASR. It supports single files, folder batches, context/hotword prompts, custom output paths, and optional word-level timestamps and SRT subtitles.

模型权重不包含在本仓库中，需按下文单独下载。Model weights are not included in this repository.

---

# 中文教程

## 0. 先下载节点并了解怎么用

第一次安装时按这个顺序操作：下载节点、放入 `custom_nodes`、安装依赖、下载模型、重启 ComfyUI。

### 下载节点

打开本仓库的 GitHub 页面，点击 **Code → Download ZIP**。解压后把文件夹改名为 `ComfyUI-Qwen3-ASR-HF`，放入：

```text
ComfyUI/custom_nodes/ComfyUI-Qwen3-ASR-HF
```

也可以直接使用 Git：

```powershell
cd "D:\ComfyUI\ComfyUI\custom_nodes"
git clone https://github.com/Faputa-in-Abyss/ComfyUI-Qwen3-ASR-HF.git
```

### 安装节点依赖

使用实际启动 ComfyUI 的 Python 安装依赖。秋叶整合包通常使用：

```powershell
cd "D:\ComfyUI-aki-v3"
.\python\python.exe -m pip install -r ".\ComfyUI\custom_nodes\ComfyUI-Qwen3-ASR-HF\requirements.txt"
```

Windows Portable 通常使用：

```powershell
cd "D:\ComfyUI_windows_portable"
.\python_embeded\python.exe -m pip install -r ".\ComfyUI\custom_nodes\ComfyUI-Qwen3-ASR-HF\requirements.txt"
```

把 `D:\...` 改成自己的安装路径。接着按第 1、2、4 节下载并放好模型，然后完全重启 ComfyUI。

### 最快使用方法

1. 在 ComfyUI 画布上右键，进入 **音频 → Qwen3-ASR-HF**，添加 **Qwen3-ASR-HF 语音识别**。
   <img width="1051" height="724" alt="image" src="https://github.com/user-attachments/assets/41b31db2-1c31-4905-841d-116ed849fed7" />

2. 添加一个 ComfyUI 音频加载节点，把它的“音频”输出连接到本节点的“音频”输入。
<img width="1242" height="318" alt="image" src="https://github.com/user-attachments/assets/391603d6-307c-4c77-b022-90e95f6dec9b" /><img width="1085" height="888" alt="image" src="https://github.com/user-attachments/assets/4bb506ba-ebd0-4f69-8620-34b79563e94f" />


3. 在“ComfyUI 模型”中选择已下载的 `Qwen3-ASR-1.7B-hf` 或 `Qwen3-ASR-0.6B-hf`。<img width="401" height="212" alt="image" src="https://github.com/user-attachments/assets/bdbff0ba-173e-4ff0-974f-3b2cd7b847ba" />
**若没有识别到模型**，直接输入模型权重所在文件夹路径即可，以下图为例，复制这个路径：C:\software\AIIIIIIIIII\model\qwen\Qwen3-ASR-1.7B-hf 
这样你不必把模型权重存放在comfyUI指定文件夹，可直接使用本地原有支持原生transformer模型。
<img width="962" height="437" alt="image" src="https://github.com/user-attachments/assets/d8805b0f-970c-4966-92c5-7ec3f7bc8809" />

4. “识别语言”保持“自动检测”，其余选项第一次使用时保持默认。
5. 点击运行。识别结果会从“转写文本”输出；打开“保存 TXT”后还会写入文本文件。

如果节点没有出现，请确认文件夹没有多套一层目录，然后重启 ComfyUI 并在浏览器中按 `Ctrl+F5`。
最终节点可以参考以下方式连接，本节点不依赖输出节点，只需要音频输入即可，输出文本显示为可选项
<img width="1005" height="881" alt="image" src="https://github.com/user-attachments/assets/bc00cdc5-c0a1-42cb-8f6d-b4bf2c8fe6a7" />

## 1. 下载什么模型

识别模型只需二选一；需要时间戳时，再下载 Forced Aligner。

| 用途 | 模型 | 是否必需 | 建议 |
| --- | --- | --- | --- |
| 语音转文字 | [`Qwen/Qwen3-ASR-1.7B-hf`](https://huggingface.co/Qwen/Qwen3-ASR-1.7B-hf) | 是，推荐 | 识别效果优先 |
| 语音转文字 | [`Qwen/Qwen3-ASR-0.6B-hf`](https://huggingface.co/Qwen/Qwen3-ASR-0.6B-hf) | 二选一 | 模型更小、速度更快 |
| 词级时间戳和 SRT | [`Qwen/Qwen3-ForcedAligner-0.6B-hf`](https://huggingface.co/Qwen/Qwen3-ForcedAligner-0.6B-hf) | 否 | 只在需要时间戳时下载 |

请认准名称末尾的 **`-hf`**。本节点使用 Transformers 原生接口，不支持同名但不带 `-hf` 的版本。

推荐组合：

```text
Qwen3-ASR-1.7B-hf
Qwen3-ForcedAligner-0.6B-hf
```

只需要文字时，不必下载 Forced Aligner。

## 2. 模型放到哪里

在 ComfyUI 的 `models` 目录下新建 `qwen3_asr`，把每个完整模型分别放进自己的子文件夹：

```text
ComfyUI/
├─ custom_nodes/
│  └─ ComfyUI-Qwen3-ASR-HF/
└─ models/
   └─ qwen3_asr/
      ├─ Qwen3-ASR-1.7B-hf/
      │  ├─ config.json
      │  ├─ model*.safetensors
      │  ├─ processor_config.json
      │  └─ tokenizer.json
      └─ Qwen3-ForcedAligner-0.6B-hf/
         ├─ config.json
         ├─ model.safetensors
         ├─ processor_config.json
         └─ tokenizer.json
```

如果使用 0.6B 识别模型，就把第一项换成 `Qwen3-ASR-0.6B-hf`。

模型目录必须直接包含 `config.json`。不要多套一层同名文件夹，也不要只下载权重文件。节点会扫描 `ComfyUI/models/qwen3_asr`，并按 `config.json` 自动区分识别模型和时间戳模型。

## 3. 安装节点

### Git 安装

在 PowerShell 中进入 ComfyUI 的 `custom_nodes` 目录：

```powershell
cd "D:\ComfyUI\ComfyUI\custom_nodes"
git clone https://github.com/Faputa-in-Abyss/ComfyUI-Qwen3-ASR-HF.git
```

把示例路径改成自己的 ComfyUI 路径。

### ZIP 安装

点击 GitHub 页面上的 **Code → Download ZIP**。解压后把文件夹改名为 `ComfyUI-Qwen3-ASR-HF`，放入：

```text
ComfyUI/custom_nodes/ComfyUI-Qwen3-ASR-HF
```

### 安装 Python 依赖

必须使用实际启动 ComfyUI 的 Python，不能随便使用系统中的另一个 Python。

秋叶整合包示例：

```powershell
cd "D:\ComfyUI-aki-v3"
.\python\python.exe -m pip install -r ".\ComfyUI\custom_nodes\ComfyUI-Qwen3-ASR-HF\requirements.txt"
```

ComfyUI Windows Portable 示例：

```powershell
cd "D:\ComfyUI_windows_portable"
.\python_embeded\python.exe -m pip install -r ".\ComfyUI\custom_nodes\ComfyUI-Qwen3-ASR-HF\requirements.txt"
```

安装后重启 ComfyUI，并在浏览器中按 `Ctrl+F5` 强制刷新。

## 4. 下载模型

下面以秋叶整合包目录 `D:\ComfyUI-aki-v3` 为例。其他版本只需替换路径，最终目录结构必须与第 2 节一致。

### 方法 A：Hugging Face 官方下载

先安装下载工具：

```powershell
cd "D:\ComfyUI-aki-v3"
.\python\python.exe -m pip install -U huggingface_hub
```

下载推荐的 1.7B 识别模型：

```powershell
.\python\Scripts\hf.exe download Qwen/Qwen3-ASR-1.7B-hf --local-dir ".\ComfyUI\models\qwen3_asr\Qwen3-ASR-1.7B-hf"
```

需要时间戳时，再下载 Forced Aligner：

```powershell
.\python\Scripts\hf.exe download Qwen/Qwen3-ForcedAligner-0.6B-hf --local-dir ".\ComfyUI\models\qwen3_asr\Qwen3-ForcedAligner-0.6B-hf"
```

如果想用较小的 0.6B 识别模型：

```powershell
.\python\Scripts\hf.exe download Qwen/Qwen3-ASR-0.6B-hf --local-dir ".\ComfyUI\models\qwen3_asr\Qwen3-ASR-0.6B-hf"
```

Portable 用户把 `.\python\python.exe` 改为 `.\python_embeded\python.exe`，把 `.\python\Scripts\hf.exe` 改为 `.\python_embeded\Scripts\hf.exe`。

命令格式见 [Hugging Face 官方下载文档](https://huggingface.co/docs/huggingface_hub/guides/download#download-from-the-cli)。

### 方法 B：ModelScope 下载

如果 Hugging Face 连接较慢，可以使用 ModelScope。以下命令通过 `python -m` 调用，可避免 PowerShell 提示“无法将 modelscope 识别为 cmdlet”。

```powershell
cd "D:\ComfyUI-aki-v3"
.\python\python.exe -m pip install -U modelscope
```

下载推荐的 1.7B 识别模型：

```powershell
.\python\python.exe -m modelscope.cli.cli download --model Qwen/Qwen3-ASR-1.7B-hf --local_dir ".\ComfyUI\models\qwen3_asr\Qwen3-ASR-1.7B-hf"
```

下载可选的时间戳模型：

```powershell
.\python\python.exe -m modelscope.cli.cli download --model Qwen/Qwen3-ForcedAligner-0.6B-hf --local_dir ".\ComfyUI\models\qwen3_asr\Qwen3-ForcedAligner-0.6B-hf"
```

下载较小的 0.6B 识别模型：

```powershell
.\python\python.exe -m modelscope.cli.cli download --model Qwen/Qwen3-ASR-0.6B-hf --local_dir ".\ComfyUI\models\qwen3_asr\Qwen3-ASR-0.6B-hf"
```

下载完成后，检查目标文件夹中是否有 `config.json`、`processor_config.json`、`tokenizer.json` 和完整的 `.safetensors` 权重文件。

## 5. 在 ComfyUI 中使用

1. 右键画布，添加 **音频 → Qwen3-ASR-HF → Qwen3-ASR-HF 语音识别**。
2. 单文件：把音频加载节点连接到本节点的“音频”输入。
3. 批量文件：点击“选择音频文件夹”。如果同时连接了音频，连接的音频也会加入任务。
4. 在“ComfyUI 模型”中选择识别模型。模型不在标准目录时，选择“自定义路径”并填写完整模型路径。
5. “识别语言”通常选“自动检测”；已知语言时可以直接指定。
6. “术语提示”可填写专有名词、人名或品牌，例如 `Vocabulary: Qwen, ComfyUI, Richard.`。它会影响识别倾向，但不保证强制输出。
7. “最大生成长度”限制模型最多生成的文本 token 数。短音频保留默认值 `1024`；只有文字被截断时再提高。
8. 打开“保存 TXT”可保存文字。“输出文件名”和“保存目录”均可自定义；保存目录留空时使用 ComfyUI 默认 `output` 目录。同名文件会自动增加编号，不会覆盖旧文件。
9. 点击运行。节点输出转写文本、识别语言、TXT 路径、时间戳 JSON 和 SRT 路径。

批处理会自动分组：1 个按 1 个处理，2 个按 2 个处理，3 个及以上每批最多 3 个。文件夹中的音频按文件名排序。

## 6. 词级时间戳和 SRT

1. 确认已下载 `Qwen3-ForcedAligner-0.6B-hf`。
2. 打开“生成词级时间戳和 SRT”。
3. 在“时间戳模型”中选择该模型；不在标准目录时可使用自定义路径。
4. 运行后，节点会输出词级时间戳 JSON，并保存 `.timestamps.json` 和 `.srt` 文件。

Forced Aligner 支持中文、英语、粤语、法语、德语、意大利语、日语、韩语、葡萄牙语、俄语和西班牙语。单段音频最长 5 分钟，超过时节点会报错。

日语时间戳需要 `nagisa`，韩语时间戳需要 `soynlp`：

```powershell
.\python\python.exe -m pip install nagisa soynlp
```

Portable 用户改用 `.\python_embeded\python.exe`。

## 7. 常见问题

### 模型没有出现在下拉菜单

- 确认模型位于 `ComfyUI/models/qwen3_asr/模型文件夹`。
- 确认该文件夹直接包含 `config.json`，没有多套一层目录。
- 确认下载的是名称末尾带 `-hf` 的模型。
- 完全重启 ComfyUI，再按 `Ctrl+F5`。

### PowerShell 找不到 `hf` 或 `modelscope`

不要使用系统全局命令。照本文使用 ComfyUI Python 对应的 `.\python\Scripts\hf.exe`，或使用 `.\python\python.exe -m modelscope.cli.cli`。

### 提示缺少模块或依赖版本不对

重新确认安装依赖时使用的是启动 ComfyUI 的同一个 Python。秋叶整合包通常是 `python\python.exe`，Portable 通常是 `python_embeded\python.exe`。

### 出现 `sm_120`、`no kernel image` 或显卡架构警告

这是 ComfyUI Python 中的 PyTorch/CUDA 不支持显卡架构，不是节点或模型目录问题。请先安装支持该显卡的 PyTorch 版本。

---

# English Guide

## 0. Install the node first

For a first-time setup, follow this order: download the node, place it under `custom_nodes`, install its dependencies, download a model, and restart ComfyUI.

### Download the node

Open this repository on GitHub and click **Code → Download ZIP**. Extract the archive, rename the folder to `ComfyUI-Qwen3-ASR-HF`, and place it in:

```text
ComfyUI/custom_nodes/ComfyUI-Qwen3-ASR-HF
```

Alternatively, install it with Git:

```powershell
cd "D:\ComfyUI\ComfyUI\custom_nodes"
git clone https://github.com/Faputa-in-Abyss/ComfyUI-Qwen3-ASR-HF.git
```

### Install node dependencies

Use the Python executable that actually starts ComfyUI. Aki integrated packages commonly use:

```powershell
cd "D:\ComfyUI-aki-v3"
.\python\python.exe -m pip install -r ".\ComfyUI\custom_nodes\ComfyUI-Qwen3-ASR-HF\requirements.txt"
```

ComfyUI Windows Portable commonly uses:

```powershell
cd "D:\ComfyUI_windows_portable"
.\python_embeded\python.exe -m pip install -r ".\ComfyUI\custom_nodes\ComfyUI-Qwen3-ASR-HF\requirements.txt"
```

Replace `D:\...` with your installation path. Next, use sections 1, 2, and 4 to download and place the models, then restart ComfyUI completely.

### First transcription

1. Right-click the ComfyUI canvas, open **Audio → Qwen3-ASR-HF**, and add the **Qwen3-ASR-HF Speech Recognition** node. The current node labels are Chinese.
2. Add a ComfyUI audio loader and connect its audio output to this node's audio input.
3. Select `Qwen3-ASR-1.7B-hf` or `Qwen3-ASR-0.6B-hf` from the model list.
4. Keep automatic language detection and the other defaults for the first run.
5. Run the workflow. The transcript is returned from the text output. Enable TXT saving if you also want a text file.

If the node is missing, make sure the plugin is not inside an extra nested folder, restart ComfyUI, and press `Ctrl+F5` in the browser.

## 1. Choose the models

You need one ASR model. Download the Forced Aligner only if you need word-level timestamps or SRT subtitles.

| Purpose | Model | Required | Recommendation |
| --- | --- | --- | --- |
| Speech to text | [`Qwen/Qwen3-ASR-1.7B-hf`](https://huggingface.co/Qwen/Qwen3-ASR-1.7B-hf) | Yes, recommended | Better recognition quality |
| Speech to text | [`Qwen/Qwen3-ASR-0.6B-hf`](https://huggingface.co/Qwen/Qwen3-ASR-0.6B-hf) | Choose one ASR model | Smaller and faster |
| Word timestamps and SRT | [`Qwen/Qwen3-ForcedAligner-0.6B-hf`](https://huggingface.co/Qwen/Qwen3-ForcedAligner-0.6B-hf) | Optional | Download only for timestamps |

The model name must end in **`-hf`**. This node uses the native Transformers implementation and does not support the similarly named non-HF checkpoints.

Recommended combination:

```text
Qwen3-ASR-1.7B-hf
Qwen3-ForcedAligner-0.6B-hf
```

## 2. Model folder layout

Create `qwen3_asr` under ComfyUI's `models` directory. Put each complete model in its own folder:

```text
ComfyUI/
├─ custom_nodes/
│  └─ ComfyUI-Qwen3-ASR-HF/
└─ models/
   └─ qwen3_asr/
      ├─ Qwen3-ASR-1.7B-hf/
      │  ├─ config.json
      │  ├─ model*.safetensors
      │  ├─ processor_config.json
      │  └─ tokenizer.json
      └─ Qwen3-ForcedAligner-0.6B-hf/
         ├─ config.json
         ├─ model.safetensors
         ├─ processor_config.json
         └─ tokenizer.json
```

Replace the first folder with `Qwen3-ASR-0.6B-hf` if you choose the smaller ASR model.

`config.json` must be directly inside the model folder. Do not add an extra nested folder and do not download only the weight file. The node scans `ComfyUI/models/qwen3_asr` and uses each model's configuration to separate ASR and aligner models.

## 3. Install the node

### Install with Git

Open PowerShell in ComfyUI's `custom_nodes` directory:

```powershell
cd "D:\ComfyUI\ComfyUI\custom_nodes"
git clone https://github.com/Faputa-in-Abyss/ComfyUI-Qwen3-ASR-HF.git
```

Replace the example path with your own ComfyUI path.

### Install from ZIP

Click **Code → Download ZIP** on GitHub. Extract it, rename the folder to `ComfyUI-Qwen3-ASR-HF`, and place it in:

```text
ComfyUI/custom_nodes/ComfyUI-Qwen3-ASR-HF
```

### Install Python dependencies

Use the same Python executable that starts ComfyUI. Installing into another system Python will not work.

Aki integrated package example:

```powershell
cd "D:\ComfyUI-aki-v3"
.\python\python.exe -m pip install -r ".\ComfyUI\custom_nodes\ComfyUI-Qwen3-ASR-HF\requirements.txt"
```

ComfyUI Windows Portable example:

```powershell
cd "D:\ComfyUI_windows_portable"
.\python_embeded\python.exe -m pip install -r ".\ComfyUI\custom_nodes\ComfyUI-Qwen3-ASR-HF\requirements.txt"
```

Restart ComfyUI, then press `Ctrl+F5` in the browser.

## 4. Download the models

The commands below use `D:\ComfyUI-aki-v3` as an example. Change the path for your installation. The final folder layout must match section 2.

### Option A: Hugging Face

Install the official download tool:

```powershell
cd "D:\ComfyUI-aki-v3"
.\python\python.exe -m pip install -U huggingface_hub
```

Download the recommended 1.7B ASR model:

```powershell
.\python\Scripts\hf.exe download Qwen/Qwen3-ASR-1.7B-hf --local-dir ".\ComfyUI\models\qwen3_asr\Qwen3-ASR-1.7B-hf"
```

Download the optional Forced Aligner for timestamps:

```powershell
.\python\Scripts\hf.exe download Qwen/Qwen3-ForcedAligner-0.6B-hf --local-dir ".\ComfyUI\models\qwen3_asr\Qwen3-ForcedAligner-0.6B-hf"
```

To use the smaller 0.6B ASR model instead:

```powershell
.\python\Scripts\hf.exe download Qwen/Qwen3-ASR-0.6B-hf --local-dir ".\ComfyUI\models\qwen3_asr\Qwen3-ASR-0.6B-hf"
```

For ComfyUI Portable, replace `.\python\python.exe` with `.\python_embeded\python.exe`, and `.\python\Scripts\hf.exe` with `.\python_embeded\Scripts\hf.exe`.

See the official [`hf download` documentation](https://huggingface.co/docs/huggingface_hub/guides/download#download-from-the-cli) for the command syntax.

### Option B: ModelScope

ModelScope can be useful when Hugging Face is slow or unavailable. Calling it through `python -m` also avoids the PowerShell error “modelscope is not recognized”.

```powershell
cd "D:\ComfyUI-aki-v3"
.\python\python.exe -m pip install -U modelscope
```

Download the recommended 1.7B ASR model:

```powershell
.\python\python.exe -m modelscope.cli.cli download --model Qwen/Qwen3-ASR-1.7B-hf --local_dir ".\ComfyUI\models\qwen3_asr\Qwen3-ASR-1.7B-hf"
```

Download the optional Forced Aligner:

```powershell
.\python\python.exe -m modelscope.cli.cli download --model Qwen/Qwen3-ForcedAligner-0.6B-hf --local_dir ".\ComfyUI\models\qwen3_asr\Qwen3-ForcedAligner-0.6B-hf"
```

Download the smaller 0.6B ASR model:

```powershell
.\python\python.exe -m modelscope.cli.cli download --model Qwen/Qwen3-ASR-0.6B-hf --local_dir ".\ComfyUI\models\qwen3_asr\Qwen3-ASR-0.6B-hf"
```

After downloading, verify that the target folder contains `config.json`, `processor_config.json`, `tokenizer.json`, and the complete `.safetensors` weights.

## 5. Use the node

1. Right-click the canvas and add **Audio → Qwen3-ASR-HF → Qwen3-ASR-HF Speech Recognition**. The current UI labels are Chinese.
2. Single file: connect a ComfyUI audio loader to the node's audio input.
3. Folder batch: click the input-folder button. A connected audio input is also included if both sources are used.
4. Select the ASR model from the ComfyUI model list. Choose the custom-path option only when the model is stored elsewhere.
5. Leave language on automatic detection unless you know the spoken language.
6. Use the prompt for names, brands, technical terms, or other context, for example `Vocabulary: Qwen, ComfyUI, Richard.` It biases recognition but does not force exact output.
7. `max_new_tokens` limits the number of generated text tokens. Keep the default `1024` for ordinary short audio and increase it only if the transcription is cut off.
8. Enable TXT saving if needed. The output filename and directory are editable. An empty directory uses ComfyUI's default `output` folder. Existing files are not overwritten; a numeric suffix is added automatically.
9. Run the workflow. The node returns the transcript, detected language, TXT path, timestamp JSON, and SRT path.

Batch size is automatic: one file uses a batch of 1, two files use 2, and three or more files are processed in batches of up to 3. Folder files are sorted by filename.

## 6. Word-level timestamps and SRT

1. Download `Qwen3-ForcedAligner-0.6B-hf`.
2. Enable word-level timestamps and SRT in the node.
3. Select the aligner model, or use its absolute path if it is stored outside the standard model folder.
4. Run the workflow. The node returns timestamp JSON and saves `.timestamps.json` and `.srt` files.

The Forced Aligner supports Chinese, English, Cantonese, French, German, Italian, Japanese, Korean, Portuguese, Russian, and Spanish. Each audio item must be no longer than 5 minutes.

Japanese timestamps require `nagisa`; Korean timestamps require `soynlp`:

```powershell
.\python\python.exe -m pip install nagisa soynlp
```

Portable users should use `.\python_embeded\python.exe` instead.

## 7. Troubleshooting

### The model is missing from the dropdown

- Put it under `ComfyUI/models/qwen3_asr/model-folder`.
- Make sure `config.json` is directly inside that folder.
- Make sure the model name ends with `-hf`.
- Restart ComfyUI completely and press `Ctrl+F5`.

### PowerShell cannot find `hf` or `modelscope`

Use the executable or module belonging to ComfyUI's Python, as shown above. Do not rely on a command installed into another system Python.

### A Python module is missing

Install `requirements.txt` with the same Python executable that starts ComfyUI. Aki packages commonly use `python\python.exe`; Portable packages commonly use `python_embeded\python.exe`.

### `sm_120`, `no kernel image`, or unsupported GPU architecture

The PyTorch/CUDA build inside ComfyUI does not support the GPU architecture. This is not a node or model-path error. Install a compatible PyTorch build before using the node.

## License

The node code is released under the [MIT License](LICENSE). Model weights are not distributed here and remain subject to the licenses shown on their model pages.

## References

- [Qwen3-ASR-1.7B-hf](https://huggingface.co/Qwen/Qwen3-ASR-1.7B-hf)
- [Qwen3-ASR-0.6B-hf](https://huggingface.co/Qwen/Qwen3-ASR-0.6B-hf)
- [Qwen3-ForcedAligner-0.6B-hf](https://huggingface.co/Qwen/Qwen3-ForcedAligner-0.6B-hf)
- [Transformers Qwen3-ASR documentation](https://huggingface.co/docs/transformers/main/model_doc/qwen3_asr)
- [Hugging Face download documentation](https://huggingface.co/docs/huggingface_hub/guides/download)
