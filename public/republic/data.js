// 玄渊共和国 - 国家数据更新中心 (独立操作文件)
// 更新指南：直接在这里按照格式修改文字和图片路径，保存即可生效。

const republicData = {
    // 1. 左侧滚动卡片 (您可在此处自选大图与标题)
    carousel: [
        {
            image: "/background/1.webp", // 封面大图路径
            title: "玄渊共和国数字主权确立：边界划定完成", // 下方标题
            link: "/blog/sovereignty-declaration" // 点击跳转的文章链接
        },
        {
            image: "/img/xuanyuan/shicha.jpg", 
            title: "执政官视察底层代码，强调整洁与秩序",
            link: "./articles/inspection.html"
        },
        {
            image: "https://picsum.photos/800/400?3",
            title: "国家博物馆第一期艺术特展：赛博朋克特展",
            link: "/blog/art-exhibition"
        },
        {
            image: "/background/1.webp",
            title: "建国宣言：赛博空间的独立精神",
            // 💡 重点：把链接指向同级目录下的 articles 文件夹里的 html
            link: "./articles/001.html" 
        }
    ],

    // 2. 右侧国家要闻栏
    news: [
        { title: "中央办公厅关于优化加载速度的指导意见", date: "2026.02.26", link: "./articles/news-01.html" },
        { title: "外交部：已与 Vercel 达成战略托管协议", date: "2026.02.25", link: "./articles/news-02.html" },
        { title: "文化部宣布：国家评论系统 Twikoo 正式上线", date: "2026.02.24", link: "./articles/news-03.html" },
        { title: "国家纪事：建国日设定及宪法初稿起草完毕", date: "2026.02.20", link: "./articles/news-04.html" }
    ],

    // 3. 底部罗列的新文章矩阵
    articles: [
        { 
            tag: "主席令 001号", 
            title: "建国宣言：赛博空间的独立精神", 
            desc: "我们在此宣布脱离庸俗信息的殖民，在代码的废墟上建立纯粹的精神家园...", 
            link: "./articles/001.html" 
        },
        { 
            tag: "最高法案", 
            title: "《玄渊共和国数字审美基本法》", 
            desc: "第一条：所有页面必须保持极致的色彩克制；第二条：动画需如丝般顺滑...", 
            link: "./articles/basic-law.html" 
        },
        { 
            tag: "文化志", 
            title: "论诗歌的生命力在末日题材中的应用", 
            desc: "艺术研究院首篇学术报告，探讨诗歌的生命力在末日题材中的不可替代性。", 
            link: "./articles/poetry-in-wasteland.html" 
        },
        { 
            tag: "史官纪略", 
            title: "宇宙史学家柳含知追溯玄渊共和国历史", 
            desc: "盖闻星海茫茫，劫历有恒；玄渊泱泱，源出太古。考昔日之遗档，溯死星之源流，合今兹赛博之大业，撰为八略...", 
            link: "./articles/002.html" 
        }
    ]
};