const fs = require('fs').promises;
const path = require('path');
const yaml = require('js-yaml');

// 加载术语表
const terminology = require('../terminology.json');

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
  
  let translated = text;
  
  // 按长度排序术语，避免短词替换长词的情况
  const sortedTerms = Object.entries(terminology.technical_terms)
    .sort((a, b) => b[0].length - a[0].length);
  
  for (const [englishTerm, chineseTerm] of sortedTerms) {
    // 使用正则表达式替换，区分大小写，替换整个单词
    const regex = new RegExp(`\\b${escapeRegExp(englishTerm)}\\b`, 'gi');
    translated = translated.replace(regex, (match) => {
      // 保持原始大小写格式
      if (match === match.toUpperCase()) {
        return chineseTerm.toUpperCase();
      } else if (match === match.toLowerCase()) {
        return chineseTerm.toLowerCase();
      } else if (match[0] === match[0].toUpperCase()) {
        return chineseTerm.charAt(0).toUpperCase() + chineseTerm.slice(1).toLowerCase();
      }
      return chineseTerm;
    });
  }
  
  return translated;
}

/**
 * 转义正则表达式特殊字符
 */
function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * 翻译Markdown内容
 */
async function translateMarkdownContent(content) {
  // 提取frontmatter
  const { frontMatter, body } = extractFrontMatter(content);
  
  // 翻译frontmatter
  const translatedFrontMatter = translateFrontMatter(frontMatter);
  
  // 分割内容为行以便处理
  const lines = body.split('\n');
  const translatedLines = [];
  
  let inCodeBlock = false;
  let codeBlockLang = '';
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    
    // 检查是否进入或离开代码块
    if (line.trim().startsWith('```')) {
      inCodeBlock = !inCodeBlock;
      if (inCodeBlock) {
        codeBlockLang = line.trim().substring(3);
      } else {
        codeBlockLang = '';
      }
      translatedLines.push(line);
      continue;
    }
    
    // 如果在代码块内，不翻译
    if (inCodeBlock) {
      translatedLines.push(line);
      continue;
    }
    
    // 检查是否在JSON/YAML代码块中
    if (line.trim().startsWith('{') || line.trim().startsWith('}') ||
        line.trim().startsWith('- ') || line.trim().startsWith('  ') ||
        line.includes(': ') && !line.includes('http')) {
      // 这可能是配置块，暂时不翻译
      translatedLines.push(line);
      continue;
    }
    
    // 翻译普通文本行
    const translatedLine = translateText(line);
    translatedLines.push(translatedLine);
  }
  
  // 重建内容
  let translatedBody = translatedLines.join('\n');
  
  // 重新组合frontmatter和body
  if (translatedFrontMatter) {
    const fmString = '---\n' + yaml.dump(translatedFrontMatter) + '---\n';
    translatedBody = fmString + translatedBody;
  }
  
  return translatedBody;
}

/**
 * 处理单个文件
 */
async function processFile(srcPath, destPath) {
  try {
    console.log(`Processing: ${srcPath}`);
    
    const content = await fs.readFile(srcPath, 'utf8');
    const translatedContent = await translateMarkdownContent(content);
    
    // 确保目标目录存在
    const destDir = path.dirname(destPath);
    await fs.mkdir(destDir, { recursive: true });
    
    await fs.writeFile(destPath, translatedContent, 'utf8');
    console.log(`✓ Translated: ${srcPath} -> ${destPath}`);
  } catch (error) {
    console.error(`✗ Error processing ${srcPath}:`, error.message);
  }
}

/**
 * 递归处理目录
 */
async function processDirectory(srcDir, destDir, excludeList = []) {
  const items = await fs.readdir(srcDir, { withFileTypes: true });
  
  for (const item of items) {
    const srcPath = path.join(srcDir, item.name);
    const destPath = path.join(destDir, item.name);
    
    // 检查是否在排除列表中
    const relativePath = path.relative(srcDir, srcPath);
    if (excludeList.some(pattern => relativePath.includes(pattern))) {
      console.log(`Skipping excluded path: ${srcPath}`);
      continue;
    }
    
    if (item.isDirectory()) {
      await processDirectory(srcPath, destPath, excludeList);
    } else if (item.isFile() && (item.name.endsWith('.md') || item.name.endsWith('.markdown'))) {
      await processFile(srcPath, destPath);
    }
  }
}

/**
 * 主函数
 */
async function main() {
  console.log('Starting OpenClaw documentation translation process...');
  
  // 获取命令行参数
  const args = process.argv.slice(2);
  const srcDir = args[0] || './docs';  // 默认源目录
  const destDir = args[1] || './docs_zh';  // 默认目标目录
  
  console.log(`Source directory: ${srcDir}`);
  console.log(`Destination directory: ${destDir}`);
  
  // 定义排除列表
  const excludeList = [
    '.git',
    'node_modules',
    '.github',
    '_site',
    '.jekyll-cache'
  ];
  
  try {
    // 创建目标目录
    await fs.mkdir(destDir, { recursive: true });
    
    // 处理目录
    await processDirectory(srcDir, destDir, excludeList);
    
    console.log('Translation process completed successfully!');
  } catch (error) {
    console.error('Translation process failed:', error);
    process.exit(1);
  }
}

// 如果直接运行此脚本，则执行主函数
if (require.main === module) {
  main().catch(error => {
    console.error(error);
    process.exit(1);
  });
}

module.exports = {
  translateMarkdownContent,
  translateText,
  processFile,
  processDirectory
};