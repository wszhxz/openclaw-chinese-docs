#!/usr/bin/env python3
"""
使用本地 Ollama 服务进行文档翻译的脚本
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path
import requests
import argparse
import subprocess
from typing import Optional, Tuple


def check_ollama_running():
    """检查 Ollama 服务是否正在运行"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def protect_code_blocks(text: str) -> Tuple[str, list]:
    """
    保护代码块和其他特殊内容，防止被翻译
    """
    protected_parts = []
    placeholder_prefix = "<<<PROTECTED_CONTENT_"
    placeholder_suffix = ">>>"
    
    # 保护 ``` 代码块
    parts = text.split('```')
    protected_text = ""
    for i, part in enumerate(parts):
        if i % 2 == 1:  # 代码块内容
            placeholder = f"{placeholder_prefix}{len(protected_parts)}{placeholder_suffix}"
            protected_text += placeholder
            protected_parts.append({
                'type': 'code_block',
                'original': f"```{part}```",
                'placeholder': placeholder,
                'content': part
            })
        else:
            protected_text += part
    
    # 保护 ` 行内代码
    parts = protected_text.split('`')
    protected_text = ""
    for i, part in enumerate(parts):
        if i % 2 == 1:  # 行内代码内容
            placeholder = f"{placeholder_prefix}{len(protected_parts)}{placeholder_suffix}"
            protected_text += placeholder
            protected_parts.append({
                'type': 'inline_code',
                'original': f"`{part}`",
                'placeholder': placeholder,
                'content': part
            })
        else:
            protected_text += part
    
    return protected_text, protected_parts


def restore_protected_parts(text: str, protected_parts: list) -> str:
    """
    恢复受保护的内容
    """
    restored_text = text
    for part in reversed(protected_parts):  # 逆序替换以避免位置偏移
        restored_text = restored_text.replace(part['placeholder'], part['original'])
    return restored_text


