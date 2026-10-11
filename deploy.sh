#!/bin/bash
# deploy.sh - 将网站部署到腾讯云 COS
# 用法: ./deploy.sh

set -e

COS_ALIAS="qintopia-1305166808"
HACKATHON_DIR="秦岭AI白客松落地页"

echo "=== 正在上传主文件 ==="
/opt/homebrew/bin/coscli cp index.html "cos://$COS_ALIAS/index.html"
/opt/homebrew/bin/coscli cp mobile.html "cos://$COS_ALIAS/mobile.html"

echo "=== 正在上传白客松活动页 ==="
/opt/homebrew/bin/coscli cp "$HACKATHON_DIR/hackathon-schedule.html" "cos://$COS_ALIAS/hackathon-schedule.html"
/opt/homebrew/bin/coscli cp "$HACKATHON_DIR/hackathon-schedule-mobile.html" "cos://$COS_ALIAS/hackathon-schedule-mobile.html"
/opt/homebrew/bin/coscli cp "$HACKATHON_DIR/hackathon-pain-points-whitepaper.html" "cos://$COS_ALIAS/hackathon-pain-points-whitepaper.html"
/opt/homebrew/bin/coscli cp "$HACKATHON_DIR/hackathon-problem-map.html" "cos://$COS_ALIAS/hackathon-problem-map.html"
/opt/homebrew/bin/coscli cp "$HACKATHON_DIR/hackathon-problem-map-mobile.html" "cos://$COS_ALIAS/hackathon-problem-map-mobile.html"
/opt/homebrew/bin/coscli cp "$HACKATHON_DIR/Data&AI-dayu.html" "cos://$COS_ALIAS/Data&AI-dayu.html"
/opt/homebrew/bin/coscli cp "$HACKATHON_DIR/Data&AI-dayu-mobile.html" "cos://$COS_ALIAS/Data&AI-dayu-mobile.html"
/opt/homebrew/bin/coscli cp "$HACKATHON_DIR/hackathon-landing.html" "cos://$COS_ALIAS/hackathon-landing.html"
/opt/homebrew/bin/coscli cp "$HACKATHON_DIR/hackathon-landing-mobile.html" "cos://$COS_ALIAS/hackathon-landing-mobile.html"

echo "=== 正在上传 SEO/AI 索引文件 ==="
/opt/homebrew/bin/coscli cp robots.txt "cos://$COS_ALIAS/robots.txt"
/opt/homebrew/bin/coscli cp sitemap.xml "cos://$COS_ALIAS/sitemap.xml"
/opt/homebrew/bin/coscli cp llms.txt "cos://$COS_ALIAS/llms.txt"
/opt/homebrew/bin/coscli cp llms-full.txt "cos://$COS_ALIAS/llms-full.txt"

echo "=== 正在同步白客松专题资源 ==="
/opt/homebrew/bin/coscli sync "$HACKATHON_DIR/assets/" "cos://$COS_ALIAS/assets/" -r

echo "=== 正在同步 images/ ==="
/opt/homebrew/bin/coscli sync images/ "cos://$COS_ALIAS/images/" -r

echo "=== 部署完成 ==="
echo "网站地址: https://qintopia.livecool.com.cn/"
