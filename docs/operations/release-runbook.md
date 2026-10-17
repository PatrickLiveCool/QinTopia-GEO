# 官网开发、发布和回滚

本流程发布 `www.qintopia.cn` 的静态内容。`qintopia.cn` 的 Nginx 跳转、Certbot 和服务器上的 CDN 证书同步服务继续独立运行。本机只用于开发，不承担定时上线或证书续期。

## 日常工作

1. 在 `codex/...` 或其他功能分支修改，通过 PR 进入 `main`。PR 标题使用 `feat: ...`、`fix: ...` 等 Conventional Commits 格式，合并时使用 squash，并保留该格式。
2. `Site checks` 检查发布清单、页面/资源引用、打包与部署失败路径、已有证书同步测试，构建并校验预览包，在运行摘要保存提交与哈希。检查不带云端写凭据。
3. 合并触发 Release Please，自动提出版本 PR（`version.txt`、版本清单、CHANGELOG）。版本 PR 合并后生成 **Draft Release**，不会部署网站。
4. 确认版本后点击 **Publish Release**。这是正常发布的上线确认；`production` 没有额外人工审批或等待定时器。
5. `Website production` 只接受已发布、非预发布的 `vMAJOR.MINOR.PATCH`，检查 tag 对应的提交在 `main` 历史中，并与 `version.txt` 一致。

同一时间只准备一个待发布版本：已有 Draft Release 时暂停新版本 PR；本次刚生成草稿时也不会继续递增版本。发布草稿后，下次 main 提交或手动运行 Prepare release 才准备下一版。

Release Please 使用 GitHub 自带短期 `GITHUB_TOKEN`。由于机器人创建的 PR 不会自动触发普通 PR 事件，工作流显式 dispatch `ci.yml` 到版本 PR 分支。仓库已启用 Actions 创建 PR 权限；脚本不自动批准或合并 PR。

本地检查：

```bash
python3 scripts/site/package.py check
python3 -m unittest discover -s scripts/site/tests -v
python3 -m unittest discover -s ops/cdn-cert-sync -p 'test_*.py' -v
./deploy.sh
```

最后一条只检查并说明发布入口，不直接上传。本地页面目录与线上路径有映射，建议预览实际发布包：

```bash
python3 scripts/site/package.py build --version v0.0.0 --revision "$(git rev-parse HEAD)" --output dist/preview
python3 -m zipfile -e dist/preview/site.zip dist/preview/www
python3 -m http.server --directory dist/preview/www 8000
```

输出目录必须为空；已有制品不会覆盖。预览版本不能作为生产版本发布。

## 发布包与上线顺序

唯一入口是 `config/site-manifest.json` 的逐文件白名单。官网只发布首页、移动页、SEO 索引和主站图片；已迁走的活动/演示不再打包。新增文件必须明确加入清单，不能把整个工作目录同步到 COS。

每个 Release 包含 `site.zip`、`manifest.json`、`SHA256SUMS`。manifest 记录版本、完整提交 SHA、文件来源、对象路径、大小、类型与 SHA-256。同一个 tag 重试时下载原有包并重新验证，禁止 `--clobber`。如果只上传成功了部分 Release 附件，流程报错并停止，需查明中断原因；不自动重建替换原包。

1. 从 `main` 读取发布工具；从已校验 tag 提取静态源文件，源文件不作为发布代码执行。
2. CSS、JS、图片等写入 `_site/<version>-<commit>/...`，打包时改写引用。所有资源先上传并逐个读回核对；已有版本路径内容不同则报错。
3. 写公开 HTML/SEO 路径，首页最后写。每个对象上传后读回比较。
4. 刷新网站根路径及本次公开入口，等待 CDN 返回刷新完成。
5. 验证 apex→www 永久跳转、两端有效 TLS 且至少还有 14 天、所有包内页面和资源的实际响应字节与打包结果一致。使用无随机查询参数的真实 URL，避免只验证绕过缓存的结果。
6. 写入并刷新 `/.well-known/qintopia-release.json`，再次验证后生成 `verified-deployment.json`，然后把首次成功凭据保存为 Release 附件 `deployed.json`。

发布、重试、回滚和连接测试共用 `qintopia-website-production` concurrency group，运行中的任务不会被新任务取消。GitHub 对排队任务的调度不作为保证按顺序逐个发布的队列；一次确认一个版本，完成后再确认下一版本。

## 连接测试与首次发布

工作流合并到 `main` 后，在 Actions → Website production → Run workflow，选择 `main`、`operation=probe`。

