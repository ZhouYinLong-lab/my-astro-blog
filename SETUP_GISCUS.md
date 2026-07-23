# Giscus 评论系统配置（一次性, 2 分钟）

## 为什么换掉 Twikoo？

旧 Twikoo 后端 `my-twikoo-server-8x6l.vercel.app` 已不可用。
Giscus 基于 GitHub Discussions, 无需服务器, 永久免费。

---

## 配置步骤

### 1. 安装 Giscus App
打开 https://github.com/apps/giscus → 点击 **Install** → 选择 `ZhouYinLong-lab/my-astro-blog`

### 2. 初始化 Discussions
打开 https://github.com/ZhouYinLong-lab/my-astro-blog/discussions
如果是第一次访问, GitHub 会自动创建默认分类

### 3. 获取配置 ID
打开 https://giscus.app/zh-CN ：
- 填入 `ZhouYinLong-lab/my-astro-blog`
- 选择页面映射：`pathname`
- 选择分类：`Announcements`（或新建一个 `Comments` 分类）
- 复制生成的 `<script>` 中的：
  - `data-category-id`（类似 `DIC_kwDORWFHIw...`）

### 4. 更新组件
编辑 `src/components/comments/Giscus.astro` 第 33 行：
```js
script.setAttribute('data-category-id', '你复制的值');
```

### 5. 提交并部署
```bash
git add -A && git commit -m "chore: 配置 Giscus 评论系统" && git push
```

---

## 页面浏览量

目前使用 localStorage 本地计数（每设备/tab 独立），部署后可在浏览器里看到"X 次阅读"。
如需服务端计数，可接入 GoatCounter(免费) 或 Supabase(已有依赖)。
