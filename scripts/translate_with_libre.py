#!/usr/bin/env python3
"""
使用 LibreTranslate API 进行文档翻译的脚本
LibreTranslate 是一个开源的翻译 API，可以自托管
"""

import os
import sys
import shutil
import requests
import argparse
from pathlib import Path
import time
import re

def is_text_file(filepath):
    """判断文件是否为需要翻译的文本文件"""
    text_extensions = {'.md', '.mdx', '.txt', '.html', '.htm'}
    return filepath.suffix.lower() in text_extensions

def is_translatable_content(content):
    """检查文件内容是否包含需要翻译的文本（中文字符）"""
    # 检查是否包含中文字符
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(chinese_pattern.search(content))

def extract_frontmatter(content):
    """提取并返回 YAML frontmatter（如果有）"""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[1].strip(), parts[2]
    return None, content

def translate_text(text, source_lang='en', target_lang='zh', api_url='http://localhost:5000'):
    """使用 LibreTranslate API 翻译文本"""
    try:
        # 分割长文本，避免超出API限制
        max_chunk_size = 5000  # 字符
        if len(text) <= max_chunk_size:
            chunks = [text]
        else:
            # 按段落分割
            paragraphs = text.split('\n\n')
            chunks = []
            current_chunk = ""
            for para in paragraphs:
                if len(current_chunk + para) <= max_chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para + "\n\n"
            if current_chunk:
                chunks.append(current_chunk.strip())
        
        translated_chunks = []
        for chunk in chunks:
            if chunk.strip():
                # 发送翻译请求
                response = requests.post(
                    f"{api_url}/translate",
                    json={
                        'q': chunk,
                        'source': source_lang,
                        'target': target_lang,
                        'format': 'text'  # text, html
                    },
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    translated_chunks.append(result['translatedText'])
                else:
                    print(f"翻译失败: {response.status_code}, {response.text}")
                    return None
                
                # 避免请求过于频繁
                time.sleep(0.1)
        
        return '\n\n'.join(translated_chunks)
    except Exception as e:
        print(f"翻译过程中出现错误: {str(e)}")
        return None

def translate_file(filepath, source_lang='en', target_lang='zh', api_url='http://localhost:5000'):
    """翻译单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取 frontmatter（如果有）
        frontmatter, main_content = extract_frontmatter(content)
        
        # 检查内容是否需要翻译
        if not is_translatable_content(main_content):
            print(f"文件 {filepath} 似乎不包含中文内容，跳过翻译")
            return content  # 返回原内容
        
        print(f"正在翻译文件: {filepath}")
        translated_content = translate_text(main_content, source_lang, target_lang, api_url)
        
        if translated_content is None:
            print(f"翻译失败: {filepath}")
            return None
        
        # 重新组合 frontmatter 和翻译后的内容
        if frontmatter:
            translated_content = f"---\n{frontmatter}\n---\n{translated_content}"
        
        return translated_content
    except Exception as e:
        print(f"处理文件 {filepath} 时出现错误: {str(e)}")
        return None

def process_directory(src_dir, dest_dir, source_lang='en', target_lang='zh', api_url='http://localhost:5000'):
    """处理整个目录，翻译需要翻译的文件，复制不需要翻译的文件"""
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)
    
    # 确保目标目录存在
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # 统计信息
    stats = {
        'total': 0,
        'translated': 0,
        'copied': 0,
        'failed': 0
    }
    
    for item in src_path.rglob('*'):
        if item.is_file():
            stats['total'] += 1
            
            # 计算相对路径
            rel_path = item.relative_to(src_path)
            dest_item = dest_path / rel_path
            
            # 确保目标目录存在
            dest_item.parent.mkdir(parents=True, exist_ok=True)
            
            if is_text_file(item):
                # 需要翻译的文件
                translated_content = translate_file(item, source_lang, target_lang, api_url)
                if translated_content is not None:
                    with open(dest_item, 'w', encoding='utf-8') as f:
                        f.write(translated_content)
                    print(f"已翻译并保存: {dest_item}")
                    stats['translated'] += 1
                else:
                    # 翻译失败，复制原文件
                    shutil.copy2(item, dest_item)
                    print(f"翻译失败，已复制原文件: {dest_item}")
                    stats['failed'] += 1
            else:
                # 不需要翻译的文件，直接复制
                shutil.copy2(item, dest_item)
                print(f"已复制非文本文件: {dest_item}")
                stats['copied'] += 1
    
    return stats

def main():
    parser = argparse.ArgumentParser(description='使用 LibreTranslate API 翻译文档')
    parser.add_argument('--source-dir', default='temp_for_translation', 
                       help='源目录 (默认: temp_for_translation)')
    parser.add_argument('--target-dir', default='docs', 
                       help='目标目录 (默认: docs)')
    parser.add_argument('--source-lang', default='en', 
                       help='源语言 (默认: en)')
    parser.add_argument('--target-lang', default='zh', 
                       help='目标语言 (默认: zh)')
    parser.add_argument('--api-url', default='http://localhost:5000', 
                       help='LibreTranslate API 地址 (默认: http://localhost:5000)')
    
    args = parser.parse_args()
    
    print(f"开始翻译进程...")
    print(f"源目录: {args.source_dir}")
    print(f"目标目录: {args.target_dir}")
    print(f"源语言: {args.source_lang}")
    print(f"目标语言: {args.target_lang}")
    print(f"API地址: {args.api_url}")
    
    # 检查源目录是否存在
    if not os.path.exists(args.source_dir):
        print(f"错误: 源目录 {args.source_dir} 不存在")
        sys.exit(1)
    
    # 处理目录
    stats = process_directory(
        args.source_dir, 
        args.target_dir, 
        args.source_lang, 
        args.target_lang, 
        args.api_url
    )
    
    print(f"\n翻译完成!")
    print(f"总计处理文件: {stats['total']}")
    print(f"成功翻译: {stats['translated']}")
    print(f"直接复制: {stats['copied']}")
    print(f"翻译失败: {stats['failed']}")

if __name__ == '__main__':
    main()