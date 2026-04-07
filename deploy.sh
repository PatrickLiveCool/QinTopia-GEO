#!/bin/bash
# deploy.sh - 将网站部署到腾讯云 COS
# 用法: ./deploy.sh

set -e

COS_ALIAS="qintopia-1305166808"
LOCAL_FILE="index.html"

echo "=== 正在上传 index.html 到 COS ==="
/opt/homebrew/bin/coscli cp "$LOCAL_FILE" "cos://$COS_ALIAS/$LOCAL_FILE"
echo "=== 正在同步 images/ 到 COS ==="
/opt/homebrew/bin/coscli sync images/ "cos://$COS_ALIAS/images/" -r
echo "=== 部署完成 ==="
echo "网站地址: http://qintopia.livecool.com.cn/index.html"