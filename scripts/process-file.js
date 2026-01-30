const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

// 加载术语表
const terminology = require('../terminology.json');

// 从命令行参数获取文件路径
const filePath = process.argv[2];

if (!filePath) {
  console.error('Usage: node process-file.js <filePath>');
  process.exit(1);
}

// 读取原始文档内容
const content = fs.readFileSync(filePath, 'utf8');

/**
 * 从Markdown内容中提取frontmatter
 */
function extractFrontMatter(content) {
  const frontMatterRegex = /^---\n([\s\S]*?)\n---\n/;
  const match = content.match(frontMatterRegex);
  
  if (match) {
    const frontMatter = yaml.load(match[1]);
    const body = content.slice(match[0].length);
    return { frontMatter, body };
  }
  
  return { frontMatter: null, body: content };
}

/**
 * 翻译frontmatter中的特定字段
 */
function translateFrontMatter(frontMatter) {
  if (!frontMatter) return null;
  
  const translatedFM = { ...frontMatter };
  
  // 翻译summary字段
  if (translatedFM.summary) {
    translatedFM.summary = translateText(translatedFM.summary);
  }
  
  // 翻译read_when字段
  if (translatedFM.read_when && Array.isArray(translatedFM.read_when)) {
    translatedFM.read_when = translatedFM.read_when.map(item => translateText(item));
  }
  
  return translatedFM;
}

/**
 * 基于术语表翻译文本
 */
function translateText(text) {
  if (!text || typeof text !== 'string') {
    return text;
  }
  
  // 使用术语表进行翻译
  let translated = text;
  for (const [english, chinese] of Object.entries(terminology)) {
    // 使用全局正则表达式替换，避免重复替换
    const regex = new RegExp(english.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
    translated = translated.replace(regex, chinese);
  }
  
  return translated;
}

/**
 * 重新构建带有frontmatter的文档
 */
function rebuildDocument(frontMatter, body) {
  let result = '';
  
  if (frontMatter) {
    result += '---\n';
    result += yaml.dump(frontMatter);
    result += '---\n\n';
  }
  
  result += body;
  return result;
}

// 执行翻译过程
try {
  const { frontMatter, body } = extractFrontMatter(content);
  const translatedFrontMatter = translateFrontMatter(frontMatter);
  const translatedBody = translateText(body);
  
  const finalContent = rebuildDocument(translatedFrontMatter, translatedBody);
  
  // 确保输出目录存在
  const outputPath = path.dirname(process.argv[3]);
  if (!fs.existsSync(outputPath)) {
    fs.mkdirSync(outputPath, { recursive: true });
  }
  
  // 写入翻译后的文件
  fs.writeFileSync(process.argv[3], finalContent, 'utf8');
  console.log('Successfully translated: ' + process.argv[2]);
} catch (error) {
  console.error('Error translating ' + process.argv[2] + ':', error.message);
  // 即使出错也复制原文件，避免缺失
  fs.copyFileSync(process.argv[2], process.argv[3]);
}