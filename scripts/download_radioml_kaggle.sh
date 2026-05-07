#!/usr/bin/env bash
set -e

mkdir -p data/raw/radioml2016
mkdir -p data/raw/radioml2018

echo "请先配置 Kaggle API token：~/.kaggle/kaggle.json"
echo "不要把 kaggle.json 上传到 GitHub"

# 示例：下载 RadioML2016.10A
# kaggle datasets download -d nolasthitnotomorrow/radioml2016-deepsigcom -p data/raw/radioml2016 --unzip

# 示例：下载 RadioML2018.01A
# kaggle datasets download -d pinxau1000/radioml2018 -p data/raw/radioml2018

echo "示例脚本已结束。请按需取消注释 kaggle datasets download 命令后手动执行。"

