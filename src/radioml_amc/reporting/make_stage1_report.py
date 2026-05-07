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


def _fmt(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


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
            "- 图表输出：`plots/training_curve.png`、`plots/confusion_matrix.png`、`plots/normalized_confusion_matrix.png`、`plots/accuracy_vs_snr.png`、`plots/per_class_accuracy.png`。",
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


def make_stage1_5_report(run_dir: str | Path, output_path: str | Path | None = None) -> Path:
    run = Path(run_dir)
    metrics = _load_json(run / "metrics.json")
    config = _load_yaml(run / "config.yaml")
    mapping = _load_json(run / "label_mapping.json")
    dataset_summary = _load_json(run / "dataset_summary.json") or _load_json(run / "data_summary.json")
    split_summary = _load_json(run / "split_summary.json")

    data_cfg = config.get("data", {})
    train_cfg = config.get("train", {})
    test_metrics = metrics.get("test", metrics.get("evaluation", {}))
    data_mode = metrics.get("data_mode", data_cfg.get("mode", mapping.get("mode", "unknown")))
    model_name = metrics.get("model", metrics.get("model_name", train_cfg.get("model", "unknown")))
    source_path = dataset_summary.get("source_path") or dataset_summary.get("metadata", {}).get("source_path")
    is_real = data_mode == "real"

    warning = ""
    if not is_real:
        warning = (
            "> **当前尚未接入真实 RadioML2016.10A 数据，本报告来自 mock/synthetic smoke test，"
            "不能作为正式实验结论。**"
        )

    lines = [
        "# 阶段 1.5 实验报告：RadioML2016.10A 真实数据基线复现实验",
        warning,
        "## 1. 阶段目标",
        "本阶段目标是从第一阶段 mock 工程闭环推进到 RadioML2016.10A 真实数据 baseline 闭环，并固定 CNN1D 与 ResNet1D 的可复现实验协议。",
        "## 2. 数据集接入",
        f"- 数据模式：`{data_mode}`",
        f"- 数据集：`{data_cfg.get('dataset', metrics.get('dataset', 'N/A'))}`",
        f"- 实际数据文件路径：{source_path or 'N/A'}",
        f"- 样本数：{dataset_summary.get('num_samples', 'N/A')}",
        f"- 输入 shape：{dataset_summary.get('shape', 'N/A')}",
        f"- X dtype：{dataset_summary.get('dtype', 'N/A')}",
        f"- 是否存在 NaN：{dataset_summary.get('has_nan', 'N/A')}",
        f"- 是否存在 Inf：{dataset_summary.get('has_inf', 'N/A')}",
        f"- 调制类别：{', '.join(mapping.get('mod_names', dataset_summary.get('mod_names', []))) or 'N/A'}",
        f"- SNR 取值：{mapping.get('snr_values', dataset_summary.get('snr_values', []))}",
        "## 3. 数据划分",
        f"- split_strategy：`{data_cfg.get('split_strategy', split_summary.get('strategy', 'N/A'))}`",
        f"- seed：{config.get('project', {}).get('seed', split_summary.get('seed', 'N/A'))}",
        f"- test_size：{data_cfg.get('test_size', 'N/A')}",
        f"- val_size：{data_cfg.get('val_size', 'N/A')}",
    ]
    for name, payload in split_summary.get("splits", {}).items():
        lines.append(f"- {name}: {payload.get('num_samples', 'N/A')} samples, ratio={_fmt(payload.get('ratio'))}")

    lines.extend(
        [
            "## 4. Baseline 模型",
            f"- 当前 run 模型：`{model_name}`",
            "- Baseline A：CNN1D，直接输入 `[batch, 2, 128]` I/Q 序列。",
            "- Baseline B：ResNet1D，保留轻量一维残差结构，仍然只使用 I/Q 序列。",
            "## 5. 实验配置",
            f"- epochs：{train_cfg.get('epochs', 'N/A')}",
            f"- batch size：{train_cfg.get('batch_size', 'N/A')}",
            f"- learning rate：{train_cfg.get('learning_rate', 'N/A')}",
            f"- weight decay：{train_cfg.get('weight_decay', 'N/A')}",
            f"- device：{metrics.get('device', train_cfg.get('device', 'N/A'))}",
            f"- early stopping patience：{train_cfg.get('early_stopping_patience', 'N/A')}",
            "## 6. 实验结果",
            f"- overall accuracy：{_fmt(metrics.get('overall_accuracy', test_metrics.get('overall_accuracy')))}",
            f"- low SNR accuracy (SNR <= -6)：{_fmt(metrics.get('low_snr_accuracy', test_metrics.get('low_snr_accuracy')))}",
            f"- mid SNR accuracy (-4 <= SNR <= 6)：{_fmt(metrics.get('mid_snr_accuracy', test_metrics.get('mid_snr_accuracy')))}",
            f"- high SNR accuracy (SNR >= 8)：{_fmt(metrics.get('high_snr_accuracy', test_metrics.get('high_snr_accuracy')))}",
            f"- 模型参数量：{_fmt(metrics.get('num_parameters'))}",
            f"- 训练时间秒：{_fmt(metrics.get('train_time_seconds'))}",
            f"- 推理时间秒：{_fmt(metrics.get('inference_time_seconds'))}",
            f"- best epoch：{_fmt(metrics.get('best_epoch'))}",
            "- 图表：`plots/training_curve.png`、`plots/confusion_matrix.png`、`plots/normalized_confusion_matrix.png`、`plots/accuracy_vs_snr.png`、`plots/per_class_accuracy.png`。",
            "## 7. 结果分析",
            "真实数据接入后，应重点检查 SNR 升高后准确率是否明显提升，以及 QAM16/QAM64、AM-DSB/WBFM 等相近或易混调制类型的混淆关系。mock run 只能验证工程链路，不能给出正式分析。",
            "## 8. 对第二阶段的启发",
            "若真实 baseline 在低 SNR 或相近调制类别上表现不足，第二阶段应引入 STFT/CWT on-the-fly 时频分支、幅度/相位特征和 I/Q + 时频多视图融合，并通过消融实验验证收益。",
            "## 9. 当前阶段结论",
            (
                "本 run 已完成真实数据 baseline 输出。"
                if is_real
                else "当前尚未接入真实数据，本报告不能作为正式实验结论。"
            ),
            "",
        ]
    )

    output = Path(output_path) if output_path is not None else run / "stage1_5_report.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n\n".join(line for line in lines if line != ""), encoding="utf-8")
    return output
