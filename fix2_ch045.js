const fs = require('fs');

const path = 'C:\\Users\\Administrator\\.openclaw\\workspace\\novel\\chapters\\ch045.md';
let content = fs.readFileSync(path, 'utf8');

const oldText = `那个——房间——里——有——另一个——培养舱。

但——这个——培养舱——里——的——不是——罪犯。

是——一个——小女孩。

大概——四五岁——的——样子。

她——在——哭。

在——无声地——哭。

她的——眼睛——被——蒙着。

她的——手脚——被——绑着。

她——的——身上——插满了——管子。

连接着——各种——仪器。`;

const newText = `那个——房间——里——有——另一个——培养舱。

但——这个——培养舱——里——的——不是——罪犯。

是——新生——的——细胞——样本。

那些——细胞——在——培养液里——悬浮。

散发着——淡淡——的——金色——光芒。`;

if (content.includes(oldText)) {
    console.log('Found! Replacing...');
    content = content.replace(oldText, newText);
    fs.writeFileSync(path, content, 'utf8');
    console.log('Done');
} else {
    console.log('Not found');
    const idx = content.indexOf('一个——小女孩');
    if (idx >= 0) {
        console.log('Found partial at:', idx);
        console.log('Context:', JSON.stringify(content.substring(Math.max(0, idx-200), idx+200)));
    }
}
