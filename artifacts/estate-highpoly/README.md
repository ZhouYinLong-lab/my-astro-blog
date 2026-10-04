# 寒柳别苑 · Blender 高细节模型

以当前网站使用的 `public/world/estate-garden.webp` 为视觉依据重新建立三维场景。沿用八个地点、书房与会客亭之间的石拱桥、大柳树、花园和四只水鸟。建模根据单张概念图解释空间与尺寸，并非测绘还原。

## 交付

- `hanliu-garden-highpoly.blend`：Blender 4.5.3 LTS 源文件，八个地点分别归入集合，并有携带名称、网址的 `nav_*` 根对象。
- `overview.png`：整体渲染，2400 × 1800。
- `bridge-detail.png`：书房、桥和会客亭局部渲染，2400 × 1800。
- `garden-detail.png`：柳树、工坊、花园局部渲染，2400 × 1800。
- `model-stats.json`：准确面数、导航坐标与相机投影。
- `validation.log`：重新打开保存文件后的验证记录。

约 255 万三角面、190 万顶点，185 个网格对象，37 种材质。瓦片、格栅、桥身石块、枝条、柳叶与花瓣是可编辑网格，按区域与材质合并，便于管理对象数量。包含四台相机：整体、桥亭局部、花园局部与俯视。

材质使用 Blender 程序纹理；参考图和中文字库已打包。采用 Cycles / OptiX、96 samples 与降噪，灯光和相机保留在源文件中。默认打开为整体相机。

## 再生成

在仓库根目录执行：

```powershell
& 'D:/Projects/其余项目/鼓楼建模/work/tools/blender-4.5.3-windows-x64/blender.exe' --background --python tools/build-garden-highpoly.py
& 'D:/Projects/其余项目/鼓楼建模/work/tools/blender-4.5.3-windows-x64/blender.exe' --background --python tools/check-garden-highpoly.py
```

脚本 `tools/build-garden-highpoly.py` 接受 `-- --draft`（低采样整体试渲染）或 `-- --no-render`（只生成模型）。后者仍保存完整高细节几何。

当前交付为静态高细节场景。水鸟、门窗与树木尚无动画；没有制作网页用减面、烘焙和 LOD 版本。源文件只保存在本地，未替换已上线的二维地图，也未推送模型或草稿状态。
