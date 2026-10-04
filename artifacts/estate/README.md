# 别苑建模初稿

这是第一阶段的空间与低模研究。由 `tools/build-estate.py` 在 Blender 4.5.3 LTS 中生成，未使用第三方模型或贴图。

## 文件

- `estate-day.blend`：日间完整场景、材质、摄像机和光照，可直接在 Blender 中编辑。
- `estate-night.blend`：相同几何的夜间光照场景。
- `../../public/world/blender/estate.glb`：几何与材质导出，不包含渲染灯光或相机。
- `../../public/world/blender/estate-day.png`、`estate-night.png`：同机位透明背景渲染。
- `../../public/world/blender/regions.json`：导航标签、原站点链接、投影坐标和模型统计。

运行博客开发服务后，打开 `/world/blender/index.html` 可比较昼夜渲染并点击导航。此预览使用静帧，尚非 WebGL 三维查看器。

## 重新生成

在仓库根目录执行 `blender --background --python tools/build-estate.py`。需要本机 Blender 命令的完整路径时替换 `blender`。脚本固定随机种子，重复运行会覆盖上述生成产物。

六个导航根对象是 `nav_home`、`nav_making`、`nav_lab`、`nav_library`、`nav_garden`、`nav_backyard`。其子网格按材质合并，保留 glTF extras 中的名称和链接。场景坐标为 Z 向上，glTF 导出转换为 Y 向上。

## 第一阶段边界

当前重点是建筑体量、围合关系和昼夜对照。中文标签由预览网页叠加。屋瓦、柳树、室内陈设为低模示意，后续可继续精修；实时查看器、手机性能、屏幕阅读器与 WebGL 回退还未验收。现有 `/world/` 页面保留原版本。

第二版按用户反馈补齐正面墙体、山墙和天花；仅在真实门窗位置留洞，书斋与工坊使用固定半开门扇，其余房门关闭。左右厢房转向院心，相机调整为接近原地图的正面俯视。当前门扇是静态姿态，不支持点击开关。

## 第三版：固定视角像素渲染

生成：`blender --background --python tools/build-estate.py -- --pixel`。

- 新增 `tools/estate_detail.py`：纯几何的层叠筒瓦、错缝石板、砖墙基座、木构细节、苔藓、垂柳叶簇、竹林、盆栽、茶盘与告示牌。
- `estate-pixel-day.blend` / `estate-pixel-night.blend` 是新版可编辑源文件，旧版仍在。
- 网站新增 `estate-pixel-day.png` / `estate-pixel-night.png`，原生 640×480，Cycles 256 samples、降噪、窄像素过滤；网页使用 `image-rendering: pixelated`。放大模式按 CSS 尺寸显示为 1280×960；适应窗口模式随容器缩放。
- 这是 Blender 生成的像素风渲染，不是手绘逐像素、限定色数的精灵图。没有调用图像生成服务或下载外部纹理。
- `estate-pixel.glb` 使用 Draco 压缩，当前 420,660 字节、55,177 个三角面、87 个网格；未来加载到 Three.js 时需要配置 Draco 解码器。预览页只加载图片，不自动下载 GLB。
- 导航数据为 `regions-pixel.json`，相机和热点投影与第二版保持一致；支持昼夜、旧版对照、地标显隐和局部滚动放大。
- 导航数据同时包含 7 处灯笼与 2 处池塘动效的相机投影位置；CSS 在对应位置叠加轻微夜灯呼吸和水纹。可手动关闭，系统 reduced-motion 默认关闭，对照旧版时隐藏。不代表门窗动画已完成。
- 检查模型：`blender --background --python tools/check-estate.py -- --pixel`。
- 检查预览：先启动 `pnpm dev --host 127.0.0.1`，再执行 `uv run --with playwright python tools/check-estate-preview.py`。测试使用本机 Chrome，截图保存在当前目录。脚本当前按 Windows Chrome 安装路径配置。

本轮两次渲染迭代：首次发现夜景采样噪声、柳树冠层稀疏；第二次提高采样并启用降噪、增加冠层和垂枝叶簇，降低瓦片色差，检查昼夜成图后接入预览。
