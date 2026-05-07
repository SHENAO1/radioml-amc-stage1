#!/usr/bin/env bash
set -e

mkdir -p data/raw/radioml2016
mkdir -p data/raw/radioml2018

cat <<'EOF'
RadioML dataset download helper
================================

This script is intentionally documentation-first. It creates the expected
directories and prints commands, but it does not force a download.

Before downloading:
  1. Install and login to Kaggle CLI:
       pip install kaggle
  2. Put your Kaggle API token at:
       Linux/macOS: ~/.kaggle/kaggle.json
       Windows PowerShell: C:\Users\<YOUR_USER>\.kaggle\kaggle.json
  3. Never commit kaggle.json to Git.
  4. On Linux servers, restrict token permissions:
       chmod 600 ~/.kaggle/kaggle.json

Expected project directories have been created:
  - data/raw/radioml2016
  - data/raw/radioml2018

Stage 1.6 only needs RadioML2016.10A. RadioML2018.01A is listed below for
future reference and should not be required for Stage 1.6.

RadioML2016.10A Kaggle example:
  kaggle datasets download -d nolasthitnotomorrow/radioml2016-deepsigcom -p data/raw/radioml2016 --unzip

RadioML2018.01A Kaggle example for later stages, not Stage 1.6:
  kaggle datasets download -d pinxau1000/radioml2018 -p data/raw/radioml2018

After downloading RadioML2016.10A, inspect the file name:
  ls -lh data/raw/radioml2016

Move or link the downloaded file to one of the project-recognized paths:
  data/raw/RML2016.10a_dict.pkl
  data/raw/RML2016.10a_dict.pkl.bz2
  data/raw/radioml2016/RML2016.10a_dict.pkl
  data/raw/radioml2016/RML2016.10a_dict.pkl.bz2

Linux symlink example:
  ln -s "$(pwd)/data/raw/radioml2016/RML2016.10a_dict.pkl" data/raw/RML2016.10a_dict.pkl

Windows PowerShell placement example:
  New-Item -ItemType Directory -Force data/raw/radioml2016
  Move-Item .\RML2016.10a_dict.pkl .\data\raw\radioml2016\RML2016.10a_dict.pkl

Then verify the subset config:
  python scripts/check_dataset.py --config configs/stage1_rml2016a_real_subset.yaml

For server full baseline after verification:
  python scripts/check_dataset.py --config configs/stage1_rml2016a_real_full.yaml
  python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_full.yaml
EOF

echo "No download was started automatically. Run the printed kaggle command manually when ready."
