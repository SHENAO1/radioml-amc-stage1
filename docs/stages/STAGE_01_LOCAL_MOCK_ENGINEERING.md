# Stage 1：本地 mock 工程闭环

## 1. 阶段定位

Stage 1 是本项目的工程落地起点，目标是在没有真实 RadioML2016.10A 数据的情况下，先跑通数据、模型、训练、评估、可视化、报告和测试的最小闭环。

## 2. 阶段目标

- 提供 mock/synthetic RadioML 风格数据，用于本地 smoke test。
- 预留 RadioML2016.10A loader 接口。
- 实现 CNN1D 和 ResNet1D baseline。
- 保存训练日志、指标、checkpoint、图表和阶段报告。
- 提供 pytest smoke tests。
- 提供服务器下载说明和 Git 忽略策略。

## 3. 本阶段不做什么

- 不实现 STFT/CWT 训练分支。
- 不实现 I/Q 与时频多视图融合。
- 不实现 Transformer、注意力机制或复杂论文创新模型。
- 不完整处理 RadioML2018.01A。
- 不自动下载大数据集。
- 不把所有样本离线转换为 STFT 图片。

## 4. 输入条件

- Python 环境与 `requirements.txt`。
- `configs/stage1_local_mock.yaml`。
- 无需真实 RadioML2016.10A 数据。

## 5. 已完成工作

| 任务 | 状态 | 说明 | 相关文件 |
|---|---|---|---|
| mock 数据生成 | Done | 生成 `[N, 2, 128]` I/Q 序列、label 和 SNR | `src/radioml_amc/data/mock_dataset.py` |
| 数据加载统一接口 | Done | mock/real 模式共用 DataBundle | `src/radioml_amc/data/dataset.py` |
| RadioML2016.10A loader 初版 | Done | 支持本地 `.pkl/.bz2` 路径检查 | `src/radioml_amc/data/rml2016a_loader.py` |
| CNN1D baseline | Done | 轻量一维卷积 baseline | `src/radioml_amc/models/cnn1d.py` |
| ResNet1D baseline | Done | 轻量一维残差 baseline | `src/radioml_amc/models/resnet1d.py` |
| 训练与评估 | Done | 保存 metrics、logs、checkpoint 和 plots | `src/radioml_amc/training/trainer.py` |
| 可视化 | Done | I/Q、星座图、幅度/相位、STFT 示例图 | `src/radioml_amc/visualization/` |
| 报告生成 | Done | 生成 `stage1_report.md` | `src/radioml_amc/reporting/make_stage1_report.py` |
| pytest smoke tests | Done | mock 和模型 forward 测试通过，真实数据缺失时 skip | `tests/` |

## 6. 修改/新增文件

- `configs/stage1_local_mock.yaml`：本地 mock smoke test 配置。
- `configs/stage1_rml2016a.yaml`：真实 RadioML2016.10A 初始配置。
- `scripts/check_dataset.py`：数据统计检查入口。
- `scripts/visualize_examples.py`：示例可视化入口。
- `scripts/train_cnn1d.py`：CNN1D 训练入口。
- `scripts/train_resnet1d.py`：ResNet1D 训练入口。
- `scripts/evaluate_model.py`：checkpoint 评估入口。
- `scripts/make_report.py`：报告生成入口。
- `reports/stage1_report_template.md`：第一阶段报告模板。
- `tests/`：smoke tests。

## 7. 执行命令

```bash
python scripts/check_dataset.py --config configs/stage1_local_mock.yaml
python scripts/visualize_examples.py --config configs/stage1_local_mock.yaml
python scripts/train_cnn1d.py --config configs/stage1_local_mock.yaml
python scripts/train_resnet1d.py --config configs/stage1_local_mock.yaml
python scripts/evaluate_model.py --config configs/stage1_local_mock.yaml --checkpoint runs/20260507_120214_cnn1d/best_model.pt
python scripts/make_report.py --run_dir runs/20260507_120214_cnn1d
pytest -q
```

## 8. 输出结果

- `runs/20260507_120214_cnn1d/`
  - mock CNN1D smoke test。
  - `metrics.json` overall accuracy: 0.2427。
  - `stage1_report.md` 已生成。
- `runs/20260507_120227_resnet1d/`
  - mock ResNet1D smoke test。
  - `metrics.json` overall accuracy: 0.2621。
  - `stage1_report.md` 已生成。
- `runs/20260507_120242_eval_cnn1d/`
  - mock CNN1D checkpoint evaluation。
  - `metrics.json` overall accuracy: 0.2427。
- `runs/20260507_120315_visualize_examples/`
  - mock 示例可视化。
  - 图表包括 `iq_examples.png`、`constellation_examples.png`、`amplitude_phase_examples.png`、`stft_examples.png`。

## 9. 实验结论

Stage 1 只能得出工程结论：本地 mock 数据闭环可运行，训练、评估、可视化和报告链路可用。

当前结果仅为 mock smoke test，不能作为正式实验结论或论文结果。真实 RadioML2016.10A 尚未下载。

## 10. 当前问题与风险

- mock 数据分布不代表真实 RadioML2016.10A。
- 真实数据 loader 需要在真实文件上进一步验证。
- 第一阶段尚未固定正式 baseline 对比协议。
- 缺少阶段过程文档体系，后续需要补齐。

## 11. 验收标准核对

| 验收项 | 状态 | 证据 |
|---|---|---|
| mock check_dataset 可运行 | Done | `python scripts/check_dataset.py --config configs/stage1_local_mock.yaml` |
| mock 可视化可运行 | Done | `runs/20260507_120315_visualize_examples/plots/` |
| CNN1D mock 训练可运行 | Done | `runs/20260507_120214_cnn1d/` |
| ResNet1D mock 训练可运行 | Done | `runs/20260507_120227_resnet1d/` |
| checkpoint 评估可运行 | Done | `runs/20260507_120242_eval_cnn1d/` |
| pytest smoke tests 通过 | Done | `.s... [100%]` |
| mock 结果不写成正式结论 | Done | README 和报告均有 warning |
| 真实 RadioML2016.10A 接入 | Need Data | 当前未检测到真实数据 |

## 12. 下一阶段计划

进入 Stage 1.5：强化 RadioML2016.10A 真实数据接入，新增 subset/full 配置，固定 CNN1D/ResNet1D baseline 协议，生成对比表和阶段 1.5 过程文档。

## 13. 下一阶段提示词

```text
请进入 Stage 1.5：基于现有 radioml-amc-stage1 工程，不实现 STFT/CWT 训练分支或多视图融合。先审计 Stage 1 代码与 mock 流程，确认 pytest、mock check_dataset 和 mock train_cnn1d 仍可运行；然后补充 docs 过程文档体系，强化 RadioML2016.10A loader 的自动路径检测、Python 3 pickle latin1 兼容、.pkl/.pkl.bz2 支持和清晰缺失提示；新增 real subset/full 配置；固定 CNN1D 与 ResNet1D baseline 协议；新增 baseline 批量运行脚本、run 对比脚本和 stage1_5_report.md；更新 README、.gitignore 和 pytest。无真实数据时必须明确 pending，不能把 mock 结果作为正式实验结论。
```
