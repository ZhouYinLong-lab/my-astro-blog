let nlist = document.querySelector(".list")

// 这里填入你想抽取的内容
let names = [
    '雪莉','妮塔','柯尔特','公牛','杰西','布洛克',
    '爆破麦克','阿渤','迪克','8比特','艾魅','斯图',
    '艾尔·普利莫','波克','巴利','罗莎','瑞科',
    '达里尔','潘妮','卡尔','雅琪','格斯','佩佩',
    '帕姆','弗兰肯','比比','贝亚','纳妮','艾德加',
    '格里夫','格罗姆','邦妮','汉克','拉里与劳里',
    '安吉洛','拜瑞','谢德','谜宝','桩','莫提斯',
    '塔拉','吉恩','麦克斯','P先生','芽芽','拜伦',
    '史魁克','戈雷','薇洛','道格','查克','米科',
    '麦乐迪','莉莉','克兰西','阿萌','珠珠','奥利',
    '露米','芬克斯','载勇','鳄梨','斯派克','黑鸦',
    '里昂','沙迪','琥珀','梅格','切斯特','凯特','德拉科',
    '健次','格尔','瑟奇','科莱特','小罗','拉夫上校',
    '贝尔','巴兹','阿拾','萝拉','阿方','伊芙','珍妮特',
    '奥蒂斯','山姆','巴斯特','曼迪','阿尔缇','麦茜',
    '科迪琉斯','珀尔','查莉'
]

// 生成扇形元素
for (var i in names) {
    let span = document.createElement("span")
    span.innerText = names[i]
    nlist.appendChild(span)
    
    // 初始化位置
    span.style.transform = "rotate(" + (i / names.length * 360) + "deg)"
}

let spans = nlist.children
let deg = 0
let slow = 0
let run = false

// 1. 键盘控制 (适配电脑键盘空格键)
document.addEventListener("keyup", function (evt) {
    if (evt.key == " ") {
        run = !run
    }
})

// 2. 【新增】点击控制 (适配手机触摸和电脑鼠标点击)
// 这样在手机上点击屏幕任何位置都能开始/停止
document.addEventListener("click", function () {
    run = !run
})

function draw() {
    // 旋转整个容器
    nlist.style.transform = `rotate(${deg}deg)`

    let total = names.length
    let singleAngle = 360 / total
    
    // 计算当前指向
    let normalizeDeg = (360 - (deg % 360)) % 360
    let index = Math.round(normalizeDeg / singleAngle)
    
    // 修正索引
    index = index % total
    if(index < 0) index += total

    // 清除高亮
    for(let s of spans){
        s.classList.remove('active')
    }

    // 添加高亮
    if(spans[index]){
        spans[index].classList.add('active')
    }

    // 速度控制
    if (run) {
        if(slow < 15) slow += 0.1
    } else {
        slow = slow * 0.98
        if(slow < 0.05) slow = 0
    }
    
    deg += slow
    
    requestAnimationFrame(draw)
}

requestAnimationFrame(draw)