# 秦托邦 AI 探索站

目标域名：`ai.qintopia.cn`。

这里是独立于 `qintopia.cn` 主站与 `opc.qintopia.cn` 招募站的 AI OPC 社区合作介绍页。页面面向政府、文旅公司及乡村运营伙伴，叙事重点是“先宜居，后宜业”，以及空间、OPC 人才、AI 基础设施、项目交付四层能力。AI 基础设施文案明确包含新加坡算力中转平台与西安算力中转平台，承担模型与算力服务接入、路由和调度。

页面素材复制自 `Qintopia&Jianya Marketing/releases/qintopia-opc-outreach-v01/deck/assets/` 的已确认终稿资源，未直接依赖另一个项目的线上资源版本。文案沿用已确认的秦托邦 AI/OPC 对外口径，避免写入未经核实的客户名称、当前人数或交付承诺。

页面已通过一次独立的腾讯云 CLI 发布验证上线：版本 `v0.1.0-ai.1`，提交 `3848475ea54564ccdeb9e14428330f7a8ab079ad`，COS 对象使用 `ai/` 前缀，CDN 回源路径为 `/ai`，并写入独立版本 marker。DNS、TLS、CDN、COS 读回、缓存刷新、真实 HTML/资源字节和浏览器桌面/移动验收均已完成。

当前 `config/site-manifest.json`、主站 `Website production` 和主站发布身份仍不包含 AI 站点；后续若要纳入自动发布，需要另建 AI 站点清单、制品、权限、marker、回滚和生产工作流，不能套用主站或已有 OPC 站点的发布配置。页面底部的“先看秦托邦实践”是一个外部了解入口，不代表两个站点共用发布包或运行配置。
