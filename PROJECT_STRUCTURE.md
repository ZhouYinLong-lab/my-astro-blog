# Project Folders Structure Blueprint — 寒柳别苑 (hanliu-biyuan)

> **生成日期**: 2026-06-23
> **项目类型**: Astro 5 静态博客 (Node.js)
> **UI 框架**: TailwindCSS 3 + daisyUI 4
> **包管理器**: pnpm

---

## 1. 结构总览

项目采用 Astro 5 标准的 **按功能分层** 组织结构，混合了 **按类型分组**（components/layouts/pages/utils）和 **按内容分组**（content/blog）两种模式。整体遵循 Astro 框架约定，包含 Frosti 主题的定制化扩展。

**组织原则**:
- `src/pages/` — 基于文件系统的路由（Astro 核心约定）
- `src/components/` — 可复用 UI 单元，按功能域分子目录
- `src/content/` — 内容集合（blog 文章）
- `src/layouts/` — 页面外壳组件
- `src/styles/` — 全局样式
- `public/` — 零处理的静态资源

---

## 2. 目录可视化（ASCII Tree, Depth=3）

```
hanliu-biyuan/
├── .astro/                          # [自动生成] Astro 缓存
├── .github/
│   ├── ISSUE_TEMPLATE/              # Issue 模板
│   └── workflows/
│       ├── ci.yml                   # PR 检查
│       └── deploy.yml               # 部署到 GitHub Pages
├── .vscode/
│   ├── extensions.json
│   ├── launch.json
│   └── settings.json
├── public/                          # 静态资源 (零处理直接复制)
│   ├── background/                  # 背景图 (15 张 .webp/.png)
│   ├── img/                         # 文章配图 (按主题分目录)
│   │   ├── 2025snow/
│   │   ├── Duncon/                  # ⚠️ 首字母大写
│   │   ├── JiNan/                   # ⚠️ 驼峰命名
│   │   ├── Rimbaud/                 # ⚠️ 首字母大写
│   │   ├── flowers/
│   │   ├── ghost/
│   │   ├── hanli/
│   │   ├── my-2025/
│   │   ├── question/
│   │   ├── random/season1/
│   │   ├── reflection/
│   │   ├── water/
│   │   ├── xiaoxiezi/
│   │   ├── xuanyuan/
│   │   ├── yelu/
│   │   └── zawu/
│   ├── labs/                        # 独立 HTML 实验项目
│   │   ├── Geng-Blade/              # ⚠️ 驼峰+连字符
│   │   ├── My-Crypto-compiler/      # ⚠️ 驼峰+连字符
│   │   ├── YanHua/
│   │   ├── huang/
│   │   ├── my-heron-app/
│   │   ├── onlyto/
│   │   ├── seal1/
│   │   └── smart-agent/
│   ├── music/                       # 音频文件
│   └── republic/                    # 子站点
│       └── articles/
├── src/
│   ├── components/
│   │   ├── comments/                # Twikoo 评论组件
│   │   ├── mdx/                     # MDX 自定义组件 (12个)
│   │   ├── sidebar/                 # 侧边栏子组件
│   │   ├── temple/                  # ⚠️ 拼写: 应为 templates/
│   │   └── widgets/                 # 通用 UI 组件
│   ├── content/
│   │   └── blog/                    # 博客文章 (50+ .mdx/.md)
│   ├── i18n/                        # 多语言翻译
│   ├── integration/                 # Astro 自定义集成
│   ├── interface/                   # TypeScript 类型定义
│   ├── layouts/                     # 页面布局
│   ├── pages/                       # 路由页面
│   │   ├── blog/                    # 博客相关路由
│   │   ├── chores/                  # 工具页面
│   │   └── og/                      # OG 图片生成
│   ├── plugins/                     # Remark 插件
│   ├── styles/                      # 全局 SCSS
│   └── utils/                       # 工具函数
├── .env.example                     # 环境变量模板
├── .gitignore
├── .gitattributes
├── astro.config.mjs                 # Astro 主配置
├── baidu_push.js                    # 百度站长推送
├── biome.json                       # Lint/Format 配置
├── ec.config.mjs                    # Expressive Code 配置
├── frosti.config.yaml               # 站点配置
├── package.json
├── pnpm-lock.yaml
├── tailwind.config.mjs              # TailwindCSS + daisyUI
└── tsconfig.json
```

