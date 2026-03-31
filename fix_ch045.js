const fs = require('fs');

const path = 'C:\\Users\\Administrator\\.openclaw\\workspace\\novel\\chapters\\ch045.md';
let content = fs.readFileSync(path, 'utf8');

const oldText = `培养舱——碎了。

玻璃——飞溅。

小女孩——站在——碎片——之中。

她的——眼睛——还是——金色——的。

她的——身上——插着的——管子——都——被——震碎了。

她的——皮肤——在——发光。

是——金色——的——光。

"这是——！"研究员——惊恐地——叫了——起来。

"这是——新生——的——力量——觉醒了——！"

铁蝎——的——眼睛——眯了起来。

他没有——害怕。

他——只有——兴奋。

"有意思。"他——说。

"这小丫头——的力量——比——我——想象的——还要——强。"

"看来——我的——研究——是对的。"

他的——眼睛——闪烁着——贪婪的——光芒。

"给我——抓住——她。"`;

const newText = `培养舱——的——玻璃——碎了。

那些——金色的——细胞——悬浮——在——空中——

闪烁着——奇异的——光芒。

"这是——！"研究员——惊恐地——叫了——起来。

"新生——的——力量——在——共振——！"

"她的——本体——一定——也——感应到了——！"

铁蝎——的——眼睛——眯了起来。

他没有——害怕。

他——只有——兴奋。

"有意思。"他——说。

"从——细胞——样本——就能——看出——这小丫头的——力量——比——我——想象的——还要——强。"

"如果——我——能得到——她——本人——"

他的——眼睛——闪烁着——贪婪的——光芒。

"继续——追。"他的——声音——很——冷。

"不惜——任何——代价。"

"我——要——得到——她。"`;

if (content.includes(oldText)) {
    console.log('Found! Replacing...');
    content = content.replace(oldText, newText);
    fs.writeFileSync(path, content, 'utf8');
    console.log('Done');
} else {
    console.log('Not found');
    const idx = content.indexOf('培养舱——碎了');
    if (idx >= 0) {
        console.log('Found partial at:', idx);
        console.log('Context:', JSON.stringify(content.substring(idx, idx+500)));
    }
}
