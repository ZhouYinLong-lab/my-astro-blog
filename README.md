<p align="center">
  柳含知发挥想象力和创造力的赛博后花园
</p>

<div align="center">

[![license](https://badgen.net/github/license/ZhouYinLong-lab/my-astro-blog)](https://github.com/ZhouYinLong-lab/my-astro-blog/blob/main/LICENSE)
[![astrolink](https://badgen.net/badge/Astro/5.x/purple)](https://astro.build)
[![status](https://badgen.net/badge/status/active/green)](https://zylatent.com)

</div>

## 关于

寒柳别苑，柳含知的个人博客。写代码、翻译兰波、偶尔散文。

> 盖闻乾元资始，令序惟春；二月建卯，苍龙奋伸。
> 君生吉日，正当雷乃发声之候；气禀清刚，恰是蛰虫始振之辰。

南京大学在读。C / C++ / Python 为主，前端也会一点。B站偶尔更新，魂 塞尔达 p系列玩家。

## 特性

- 浅色 / 深色模式 (lemonade + forest)
- 10 种语言界面 (zh / en / fr / ja / ko / es / de / ru / pt / it)
- Pagefind 全文搜索
- TailwindCSS + daisyUI 响应式设计
- RSS 订阅
- 动态 OG 图片生成 (satori + sharp)
- KaTeX 数学公式渲染
- Twikoo 评论系统
- MDX 自定义组件（时间线、折叠块、GitHub 卡片、音乐播放器……）
- 站点地图 & SEO
- Swup / View Transitions 页面过渡动画

## 本地运行

```bash
# 安装 pnpm（已有可跳过）
npm i -g pnpm

# 克隆项目
git clone git@github.com:ZhouYinLong-lab/my-astro-blog.git
cd my-astro-blog

# 安装依赖
pnpm i

# 生成搜索索引（首次运行）
pnpm run search:index

# 启动开发服务器
pnpm run dev
```

## 构建

```bash
pnpm run build    # 输出到 dist/
pnpm run preview  # 本地预览
```

构建时自动运行 Pagefind 索引。

## 项目结构

```
my-astro-blog/
├── src/
│   ├── content/blog/        # 文章 (MDX + MD)
│   ├── pages/               # 路由
│   │   ├── blog/            # 列表 / 文章 / 归档 / 标签 / 分类 / 搜索
│   │   ├── chores/          # 更新日志 / 热力图
│   │   └── ...              # 关于 / 实验室 / 友链 / 后院 / 人文十问
│   ├── components/          # Astro 组件
│   │   ├── mdx/             # MDX 自定义组件
│   │   ├── widgets/         # 通用组件
│   │   └── comments/        # Twikoo 评论
│   ├── layouts/             # 布局
│   ├── i18n/                # 多语言翻译
│   ├── styles/              # SCSS 样式
│   └── utils/               # 工具函数
├── public/                  # 静态资源
├── frosti.config.yaml       # 站点配置
├── astro.config.mjs         # Astro 配置
└── tailwind.config.mjs      # TailwindCSS + daisyUI 配置
```

## 技术栈

| 类别 | 技术 |
|------|------|
| 框架 | Astro 5 |
| UI | TailwindCSS 3 + daisyUI 4 |
| 内容 | MDX / Markdown |
| 评论 | Twikoo |
| 搜索 | Pagefind |
| 数据库 | Supabase |
| 图标 | astro-icon |
| 代码高亮 | Expressive Code |
| 数学 | KaTeX |
| 格式化 | Biome |

## 文章 Frontmatter

```yaml
---
title: 文章标题        # 必填
description: 文章描述   # 必填
pubDate: 2025-01-01    # 必填
image: /img/cover.webp # 可选
categories: [技术]     # 可选
tags: [Astro, 博客]    # 可选
badge: Pin             # 设为 Pin 可置顶
draft: true            # 草稿不会出现在列表中
featured: true         # 精选文章
---
```

## 链接

- 博客：[zylatent.com](https://zylatent.com)
- B站：[柳含知](https://space.bilibili.com/511060666)
- Twitter：[@Liuhanzhi23](https://x.com/Liuhanzhi23)
- 邮箱：Liuhanzhi23@outlook.com/Liuhanzhi514@gmail.com

## 许可

基于 [Frosti](https://github.com/EveSunMaple/Frosti) 主题构建，MIT License。

---

<p align="center">柳含知 · 寒柳别苑</p>