这会从 GitHub hosted runner 向 `_site/connectivity-probe.txt` 写入含时间标识的少量测试文本并读回，只刷新该测试 URL，再验证实际响应、TLS 和跳转；不会更新任何网站页面。CI 的匿名 HEAD 只证明公网源站可达，**不能代替凭据上传测试**。成都地域不等于 COS 只能内网访问；以实际 runner 的测试结果为准。

第一次上线只涉及官网主站，专题内容不在本流程中。当前线上还没有这套流程产生的成功版本，因此首次上线不能靠本流程回到改造前；需要保留旧 COS 对象，必要时另做经过审核的线上基线备份。此阶段没有清理 COS 对象。

## 重试与回滚

- 重试：选择 `operation=deploy`，填写已发布版本 tag，复用同一包。
- 回滚：选择 `operation=rollback`，填写曾经成功上线的 tag。必须存在与该包版本、提交、manifest 哈希绑定的 `deployed.json`；仅有 tag 或上传过包不够。
- 回滚上传旧版本的公开入口，复用其资源，再执行相同刷新和验证流程。
- 自动化不删除对象。回滚后，新版本新增、旧版本未包含的 URL 仍可能存在；若要求撤下页面，必须单独设计 URL 删除/跳转方案。正常发布移除已管理入口会被阻止。
- COS 多对象更新不是原子事务，中途故障可能造成不同页面暂处不同版本。版本资源路径避免一个页面混用新旧样式；失败不会自动宣称成功，需检查日志后重试或明确回滚。
- 如果页面已成功验证、但 marker/成功凭据写入中断，Actions 仍报失败。先看线上 marker、任务日志和验证摘要，再重试同一版本；不要误认为完全没有发生写入。

本阶段不自动清理历史版本。旧资源路径供缓存页面和回滚使用，后续清理必须加入相同 concurrency group，保留当前/可回滚版本，并单独配置删除身份。

## 凭据和权限

GitHub `production` 环境仅允许 `main` 分支及 `v*` tag；工作流额外校验发布身份。四个环境 Secrets：

- `COS_SECRET_ID` / `COS_SECRET_KEY`：专用 COS 发布身份；仅允许清单中的公开入口、`_site/*`、版本 marker 的 `GetObject` 和 `PutObject`。
- `CDN_SECRET_ID` / `CDN_SECRET_KEY`：专用 CDN 发布身份；只允许查询域名/刷新任务及刷新 `www.qintopia.cn`。

策略见 `config/cos-release-policy.json`、`config/cdn-release-policy.json`；无密钥的实际身份记录见 `config/provisioned-identities.json`。新增公开入口还需同步更新 COS CAM 策略。身份不复用网站证书同步、Green PMS 或管理员密钥，不具备删除对象、改 DNS、改证书、改账单或启停 CDN 的权限。查询 API 的资源级限制按腾讯云接口能力使用 `*`，刷新写操作限制官网域名。

依赖版本和包哈希固定在 `scripts/site/requirements.lock`；Actions 固定提交 SHA。升级时重新验证，不能仅改版本号而忽略哈希文件。

## GitHub 套餐限制

2026-10-17 实际请求 `main` 分支保护接口返回 403，提示私有仓库需要 GitHub Pro。本次没有升级套餐，也没有把仓库设为公开。`.github/main-protection.json` 保存了所需配置：必须经过 PR、`Site checks` 成功、禁止强推/删除、解决 review 对话；升级后可通过 API应用。

在分支保护真正启用前，PR 是团队流程约定，管理员/有写权限者仍能绕过；不要把它描述为已经强制执行。当前 `production` 环境的分支/tag 限制已通过 API建立，但它不能替代源码分支保护。

## 与 Green PMS 的关系

采用 PR→版本 PR→Draft Release→Publish Release、固定版本制品、哈希读回、验证后记录成功、显式回滚、最小权限和串行生产操作。静态站没有引入 Docker、数据库迁移或 SSH 执行应用容器；部署直接由 GitHub runner 调用 COS/CDN。证书服务器部署不混入网站工作流。

## Actions 存储配额

2026-10-17 实测 Actions artifact 上传因账户存储额度已满而失败。CI 仍完整构建、验证发布包，哈希保存在运行摘要，不为每个 PR 额外保存约 35 MB 预览文件。生产版本包及成功凭据使用 GitHub Release 附件；部署日志和校验摘要保留在 Actions。没有删除其他项目的 artifact 或增加费用。
