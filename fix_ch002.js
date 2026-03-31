const fs = require('fs');
let content = fs.readFileSync('novel/chapters/ch002.md', 'utf8');

// Fix line 181
content = content.replace(
  '"赊账。"声音说，"20剧情点上限，没有利息，简单明了，但至少能让您先活着。"',
  '"赊账。"声音说，"20剧情点上限，没有利息。简单明了，但至少能让您先活着。"'
);

// Fix the calculation dialogue
content = content.replace(
  '"没有利息。"声音说，"您赊20点，明天这个时候就是22点，后天是24.2点。以此类推。',
  '"没有利息。"声音说，"您赊多少，就还多少。"'
);

// Fix status display
content = content.replace(
  '剧情点：-20\n利息：10%/天',
  '剧情点：-20'
);

// Fix the dialogue about repaying
content = content.replace(
  '"系统。"他忽然问，"如果我提前还债呢？利息还收吗？"',
  '"系统。"他忽然问，"如果我提前还债呢？"'
);

// Fix the response about interest
content = content.replace(
  '"收。"声音说，"但您可以协商。如果您完成任务拿到120点奖励，扣掉20点债务，理论上您能剩一些。"\n\n"能剩多少？"\n\n"看您活得多久。"声音说，"活得越久，能攒下的越多。"',
  '"可以。"声音说，"如果您完成任务拿到120点奖励，扣掉20点债务，理论上您能剩一些。"'
);

fs.writeFileSync('novel/chapters/ch002.md', content, 'utf8');
console.log('Fixed');
