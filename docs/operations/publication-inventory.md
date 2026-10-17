# 官网发布范围（2026-10-17）

用户确认拆分活动专题后，现有官网发布流程只管理主站。发布白名单共 38 个文件：2 个 HTML、4 个 SEO/AI 索引文件、32 张图片。资源发布到 `_site/<version>-<commit>/`，首页与移动页 URL 不变。

同日另行确认：OPC 招募站与生活社区主站在同一仓库维护，使用独立域名、内容和发布版本。OPC 源目录预留为 `sites/opc/`，目前不在上述 38 个文件或主站发布包内；新增基础设施不代表已具备独立发布能力。详见 [OPC 准备记录](opc-site-preparation.md)。迁出的活动项目继续独立管理。

## 已执行的目录整理

- `.cursor/` 已按用户要求移除。
- `从热情驱动到智能体驱动的乡村运营/` 已移入相邻 `Qintopia&Jianya Marketing/`，22 个文件移动前后逐一通过 SHA-256 核对。
- `秦岭AI白客松落地页/` 已移至 Codex 项目根目录，46 个文件移动前后通过 SHA-256 核对，今后作为独立 AI 活动项目。迁移后两个大羽页面的返回官网链接已改为 `https://www.qintopia.cn/`。
- `屏南乡建黑客松（路演）/` 由用户手动迁走；官网仓库不再跟踪。
- `coscli_output/`、日志和 `.DS_Store` 已清理。

Git 历史保留迁移前的文件。移动到其他项目的资料不再进入官网发布包；其他项目的发布与版本管理不在本流程内。

## 线上旧对象

只读盘点曾返回 72 个 COS 对象（含目录占位对象）。线上旧活动入口包括 `baikesong.html`、`m.html`、`qinling-hackathon.html`、`qinling-hackathon-mobile.html`、`tucao.html`、`wenti.html`、`wenti-mobile.html`、`chaochao.html`、`chaochao-mobile.html`、`吐槽白皮书.html`。

本流程不覆盖、不删除这些入口及其旧 images/assets/styles.css/script.js，也不操作 `mp_wechat/`。本地目录搬走不代表网站上的旧 URL 下线。活动 URL 后续迁移需在独立活动项目里核对内容和跳转规则。

robots.txt、sitemap.xml、llms*.txt 仍包含旧域名 `qintopia.livecool.com.cn`，需要另做 SEO 内容迁移。本次不修改业务文案。

## 逐文件白名单

| 源文件 | 逻辑路径 | 类型 |
|---|---|---|
| `index.html` | `index.html` | route |
| `mobile.html` | `mobile.html` | route |
| `robots.txt` | `robots.txt` | route |
| `sitemap.xml` | `sitemap.xml` | route |
| `llms.txt` | `llms.txt` | route |
| `llms-full.txt` | `llms-full.txt` | route |
| `images/activity_calligraphy.jpg` | `images/activity_calligraphy.jpg` | asset |
| `images/activity_cpr.jpg` | `images/activity_cpr.jpg` | asset |
| `images/activity_familyday.jpg` | `images/activity_familyday.jpg` | asset |
| `images/activity_familyday.png` | `images/activity_familyday.png` | asset |
| `images/activity_movie.jpg` | `images/activity_movie.jpg` | asset |
| `images/activity_wildherb.jpg` | `images/activity_wildherb.jpg` | asset |
| `images/consult_qrcode.png` | `images/consult_qrcode.png` | asset |
| `images/drone_flying_takeaway.png` | `images/drone_flying_takeaway.png` | asset |
| `images/eating_communal.png` | `images/eating_communal.png` | asset |
| `images/img1.jpg` | `images/img1.jpg` | asset |
| `images/img2.jpg` | `images/img2.jpg` | asset |
| `images/img3.jpg` | `images/img3.jpg` | asset |
| `images/img4.jpg` | `images/img4.jpg` | asset |
| `images/img5.jpg` | `images/img5.jpg` | asset |
| `images/img6.jpg` | `images/img6.jpg` | asset |
| `images/img7.jpg` | `images/img7.jpg` | asset |
| `images/laundry_selfservice.png` | `images/laundry_selfservice.png` | asset |
| `images/room_bunk.png` | `images/room_bunk.png` | asset |
| `images/room_minimal.png` | `images/room_minimal.png` | asset |
| `images/room_platform.png` | `images/room_platform.png` | asset |
| `images/space_3f.jpg` | `images/space_3f.jpg` | asset |
| `images/space_coworking.jpg` | `images/space_coworking.jpg` | asset |
| `images/space_gym.jpg` | `images/space_gym.jpg` | asset |
| `images/space_kitchen.jpg` | `images/space_kitchen.jpg` | asset |
| `images/space_kitchen2.jpg` | `images/space_kitchen2.jpg` | asset |
| `images/space_life_coffee.png` | `images/space_life_coffee.png` | asset |
| `images/space_life_pod.png` | `images/space_life_pod.png` | asset |
| `images/space_meeting.jpg` | `images/space_meeting.jpg` | asset |
| `images/space_meeting2.jpg` | `images/space_meeting2.jpg` | asset |
| `images/space_office_rooftop.png` | `images/space_office_rooftop.png` | asset |
| `images/space_room.jpg` | `images/space_room.jpg` | asset |
| `images/space_room2.jpg` | `images/space_room2.jpg` | asset |
