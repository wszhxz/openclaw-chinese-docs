#!/usr/bin/env python3
"""
使用大语言模型进行文档翻译的脚本（简化版 - 仅 OpenRouter）
支持大文件分段翻译，保持HTML格式完整性
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
import time
import re
import json
import requests

def is_text_file(filepath):
    text_extensions = {'.md', '.mdx', '.txt', '.html', '.htm', '.yaml', '.yml'}
    return filepath.suffix.lower() in text_extensions

def extract_frontmatter(content):
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[1].strip(), parts[2]
    return None, content

def protect_html_tags(text):
    protected_parts = {}
    html_pattern = r'<([^>]+)>(.*?)</\1>|<[^>]+/>'
    matches = re.findall(html_pattern, text, re.DOTALL)
    for i, match in enumerate(matches):
        if isinstance(match, tuple) and len(match) >= 2 and match[1].strip():
            full_tag = f"<{match[0]}>{match[1]}</{match[0]}>"
        elif isinstance(match, str) and '<' in match and '>' in match:
            full_tag = match
        else:
            continue
        placeholder = f"__HTML_TAG_{i}__"
        protected_parts[placeholder] = full_tag
        text = text.replace(full_tag, placeholder, 1)
    return text, protected_parts

def protect_code_blocks(text):
    protected_parts = {}
    pattern = r'(```[\s\S]*?```|\`[^\`]*\`)'
    matches = re.findall(pattern, text)
    for i, match in enumerate(matches):
        placeholder = f"__CODE_BLOCK_{i}__"
        protected_parts[placeholder] = match
        text = text.replace(match, placeholder, 1)
    text, html_parts = protect_html_tags(text)
    protected_parts.update(html_parts)
    inline_pattern = r'`(.*?)`'
    inline_matches = re.findall(inline_pattern, text)
    for i, match in enumerate(inline_matches):
        placeholder = f"__INLINE_CODE_{i}__"
        protected_parts[placeholder] = f'`{match}`'
        text = text.replace(f'`{match}`', placeholder)
    return text, protected_parts

def restore_protected_parts(text, protected_parts):
    for placeholder, original in protected_parts.items():
        text = text.replace(placeholder, original)
    return text

def split_text(text, max_chars=100000):
    chunks = []
    paragraphs = text.split('\n\n')
    current_chunk = ""
    for paragraph in paragraphs:
        if len(current_chunk + paragraph) < max_chars:
            current_chunk += paragraph + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chars:
            sentences = re.split(r'[.!?。！？]\s+', chunk)
            temp_chunk = ""
            for sentence in sentences:
                if len(temp_chunk + sentence) < max_chars:
                    temp_chunk += sentence + ". "
                else:
                    if temp_chunk:
                        final_chunks.append(temp_chunk.strip())
                    temp_chunk = sentence + ". "
            if temp_chunk.strip():
                final_chunks.append(temp_chunk.strip())
        else:
            final_chunks.append(chunk)
    return final_chunks

def call_openrouter(text, source_lang='English', target_lang='Chinese', api_key=None, model='stepfun/step-3.5-flash:free', base_url='https://openrouter.ai/api/v1'):
    if not api_key:
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("❌ OPENROUTER_API_KEY 未设置")
            return None
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'HTTP-Referer': 'https://openclaw.ai',
        'X-Title': 'OpenClaw Translate'
    }
    
    protected_text, protected_parts = protect_code_blocks(text)
    
    prompt = f"""请将以下{source_lang}文本翻译为高质量的{target_lang}。翻译时请严格遵守以下要求：
