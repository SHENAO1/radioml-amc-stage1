# radioml-amc-stage1

## 1. 项目简介

本项目是机器学习结课作业第一阶段工程：基于 RadioML2016.10A 的无线电自动调制识别 AMC 最小可运行闭环。当前目标是先把本地工程、mock smoke test、训练评估、可视化、报告和服务器衔接流程跑通，后续再扩展到论文级实验。

研究主题：

《基于时频特征与深度神经网络融合的无线电调制识别方法研究——以 RadioML2016.10A 与 RadioML2018.01A 数据集为例》

## 2. 第一阶段目标

- 支持 RadioML2016.10A 数据读取接口；
- 支持无真实数据集时的 mock/synthetic smoke test；
- 提供数据统计、示例可视化、CNN1D 和 ResNet1D baseline；
- 保存训练日志、指标、混淆矩阵、SNR 准确率曲线和阶段报告；
- 保证代码可以后续上传 GitHub，并在服务器上下载数据后继续训练。

## 3. 当前阶段范围限制

本阶段不实现 Transformer、多视图融合、复杂注意力机制或论文创新模型；不完整处理 RadioML2018.01A；不自动下载大数据集；不把数据集或训练输出加入 Git；不把所有样本离线转成时频图图片。

## 4. 环境配置

建议在项目根目录执行：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 5. 本地无数据集 smoke test 流程

当前没有真实数据集也可以完整跑通工程闭环：

```bash
python scripts/check_dataset.py --config configs/stage1_local_mock.yaml
python scripts/visualize_examples.py --config configs/stage1_local_mock.yaml
python scripts/train_cnn1d.py --config configs/stage1_local_mock.yaml
python scripts/train_resnet1d.py --config configs/stage1_local_mock.yaml
python scripts/make_report.py --run_dir runs/某次运行目录
pytest -q
```

mock 数据只用于检查工程是否可运行，不能作为正式实验结果或论文结论。

## 6. RadioML2016.10A 数据集放置说明

请手动下载 RadioML2016.10A，并放到以下任一位置：

```text
data/raw/RML2016.10a_dict.pkl
data/raw/RML2016.10a_dict.pkl.bz2
```

真实数据检查和训练：

```bash
python scripts/check_dataset.py --config configs/stage1_rml2016a.yaml
python scripts/visualize_examples.py --config configs/stage1_rml2016a.yaml
python scripts/train_cnn1d.py --config configs/stage1_rml2016a.yaml
python scripts/train_resnet1d.py --config configs/stage1_rml2016a.yaml
python scripts/evaluate_model.py --config configs/stage1_rml2016a.yaml --checkpoint runs/某次运行目录/best_model.pt
python scripts/make_report.py --run_dir runs/某次运行目录
```

如果数据文件不存在，脚本会给出清晰提示，不会打印难以阅读的 traceback。

## 7. 输出目录说明

每次训练会创建：

```text
runs/YYYYMMDD_HHMMSS_modelname/
├── config.yaml
├── logs.txt
├── metrics.json
├── metrics.csv
├── label_mapping.json
├── best_model.pt
├── plots/
│   ├── training_curve.png
│   ├── confusion_matrix.png
│   ├── accuracy_vs_snr.png
│   ├── iq_examples.png
│   ├── constellation_examples.png
│   ├── amplitude_phase_examples.png
│   └── stft_examples.png
└── stage1_report.md
```

`runs/` 不上传 GitHub。

## 8. CNN1D 和 ResNet1D 方法说明

CNN1D 是轻量一维卷积 baseline，输入 `[batch, 2, 128]`，经过 Conv1d、BatchNorm1d、ReLU、MaxPool1d、AdaptiveAvgPool1d 和 Linear 分类器输出类别 logits。

ResNet1D 使用 2 到 3 个轻量残差块，仍然直接处理 I/Q 序列。它用于验证残差结构在该任务上的基础表现，不包含复杂注意力或多分支融合。

## 9. 可视化说明

`scripts/visualize_examples.py` 会随机抽样并保存：

- I/Q 时域波形；
- 星座图；
- 幅度和相位曲线；
- STFT 时频图。

STFT 在第一阶段只用于示例可视化，不会把全量样本离线转换成图片数据集。

## 10. 服务器训练与数据集下载说明

本地推荐流程：

1. 创建虚拟环境；
2. `pip install -r requirements.txt`；
3. 用 mock 配置跑 smoke test；
4. 确认脚本和 pytest 无误；
5. git push 到 GitHub。

服务器推荐流程：

1. `git clone` 仓库；
2. 创建虚拟环境；
3. `pip install -r requirements.txt`；
4. 配置 Kaggle API token 到 `~/.kaggle/kaggle.json`；
5. 参考 `scripts/download_radioml_kaggle.sh` 下载数据集；
6. 执行 `bash scripts/check_storage.sh`；
7. 执行 `python scripts/check_dataset.py --config configs/stage1_rml2016a.yaml`；
8. 执行训练脚本；
9. 查看 `runs/` 输出。

`scripts/download_radioml_kaggle.sh` 是示例脚本，不会自动执行。不要把 `kaggle.json` 上传到 GitHub。

## 11. GitHub 上传注意事项

GitHub 只上传代码、配置、说明和测试文件。以下内容不上传：

- `data/raw/` 中的数据集；
- `data/processed/` 中的大文件；
- `runs/` 中的训练输出；
- Kaggle token；
- `.pt`、`.pth`、`.pkl`、`.bz2` 等大文件或模型文件。

## 12. 常见问题

**没有数据集能不能运行？**  
可以，使用 `configs/stage1_local_mock.yaml`。

**mock 结果能不能写进论文？**  
不能。mock 结果只说明工程链路可运行。

**为什么默认真实配置开启 subset_mode？**  
为了本地先用少量类别、少量 SNR 和每组有限样本做调试。服务器正式训练时可以关闭 `subset_mode`。

**RadioML2018.01A 是否已完整支持？**  
没有。本阶段只预留说明和服务器检查项，完整处理留到第二阶段。

## 13. 第二阶段计划

第二阶段建议加入 STFT/CWT 时频分支、多视图融合、低 SNR 鲁棒训练、消融实验和正式论文表格。届时需要固定实验协议，区分 mock、本地 subset 和服务器全量结果。

