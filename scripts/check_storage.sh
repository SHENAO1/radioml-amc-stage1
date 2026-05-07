#!/usr/bin/env bash
set -e

echo "== Path =="
pwd

echo
echo "== Python =="
python --version || true

echo
echo "== GPU =="
python - <<'PY'
try:
    import torch
    print("torch:", torch.__version__)
    print("cuda_available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("device_count:", torch.cuda.device_count())
        for idx in range(torch.cuda.device_count()):
            print(f"cuda:{idx}", torch.cuda.get_device_name(idx))
except Exception as exc:
    print("torch check failed:", exc)
PY

echo
echo "== Disk =="
df -h .

echo
echo "== Data directories =="
test -d data/raw && echo "data/raw exists" || echo "data/raw missing"
test -d runs && echo "runs exists" || echo "runs missing"

echo
echo "== RadioML files =="
test -f data/raw/RML2016.10a_dict.pkl && echo "RML2016.10A pkl found" || echo "RML2016.10A pkl missing"
test -f data/raw/RML2016.10a_dict.pkl.bz2 && echo "RML2016.10A bz2 found" || echo "RML2016.10A bz2 missing"
find data/raw -maxdepth 2 -iname '*2018*' -print | grep -q . && find data/raw -maxdepth 2 -iname '*2018*' -print || echo "RadioML2018.01A file not found"

