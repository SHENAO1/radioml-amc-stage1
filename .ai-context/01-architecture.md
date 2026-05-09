# 01 · 架构与技术栈

<!-- 静态文档。重大重构时更新。 -->

## 技术栈
- Python 3.13 local
- Python 3.11 server
- PyTorch
- NumPy
- SciPy
- scikit-learn
- matplotlib
- PyYAML
- LaTeX

## 模块划分

| 模块 | 职责 | 关键入口文件 |
| --- | --- | --- |
| `src/radioml_amc/` | 数据读取、split、Dataset、模型、训练、指标、profiling 和报告输出核心包 | `data/`, `models/`, `training/`, `reporting/` |
| `scripts/` | 阶段化命令行入口：数据检查、训练、评估、对比和分析 | `check_dataset.py`, `compare_runs.py`, `paper/*.py` |
| `configs/` | mock、subset、full、paper protocol 和 Stage 6B diagnostic 配置 | `stage*_*.yaml`, `paper/` |
| `docs/` | 项目过程文档、阶段日志、论文计划、manuscript 草稿和证据边界 | `PROGRESS_LOG.md`, `paper/`, `session_state.md` |
| `results/` | paper-stage 结构化结果、aggregate、diagnostic 输出和协议证据 | `paper_stage2/`, `paper_stage6/` |
| `runs/` | 本地开发训练产物和早期阶段 run 输出；默认不进 Git | `README.md`, timestamped run dirs |
| `paper_package/` | 从服务器同步的 manuscript/evidence package、predictions archive、full-results archive 和 statistical-test archive | `server_sync_20260508/`, `server_full_results_sync_20260508/`, `predictions_archive_20260508/`, `statistical_tests_20260508/` |
| `.ai-context/` | 跨助手共享上下文、当前状态、决策和会话日志 | `05-current-state.md`, `06-session-log.md` |

## 数据流

```text
RadioML data / archived predictions
  -> configs + scripts
  -> src/radioml_amc data/model/training/reporting code
  -> runs/ or results/
  -> aggregate tables + statistical tests + figures
  -> docs/paper/manuscript and paper_package/
```

## 本地与服务器分工
- 本地 Windows 环境：Python 3.13.7、PyTorch 2.11.0+cpu、CUDA unavailable。用于文档、manifest、统计 artifact 检查、轻量 CPU inspection 和 manuscript drafting。
- 服务器环境：`/hy-tmp/radioml-amc-stage1`，Python 3.11.12、PyTorch 2.9.1+cu128、NVIDIA GeForce RTX 4070、CUDA available。只在明确 protocol 授权后用于 GPU 训练或 diagnostic。
- Stage 5A 完整 `best_model.pt` 权重仍在服务器；本地预测归档和统计 artifacts 已同步，但本地 Stage 5A result tree 不含完整权重矩阵。

## 构建与运行

```powershell
# 本地只做检查/文档/轻量 inspection；不要在本地启动 GPU 训练
python -m compileall -q src scripts
git diff --check
```

```bash
# 服务器训练必须由具体 protocol 授权，并使用新的 output root
python scripts/paper/run_stage5a_full_training.py --config <approved-config>
```

## 目录结构

```text
.
├── .ai-context/              # 跨助手共享上下文
├── configs/                  # 阶段与论文实验配置
├── data/                     # 数据占位与 split artifact；大数据不提交
├── docs/                     # 过程文档、paper docs、manuscript
├── paper_package/            # 本地同步/归档包
├── results/                  # paper-stage evidence roots
├── runs/                     # 开发 run 输出，不提交
├── scripts/                  # 命令行脚本
├── src/radioml_amc/          # 核心包
└── tests/                    # 回归和协议基础测试
```
