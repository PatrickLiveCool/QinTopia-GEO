# QinTopia 静态官网项目约定

- 用简体中文沟通，保留用户改动；修改通过功能分支和 PR。目录整理另开 PR，保持公开 URL。
- `config/site-manifest.json` 是唯一网站发布范围；新增入口需同步 COS 发布权限策略。仓库中其他文件不等于可公开发布的内容。
- 合并不等于上线；Publish Release 是正常上线入口。生产发布、重试和回滚统一在 `Website production` 执行。不得恢复整目录 `coscli sync` 或直接覆盖生产的本地脚本。
- 网站发布与 `ops/cdn-cert-sync/` 的服务器证书服务相互独立。保持现有证书测试通过。
- 不把密钥、日志、工具目录、独立演示或本地附件加入发布包。不得替换已存在的 Release 制品，也不得自动删除旧 COS 对象。
- 验证发布行为用 `python3 -m unittest discover -s scripts/site/tests -v`；检查页面依赖用 `python3 scripts/site/package.py check`；更改 GitHub 工作流运行 actionlint。
- 上线成功必须具备 COS 读回、CDN 刷新、实际 TLS/响应内容和版本 marker 的证据；仅上传或返回 HTTP 200 不足以认定成功。
- 实际上线步骤和限制见 `docs/operations/release-runbook.md`，目录盘点见 `docs/operations/publication-inventory.md`。
