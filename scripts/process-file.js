const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

// 加载术语表
const terminology = require("../terminology.json");

// 从命令行参数获取文件路径
const filePath = process.argv[2];
const outputPath = process.argv[3]; // 添加输出路径参数

if (!filePath || !outputPath) {
  console.error("Usage: node process-file.js <inputFilePath> <outputFilePath>");
  process.exit(1);
}

// 读取原始文档内容
const content = fs.readFileSync(filePath, "utf8");

/**
 * 从Markdown内容中提取frontmatter
 */
function extractFrontMatter(content) {
  const frontMatterRegex = /^---
([\s\S]*?)
---
/;
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
  if (!text || typeof text !== "string") {
    return text;
  }
  
  // 使用术语表进行翻译，注意使用正确的术语表结构
  let translated = text;
  
  // 按长度排序术语，避免短词替换长词的情况
  const sortedTerms = Object.entries(terminology.technical_terms)
    .sort((a, b) => b[0].length - a[0].length);
  
  for (const [englishTerm, chineseTerm] of sortedTerms) {
    // 使用正则表达式替换，区分大小写，替换整个单词
    const regex = new RegExp(`\b${escapeRegExp(englishTerm)}\b`, "gi");
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
  return string.replace(/[.*+?^${}()|[\\]/g, "\$&");
}

/**
 * 重新构建带有frontmatter的文档
 */
function rebuildDocument(frontMatter, body) {
  let result = "";
  
  if (frontMatter) {
    result += "---
";
    result += yaml.dump(frontMatter);
    result += "---

";
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
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  // 写入翻译后的文件
  fs.writeFileSync(outputPath, finalContent, "utf8");
  console.log("Successfully translated: " + filePath + " -> " + outputPath);
} catch (error) {
  console.error("Error translating " + filePath + ":", error.message);
  // 即使出错也复制原文件，避免缺失
  fs.copyFileSync(filePath, outputPath);
}
