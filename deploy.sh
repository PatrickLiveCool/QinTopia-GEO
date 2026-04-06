#!/bin/bash
# deploy.sh - 将网站部署到腾讯云 COS
# 用法: ./deploy.sh

set -e

COS_ALIAS="qintopia-1305166808"
LOCAL_FILE="index.html"

echo "=== 正在上传 index.html 到 COS ==="
/opt/homebrew/bin/coscli cp "$LOCAL_FILE" "cos://$COS_ALIAS/$LOCAL_FILE"
echo "=== 上传成功 ==="
echo "网站地址: http://qintopia.livecool.com.cn/index.html"