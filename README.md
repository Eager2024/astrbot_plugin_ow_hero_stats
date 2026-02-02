这是一个完整、排版精美且包含了你所有要求的 `README.md` 文件。你可以直接点击代码块右上角的“复制”按钮，然后粘贴到你的项目中。

---

```markdown   ”“减价
# 📊 AstrBot OW2 Hero Stats Plugin

<div align="center">

**守望先锋 2（国服）数据可视化查询插件**

[![AstrBot](https://img.shields.io/badge/AstrBot-Plugin-violet)](https://github.com/Soulter/AstrBot)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

数据来源：暴雪国服官方接口 | 适配 AstrBot 框架

</div>

## 📖 简介

这是一个专为 [AstrBot](https://github.com/Soulter/AstrBot) 设计的守望先锋 2（国服）数据查询插件。

它摒弃了枯燥的纯文本回复，能够直接从暴雪国服 API 获取最新的英雄数据，并生成包含 **英雄头像、段位图标、胜率/出场率/禁用率/KDA** 的精美可视化图片战报。

## ✨ 核心功能

- **🎨 数据可视化**：生成暗色风格的精美排行榜图片，手机/电脑端阅读体验极佳。
- **⚔️ 双模式支持**：完美适配 **竞技模式**（默认）与 **快速模式** 的数据查询。
- **📊 多维度排行**：
  - 支持按 **胜率**（默认）、**出场率**（热度）、**禁用率**（Ban率）、**KDA** 排序。
  - 支持筛选 **所有段位**（青铜~冠军）和 **所有职责**（重装/输出/支援）。
- **🔍 英雄趋势查询**：
  - 输入特定英雄名（如 `/ow数据 源氏`），即可查看该英雄在 **全分段** 的数据变化趋势。
- **🧠 智能指令识别**：
  - 支持模糊匹配：输入“坦克”识别为重装，输入“休闲”识别为快速模式，输入“排位”识别为竞技模式。
- **🚀 高效缓存**：内置 30 分钟数据缓存，防止频繁请求导致接口受限，秒级响应。

---

## 🛠️ 安装与配置

### 1. 安装插件
进入 AstrBot 的插件目录并克隆本项目：

```bash   ”“bash
cd data/plugins/
git clone [https://github.com/Eager2024/astrbot_plugin_ow_hero_stats.git](https://github.com/Eager2024/astrbot_plugin_ow_hero_stats.git)

```

### 2. 安装依赖

本插件依赖 `Pillow` 进行绘图，依赖 `requests` 获取数据：

```bash
pip install pillow requests

```

### 3. 资源配置（⚠️ 必须步骤）

为了获得最佳的图片生成效果，你需要手动配置**字体**和**头像**文件。

#### A. 字体文件

请将字体文件 **`思源黑体 CN Bold.otf`** 放入插件根目录：
`data/plugins/astrbot_plugin_ow_hero_stats/思源黑体 CN Bold.otf`

> 💡 提示：如果没有该字体，插件将回退到系统默认字体，中文显示效果可能会变差。

#### B. 英雄头像

需要在插件目录下新建 `icons` 文件夹，并放入英雄头像图片。
**图片文件名必须是英雄的英文 ID（小写）**，格式为 `.png`。

1. **新建目录**：`data/plugins/astrbot_plugin_ow_hero_stats/icons/`
2. **下载资源**：推荐使用 [此仓库的 normal 文件夹](https://github.com/drippinghere/overwatch2-hero-icons/tree/223584141bf91b838459ef159998f98a11f4119a/normal)。
3. **放入图片**：将下载的 `ana.png`, `genji.png` 等图片放入 `icons` 文件夹。

---

## 💻 指令使用手册

核心指令：`/ow数据`

### 1. 查询排行榜 (Leaderboard)

查询指定段位、职责下的英雄排名。

**指令格式：**
`/ow数据 [模式] [分段] [职责] [排序]`
*(参数顺序不限，插件会自动识别)*

* **模式关键词**：
* 竞技（默认）：`竞技`, `排位`, `天梯`, `上分`
* 快速：`快速`, `休闲`, `娱乐`, `匹配`


* **分段**：`青铜` ~ `宗师` (或 `冠军`)，不填默认“所有分段”。
* **职责**：`重装` (或 `坦克`), `输出`, `支援` (或 `奶`), `所有`。
* **排序**：`胜率` (默认), `出场`, `禁用`, `KDA`。

**📝 常用示例：**

| 指令 | 说明 |
| --- | --- |
| `/ow数据` | 查询当前赛季 **所有分段、所有职责** 的胜率榜 |
| `/ow数据 宗师 输出` | 查询 **宗师段位** 的 **输出位** 英雄排名 |
| `/ow数据 钻石 坦克 禁用` | 查询 **钻石段位** **重装英雄** 的禁用率排名 |
| `/ow数据 快速 支援` | 查询 **快速模式** 下 **辅助英雄** 的数据榜 |
| `/ow数据 休闲 KDA` | 查询 **快速模式** 下全英雄 KDA 排名 |

### 2. 查询特定英雄趋势 (Hero Trend)

查看某个本命英雄在当前赛季从青铜到宗师的所有数据变化。

**指令格式：**
`/ow数据 [英雄名]`

**📝 示例：**

* `/ow数据 源氏`
* `/ow数据 安娜`
* `/ow数据 斩仇`

---

## ❓ 常见问题 (FAQ)

**Q: 发送指令后图片里的字是方框？**
A: 缺少字体文件。请确保 `思源黑体 CN Bold.otf` 已正确放入插件根目录。

**Q: 排行榜里英雄头像是空白的？**
A: 缺少头像文件或文件名不对。请检查 `icons` 文件夹，并确保文件名是英文小写（如 `soldier-76.png` 不是 `Soldier76.png`）。

**Q: 为什么没有显示“冠军”段位的数据？**
A: 暴雪官方接口有时未开放冠军段位数据，或者该段位样本过少，此时会显示无数据。

---

## 👨‍💻 关于作者 & 开发幕后

👋 **Hello!**   👋* *用人!*＊
我是名为 Echo 的 QQ 群机器人的持有者Eager，也是一名正在摸索的菜鸟大学生。

这是我**第一个**正式上传到 GitHub 的开源项目。起初是因为心血来潮想给群友整一个查国服数据的插件，但在 AstrBot 插件市场搜了一圈，只发现了查询国际服战绩的 [astrbot_plugin_owcx](https://github.com/TZYCeng/astrbot_plugin_owcx)。

受到该作者以及群友们的启发，我决定自己动手（虽然大部分是动嘴）。

🤖 **特别说明**：
本项目是在 **Google Gemini** 的全程指（脑）导（控）下完成的。代码的“含人量”极低，主打一个 AI 编程。
作为新手作品，难免会有 BUG 或设计不周的地方，希望大家多多包涵！如果你有任何建议或发现问题，欢迎提交 Issue，我会尝试（让 Gemini）修复它。

---

## 🙏 致谢 & 资源来源

* **灵感来源**：感谢 [astrbot_plugin_owcx](https://github.com/TZYCeng/astrbot_plugin_owcx) 项目提供的灵感。
* **美术资源**：插件中使用的全套英雄头像图标来自开源仓库 [overwatch2-hero-icons](https://github.com/drippinghere/overwatch2-hero-icons/tree/223584141bf91b838459ef159998f98a11f4119a/normal)。* **美术资源**：插件中使用的全套英雄头像图标来自开源仓库 [overwatch2-hero-icons](https://github.com/drippinghere/overwatch2-hero-icons/tree/223584141bf91b838459ef159998f98a11f4119a
ormal)。
* **AI 协力**：Google Gemini 2.0 Flash (Thinking)** *AI ** *：谷歌Gemini 2.0 Flash（思考）

---

## 📄 声明

* 数据来源：[Blizzard CN Overwatch API](https://www.google.com/search?q=https://webapi.blizzard.cn/)
* 英雄图标版权归 Blizzard Entertainment 所有。
* 本插件仅供学习交流使用。

```

```
