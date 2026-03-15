/**
 * 百度搜索资源平台 - 链接自动推送脚本
 * 使用方法：node baidu_push.js
 * * 原理：读取你的本地站点地图，提取所有博文链接，一次性推送到百度 API
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// --- 你的配置信息 (基于你的截图) ---
const SITE = 'https://zylatent.com';
const TOKEN = 'oKw1XqRXs6vAcFz5'; // 👈 这是你截图里的准入密钥
const SITEMAP_PATH = path.join(__dirname, 'dist', 'sitemap-0.xml'); // 指向编译后的地图文件

// 1. 读取 sitemap-0.xml 中的链接
try {
  const content = fs.readFileSync(SITEMAP_PATH, 'utf-8');
  const urls = content.match(/<loc>(.*?)<\/loc>/g)
    .map(val => val.replace(/<\/?loc>/g, ''))
    .join('\n');

  console.log('🚀 准备推送以下链接到百度：\n', urls);

  // 2. 发送 POST 请求到百度接口
  const options = {
    hostname: 'data.zz.baidu.com',
    path: `/urls?site=${SITE}&token=${TOKEN}`,
    method: 'POST',
    headers: {
      'Content-Type': 'text/plain',
      'Content-Length': Buffer.byteLength(urls)
    }
  };

  const req = https.request(options, (res) => {
    let data = '';
    res.on('data', (chunk) => data += chunk);
    res.on('end', () => {
      const result = JSON.parse(data);
      if (result.success) {
        console.log(`✅ 推送成功！今日剩余配额: ${result.remain}`);
      } else {
        console.log(`❌ 推送失败：${result.message}`);
      }
    });
  });

  req.on('error', (e) => {
    console.error(`🚨 请求报错: ${e.message}`);
  });

  req.write(urls);
  req.end();

} catch (err) {
  console.error('❌ 错误：找不到 sitemap 文件。请确保先执行过 pnpm build。');
}