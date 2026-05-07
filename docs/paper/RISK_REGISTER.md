# Risk Register

## SCI-Track Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Current fusion model has lower overall accuracy than ResNet1D | Weakens broad fusion claims | Reframe the paper around low-SNR complementary value and adaptive fusion |
| Low-SNR improvement is small | May not be publishable | Run multi-seed experiments and seek larger gains through gate, loss, sampler, and augmentation |
| Single-seed results may be unstable | False conclusions | Use at least three seeds for main comparisons and report mean plus/minus std |
| RadioML2016.10A alone may be insufficient | Limited external validity | Add RadioML2018.01A validation after protocol stabilization |
| CWT full computation is expensive | Blocks three-view experiments | Keep CWT optional, optimize feature extraction before any full CWT claim |
| Over-stacking models may lack innovation | Method may look incremental | Keep method lightweight and connect design directly to observed SNR trade-off |
| No real OTA data | Limits deployment claim | State dataset limitation clearly and avoid real-world overclaims |
| Paper conclusion may remain course-project extension | Publication value uncertain | Let literature review decide novelty and tighten the gap before implementation |
| Server cost may grow | Full multi-seed experiments may be expensive | Use subset screening and promote only necessary experiments to full runs |
| Git data leakage risk | Severe security and repository risk | Keep `data/raw`, `runs`, checkpoints, `.venv`, tokens, SSH keys, and passwords out of Git |

## Claim-Control Risks

| Risk | Mitigation |
|---|---|
| Accidentally claiming fusion is comprehensively better | Use the frozen snapshot and claim boundaries in every paper draft |
| Reporting subset as full | Require dataset/split labels in every table |
| Reporting CWT as completed | Keep CWT marked as optional skipped until a full run is valid |
| Ignoring complexity | Add params, FLOPs, latency, training time, and memory to the protocol |
