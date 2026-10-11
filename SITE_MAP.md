# 网站地图

## 说明

这个目录当前分为两部分：

- 主站页面：放在根目录
- 秦岭 AI 白客松专题：集中放在 `秦岭AI白客松落地页/`

---

## 目录结构

```text
秦托邦静态网站+GEO/
├── index.html
├── mobile.html
├── deploy.sh
├── robots.txt
├── sitemap.xml
├── llms.txt
├── llms-full.txt
├── images/
├── 秦岭AI白客松落地页/
│   ├── hackathon-landing.html
│   ├── hackathon-landing-mobile.html
│   ├── hackathon-schedule.html
│   ├── hackathon-schedule-mobile.html
│   ├── hackathon-pain-points-whitepaper.html
│   ├── hackathon-problem-map.html
│   ├── hackathon-problem-map-mobile.html
│   ├── Data&AI-dayu.html
│   ├── Data&AI-dayu-mobile.html
│   ├── styles.css
│   ├── script.js
│   └── assets/
└── README.md
```

---

## 页面分组

### 1. 主站

- `index.html`：秦托邦主站桌面页
- `mobile.html`：秦托邦主站移动页

主站图片资源放在：

- `images/`

### 2. 白客松专题

专题目录：

- `秦岭AI白客松落地页/`

其中页面包括：

- `hackathon-landing.html`：白客松落地页桌面版
- `hackathon-landing-mobile.html`：白客松落地页移动版
- `hackathon-schedule.html`：白客松活动安排页桌面版
- `hackathon-schedule-mobile.html`：白客松活动安排页移动版
- `hackathon-pain-points-whitepaper.html`：槽点白皮书
- `hackathon-problem-map.html`：问题地图桌面版
- `hackathon-problem-map-mobile.html`：问题地图移动版
- `Data&AI-dayu.html`：大羽分享页桌面版
- `Data&AI-dayu-mobile.html`：大羽分享页移动版

专题共享资源：

- `styles.css`
- `script.js`
- `assets/`

---

## 页面关系

### 主站

- `index.html` <-> `mobile.html`

### 白客松专题内部

- `hackathon-landing.html` <-> `hackathon-landing-mobile.html`
- `hackathon-schedule.html` <-> `hackathon-schedule-mobile.html`
- `hackathon-problem-map.html` <-> `hackathon-problem-map-mobile.html`
- `Data&AI-dayu.html` <-> `Data&AI-dayu-mobile.html`

### 白客松专题跳转链路

- `hackathon-schedule.html` / `hackathon-schedule-mobile.html`
  - 专题活动安排主入口
- `hackathon-problem-map.html` / `hackathon-problem-map-mobile.html`
  - 从活动安排进入问题地图
- `hackathon-pain-points-whitepaper.html`
  - 从问题地图进入槽点白皮书
- `Data&AI-dayu.html` / `Data&AI-dayu-mobile.html`
  - 从活动主线进入大羽分享页
- `hackathon-landing.html` / `hackathon-landing-mobile.html`
  - 独立的白客松落地页素材页

---

## 资源归属

### 根目录资源

- `images/`：主站图片资源
- `robots.txt`：搜索引擎抓取规则
- `sitemap.xml`：搜索引擎站点地图
- `llms.txt`
- `llms-full.txt`

### 白客松专题资源

- `秦岭AI白客松落地页/assets/`：白客松专题图片、logo、二维码等资源
- `秦岭AI白客松落地页/styles.css`：白客松落地页样式
- `秦岭AI白客松落地页/script.js`：白客松落地页脚本

---

## 部署入口

部署脚本：

- `deploy.sh`

当前部署逻辑：

- 根目录上传主站页面和 SEO 文件
- `images/` 同步到 COS 的 `images/`
- `秦岭AI白客松落地页/` 下的专题页面上传到 COS 根目录对应页面名
- `秦岭AI白客松落地页/assets/` 同步到 COS 的 `assets/`

---

## 后续维护建议

- 主站文件继续放根目录
- 白客松相关页面统一只放 `秦岭AI白客松落地页/`
- 如果后面还有新的专题页，建议新增同级目录，例如：
  - `活动名落地页/`
  - `专题名专题页/`
- 不要再把专题页直接散放到根目录，否则部署来源和页面关系会再次变乱
