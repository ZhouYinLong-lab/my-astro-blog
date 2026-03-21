// ==========================================
// 1. 基础工具：二进制流与 BigInt 互相转换
// ==========================================

// 将 Uint8Array 转换为 BigInt (引入哨兵位防止丢失前导零)
function bufferToBigInt(buffer) {
    const u8 = new Uint8Array(buffer.byteLength + 1);
    u8[0] = 1; // 哨兵位
    u8.set(new Uint8Array(buffer), 1);
    let hex = [...u8].map(b => b.toString(16).padStart(2, '0')).join('');
    return BigInt('0x' + hex);
}

// 将 BigInt 还原为 Uint8Array (移除哨兵位)
function bigIntToBuffer(bigInt) {
    let hex = bigInt.toString(16);
    if (hex.length % 2 !== 0) hex = '0' + hex;
    let u8 = new Uint8Array(hex.length / 2 - 1);
    for (let i = 1; i < hex.length / 2; i++) { // 从索引 1 开始读取，跳过哨兵位
        u8[i - 1] = parseInt(hex.slice(i * 2, i * 2 + 2), 16);
    }
    return u8;
}

// ==========================================
// 2. 核心伪装：Base-N 编码与解码
// ==========================================

function encodeBaseN(bigInt, alphabet) {
    if (bigInt === 0n) return alphabet[0];
    const base = BigInt(alphabet.length);
    let result = '';
    while (bigInt > 0n) {
        result = alphabet[Number(bigInt % base)] + result;
        bigInt = bigInt / base;
    }
    return result;
}

function decodeBaseN(str, alphabet) {
    const base = BigInt(alphabet.length);
    let bigInt = 0n;
    for (let i = 0; i < str.length; i++) {
        const index = alphabet.indexOf(str[i]);
        if (index === -1) throw new Error("密文包含字典外的非法字符！");
        bigInt = bigInt * base + BigInt(index);
    }
    return bigInt;
}

// ==========================================
// 3. 高强度加密层：Web Crypto API (AES-GCM)
// ==========================================

const enc = new TextEncoder();
const dec = new TextDecoder();

// 根据用户输入的密码生成 AES 密钥
async function getKeyMaterial(password) {
    return window.crypto.subtle.importKey(
        "raw", enc.encode(password), { name: "PBKDF2" }, false, ["deriveBits", "deriveKey"]
    );
}

async function deriveKey(keyMaterial, salt) {
    return window.crypto.subtle.deriveKey(
        { name: "PBKDF2", salt: salt, iterations: 100000, hash: "SHA-256" },
        keyMaterial, { name: "AES-GCM", length: 256 }, true, ["encrypt", "decrypt"]
    );
}

// 加密主函数
async function encryptMessage(message, password) {
    const salt = window.crypto.getRandomValues(new Uint8Array(16));
    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    const keyMaterial = await getKeyMaterial(password);
    const key = await deriveKey(keyMaterial, salt);
    
    const cipherBuffer = await window.crypto.subtle.encrypt(
        { name: "AES-GCM", iv: iv }, key, enc.encode(message)
    );
    
    // 将 Salt (16), IV (12), 和密文打包在一起
    const combinedBuffer = new Uint8Array(16 + 12 + cipherBuffer.byteLength);
    combinedBuffer.set(salt, 0);
    combinedBuffer.set(iv, 16);
    combinedBuffer.set(new Uint8Array(cipherBuffer), 28);
    
    return combinedBuffer;
}

// 解密主函数
async function decryptMessage(combinedBuffer, password) {
    const salt = combinedBuffer.slice(0, 16);
    const iv = combinedBuffer.slice(16, 28);
    const data = combinedBuffer.slice(28);
    
    const keyMaterial = await getKeyMaterial(password);
    const key = await deriveKey(keyMaterial, salt);
    
    const decryptedBuffer = await window.crypto.subtle.decrypt(
        { name: "AES-GCM", iv: iv }, key, data
    );
    return dec.decode(decryptedBuffer);
}

// ==========================================
// 4. UI 交互绑定
// ==========================================

async function handleEncrypt() {
    try {
        const key = document.getElementById('secretKey').value;
        const alphabet = document.getElementById('alphabet').value;
        const plainText = document.getElementById('plainText').value;

        if (!key || !alphabet || !plainText) return alert("请填写完整参数！");
        if (new Set(alphabet).size !== alphabet.length) return alert("字典表不能有重复字符！");

        const encryptedBuffer = await encryptMessage(plainText, key);
        const bigIntData = bufferToBigInt(encryptedBuffer);
        const baseNString = encodeBaseN(bigIntData, alphabet);
        
        document.getElementById('resultOutput').value = baseNString;
    } catch (e) {
        alert("加密失败: " + e.message);
    }
}

async function handleDecrypt() {
    try {
        const key = document.getElementById('secretKey').value;
        const alphabet = document.getElementById('alphabet').value;
        const cipherText = document.getElementById('cipherText').value.trim();

        if (!key || !alphabet || !cipherText) return alert("请填写完整参数！");

        const bigIntData = decodeBaseN(cipherText, alphabet);
        const encryptedBuffer = bigIntToBuffer(bigIntData);
        const plainText = await decryptMessage(encryptedBuffer, key);
        
        document.getElementById('resultOutput').value = plainText;
    } catch (e) {
        alert("解密失败！请检查私钥、字典表是否匹配，或密文是否完整。");
        console.error(e);
    }
}