---

## 3. 关键目录分析

### 3.1 `src/pages/` — Astro 路由层 (18 文件)

| 子目录 | 用途 | 文件数 |
|--------|------|--------|
| `blog/` | 博客列表、详情、归档、分类、标签、搜索 | 8 |
| `chores/` | 更新日志、热力图 | 2 |
| `og/` | 动态 OG 图片生成 (satori + sharp) | 1 |
| 根目录 | 首页、关于、实验室、友链、后院、人文十问、RSS、robots | 7 |

**现状**: 结构合理，路由清晰。

### 3.2 `src/components/` — 组件层 (30+ 文件)

| 子目录 | 内容 | 评估 |
|--------|------|------|
| `mdx/` | AlertBase, Collapse, Diff, Error, FeatureCard, FriendCard, GitHubStats, Info, Kbd, LinkCard, MusicPlayer, Success, TimeLine, Warning | 删除了 3 个死代码，剩余 12 个 |
| `sidebar/` | ProfileBar, SearchBar, TOCBar, ToolBar | ✅ 完整 |
| `widgets/` | Heading, Pagination, PostFilter, PostInfo, ReadingProgress, ScrollToTop, SiteInfo, ThemeToggle, etc. | ✅ 合理 |
| `temple/` | Card, CardGroup | ⚠️ 目录名拼写错误，应为 `templates/` |
| `comments/` | Twikoo | ✅ |

### 3.3 `public/img/` — 图片资源 (15 子目录)

**现状问题**:
- 命名不一致: `Duncon/`（首字母大写）、`JiNan/`（驼峰）、`hanli/`（小写拼音）、`yelu/`（小写拼音）混合
- `water/` 下有 `water1.jpg` ~ `water15.jpg`，可能未被引用
- 根 `public/img/` 下有零散文件: `image1.jpg`, `image2.jpg`, `left.png`, `right.png`, `loading.gif`, `moonlight.png`, `stamp.png` 等需审计

**建议**: 统一为全小写+连字符命名（如 `ji-nan/`, `duncon/`, `rimbaud/`）

### 3.4 `public/labs/` — 实验项目 (8 子目录)

独立 HTML/CSS/JS 实验项目，每个是一个完整小应用。

**现状**: 命名混合（驼峰、连字符、纯小写），建议统一为小写+连字符。

---

## 4. 文件放置模式

| 文件类型 | 放置位置 | 命名约定 |
|----------|----------|----------|
| 页面路由 | `src/pages/` 或 `src/pages/<section>/` | `.astro` 后缀，文件名即 URL |
| 可复用组件 | `src/components/<domain>/` | PascalCase `.astro` |
| 博客文章 | `src/content/blog/` | 描述性中文名 `.mdx` |
| 类型定义 | `src/interface/` | `.ts` 文件 |
| 工具函数 | `src/utils/` | `camelCase.ts` |
| 全局样式 | `src/styles/` | `kebab-case.scss` |
| 静态资源 | `public/` 对应子目录 | 描述性名称 |
| 配置文件 | 项目根目录 | `<tool>.config.*` |

---

## 5. 命名和组织约定

### 当前状态
- **组件文件**: PascalCase（`MainCard.astro`, `PostFilter.astro`）✅
- **工具/类型**: camelCase（`blogUtils.ts`, `site.ts`）✅
- **配置文件**: 工具前缀（`astro.config.mjs`, `tailwind.config.mjs`）✅
- **博客文章**: 中文命名为主，少量英文 ⚠️
- **图片目录**: 混合命名 ⚠️

### 建议规范
- `public/img/` 子目录: 全小写 + 连字符（`ji-nan/`, `night-heron/`）
- `public/labs/` 子目录: 全小写 + 连字符（`smart-agent/`, `geng-blade/`）
- 博客文章: 全中文或中文拼音 slug，避免空格和英文混合