1. 只翻译普通文本内容，不要翻译代码块、配置项或技术术语
2. 保留所有代码块（用\`\`\`包围的内容）、行内代码（用\`包围的内容）和配置项不变
3. 保持原文的格式、结构和技术术语准确性
4. 保持Markdown和HTML格式不变
5. 只返回翻译后的内容，不要添加任何解释或前缀：

{protected_text}"""

    data = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': 'You are a professional translator specializing in technical documentation. Translate the provided text accurately while preserving formatting, structure, and technical terminology. DO NOT translate code blocks, configuration options, HTML tags, or technical terms.'},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.3,
        'max_tokens': 4000
    }

    try:
        print(f"📡 发送请求到 OpenRouter: {base_url}/chat/completions")
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=180
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                translated_text = result['choices'][0]['message']['content'].strip()
                final_text = restore_protected_parts(translated_text, protected_parts)
                return final_text
            else:
                print(f"⚠️ OpenRouter 响应格式异常: {result}")
                return None
        else:
            print(f"❌ OpenRouter 翻译失败: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"❌ OpenRouter 翻译错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def translate_with_any_llm(text, source_lang='English', target_lang='Chinese', config=None):
    if config is None:
        config = {
            'api_key': os.getenv('OPENROUTER_API_KEY'),
            'model': 'stepfun/step-3.5-flash:free',
            'base_url': 'https://openrouter.ai/api/v1'
        }

    api_key = config.get('api_key')
    model = config.get('model')
    base_url = config.get('base_url')

    if not api_key:
        print("❌ OPENROUTER_API_KEY 未设置")
        return None

    print(f"📡 使用模型: {model}")
    
    if len(text) > 100000:
        print(f"📏 文本大小 ({len(text)} 字符) 超过 100K，使用分段翻译")
        chunks = split_text(text, max_chars=100000)
        print(f"✂️ 文本已分割为 {len(chunks)} 个片段")
        
        translated_chunks = []
        for i, chunk in enumerate(chunks):
            print(f"📝 翻译片段 {i+1}/{len(chunks)} (长度: {len(chunk)} 字符)")
            translated = call_openrouter(chunk, source_lang, target_lang, api_key, model, base_url)
            if translated:
                translated_chunks.append(translated)
                print(f"✅ 片段 {i+1} 翻译完成")
            else:
                print(f"❌ 片段 {i+1} 翻译失败")
                return None
            time.sleep(1)
        
        final_text = "\n\n".join(translated_chunks)
        print(f"📦 所有片段合并完成，最终文本长度: {len(final_text)} 字符")
        return final_text
    else:
        print(f"📏 文本大小 ({len(text)} 字符) 在范围内，直接翻译")
        return call_openrouter(text, source_lang, target_lang, api_key, model, base_url)

def translate_file(filepath, source_lang='English', target_lang='Chinese', config=None):
    print(f"🔍 开始处理文件: {filepath}")
    sys.stdout.flush()
    
    try:
        print(f"📖 正在读取文件内容...")
        sys.stdout.flush()
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ 文件读取完成，大小: {len(content)} 字符")
        sys.stdout.flush()

        print(f"🔧 提取 frontmatter（如果有）")
        sys.stdout.flush()
        frontmatter, main_content = extract_frontmatter(content)
        print(f"✅ frontmatter提取完成，main_content大小: {len(main_content)} 字符")
        sys.stdout.flush()

        print(f"🔄 调用LLM进行翻译...")
        sys.stdout.flush()
        translated_content = translate_with_any_llm(main_content, source_lang, target_lang, config)

        if translated_content is None:
            print(f"❌ 翻译失败: {filepath}")
            sys.stdout.flush()
            return None
        
        if not translated_content or len(translated_content.strip()) == 0:
            print(f"⚠️ 翻译返回了空内容: {filepath}")
            sys.stdout.flush()
            return None
        
        print(f"✅ 翻译完成，内容长度: {len(translated_content)} 字符")
        sys.stdout.flush()

        print(f"📦 重新组合 frontmatter 和翻译后的内容")
        sys.stdout.flush()
        if frontmatter:
            translated_content = f"---\n{frontmatter}\n---\n{translated_content}"

        print(f"✅ 文件处理完成: {filepath}")
        sys.stdout.flush()
        return translated_content
    except Exception as e:
        print(f"❌ 处理文件 {filepath} 时出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        return None

def process_directory(src_dir, dest_dir, source_lang='English', target_lang='Chinese', config=None, max_retries=2):
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)
    dest_path.mkdir(parents=True, exist_ok=True)

    all_files = []
    docs_subdir = src_path / 'docs'
    if docs_subdir.exists() and docs_subdir.is_dir():
        print(f"检测到 docs 子目录，将在 {docs_subdir} 中搜索文件...")
        for item in docs_subdir.rglob('*'):
            if item.is_file():
                all_files.append(item)
    else:
        print(f"在 {src_path} 中搜索文件...")
        for item in src_path.rglob('*'):
            if item.is_file():
                all_files.append(item)

    stats = {'total': len(all_files), 'translated': 0, 'copied': 0, 'failed': 0}
    failed_files = []

    print(f"🚀 开始处理 {len(all_files)} 个文件...")
    print("::group::Processing all files")
    processed_count = 0
    sys.stdout.flush()

    for item in all_files:
        processed_count += 1
        docs_subdir = src_path / 'docs'
        if docs_subdir.exists() and docs_subdir.is_dir() and str(item).startswith(str(docs_subdir)):
            rel_path = item.relative_to(docs_subdir)
        else:
            rel_path = item.relative_to(src_path)
        dest_item = dest_path / rel_path
        dest_item.parent.mkdir(parents=True, exist_ok=True)

        if is_text_file(item):
            msg = f"[{processed_count}/{len(all_files)}] 正在翻译: {rel_path}"
            print(msg)
            print(f"::group::{msg}")
            sys.stdout.flush()
            translated_content = translate_file(item, source_lang, target_lang, config)
            if translated_content is not None:
                print(f"📝 准备写入翻译后的内容，大小: {len(translated_content)} 字符")
                sys.stdout.flush()
                try:
                    with open(dest_item, 'w', encoding='utf-8') as f:
                        f.write(translated_content)
                    print(f"✅ [{processed_count}/{len(all_files)}] 已翻译并保存: {rel_path}")
                    sys.stdout.flush()
                    if dest_item.exists():
                        written_size = dest_item.stat().st_size
                        print(f"📊 验证文件: {rel_path} 已创建，大小: {written_size} 字节")
                        sys.stdout.flush()
                except Exception as e:
                    print(f"❌ 写入文件 {rel_path} 时出错: {str(e)}")
                    traceback.print_exc()
                    sys.stdout.flush()
                
                try:
                    subprocess.run(['git', 'config', 'user.email', 'action@github.com'], check=True, capture_output=True, text=True)
                    subprocess.run(['git', 'config', 'user.name', 'GitHub Action'], check=True, capture_output=True, text=True)
                    subprocess.run(['git', 'add', str(dest_item)], check=True, capture_output=True, text=True)
                    result = subprocess.run(['git', 'diff', '--cached', '--quiet'], check=False, capture_output=True, text=True)
                    if result.returncode != 0:
                        subprocess.run(['git', 'commit', '-m', f'Translate: {rel_path} [skip ci]'], check=True, capture_output=True, text=True)
                        if os.path.exists(item):
                            subprocess.run(['git', 'rm', str(item)], check=True, capture_output=True, text=True)
                            subprocess.run(['git', 'commit', '-m', f'Delete: Remove original file after successful translation {rel_path} [skip ci]'], check=True, capture_output=True, text=True)
                        subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True, text=True)
                        print(f"💾 [{processed_count}/{len(all_files)}] 已提交并推送: {rel_path}")
                    else:
                        print(f"📊 [{processed_count}/{len(all_files)}] {rel_path} 无更改需要提交")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️ 提交文件 {rel_path} 时出错: {e.stderr if e.stderr else str(e)}")
                
                stats['translated'] += 1
            else:
                failed_files.append({'src': str(item), 'dest': str(dest_item), 'attempts': 1})
                stats['failed'] += 1
                print(f"❌ [{processed_count}/{len(all_files)}] 翻译失败，加入重试队列: {rel_path}")
            print("::endgroup::")
            sys.stdout.flush()
        else:
            msg = f"::group::Copying {rel_path}"
            print(msg)
            sys.stdout.flush()
            shutil.copy2(item, dest_item)
            print(f"📋 [{processed_count}/{len(all_files)}] 已复制非文本文件: {rel_path}")
            stats['copied'] += 1
            
            try:
                subprocess.run(['git', 'config', 'user.email', 'action@github.com'], check=True, capture_output=True, text=True)
                subprocess.run(['git', 'config', 'user.name', 'GitHub Action'], check=True, capture_output=True, text=True)
                subprocess.run(['git', 'add', str(dest_item)], check=True, capture_output=True, text=True)
                result = subprocess.run(['git', 'diff', '--cached', '--quiet'], check=False, capture_output=True, text=True)
                if result.returncode != 0:
                    subprocess.run(['git', 'commit', '-m', f'Copy: {rel_path} [skip ci]'], check=True, capture_output=True, text=True)
                    if os.path.exists(item):
                        subprocess.run(['git', 'rm', str(item)], check=True, capture_output=True, text=True)
                        subprocess.run(['git', 'commit', '-m', f'Delete: Remove original file after successful copy {rel_path} [skip ci]'], check=True, capture_output=True, text=True)
                    subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True, text=True)
                    print(f"💾 [{processed_count}/{len(all_files)}] 已提交并推送: {rel_path}")
                else:
                    print(f"📊 [{processed_count}/{len(all_files)}] {rel_path} 无更改需要提交")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ 提交文件 {rel_path} 时出错: {e.stderr if e.stderr else str(e)}")
            
            try:
                os.remove(item)
                print(f"🗑️ [{processed_count}/{len(all_files)}] 已删除原始文件: {rel_path}")
            except OSError as e:
                print(f"⚠️ 删除原始文件 {rel_path} 时出错: {e}")
            print("::endgroup::")
            sys.stdout.flush()

        time.sleep(0.5)
    
    print(f"第一轮处理完成: 总计{len(all_files)}个文件，成功翻译{stats['translated']}个，失败{stats['failed']}个")

    retry_count = 0
    while failed_files and retry_count < max_retries:
        retry_count += 1
        print(f"第 {retry_count} 次重试 {len(failed_files)} 个失败的文件...")
        still_failed = []
        for idx, file_info in enumerate(failed_files):
            item = Path(file_info['src'])
            dest_item = Path(file_info['dest'])
            rel_path = Path(file_info['src']).relative_to(Path(src_dir))
            dest_item.parent.mkdir(parents=True, exist_ok=True)
            
            msg = f"::group::Retrying {rel_path}"
            print(msg)
            sys.stdout.flush()
            msg = f"[重试 {idx+1}/{len(failed_files)}] 正在重试: {rel_path}"
            print(msg)
            sys.stdout.flush()
            translated_content = translate_file(item, source_lang, target_lang, config)
            if translated_content is not None:
                print(f"📝 准备写入重试后的翻译内容，大小: {len(translated_content)} 字符")
                sys.stdout.flush()
                try:
                    with open(dest_item, 'w', encoding='utf-8') as f:
                        f.write(translated_content)
                    msg = f"✅ [重试 {idx+1}/{len(failed_files)}] 重试成功，已翻译并保存: {rel_path}"
                    print(msg)
                    sys.stdout.flush()
                    if dest_item.exists():
                        written_size = dest_item.stat().st_size
                        print(f"📊 验证文件: {rel_path} 已创建，大小: {written_size} 字节")
                        sys.stdout.flush()
                except Exception as e:
                    print(f"❌ 写入文件 {rel_path} 时出错: {str(e)}")
                    traceback.print_exc()
                    sys.stdout.flush()
                
                try:
                    subprocess.run(['git', 'config', 'user.email', 'action@github.com'], check=True, capture_output=True, text=True)
                    subprocess.run(['git', 'config', 'user.name', 'GitHub Action'], check=True, capture_output=True, text=True)
                    subprocess.run(['git', 'add', str(dest_item)], check=True, capture_output=True, text=True)
                    result = subprocess.run(['git', 'diff', '--cached', '--quiet'], check=False, capture_output=True, text=True)
                    if result.returncode != 0:
                        subprocess.run(['git', 'commit', '-m', f'Retry Translate: {rel_path} [skip ci]'], check=True, capture_output=True, text=True)
                        if os.path.exists(item):
                            subprocess.run(['git', 'rm', str(item)], check=True, capture_output=True, text=True)
                            subprocess.run(['git', 'commit', '-m', f'Delete: Remove original file after successful retry translation {rel_path} [skip ci]'], check=True, capture_output=True, text=True)
                        subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True, text=True)
                        print(f"💾 [重试 {idx+1}/{len(failed_files)}] 已提交并推送: {rel_path}")
                    else:
                        print(f"📊 [重试 {idx+1}/{len(failed_files)}] {rel_path} 无更改需要提交")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️ 提交文件 {rel_path} 时出错: {e.stderr if e.stderr else str(e)}")
                
                stats['translated'] += 1
                stats['failed'] -= 1
                try:
                    os.remove(item)
                    print(f"🗑️ [重试 {idx+1}/{len(failed_files)}] 已删除原始文件: {rel_path}")
                except OSError as e:
                    print(f"⚠️ 删除原始文件 {rel_path} 时出错: {e}")
            else:
                file_info['attempts'] += 1
                if file_info['attempts'] <= max_retries:
                    still_failed.append(file_info)
                else:
                    print(f"❌ [重试 {idx+1}/{len(failed_files)}] 重试超过 {max_retries} 次，放弃翻译: {rel_path}")
            print("::endgroup::")
            sys.stdout.flush()
        
        failed_files = still_failed
        if still_failed:
            print(f"第 {retry_count} 次重试完成，仍有 {len(still_failed)} 个文件未能翻译")
        else:
            print(f"第 {retry_count} 次重试完成，所有文件均已成功翻译")

    if failed_files:
        print("\n=== 翻译失败的文件列表 ===")
        failed_paths = []
        for file_info in failed_files:
            src_path = Path(file_info['src'])
            rel_path = src_path.relative_to(src_path.parent.parent)
            failed_paths.append(str(rel_path))
        for file_path in sorted(failed_paths):
            print(f"  - {file_path}")
        with open('/tmp/failed_translation_files.json', 'w', encoding='utf-8') as f:
            json.dump(failed_paths, f, ensure_ascii=False, indent=2)
        print(f"\n详细失败列表已保存到 /tmp/failed_translation_files.json")

    return stats, failed_files

def main():
    parser = argparse.ArgumentParser(description='使用大语言模型翻译文档（支持大文件分段翻译）')
    parser.add_argument('--source-dir', default='temp_for_translation', help='源目录 (默认: temp_for_translation)')
    parser.add_argument('--target-dir', default='docs', help='目标目录 (默认: docs)')
    parser.add_argument('--source-lang', default='English', help='源语言 (默认: English)')
    parser.add_argument('--target-lang', default='Chinese', help='目标语言 (默认: Chinese)')
    parser.add_argument('--max-retries', type=int, default=2, help='最大重试次数 (默认: 2)')

    args = parser.parse_args()

    print(f"开始LLM翻译进程...")
    print(f"源目录: {args.source_dir}")
    print(f"目标目录: {args.target_dir}")
    print(f"源语言: {args.source_lang}")
    print(f"目标语言: {args.target_lang}")
    print(f"模型: stepfun/step-3.5-flash:free (固定)")
    print(f"API密钥环境变量: OPENROUTER_API_KEY")
    
    config = {
        'api_key': os.getenv('OPENROUTER_API_KEY'),
        'model': 'stepfun/step-3.5-flash:free',
        'base_url': 'https://openrouter.ai/api/v1'
    }

    if not os.path.exists(args.source_dir):
        print(f"错误: 源目录 {args.source_dir} 不存在")
        sys.exit(1)

    stats, failed_files = process_directory(
        args.source_dir, 
        args.target_dir, 
        args.source_lang, 
        args.target_lang, 
        config,
        args.max_retries
    )

    print("::endgroup::")
    msg = f"\n✅ 翻译完成!"
    print(msg)
    print(f"📊 总计处理文件: {stats['total']}")
    print(f"✅ 成功翻译: {stats['translated']}")
    print(f"📋 直接复制: {stats['copied']}")
    print(f"❌ 翻译失败: {stats['failed']}")

    try:
        subprocess.run(['git', 'config', 'user.email'], check=True, capture_output=True, text=True)
        subprocess.run(['git', 'config', 'user.name'], check=True, capture_output=True, text=True)
        subprocess.run(['git', 'add', 'docs/'], check=True, capture_output=True, text=True)
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], check=False, capture_output=True, text=True)
        if result.returncode != 0:
            subprocess.run(['git', 'commit', '-m', f'Translate: Processed {stats["translated"]} files, copied {stats["copied"]} files [skip ci]'], check=True, capture_output=True, text=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True, text=True)
            print("🎉 所有翻译文件已提交到仓库")
        else:
            print("ℹ️ 没有更改需要提交")
    except subprocess.CalledProcessError as e:
        print(f"❌ 提交更改时出错: {e.stderr if e.stderr else str(e)}")
        print("⚠️ 请手动提交更改")

    if failed_files:
        print(f"❌ 以下 {len(failed_files)} 个文件未能完成翻译，已记录到 /tmp/failed_translation_files.json")
        for file_info in failed_files:
            src_path = Path(file_info['src'])
            rel_path = src_path.relative_to(src_path.parent.parent)
            print(f"  - {rel_path}")
    else:
        print("🎉 所有文件都已成功处理！")
    
    sys.stdout.flush()

if __name__ == '__main__':
    main()