def translate_with_ollama(text: str, source_lang: str = 'English', target_lang: str = 'Chinese', 
                         model: str = 'qwen3:8b', base_url: str = 'http://localhost:11434'):
    """使用 Ollama 服务进行翻译"""
    print("🔍 开始Ollama翻译流程")
    sys.stdout.flush()
    
    try:
        print("🛡️ 正在保护代码块和其他特殊内容")
        sys.stdout.flush()
        # 保护代码块和其他特殊内容
        protected_text, protected_parts = protect_code_blocks(text)
        print(f"✅ 代码块保护完成，共有 {len(protected_parts)} 个受保护部分")
        sys.stdout.flush()
        
        headers = {
            'Content-Type': 'application/json'
        }

        print("📝 准备翻译提示词")
        sys.stdout.flush()
        # 创建翻译提示，特别指示不要翻译代码块
        prompt = f"""请将以下{source_lang}文本翻译为高质量的{target_lang}。翻译时请严格遵守以下要求：
        1. 只翻译普通文本内容，不要翻译代码块、配置项或技术术语
        2. 保留所有代码块（用```包围的内容）、行内代码（用`包围的内容）和配置项不变
        3. 保持原文的格式、结构和技术术语准确性
        4. 保持Markdown格式不变
        5. 只返回翻译后的内容，不要添加任何解释或前缀：

        {protected_text}"""

        data = {
            'model': model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.3  # 较低的温度以获得更一致的翻译
            }
        }

        print(f"📡 正在发送API请求到: {base_url}/api/generate")
        sys.stdout.flush()
        response = requests.post(f'{base_url}/api/generate', headers=headers, json=data, timeout=300)
        
        if response.status_code == 200:
            print("🔍 解析API响应")
            sys.stdout.flush()
            result = response.json()
            print(f"🔍 API响应解析完成，响应长度: {len(str(result))} 字符")
            sys.stdout.flush()
            
            translated_text = result.get('response', '').strip()
            print(f"✅ API响应解析成功，翻译文本长度: {len(translated_text)} 字符")
            sys.stdout.flush()
            
            # 恢复受保护的内容
            print("🔄 正在恢复受保护的内容")
            sys.stdout.flush()
            final_text = restore_protected_parts(translated_text, protected_parts)
            print(f"✅ 翻译完成，最终文本长度: {len(final_text)} 字符")
            sys.stdout.flush()
            return final_text
        else:
            print(f"❌ Ollama翻译失败: {response.status_code}, {response.text}")
            print(f"❌ 响应内容预览: {response.text[:500]}...")  # 显示前500个字符
            sys.stdout.flush()
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Ollama请求超时")
        sys.stdout.flush()
        return None
    except Exception as e:
        print(f"❌ Ollama翻译出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        return None


def is_text_file(file_path: Path) -> bool:
    """判断是否为文本文件"""
    text_extensions = {'.txt', '.md', '.rst', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml', '.xml', '.csv'}
    return file_path.suffix.lower() in text_extensions


def translate_file(file_path: Path, source_lang: str, target_lang: str, config: dict) -> Optional[str]:
    """翻译单个文件"""
    try:
        print(f"📖 正在读取文件内容...")
        sys.stdout.flush()
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ 文件读取完成，大小: {len(content)} 字符")
        sys.stdout.flush()
        
        # 提取 frontmatter（如果有）
        print("🔧 提取 frontmatter（如果有）")
        sys.stdout.flush()
        frontmatter = ""
        main_content = content
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = f"---\n{parts[1]}\n---\n"
                main_content = parts[2]
        
        print(f"✅ frontmatter提取完成，main_content大小: {len(main_content)} 字符")
        sys.stdout.flush()
        
        # 调用LLM进行翻译
        print("🔄 调用LLM进行翻译...")
        sys.stdout.flush()
        translated_main_content = translate_with_ollama(
            main_content, 
            source_lang, 
            target_lang, 
            config.get('ollama_model', 'qwen3:8b'), 
            config.get('ollama_base_url', 'http://localhost:11434')
        )
        
        if translated_main_content is not None:
            print(f"✅ 翻译完成，内容长度: {len(translated_main_content)} 字符")
            sys.stdout.flush()
            
            # 重新组合 frontmatter 和翻译后的内容
            print("📦 重新组合 frontmatter 和翻译后的内容")
            combined_content = frontmatter + translated_main_content
            sys.stdout.flush()
            return combined_content
        else:
            print("❌ 文件翻译失败")
            sys.stdout.flush()
            return None
            
    except Exception as e:
        print(f"❌ 翻译文件 {file_path} 时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        return None


def main():
    parser = argparse.ArgumentParser(description='使用大语言模型翻译文档')
    parser.add_argument('--source-dir', default='temp_for_translation', help='源目录 (默认: temp_for_translation)')
    parser.add_argument('--target-dir', default='docs', help='目标目录 (默认: docs)')
    parser.add_argument('--source-lang', default='English', help='源语言 (默认: English)')
    parser.add_argument('--target-lang', default='Chinese', help='目标语言 (默认: Chinese)')
    parser.add_argument('--ollama-model', default='qwen3:8b', help='Ollama 模型名称 (默认: qwen3:8b)')
    parser.add_argument('--ollama-url', default='http://localhost:11434', help='Ollama 服务URL (默认: http://localhost:11434)')
    parser.add_argument('--max-retries', type=int, default=2, help='最大重试次数 (默认: 2)')
    
    args = parser.parse_args()
    
    print("开始LLM翻译进程...")
    print(f"源目录: {args.source_dir}")
    print(f"目标目录: {args.target_dir}")
    print(f"源语言: {args.source_lang}")
    print(f"目标语言: {args.target_lang}")
    print(f"LLM提供商: ollama")
    
    # 检查 Ollama 是否正在运行
    if not check_ollama_running():
        print("❌ Ollama 服务未运行，请先启动 Ollama")
        sys.exit(1)
    
    src_path = Path(args.source_dir)
    dest_path = Path(args.target_dir)
    
    if not src_path.exists():
        print(f"❌ 源目录不存在: {src_path}")
        sys.exit(1)
    
    # 检查是否包含 docs 子目录
    docs_subdir = src_path / 'docs'
    if docs_subdir.exists() and docs_subdir.is_dir():
        print(f"检测到 docs 子目录，将在 {docs_subdir} 中搜索文件...")
        search_path = docs_subdir
    else:
        search_path = src_path
    
    # 收集所有待处理的文件
    all_files = []
    for item in search_path.rglob('*'):
        if item.is_file():
            all_files.append(item)
    
    print(f"🚀 开始处理 {len(all_files)} 个文件...")
    sys.stdout.flush()
    
    # 配置
    config = {
        'provider': 'ollama',
        'ollama_model': args.ollama_model,
        'ollama_base_url': args.ollama_url,
    }
    
    # 统计信息
    stats = {
        'processed': 0,
        'translated': 0,
        'copied': 0,
        'failed': 0
    }
    
    # 失败的文件列表
    failed_files = []
    
    # 处理所有文件
    print("::group::Processing all files")
    processed_count = 0
    for item in all_files:
        processed_count += 1
        # 计算相对路径
        # 如果源文件来自 docs 子目录，需要相应调整相对路径计算
        docs_subdir = src_path / 'docs'
        if docs_subdir.exists() and docs_subdir.is_dir() and str(item).startswith(str(docs_subdir)):
            rel_path = item.relative_to(docs_subdir)
        else:
            rel_path = item.relative_to(src_path)
        
        dest_item = dest_path / rel_path
        
        # 确保目标目录存在
        dest_item.parent.mkdir(parents=True, exist_ok=True)
        
        if is_text_file(item):
            # 需要翻译的文件
            msg = f"[{processed_count}/{len(all_files)}] 正在翻译: {rel_path}"
            print(msg)
            print(f"::group::{msg}")  # GitHub Actions 分组开始
            # 强制刷新输出缓冲区
            sys.stdout.flush()
            translated_content = translate_file(item, args.source_lang, args.target_lang, config)
            if translated_content is not None:
                print(f"📝 准备写入翻译后的内容，大小: {len(translated_content)} 字符")
                sys.stdout.flush()
                try:
                    with open(dest_item, 'w', encoding='utf-8') as f:
                        f.write(translated_content)
                    print(f"✅ [{processed_count}/{len(all_files)}] 已翻译并保存: {rel_path}")
                    sys.stdout.flush()
                    # 验证文件是否真的被写入
                    if dest_item.exists():
                        written_size = dest_item.stat().st_size
                        print(f"📊 验证文件: {rel_path} 已创建，大小: {written_size} 字节")
                        sys.stdout.flush()
                    else:
                        print(f"⚠️ 警告: {rel_path} 文件似乎未创建")
                        sys.stdout.flush()
                except Exception as e:
                    print(f"❌ 写入文件 {rel_path} 时出错: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    sys.stdout.flush()
                stats['translated'] += 1
                
                # 标记此文件待删除
                try:
                    os.remove(item)
                    msg = f"🗑️ [{processed_count}/{len(all_files)}] 已删除原始文件: {rel_path}"
                    print(msg)
                except OSError as e:
                    msg = f"⚠️ 删除原始文件 {rel_path} 时出错: {e}"
                    print(msg)
            else:
                # 翻译失败，加入失败列表
                failed_files.append({
                    'src': str(item),
                    'dest': str(dest_item),
                    'attempts': 1
                })
                stats['failed'] += 1
                msg = f"❌ [{processed_count}/{len(all_files)}] 翻译失败，加入重试队列: {rel_path}"
                print(msg)
            print("::endgroup::")  # GitHub Actions 分组结束
            # 再次强制刷新输出缓冲区
            sys.stdout.flush()
        else:
            # 不需要翻译的文件，直接复制
            msg = f"::group::Copying {rel_path}"  # GitHub Actions 分组开始
            print(msg)
            # 强制刷新输出缓冲区
            sys.stdout.flush()
            shutil.copy2(item, dest_item)
            msg = f"📋 [{processed_count}/{len(all_files)}] 已复制非文本文件: {rel_path}"
            print(msg)
            stats['copied'] += 1
            
            # 标记此文件待删除
            try:
                os.remove(item)
                msg = f"🗑️ [{processed_count}/{len(all_files)}] 已删除原始文件: {rel_path}"
                print(msg)
            except OSError as e:
                msg = f"⚠️ 删除原始文件 {rel_path} 时出错: {e}"
                print(msg)
    
    # 重试失败的文件
    retry_count = 0
    while failed_files and retry_count < args.max_retries:
        retry_count += 1
        print(f"第 {retry_count} 次重试 {len(failed_files)} 个失败的文件...")
        
        still_failed = []
        for idx, file_info in enumerate(failed_files):
            item = Path(file_info['src'])
            dest_item = Path(file_info['dest'])
            
            # 获取相对路径用于显示
            rel_path = Path(file_info['src']).relative_to(Path(args.source_dir))
            
            # 确保目标目录存在
            dest_item.parent.mkdir(parents=True, exist_ok=True)
            
            # 重新尝试翻译
            msg = f"::group::Retrying {rel_path}"
            print(msg)
            # 强制刷新输出缓冲区
            sys.stdout.flush()
            msg = f"[重试 {idx+1}/{len(failed_files)}] 正在重试: {rel_path}"
            print(msg)
            # 强制刷新输出缓冲区
            sys.stdout.flush()
            translated_content = translate_file(item, args.source_lang, args.target_lang, config)
            if translated_content is not None:
                print(f"📝 准备写入重试后的翻译内容，大小: {len(translated_content)} 字符")
                sys.stdout.flush()
                try:
                    with open(dest_item, 'w', encoding='utf-8') as f:
                        f.write(translated_content)
                    msg = f"✅ [重试 {idx+1}/{len(failed_files)}] 重试成功，已翻译并保存: {rel_path}"
                    print(msg)
                    sys.stdout.flush()
                    # 验证文件是否真的被写入
                    if dest_item.exists():
                        written_size = dest_item.stat().st_size
                        print(f"📊 验证文件: {rel_path} 已创建，大小: {written_size} 字节")
                        sys.stdout.flush()
                    else:
                        print(f"⚠️ 警告: {rel_path} 文件似乎未创建")
                        sys.stdout.flush()
                except Exception as e:
                    print(f"❌ 写入文件 {rel_path} 时出错: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    sys.stdout.flush()
                stats['translated'] += 1
                
                # 标记此文件待删除
                try:
                    os.remove(item)
                    msg = f"🗑️ [重试] 已删除原始文件: {rel_path}"
                    print(msg)
                except OSError as e:
                    msg = f"⚠️ [重试] 删除原始文件 {rel_path} 时出错: {e}"
                    print(msg)
            else:
                # 仍然失败，加入下次重试列表
                file_info['attempts'] += 1
                still_failed.append(file_info)
                stats['failed'] += 1
                msg = f"❌ [重试 {idx+1}/{len(failed_files)}] 重试失败: {rel_path}"
                print(msg)
        
        failed_files = still_failed
    
    print("::endgroup::")  # GitHub Actions 分组结束
    
    # 输出统计信息
    print("\n📊 翻译完成统计:")
    print(f"  总处理文件: {sum(stats.values())}")
    print(f"  成功翻译: {stats['translated']}")
    print(f"  复制文件: {stats['copied']}")
    print(f"  翻译失败: {stats['failed']}")
    
    if stats['failed'] > 0:
        print(f"⚠️  有 {stats['failed']} 个文件翻译失败")
    
    print("✅ 全部处理完成")


if __name__ == "__main__":
    main()