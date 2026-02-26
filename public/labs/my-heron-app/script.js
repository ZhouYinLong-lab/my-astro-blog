// 多图片随机映射字典 (请确保文件名与你 images 文件夹里的一致)
const heronImages = {
    joy: ['AAA1.gif', 'AAA2.jpg','joy_1.gif','joy_2.gif','joy_3.gif','joy_4.gif',
        'joy_5.jpg','joy_6.jpg','joy_7.jpg','joy_8.gif','joy_9.jpg','joy_10.jpg','joy_11.jpg'],

    sadness: ['AAA1.gif', 'AAA2.jpg','sad_1.gif','sad_2.jpg','sad_3.jpg','sad_4.jpg','sad_5.gif',
        'sad_6.jpg','sad_7.jpg','sad_8.jpg',],

    anger: ['AAA1.gif', 'AAA2.jpg','angry_1.jpg','angry_1.jpg','angry_2.gif','angry_3.jpg','angry_4.jpg','angry_5.jpg',
        'angry_6.jpg','angry_7.jpg','angry_8.jpg'],

    fear: ['AAA1.gif', 'AAA2.jpg','scared_1.jpg'],

    surprise: ['AAA1.gif', 'AAA2.jpg','shocked_1.jpg','shocked_2.jpg'],

    love: ['AAA1.gif', 'AAA2.jpg','love_1.jpg','love_2.jpg','love_3.jpg',],

    default: ['AAA1.gif', 'AAA2.jpg','neutral_1.jpg','neutral_2.gif','neutral_3.jpg','neutral_4.jpg','neutral_5.jpg','neutral_6.jpg']

};

const textInput = document.getElementById('text-input');
const analyzeBtn = document.getElementById('analyze-btn');
const statusMsg = document.getElementById('status-msg');
const heronImg = document.getElementById('heron-img');
const emotionLabel = document.getElementById('emotion-label');

analyzeBtn.addEventListener('click', async () => {
    const text = textInput.value.trim();
    if (!text) {
        statusMsg.style.color = "#666";
        statusMsg.textContent = "请先输入一点内容哦！";
        return;
    }

    // 每次点击重置文字颜色和状态
    statusMsg.style.color = "#666";
    statusMsg.textContent = "夜鹭正在跨海求签...";
    analyzeBtn.disabled = true;

    try {
        let response = await fetch('https://my-blog-pearl-two.vercel.app/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        
        // 【关键防御】如果 Vercel 根本没有部署 api 文件夹,它会返回一个 HTML 的 404 页面
        // 这里提前拦截,防止后面的 JSON 解析直接崩溃
        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
             throw new Error("后端接口不存在 (404)！Vercel 没有正确部署 api 文件夹。");
        }

        let data = await response.json();

        // 自动重试逻辑：处理模型冷启动
        if (data.error === 'cold_start') {
            let waitTime = Math.ceil(data.estimated_time);
            
            // 倒计时循环
            for (let i = waitTime; i > 0; i--) {
                statusMsg.textContent = `夜鹭还在云端睡觉,强行唤醒中... 请稍等 ${i} 秒`;
                await new Promise(resolve => setTimeout(resolve, 1000));
            }

            statusMsg.textContent = "夜鹭醒了,正在光速识别...";
            
            // 倒计时结束后,自动发起第二次请求
            response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            data = await response.json();
        }

        // 如果重试后,或第一次请求本身就携带了确切的 error 报错信息
        if (data.error && data.error !== 'cold_start') {
             throw new Error(data.error); 
        }

        const topEmotion = data.label;

        // 随机出图逻辑
        const imagesArray = heronImages[topEmotion] || heronImages['default'];
        const imagePath = `images/${imagesArray[Math.floor(Math.random() * imagesArray.length)]}`;

        statusMsg.style.color = "#4a90e2"; // 成功后变成蓝色
        statusMsg.textContent = "识别成功！";
        emotionLabel.textContent = `心情: ${topEmotion}`;
        
        // 触发 Q弹 动画逻辑
        heronImg.style.display = 'inline-block';
        heronImg.src = imagePath;
        
        heronImg.classList.remove('animate-pop');
        void heronImg.offsetWidth; // 触发浏览器重排
        heronImg.classList.add('animate-pop');

    } catch (error) {
        // 【核心修改】将真实的报错信息直接变成红色显示在屏幕上！
        console.error("详细错误信息:", error);
        statusMsg.style.color = "red";
        statusMsg.textContent = `🚨 报错啦: ${error.message}`;
    } finally {
        // --- 替换原本直接恢复按钮的代码,加入 3秒 冷却机制 ---
        let cooldown = 3;
        analyzeBtn.textContent = `让夜鹭喘口气 (${cooldown}s)`;
        
        const timer = setInterval(() => {
            cooldown--;
            if (cooldown <= 0) {
                clearInterval(timer);
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = "召唤夜鹭！";
            } else {
                analyzeBtn.textContent = `让夜鹭喘口气 (${cooldown}s)`;
            }
        }, 1000);
        // ----------------------------------------------------
    }
    });