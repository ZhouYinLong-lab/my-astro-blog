/**
 * 百度搜索资源平台 - 链接自动推送脚本 (精简版)
 * 使用方法：node baidu_push.js
 */

import fs from 'fs';
import path from 'path';
import http from 'http';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SITE = 'https://zylatent.com';
const TOKEN = 'oKw1XqRXs6vAcFz5'; 
const SITEMAP_PATH = path.join(__dirname, 'dist', 'sitemap-0.xml'); 

try {
  if (!fs.existsSync(SITEMAP_PATH)) {
    throw new Error(`找不到文件: ${SITEMAP_PATH}。请确保先执行过 pnpm build。`);
  }

  const content = fs.readFileSync(SITEMAP_PATH, 'utf-8');
  const urlMatches = content.match(/<loc>(.*?)<\/loc>/g);
  
  if (!urlMatches) {
    throw new Error('站点地图中未发现有效的链接。');
  }

  // 💡 优化点：只筛选包含 /blog/ 且不包含 /tag/ 或 /category/ 的真实博文链接
  const urls = urlMatches
    .map(val => val.replace(/<\/?loc>/g, ''))
    .filter(url => url.includes('/blog/') && !url.includes('/tag/') && !url.includes('/category/'))
    .join('\n');

  console.log('🚀 准备推送博文链接到百度...');

  const options = {
    hostname: 'data.zz.baidu.com',
    path: `/urls?site=${SITE}&token=${TOKEN}`,
    method: 'POST',
    headers: {
      'Content-Type': 'text/plain',
      'Content-Length': Buffer.byteLength(urls)
    }
  };

  const req = http.request(options, (res) => {
    let data = '';
    res.on('data', (chunk) => data += chunk);
    res.on('end', () => {
      try {
        const result = JSON.parse(data);
        if (result.success) {
          console.log(`✅ 推送成功！本次推送: ${result.success} 条`);
          console.log(`📊 今日剩余配额: ${result.remain}`);
        } else {
          console.log(`❌ 百度返回错误：${result.message}`);
          if (result.message === 'over quota') {
            console.log('💡 提示：你的新站配额已用完，请明天再试，或者去百度后台“手动提交”最重要的一条。');
          }
        }
      } catch (e) {
        console.log('❌ 解析失败:', data);
      }
    });
  });

  req.on('error', (e) => {
    console.error(`🚨 脚本报错: ${e.message}`);
  });

  req.write(urls);
  req.end();

} catch (err) {
  console.error(`❌ 错误：${err.message}`);
}