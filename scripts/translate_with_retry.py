#!/usr/bin/env python3
"""
使用 LibreTranslate API 进行文档翻译的脚本，带重试机制
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
import json

def is_text_file(filepath):
    """判断文件是否为需要翻译的文本文件"""
    text_extensions = {'.md', '.mdx', '.txt', '.html', '.htm'}
    return filepath.suffix.lower() in text_extensions

def is_translatable_content(content):
    """检查文件内容是否包含可翻译的文本（英文字符或中文字符）"""
    # 检查是否包含英文字符（字母）或中文字符，以确定是否为可翻译的文本内容
    text_pattern = re.compile(r'[\u4e00-\u9fff]|[a-zA-Z]')
    return bool(text_pattern.search(content))

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
        
        # 对所有文本文件都尝试翻译
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

def process_directory_with_retry(src_dir, dest_dir, source_lang='en', target_lang='zh', api_url='http://localhost:5000', max_retries=3):
    """处理整个目录，带重试机制"""
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)
    
    # 确保目标目录存在
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # 找出所有需要处理的文件
    all_files = []
    for item in src_path.rglob('*'):
        if item.is_file():
            all_files.append(item)
    
    # 统计信息
    stats = {
        'total': len(all_files),
        'translated': 0,
        'copied': 0,
        'failed': 0
    }
    
    # 需要重试的文件列表
    failed_files = []
    
    print(f"开始处理 {len(all_files)} 个文件...")
    
    # 第一轮：尝试翻译所有文件
    for item in all_files:
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
                # 翻译失败，加入失败列表
                failed_files.append({
                    'src': str(item),
                    'dest': str(dest_item),
                    'attempts': 1
                })
                stats['failed'] += 1
                print(f"翻译失败，加入重试队列: {item}")
        else:
            # 不需要翻译的文件，直接复制
            shutil.copy2(item, dest_item)
            print(f"已复制非文本文件: {dest_item}")
            stats['copied'] += 1
    
    # 重试失败的文件
    retry_count = 0
    while failed_files and retry_count < max_retries:
        retry_count += 1
        print(f"第 {retry_count} 次重试 {len(failed_files)} 个失败的文件...")
        
        still_failed = []
        for file_info in failed_files:
            item = Path(file_info['src'])
            dest_item = Path(file_info['dest'])
            
            # 确保目标目录存在
            dest_item.parent.mkdir(parents=True, exist_ok=True)
            
            # 重新尝试翻译
            translated_content = translate_file(item, source_lang, target_lang, api_url)
            if translated_content is not None:
                with open(dest_item, 'w', encoding='utf-8') as f:
                    f.write(translated_content)
                print(f"重试成功，已翻译并保存: {dest_item}")
                stats['translated'] += 1
                stats['failed'] -= 1
            else:
                # 重试失败，增加尝试次数
                file_info['attempts'] += 1
                if file_info['attempts'] <= max_retries:
                    still_failed.append(file_info)
                else:
                    print(f"重试超过 {max_retries} 次，放弃翻译: {item}")
        
        failed_files = still_failed
    
    # 输出未完成翻译的文件列表
    if failed_files:
        print("\n=== 翻译失败的文件列表 ===")
        failed_paths = []
        for file_info in failed_files:
            src_path = Path(file_info['src'])
            rel_path = src_path.relative_to(src_path.parent.parent)  # 相对于源目录
            failed_paths.append(str(rel_path))  # 完整相对路径
        
        # 按完整路径排序并输出
        for file_path in sorted(failed_paths):
            print(f"  - {file_path}")
        
        # 按目录结构组织以便输出
        failed_by_dir = {}
        for file_path in failed_paths:
            path_obj = Path(file_path)
            dir_path = str(path_obj.parent)
            if dir_path not in failed_by_dir:
                failed_by_dir[dir_path] = []
            failed_by_dir[dir_path].append(path_obj.name)
        
        # 将失败文件列表写入文件（包含完整路径）
        with open('/tmp/failed_translation_files.json', 'w', encoding='utf-8') as f:
            json.dump(failed_paths, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细失败列表已保存到 /tmp/failed_translation_files.json")
    
    return stats, failed_files

def main():
    parser = argparse.ArgumentParser(description='使用 LibreTranslate API 翻译文档，带重试机制')
    parser.add_argument('--source-dir', default='temp_for_translation', 
                       help='源目录 (默认: temp_for_translation)')
    parser.add_argument('--target-dir', default='docs', 
                       help='目标目录 (默认: docs)')
    parser.add_argument('--source-lang', default='en', 
                       help='源语言 (默认: en)')
    parser.add_argument('--target-lang', default='zh', 
                       help='目标语言 (默认: zh)')
    parser.add_argument('--api-url', default='https://libretranslate.de', 
                       help='LibreTranslate API 地址 (默认: https://libretranslate.de)')
    parser.add_argument('--max-retries', type=int, default=3, 
                       help='最大重试次数 (默认: 3)')
    
    args = parser.parse_args()
    
    print(f"开始翻译进程...")
    print(f"源目录: {args.source_dir}")
    print(f"目标目录: {args.target_dir}")
    print(f"源语言: {args.source_lang}")
    print(f"目标语言: {args.target_lang}")
    print(f"API地址: {args.api_url}")
    print(f"最大重试次数: {args.max_retries}")
    
    # 检查源目录是否存在
    if not os.path.exists(args.source_dir):
        print(f"错误: 源目录 {args.source_dir} 不存在")
        sys.exit(1)
    
    # 处理目录
    stats, failed_files = process_directory_with_retry(
        args.source_dir, 
        args.target_dir, 
        args.source_lang, 
        args.target_lang, 
        args.api_url,
        args.max_retries
    )
    
    print(f"\n翻译完成!")
    print(f"总计处理文件: {stats['total']}")
    print(f"成功翻译: {stats['translated']}")
    print(f"直接复制: {stats['copied']}")
    print(f"翻译失败: {stats['failed']}")
    
    if failed_files:
        print(f"以下 {len(failed_files)} 个文件未能完成翻译，已记录到 /tmp/failed_translation_files.json")

if __name__ == '__main__':
    main()