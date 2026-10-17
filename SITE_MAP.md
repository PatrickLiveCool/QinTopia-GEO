# 网站地图

官网根目录：

- `index.html`：桌面首页。
- `mobile.html`：移动首页。
- `images/`：主站图片。
- `robots.txt`、`sitemap.xml`、`llms.txt`、`llms-full.txt`：SEO/AI 索引。

完整逐文件发布范围以 `config/site-manifest.json` 为准，当前 38 个文件。打包时图片改为版本资源路径；页面的公开 URL 不变。

AI 活动专题与两个独立演示已移出官网项目。线上旧活动对象保留，详细迁移记录见 [发布范围盘点](docs/operations/publication-inventory.md)。

发布流程：功能 PR → main → 版本 PR → Draft Release → Publish Release → COS/CDN 上传、刷新与验证。`deploy.sh` 仅本地检查；详见 [发布与回滚手册](docs/operations/release-runbook.md)。
