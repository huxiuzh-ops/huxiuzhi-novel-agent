const fs = require('fs');
let content = fs.readFileSync('novel/chapters/ch002.md', 'utf8');

// Find and remove the problematic line
const searchStr = '"合法的。"声音说，"而且我提前告知您了。您要是不满意，可以不赊。"';
const idx = content.indexOf(searchStr);
if (idx > -1) {
  console.log('Found at', idx);
  // Remove it and surrounding whitespace
  const before = content.substring(0, idx);
  const after = content.substring(idx + searchStr.length);
  // Clean up extra newlines
  content = before.trim() + '\n\n' + after.trim();
}

fs.writeFileSync('novel/chapters/ch002.md', content, 'utf8');
console.log('Done');
