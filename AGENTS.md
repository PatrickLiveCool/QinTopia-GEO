# QinTopia 静态官网项目约定

- 用简体中文沟通，保留用户改动；修改通过功能分支和 PR。目录整理另开 PR，保持公开 URL。
- 同一仓库管理生活社区主站与 OPC 招募站。主站公开 URL 保持原样；OPC 源文件放在 `sites/opc/`，目标域名为 `opc.qintopia.cn`，两站不设置互相导航。共享素材与已确认的基础事实，招募文案、申请入口和发布版本分别管理。
- `config/site-manifest.json` 是唯一网站发布范围；新增入口需同步 COS 发布权限策略。仓库中其他文件不等于可公开发布的内容。
- 当前发布清单和 `Website production` 只支持主站；OPC 目录暂不发布。OPC 首次发布前须显式扩展中央清单、打包和发布流程，实现站点选择、独立制品、权限、版本 marker 与回滚，禁止把 OPC 页面加入主站发布包代替独立发布。准备情况见 `docs/operations/opc-site-preparation.md`。
- 合并不等于上线；Publish Release 是正常上线入口。生产发布、重试和回滚统一在 `Website production` 执行。不得恢复整目录 `coscli sync` 或直接覆盖生产的本地脚本。
- 网站发布与 `ops/cdn-cert-sync/`（主站）、`ops/opc-cert-sync/`（OPC）的服务器证书服务相互独立。证书服务修改须运行各自测试，保持既有测试通过。
- 不把密钥、日志、工具目录、独立演示或本地附件加入发布包。不得替换已存在的 Release 制品，也不得自动删除旧 COS 对象。
- 验证发布行为用 `python3 -m unittest discover -s scripts/site/tests -v`；检查页面依赖用 `python3 scripts/site/package.py check`；更改 GitHub 工作流运行 actionlint。
- 上线成功必须具备 COS 读回、CDN 刷新、实际 TLS/响应内容和版本 marker 的证据；仅上传或返回 HTTP 200 不足以认定成功。
- 实际上线步骤和限制见 `docs/operations/release-runbook.md`，目录盘点见 `docs/operations/publication-inventory.md`。
