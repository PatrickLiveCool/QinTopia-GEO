#!/usr/bin/env bash
# Production changes now go through a published GitHub Release.
set -euo pipefail
cd -- "$(dirname -- "$0")"
python3 scripts/site/package.py check
cat <<'EOF'
本地发布清单检查通过。线上发布入口已改为 GitHub Release：
1. 功能 PR 合并 → Release Please 创建版本 PR。
2. 版本 PR 合并 → 生成 Draft Release。
3. 确认版本后 Publish Release → GitHub 执行 COS 上传、CDN 刷新及验证。
重试/回滚使用 Website production workflow，详见 docs/operations/release-runbook.md。
EOF
