<p align="center">
  柳含知发挥想象力和创造力的赛博后花园 🌿
</p>

<div align="center">

[![license](https://badgen.net/github/license/ZhouYinLong-lab/my-astro-blog)](https://github.com/ZhouYinLong-lab/my-astro-blog/blob/main/LICENSE)
[![astrolink](https://badgen.net/badge/Astro/5.x/purple)](https://astro.build)
[![status](https://badgen.net/badge/status/active/green)](https://zylatent.com)

</div>

## 📝 关于

**寒柳别苑** 是柳含知的个人博客，记录技术探索、文学创作与生活随想。

> 盖闻乾元资始，令序惟春；二月建卯，苍龙奋伸。
> 君生吉日，正当雷乃发声之候；气禀清刚，恰是蛰虫始振之辰。

- 🏫 南京大学
- 💻 C / C++ / Python / Web
- 📖 兰波诗歌翻译、散文写作、技术笔记
- 🎮 荒野乱斗 / B站 UP主

## ✨ 特性

- 🌗 **浅色 / 深色** 模式 (lemonade + forest)
- 🌍 **10 种语言** 国际化支持 (zh / en / fr / ja / ko / es / de / ru / pt / it)
- 🔍 **全文搜索** (Pagefind)
- 📱 **响应式设计** (TailwindCSS + daisyUI)
- 📡 **RSS 订阅** 支持
- 🖼️ **动态 OG 图片** 生成 (satori + sharp)
- 📐 **KaTeX** 数学公式渲染
- 💬 **Twikoo** 评论系统
- 🎨 **MDX** 自定义组件 (时间线、折叠块、GitHub 卡片、音乐播放器等)
- 🗺️ **站点地图** & SEO 优化
- 🔄 **页面过渡动画** (Swup / View Transitions)

## 🚀 本地运行

```bash
# 1. 安装 pnpm (如已安装可跳过)
npm i -g pnpm

# 2. 克隆项目
git clone git@github.com:ZhouYinLong-lab/my-astro-blog.git
cd my-astro-blog

# 3. 安装依赖
pnpm i

# 4. 生成搜索索引（首次运行）
pnpm run search:index

# 5. 启动开发服务器
pnpm run dev
```

## 📦 构建部署

```bash
pnpm run build    # 构建到 dist/
pnpm run preview  # 本地预览构建结果
```

构建时会自动运行 Pagefind 索引生成。

## 📂 项目结构

```
my-astro-blog/
├── src/
│   ├── content/blog/        # 博客文章 (MDX + MD)
│   ├── pages/               # 路由页面
│   │   ├── blog/            # 博客列表 / 文章 / 归档 / 标签 / 分类 / 搜索
│   │   ├── chores/          # 更新日志 / 博客热力图
│   │   └── ...              # 关于 / 实验室 / 友链 / 后院 / 人文十问
│   ├── components/          # Astro 组件
│   │   ├── mdx/             # 自定义 MDX 组件 (时间线、折叠块、音乐播放器等)
│   │   ├── widgets/         # 通用组件 (分页、目录、进度条等)
│   │   └── comments/        # Twikoo 评论
│   ├── layouts/             # 布局组件
│   ├── i18n/                # 多语言翻译
│   ├── styles/              # 全局样式 (SCSS)
│   └── utils/               # 工具函数
├── public/                  # 静态资源 (图片、字体等)
├── frosti.config.yaml       # 站点配置
├── astro.config.mjs         # Astro 配置
└── tailwind.config.mjs      # TailwindCSS + daisyUI 配置
```

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 框架 | Astro 5 |
| UI | TailwindCSS 3 + daisyUI 4 |
| 内容 | MDX / Markdown |
| 评论 | Twikoo |
| 搜索 | Pagefind |
| 数据库 | Supabase |
| 图标 | astro-icon (Lucide / Simple Icons / Material Symbols) |
| 代码高亮 | Expressive Code |
| 数学 | KaTeX |
| 格式化 | Biome |

## 📄 文章 Frontmatter

```yaml
---
title: 文章标题        # 必填
description: 文章描述   # 必填
pubDate: 2025-01-01    # 必填 - 发布日期
image: /img/cover.webp # 可选 - 封面图
categories: [技术]     # 可选 - 分类
tags: [Astro, 博客]    # 可选 - 标签
badge: Pin             # 可选 - 置顶标记
draft: true            # 可选 - 草稿 (不会出现在列表中)
featured: true         # 可选 - 精选文章
---
```

## 🔗 链接

- 🌐 博客：[zylatent.com](https://zylatent.com)
- 📺 B站：[柳含知](https://space.bilibili.com/511060666)
- 🐦 Twitter：[@Liuhanzhi23](https://x.com/Liuhanzhi23)
- 📧 邮箱：Liuhanzhi23@outlook.com

## 📜 许可

基于 [Frosti](https://github.com/EveSunMaple/Frosti) 主题构建，使用 [MIT License](LICENSE)。

---

<p align="center">Made with ❤️ by 柳含知</p>