---

## 6. 导航和开发工作流

### 入口点
| 任务 | 起点 |
|------|------|
| 修改站点配置 | `frosti.config.yaml` |
| 添加新页面 | `src/pages/` → 创建 `.astro` 文件 |
| 写新文章 | `src/content/blog/` → 创建 `.mdx` 文件 |
| 修改布局 | `src/layouts/BaseLayout.astro` |
| 添加组件 | `src/components/` 对应子目录 |
| 修改样式 | `src/styles/global.scss` |
| 添加翻译 | `src/i18n/translations.yaml` |

### 常见开发任务
- **新增博客文章**: 在 `src/content/blog/` 创建 `.mdx`，添加 frontmatter
- **新增页面**: 在 `src/pages/` 创建 `.astro`，可选继承 `BaseLayout`
- **新增 MDX 组件**: 在 `src/components/mdx/` 创建，文章中 `import` 使用
- **修改主题色**: 编辑 `frosti.config.yaml` + `tailwind.config.mjs`

---

## 7. 构建与输出

- `pnpm dev` → Astro 开发服务器（端口默认 4321）
- `pnpm build` → `astro build && pagefind --site dist` → 输出到 `dist/`
- `pnpm preview` → 预览构建结果
- CI/CD: GitHub Actions → 构建后部署到 GitHub Pages（域名 `zylatent.com`）

---

## 8. 结构问题与改进建议

### 🔴 需要修改

| # | 问题 | 当前 | 建议 |
|---|------|------|------|
| 1 | `temple/` 目录名拼写错误 | `src/components/temple/` | → `src/components/cards/` |
| 2 | 图片目录命名不一致 | `Duncon/`, `JiNan/`, `hanli/` | → 全部 `kebab-case` |
| 3 | labs 目录命名不一致 | `Geng-Blade/`, `My-Crypto-compiler/` | → 全部 `kebab-case` |

### 🟡 建议优化

| # | 问题 | 当前 | 建议 |
|---|------|------|------|
| 4 | `public/img/` 零散文件 | `image1.jpg`, `left.png` 等 | 审计后删除未引用文件 |
| 5 | `public/img/water/` 批量编号 | `water1~15.jpg` | 仅保留被文章引用的 |
| 6 | `src/interface/` 别名不一致 | `@interfaces/*` → `src/interface/*` | 统一为单数形式 |

### 🟢 已修复

| # | 问题 | 状态 |
|---|------|------|
| 7 | `docs/` 为上游主题文档 | ✅ 已删除 |
| 8 | 博客文件名含空格 | ✅ 已改为连字符 |
| 9 | `waline.scss` 死代码 | ✅ 已删除 |
| 10 | `.frosti-*` 类名耦合 | ✅ 已改为 `.section-heading` / `.blog-code` |

---

## 9. 扩展模板

### 新增博客文章
```
src/content/blog/
└── <slug>.mdx          # 描述性中文名，使用连字符而非空格
```
```yaml
---
title: 文章标题
description: 文章描述
pubDate: YYYY-MM-DD
categories:
  - 分类名
tags:
  - 标签1
  - 标签2
image: /img/<dir>/<image>.webp
---
```

### 新增页面
```
src/pages/
└── <route-name>.astro  # 若需要子路由则创建同名目录
```

### 新增 MDX 组件
```
src/components/mdx/
└── <ComponentName>.astro
```

### 新增图片目录
```
public/img/
└── <topic-name>/       # 全小写 + 连字符，与文章 slug 对应
```

---

## 10. 结构强制

- **Biome**: `biome.json` 控制格式化和 lint 规则
- **Astro Check**: `pnpm check` 验证 TypeScript 类型
- **CI**: GitHub Actions 在 PR 时运行 `biome:check` + `astro check`
- **Git**: `.gitignore` 排除 `node_modules/`、`dist/`、`.astro/`、`.env`

---

> **下次更新**: 当项目结构发生重大变化时更新此文档。
> **维护者**: 柳含知 (ZhouYinLong-lab)
