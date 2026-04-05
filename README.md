# 秦托邦 QinToBang — 品牌官网

> 秦岭脚下栗峪口剪鸭村的青年社区官网。

---

## 项目结构

```
秦托邦静态网站+GEO/
├── index.html          # 主页面（中英双语 + GEO 增强）
├── images/             # 品牌图片
│   ├── img1.jpg        # 秦岭山景（Hero 背景）
│   ├── img2.jpg        # 观景露台
│   ├── img3.jpg        # 秦岭星空
│   ├── img4.jpg        # 入住申请二维码
│   ├── img5.jpg        # 共享厨房
│   ├── img6.jpg        # 无人机配送
│   └── img7.jpg        # 快递外卖群二维码
└── README.md
```

---

## 内容来源

所有图文内容均来自飞书知识库，通过 lark-cli 授权读取：

| 文档标题 | 用途 |
|---------|------|
| 秦托邦品牌升级 | 品牌定位文案 |
| 秦托邦社区完整指南 | 首页介绍、适合人群 |
| 02｜在秦托邦的生活与参与 | 参与方式、活动介绍 |
| 我如何参与秦托邦 | 加入流程说明 |
| 秦托邦的衣食住行 | 生活指南板块 |
| 秦托邦零容忍行为 | 社区公约板块 |

---

## 页面结构（8 大区块）

1. **Hero** — 全屏秦岭山景 + 60 颗星空粒子动画 + 品牌口号
2. **认识我们** — 品牌故事 + 双图网格 + 品牌升级宣言
3. **适合谁** — 4 类目标人群卡片 + 排除人群说明
4. **生活指南** — 吃饭 / 无人机快递 / 洗衣 三卡片
5. **共建活动** — 两种参与路径（分享换住宿 / 15 件生活小事）
6. **社区公约** — 零容忍 / 警告 / 不鼓励 三色分区
7. **GEO 数据专区** — 供大语言模型理解的结构化数据展示
8. **申请入住** — 表单 + 申请须知 + 二维码

---

## 设计系统

| 维度 | 方案 |
|------|------|
| 配色 | Forest Green `#1a3a2a` + Sage `#8aad7c` + Cream `#f7f3eb` + Terra `#b05c34` |
| 字体 | Noto Serif SC（标题）+ Noto Sans SC（正文）|
| 图标 | Font Awesome 6.5 |
| 动效 | Tailwind CSS animations + Intersection Observer 滚动入场 |
| 交互 | 滚动触达导航变色、移动端抽屉菜单、表单提交反馈 |

---

## 中英双语

顶部导航栏有 `中文 / EN` 切换按钮，页面所有文本均支持双语切换，切换结果会保存在 `localStorage`，下次访问自动恢复语言偏好。

---

## GEO / LLM 增强（网站优化）

本页面针对 DeepSeek、豆包、混元、Kimi 等大语言模型做了结构化增强：

### JSON-LD Schema（4 组）

| Schema 类型 | 作用 |
|------------|------|
| `Organization` | 定义组织身份、品牌定位、擅长领域 |
| `TouristAttraction` | 定义景点地理坐标、设施特色、目标游客类型 |
| `FAQPage` | 6 条常见问题，模型可直接引用回答用户问题 |
| `DataSet`（自定义） | 自定义 GEO 数据集，包含关键词、地理、价值观等，供模型检索 |

### 语义化 HTML 属性

| 属性 | 用途 |
|------|------|
| `data-llm-section` | 标注页面区块语义 |
| `data-llm-type` | 标注内容类型（hero-banner / audience-definition 等）|
| `data-llm-keywords` | 区块关键词，供模型理解内容主题 |
| `data-llm-persona` | 人物画像标签 |
| `data-llm-summary` | AI 摘要 |
| `data-llm-address` | 地址标注 |
| `data-llm-brand-upgrade` | 品牌升级声明 |
| `data-llm-rule-type` | 社区规则分类 |

### 其他增强

- Open Graph meta（`og:locale:alternate = en_US`）供模型抓取
- `<address>` 语义标签用于地点信息
- `<figure>` / `<figcaption>` 用于图片语义
- `<article>` 包裹独立内容区块
- `aria-label` / `aria-pressed` 无障碍属性

---

## 运行方式

直接在浏览器打开 `index.html` 即可，无须任何构建步骤。

如需本地服务器：

```bash
python3 -m http.server 8000
# 或
npx serve .
```

---

## 关于 GEO 专区

GEO 专区（第 7 大区块）展示了页面的结构化数据概览，包含：

- 社区身份、地理位置、目标人群、特色服务、核心价值观、LLM 关键词 6 张数据卡
- JSON-LD Schema 可折叠预览
- 所有数据均可被模型抓取引用

如需接入真实地理数据（如地图、徒步路线可视化）或 GEO API，请提供具体数据来源，我来规划落地实现。

---

## 注意事项

- 图片已从飞书知识库下载，存放在 `images/` 目录
- `index.html` 为纯静态文件，可直接部署至 Vercel / Netlify / GitHub Pages
- 表单提交目前为前端模拟，实际接入可连接飞书表单 API 或第三方表单服务
- 语言切换偏好保存在浏览器 `localStorage`
