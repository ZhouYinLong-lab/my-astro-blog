/**
 * 百度搜索资源平台 - 链接自动推送脚本 (ESM 版本 - 修复 SSL 错误)
 * 使用方法：node baidu_push.js
 */

import fs from 'fs';
import path from 'path';
import http from 'http'; // 改用 http 以避免百度接口的 SSL 证书校验问题
import { fileURLToPath } from 'url';

// 兼容 ESM 的 __dirname 逻辑
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// --- 你的配置信息 ---
const SITE = 'https://zylatent.com';
const TOKEN = 'oKw1XqRXs6vAcFz5'; 
const SITEMAP_PATH = path.join(__dirname, 'dist', 'sitemap-0.xml'); 

// 1. 读取 sitemap-0.xml 中的链接
try {
  if (!fs.existsSync(SITEMAP_PATH)) {
    throw new Error(`找不到文件: ${SITEMAP_PATH}。请确保先执行过 pnpm build。`);
  }

  const content = fs.readFileSync(SITEMAP_PATH, 'utf-8');
  // 匹配所有 <loc> 标签内的 URL
  const urlMatches = content.match(/<loc>(.*?)<\/loc>/g);
  
  if (!urlMatches) {
    throw new Error('站点地图中未发现有效的 <loc> 链接。');
  }

  // 过滤掉非必要的 URL（可选，如果需要只推送文章，可以在这里 filter）
  const urls = urlMatches
    .map(val => val.replace(/<\/?loc>/g, ''))
    .join('\n');

  console.log('🚀 准备推送以下链接到百度：\n', urls);

  // 2. 发送 POST 请求到百度接口 (使用 http 协议)
  const options = {
    hostname: 'data.zz.baidu.com',
    path: `/urls?site=${SITE}&token=${TOKEN}`,
    method: 'POST',
    headers: {
      'Content-Type': 'text/plain',
      'Content-Length': Buffer.byteLength(urls)
    }
  };

  // 百度 API 的证书经常过期或不匹配，使用 http 模块是最稳妥的
  const req = http.request(options, (res) => {
    let data = '';
    res.on('data', (chunk) => data += chunk);
    res.on('end', () => {
      try {
        const result = JSON.parse(data);
        if (result.success) {
          console.log(`✅ 百度收录报备成功！`);
          console.log(`📈 本次推送: ${result.remain === undefined ? '未知' : (result.success || 0)} 条`);
          console.log(`📊 今日剩余配额: ${result.remain}`);
        } else {
          console.log(`❌ 百度返回错误：${result.message}`);
        }
      } catch (e) {
        console.log('❌ 解析百度响应失败，原始响应内容:', data);
      }
    });
  });

  req.on('error', (e) => {
    console.error(`🚨 脚本执行报错: ${e.message}`);
    console.log('💡 提示：如果依然报错，请确认你是否开启了代理，建议在终端关闭代理后重试。');
  });

  req.write(urls);
  req.end();

} catch (err) {
  console.error(`❌ 错误：${err.message}`);
}