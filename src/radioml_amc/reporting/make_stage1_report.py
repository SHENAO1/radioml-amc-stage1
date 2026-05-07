from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def make_stage1_report(run_dir: str | Path, output_path: str | Path | None = None) -> Path:
    run = Path(run_dir)
    metrics = _load_json(run / "metrics.json")
    config = _load_yaml(run / "config.yaml")
    mapping = _load_json(run / "label_mapping.json")

    data_mode = config.get("data", {}).get("mode", mapping.get("mode", "unknown"))
    train_cfg = config.get("train", {})
    project_cfg = config.get("project", {})
    test_metrics = metrics.get("test", metrics.get("evaluation", {}))
    overall = test_metrics.get("overall_accuracy")
    per_class = test_metrics.get("per_class_accuracy", {})
    per_snr = test_metrics.get("per_snr_accuracy", {})
    model_name = metrics.get("model_name", train_cfg.get("model", "unknown"))

    mock_warning = ""
    if data_mode == "mock":
        mock_warning = (
            "\n> **重要说明：当前结果来自 mock/synthetic 数据，仅用于工程 smoke test，"
            "不能作为正式实验结论或论文结果。**\n"
        )

    lines = [
        "# 第一阶段实验报告：RadioML2016.10A 基线实验闭环",
        mock_warning,
        "## 1. 任务背景",
        "无线电自动调制识别 AMC 是一个监督分类任务，目标是根据接收端 I/Q 序列预测调制类别。本阶段重点是建立可复现实验闭环。",
        "## 2. 数据集说明",
        f"- 数据模式：`{data_mode}`",
        f"- 调制类别：{', '.join(mapping.get('mod_names', [])) or 'N/A'}",
        f"- SNR 取值：{mapping.get('snr_values', [])}",
        "- 输入形式：`[N, 2, 128]`",
        "## 3. 数据预处理",
        "读取数据后统一转换为 float32 I/Q 张量，调制类别编码为整数标签，并记录每个样本的 SNR。数据划分策略由配置文件控制。",
        "## 4. 方法设计",
        f"本次运行模型为 `{model_name}`。CNN1D 与 ResNet1D 均为轻量 baseline，直接处理 I/Q 序列，不包含复杂注意力或多视图融合。",
        "## 5. 实验设置",
        f"- seed：{project_cfg.get('seed', 'N/A')}",
        f"- batch size：{train_cfg.get('batch_size', 'N/A')}",
        f"- epochs：{train_cfg.get('epochs', 'N/A')}",
        f"- learning rate：{train_cfg.get('learning_rate', 'N/A')}",
        f"- device：{metrics.get('device', train_cfg.get('device', 'N/A'))}",
        "## 6. 实验结果",
        f"- overall accuracy：{overall if overall is not None else 'N/A'}",
        "- per-class accuracy：",
    ]
    for name, acc in per_class.items():
        lines.append(f"  - {name}: {acc}")
    lines.append("- per-SNR accuracy：")
    for snr, acc in per_snr.items():
        lines.append(f"  - {snr} dB: {acc}")
    lines.extend(
        [
            "- 图表输出：`plots/training_curve.png`、`plots/confusion_matrix.png`、`plots/accuracy_vs_snr.png`。",
            "## 7. 结果分析",
            "正式数据上通常应重点观察高 SNR 分类是否更容易、低 SNR 下混淆是否更明显，以及相近调制类别之间的混淆关系。mock 数据不用于结论分析。",
            "## 8. 本阶段不足",
            "当前还没有正式引入时频分支、多视图融合、低 SNR 鲁棒训练，也没有进行论文级系统调参。",
            "## 9. 下一阶段计划",
            "第二阶段将加入 STFT/CWT 时频分支、多视图融合和消融实验，并完善正式实验记录与论文图表。",
            "",
        ]
    )

    output = Path(output_path) if output_path is not None else run / "stage1_report.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n\n".join(line for line in lines if line != ""), encoding="utf-8")
    return output

