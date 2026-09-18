import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

const widgetLabels = {
  input_dir: "批量音频文件夹",
  model_name: "ComfyUI 模型",
  model_path: "模型路径",
  generate_timestamps: "生成词级时间戳和 SRT",
  aligner_model_name: "时间戳模型",
  aligner_model_path: "时间戳模型路径",
  language: "识别语言",
  prompt: "术语提示",
  max_new_tokens: "最大生成长度",
  device: "运行设备",
  precision: "计算精度",
  save_txt: "保存 TXT",
  output_filename: "输出文件名",
  output_dir: "保存目录",
};

const inputLabels = { audio: "音频" };
const outputLabels = {
  text: "转写文本",
  language: "识别语言",
  txt_path: "TXT 文件路径",
  timestamps_json: "词级时间戳 JSON",
  srt_path: "SRT 文件路径",
};

async function folderAction(endpoint, path) {
  const response = await api.fetchApi(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  });

  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

app.registerExtension({
  name: "Qwen3.ASR.HF.ChineseUI",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "Qwen3ASRHFNode") return;

    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const result = onNodeCreated?.apply(this, arguments);
      this.title = "Qwen3-ASR-HF 语音识别";

      for (const widget of this.widgets ?? []) {
        if (widgetLabels[widget.name]) widget.label = widgetLabels[widget.name];
      }
      for (const input of this.inputs ?? []) {
        if (inputLabels[input.name]) input.label = inputLabels[input.name];
      }
      for (const output of this.outputs ?? []) {
        if (outputLabels[output.name]) output.label = outputLabels[output.name];
      }

      const outputDir = this.widgets?.find((widget) => widget.name === "output_dir");
      const inputDir = this.widgets?.find((widget) => widget.name === "input_dir");

      if (inputDir) {
        const inputButton = this.addWidget("button", "📁 选择音频文件夹", null, async () => {
          try {
            const data = await folderAction(
              "/qwen3_asr_hf/select_input_dir",
              inputDir.value ?? ""
            );
            if (data.path) inputDir.value = data.path;
          } catch (error) {
            alert(`选择音频文件夹失败：${error.message}`);
          }
        });
        inputButton.options.serialize = false;
      }

      if (!outputDir) return result;

      const chooseButton = this.addWidget("button", "📁 选择文件夹", null, async () => {
        try {
          const data = await folderAction(
            "/qwen3_asr_hf/select_output_dir",
            outputDir.value ?? ""
          );
          if (data.path) outputDir.value = data.path;
        } catch (error) {
          alert(`选择文件夹失败：${error.message}`);
        }
      });
      chooseButton.options.serialize = false;

      const openButton = this.addWidget("button", "📂 打开文件夹", null, async () => {
        try {
          await folderAction(
            "/qwen3_asr_hf/open_output_dir",
            outputDir.value ?? ""
          );
        } catch (error) {
          alert(`打开文件夹失败：${error.message}`);
        }
      });
      openButton.options.serialize = false;

      this.setSize(this.computeSize(this.size));
      return result;
    };
  },
});
