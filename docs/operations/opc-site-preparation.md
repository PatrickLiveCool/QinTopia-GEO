# OPC 招募站准备记录

确认日期：2026-10-17（Asia/Shanghai）。

## 已确认的边界

同一 Git 仓库管理两个独立站点：生活社区主站 `www.qintopia.cn` 与 OPC 招募站 `opc.qintopia.cn`。两站不设置互相导航；共享素材与基础事实，各自维护招募表达、申请入口与发布版本。现阶段不拆仓库、不迁移主站目录、不改变现有公开 URL。

OPC 源目录为 `sites/opc/`。本次只准备基础设施和开发边界，没有制作招募页面、上传网站对象或发布 Release。

## 腾讯云准备

复用现有 COS 桶 `qintopia-1305166808`（`ap-chengdu`），OPC 所有对象放在 `opc/` 前缀内。CDN 的 `Origin.BasePath=/opc` 把新域名的根路径映射到该前缀；没有把新域名指向桶里的主站首页。

这是源站路径与发布权限的划分，不是新建私有存储空间。桶内仍只应上传允许公开发布的文件；主站域名或 COS 源站也可能访问已公开的 OPC 对象。

| 对象 | 标识与设置 |
|---|---|
| OPC CDN | `opc.qintopia.cn`，资源 `cdn-prnjvumm`，中国大陆、网页小文件 |
| CDN CNAME | `opc.qintopia.cn.cdn.dnsv1.com` |
| 源站 | `qintopia-1305166808.cos-website.ap-chengdu.myqcloud.com`，HTTPS 回源，回源路径 `/opc` |
| DNS CNAME | DNSPod `qintopia.cn` 下的 `opc`，记录 ID `2432006225`，TTL 600；准备阶段保持 `DISABLE` |
| 已签发并绑定的免费证书 | `bdirFvdi`，`opc.qintopia.cn`，TrustAsia C1 DV Free，DNS_AUTO；有效期至 2027-01-15 12:59:59（北京时间） |
| DNS 证书验证 | `_dnsauth.opc`，记录 ID `2432005727`；由证书申请自动添加，保留供本次签发验证 |
| HTTPS 配置 | 已绑定上述证书，TLS 1.2/1.3、HTTP/2；HTTP 配置为 301 跳转 HTTPS；准备阶段 `HttpsBilling.Switch=off`，尚不开放 HTTPS 内容服务 |
| 抓取控制 | CDN 响应头 `X-Robots-Tag: noindex, nofollow`；首次正式发布再按收录决定调整 |
| 缓存 | 遵循源站 Cache-Control，默认缓存时间 0；404 缓存 10 秒 |

证书签发、CDN 最终状态与核查结果见下文。没有修改主站 DNS、主站 CDN 配置、原发布身份权限或服务器上的主站证书同步服务。

## 发布边界

当前 `config/site-manifest.json`、打包工具和 `Website production` 仍只发布主站。新目录不自动进入主站发布包，CNAME 准备也不等于 OPC 已上线。

OPC 首次发布前需要完成：

1. 在现有中央发布清单中显式表达两个站点的逐文件发布范围，同时扩展打包、校验和发布工具；不要另建未经约束的整目录同步入口。
2. 让 `Website production` 明确选择站点；主站现有 Release 行为保持兼容，OPC 拥有独立版本、不可变制品、成功凭据与回滚目标。禁止仅给现有脚本换一个域名便发布主站制品。
3. 为 OPC 准备独立发布身份和 GitHub 环境。COS 只允许已确认的 `opc/` 对象入口、`opc/_site/*` 和 OPC marker 的读取/写入；CDN 刷新写权限只允许 `opc.qintopia.cn`。不扩大主站身份权限，不授予删除、DNS、证书或计费权限。页面清单确认前不创建发布密钥。
4. 共享图片按 OPC 清单打入它自己的版本资源路径；页面引用站内路径，部署时统一加 COS 的 `opc/` 前缀，包括资源、入口和 marker。
5. OPC 证书续期与部署另行接入持久运行的运维流程。现有 `ops/cdn-cert-sync/` 只负责 `www.qintopia.cn`，不能声称已覆盖 OPC，也不在本次顺手扩权。
6. 页面验收后，通过 `Website production` 完成首次发布；配合启用已准备的 DNS CNAME 和 CDN HTTPS 内容服务（`HttpsBilling.Switch=on`，按腾讯云当时的 HTTPS 请求/流量规则计费；本次没有开启该开关或购买产品）。完成 COS 读回、CDN 刷新、正常 DNS 下的有效 TLS、真实页面/资源字节和独立版本 marker 校验，之后才能认定上线成功。DNS 启用与 CDN 配置变更使用受控运维身份，不给发布身份增加这些权限。

如需撤回本次准备，先查询对象当前状态与是否已有正式发布；只针对上述 OPC 新增资源操作。若已有 OPC 版本上线，按站点回滚和 URL 迁移方案处理，不能把准备阶段的撤回当成上线后的回滚。保留既有主站、旧 COS 对象及证书验证记录，不做批量清理。

## 核查结果

- DNSPod 读回：`opc` CNAME 的记录 ID、目标、TTL 与禁用状态均与上表一致。权威 DNS 已能返回 `_dnsauth.opc` 的验证 TXT。
- 腾讯云 SSL 返回证书 `Status=1`（已颁发），CDN 返回 `Https.Switch=on`、`SslStatus=deployed` 且绑定 ID 为 `bdirFvdi`。
- 在保持公网 CNAME 禁用的条件下，直连 CDN CNAME，使用 `opc.qintopia.cn` 作为 SNI 做正常证书校验：TLS 握手通过，证书 SAN 为 `opc.qintopia.cn`，实际到期时间为 2027-01-15 04:59:59 UTC（北京时间 12:59:59）。这只证明已抽查边缘节点的证书，不代表通过正常 DNS 访问或全网配置已完成。
- HTTPS 内容服务关闭时，直连抽查返回 HTTP 514，符合当前准备状态，不能当成网站上线成功。配置 HTTPS 前的 HTTP 回源抽查为 404，响应带 `X-Robots-Tag: noindex, nofollow`；COS 的 `opc/` 与 `opc/index.html` 均为 404，未误用主站首页。
- 主站抽查：正常 DNS 下 TLS 校验通过，首页返回 200，标题包含“秦托邦”，响应 93,628 字节；本次没有调用主站写接口。
- 本地 `python3 scripts/site/package.py check` 通过，仍为 38 个文件；发布测试 23 项、既有证书同步测试 5 项全部通过；`git diff --check` 通过。没有更改 GitHub 工作流。
- 2026-10-17 最终读回：CDN 整体状态为 `online`，证书子状态为 `deployed`；回源路径、绑定证书、缓存与抓取控制均符合上表。DNS CNAME 仍为 `DISABLE`，HTTPS 内容服务仍为 `off`。这表示基础设施配置准备完成，网站内容仍未上线。
