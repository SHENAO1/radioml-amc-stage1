# 07 · 已知问题与 Workaround

<!-- 准静态文档。遇到坑就记，解决了在条目下标注“已解决”而非删除。 -->

---

### 内层仓库已有大量 dirty files
- **症状**: `git status --short` 显示已修改 README/config/docs/source 文件，以及大量 untracked configs、docs、paper_package、results、scripts、tests。
- **定位**: 这是本次上下文初始化前已经存在的工作区状态；外层仓库也仍把 `radioml-amc-stage1/` 视为未跟踪目录。
- **Workaround**: 不回滚、不清理、不自动 stage。提交前必须人工审查新增范围，尤其避免把大 artifact 或无关实验输出带入提交。
- **状态**: 待解决

### 本地环境无 CUDA，不能代表服务器训练环境
- **症状**: 本地 PyTorch 为 CPU 版本，`CUDA available: false`。
- **定位**: 本地适合文档、manifest、统计 artifact review 和轻量 inspection；服务器 RTX 4070 才是训练环境。
- **Workaround**: 本地不跑 GPU 训练；任何新训练都必须在服务器上由明确 protocol 授权。
- **状态**: 待解决

### Stage 5A 完整权重未同步到本地
- **症状**: 27 个服务器 Stage 5A `best_model.pt` 存在于 `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/*/seed_*/best_model.pt`，但本地 Stage 5A result tree 和 paper package 中没有完整权重矩阵。
- **定位**: 本地已有 prediction archive 和 statistical tests，尚未做 weight archive。
- **Workaround**: 如需本地 inference、resume 或归档完整性，先同步到单独 archive/package path 并 hash-check；不要覆盖本地 `results/` 或 Stage 5A/5B roots。
- **状态**: 待解决

### Stage 6B diagnostic 不能混入 Stage 5A/5B 主表
- **症状**: Stage 6B 已有 smoke/diagnostic artifact，但不是 main-table evidence。
- **定位**: 证据标签不同；`SMOKE TEST` / `DIAGNOSTIC` 不能替代 `PROJECT_SUPPORTED` full evidence。
- **Workaround**: 主表、统计检验和 manuscript performance claims 只使用 Stage 5A/5B `PROJECT_SUPPORTED` evidence。
- **状态**: 待解决

### CWT full on-the-fly 计算成本过高
- **症状**: `fusion_iq_stft_cwt` 在 RTX 4070 12GB 上出现 CPU-bound CWT、NNPACK warning flood、GPU 利用率接近 0。
- **定位**: 当前 CWT on-the-fly 实现不适合直接 full 主实验。
- **Workaround**: 在优化 CWT 成本或更换计算协议前，不反复强跑 full CWT；如需测试，标为 diagnostic 并包含 same-subset controls。
- **状态**: 待解决

### `results/`、`paper_package/`、`runs/` 容易误提交
- **症状**: 当前工作区有大量 artifact 目录；其中可能包含大文件、预测、同步包或本地开发 run。
- **定位**: `.gitignore` 忽略了 `runs/*` 和大模型/数据类型，但 `results/` 与 `paper_package/` 当前仍显示为 untracked，需要特别审查。
- **Workaround**: 提交前先用 `git status --short` 和必要的 `git check-ignore` 检查；本次初始化不修改 `.gitignore`。
- **状态**: 待解决
