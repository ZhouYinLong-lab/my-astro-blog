class FireworksApp {
  constructor() {
    this.fireworksContainer = document.querySelector('.fireworks-container');
    this.bulletsContainer = document.querySelector('.bullets-container');
    
    this.wishes = [
      '新年快乐！',
      '早日脱单！',
      '平安喜乐,万事顺心！',
      '保持热爱,远赴山海',
      '我是泥巴',
      '祝你每天都有小幸运',
      '好运马上到账,请查收！',
      '今天也要闪闪发光哦！',
      '岁岁平安！',
      '前路漫漫,亦有光亮',
      '愿所有美好如约而至',
      '熬过黑夜就是黎明,加油！',
      '愿平安常在,快乐常伴',
      '愿你眉眼如初,岁月如故',
      '祝你钱包和心情都鼓鼓的',
      '今天也要元气满满',
      '我是奶龙',
      '未来可期,你值得最好的！'
    ];
    
    this.macaronColors = [
      '#ffb3ba',
      '#baffc9',
      '#c9a0ff',
      '#bae1ff',
      '#ffffba',
      '#ffdfba'
    ];
    
    this.animationId = null;
    this.fireworks = [];
    this.particles = [];
    this.bullets = [];
    
    this.init();
  }
  
  init() {
    this.createFireworksCanvas();
    this.animate();
    this.startBulletGeneration();
  }
  
  createFireworksCanvas() {
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
    
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
    
    this.fireworksContainer.appendChild(this.canvas);
  }
  
  resizeCanvas() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }
  
  startBulletGeneration() {
    for (let i = 0; i < 10; i++) {
      setTimeout(() => {
        this.createBullet();
      }, i * 300);
    }
    
    setInterval(() => {
      this.createBullet();
    }, 500);
  }
  
  createBullet() {
    if (this.bullets.length > 20) {
      return;
    }
    
    const bullet = document.createElement('div');
    bullet.className = 'bullet';
    
    const wish = this.wishes[Math.floor(Math.random() * this.wishes.length)];
    bullet.textContent = wish;
    
    const color = this.macaronColors[Math.floor(Math.random() * this.macaronColors.length)];
    bullet.style.backgroundColor = color;
    
    const x = Math.random() * (window.innerWidth - 200) + 100;
    const y = Math.random() * (window.innerHeight - 100) + 50;
    bullet.style.left = `${x}px`;
    bullet.style.top = `${y}px`;
    
    const duration = 3000 + Math.random() * 2000;
    bullet.style.animationDuration = `${duration}ms`;
    
    const scale = 0.8 + Math.random() * 0.4;
    bullet.style.transform = `scale(${scale})`;
    
    this.bulletsContainer.appendChild(bullet);
    
    this.bullets.push(bullet);
    
    setTimeout(() => {
      if (bullet.parentNode) {
        bullet.parentNode.removeChild(bullet);
      }
      this.bullets = this.bullets.filter(b => b !== bullet);
    }, duration);
  }
  
  createFirework() {
    const firework = {
      x: Math.random() * window.innerWidth,
      y: window.innerHeight,
      targetY: Math.random() * (window.innerHeight * 0.6),
      targetX: Math.random() * window.innerWidth,
      speed: 8 + Math.random() * 5,
      angle: Math.atan2(
        Math.random() * (window.innerHeight * 0.6),
        Math.random() * window.innerWidth - window.innerWidth / 2
      ),
      hue: Math.random() * 360,
      trail: [],
      trailLength: 10,
      exploded: false
    };
    
    this.fireworks.push(firework);
  }
  
  // 在 script.js 的 createParticles 方法中修改：
  createParticles(x, y, hue) {
    const particles = [];
    // 粒子数量从 80-140 增加到 150-250
    const particleCount = 150 + Math.random() * 100; 
  
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: x,
        y: y,
        angle: (Math.PI * 2 / particleCount) * i,
        speed: 4 + Math.random() * 10, // 初始速度从 3-9 增加到 4-14
        friction: 0.95, // 摩擦力略微调大,让扩散更自然
        gravity: 0.12,  // 重力略微调小,让粒子飘得更久
        hue: hue + Math.random() * 40 - 20,
        brightness: 70 + Math.random() * 30,
        alpha: 1,
        decay: 0.01 + Math.random() * 0.01, // 衰减率减小,烟花更持久
        size: 1 + Math.random() * 3
    });
  }
  
  // 全局粒子上限从 800 增加到 2000,防止频繁闪烁消失
    if (this.particles.length > 2000) {
      this.particles = this.particles.slice(-1500);
    }
  
    this.particles = this.particles.concat(particles);
  }
  
  updateFireworks() {
    for (let i = this.fireworks.length - 1; i >= 0; i--) {
      const firework = this.fireworks[i];
      
      firework.trail.push({ x: firework.x, y: firework.y });
      if (firework.trail.length > firework.trailLength) {
        firework.trail.shift();
      }
      
      const dx = firework.targetX - firework.x;
      const dy = firework.targetY - firework.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance < 50) {
        this.createParticles(firework.x, firework.y, firework.hue);
        this.fireworks.splice(i, 1);
      } else {
        firework.angle = Math.atan2(dy, dx);
        
        firework.x += Math.cos(firework.angle) * firework.speed;
        firework.y += Math.sin(firework.angle) * firework.speed;
      }
    }
  }
  
  updateParticles() {
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const particle = this.particles[i];
      
      particle.x += Math.cos(particle.angle) * particle.speed;
      particle.y += Math.sin(particle.angle) * particle.speed + particle.gravity;
      
      particle.speed *= particle.friction;
      
      particle.alpha -= particle.decay;
      
      if (particle.alpha <= 0) {
        this.particles.splice(i, 1);
      }
    }
  }
  
  drawFireworks() {
    this.ctx.globalCompositeOperation = 'lighter';
    
    this.fireworks.forEach(firework => {
      this.ctx.beginPath();
      this.ctx.moveTo(firework.trail[0].x, firework.trail[0].y);
      
      for (let i = 1; i < firework.trail.length; i++) {
        this.ctx.lineTo(firework.trail[i].x, firework.trail[i].y);
      }
      
      this.ctx.strokeStyle = `hsl(${firework.hue}, 100%, 70%)`;
      this.ctx.lineWidth = 3;
      this.ctx.stroke();
      
      this.ctx.beginPath();
      this.ctx.moveTo(firework.trail[0].x, firework.trail[0].y);
      
      for (let i = 1; i < firework.trail.length; i++) {
        this.ctx.lineTo(firework.trail[i].x, firework.trail[i].y);
      }
      
      this.ctx.strokeStyle = `hsl(${firework.hue}, 100%, 90%)`;
      this.ctx.lineWidth = 6;
      this.ctx.globalAlpha = 0.3;
      this.ctx.stroke();
      this.ctx.globalAlpha = 1;
    });
    
    this.particles.forEach(particle => {
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
      this.ctx.fillStyle = `hsla(${particle.hue}, 100%, ${particle.brightness}%, ${particle.alpha})`;
      this.ctx.fill();
      
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, particle.size * 2, 0, Math.PI * 2);
      this.ctx.fillStyle = `hsla(${particle.hue}, 100%, ${particle.brightness}%, ${particle.alpha * 0.2})`;
      this.ctx.fill();
    });
  }
  
  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    if (Math.random() < 0.40) {
      this.createFirework();
    }
    
    if (this.fireworks.length > 20) {
      this.fireworks = this.fireworks.slice(-15);
    }
    
    this.updateFireworks();
    this.updateParticles();
    this.drawFireworks();
    
    this.animationId = requestAnimationFrame(() => this.animate());
  }
  
  destroy() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    
    this.bullets.forEach(bullet => {
      if (bullet.parentNode) {
        bullet.parentNode.removeChild(bullet);
      }
    });
    
    this.bullets = [];
    this.fireworks = [];
    this.particles = [];
  }
}

window.addEventListener('DOMContentLoaded', () => {
  new FireworksApp();
});

window.addEventListener('unload', () => {
});