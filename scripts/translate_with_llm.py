#!/usr/bin/env python3
"""
使用大语言模型进行文档翻译的脚本
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
    """判断文件是否为需要翻译的文本文件"""
    text_extensions = {'.md', '.mdx', '.txt', '.html', '.htm', '.yaml', '.yml'}
    return filepath.suffix.lower() in text_extensions

def extract_frontmatter(content):
    """提取并返回 YAML frontmatter（如果有）"""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[1].strip(), parts[2]
    return None, content

def protect_html_tags(text):
    """保护HTML标签，防止被翻译"""
    protected_parts = {}
    
    # 保护完整的HTML标签对（包括内容）
    html_pattern = r'<([^>]+)>(.*?)</\1>|<[^>]+/>'
    matches = re.findall(html_pattern, text, re.DOTALL)
    
    for i, match in enumerate(matches):
        if isinstance(match, tuple) and len(match) >= 2 and match[1].strip():
            # 匹配到标签对的情况
            full_tag = f"<{match[0]}>{match[1]}</{match[0]}>"
        elif isinstance(match, str) and '<' in match and '>' in match:
            # 匹配到自闭合标签的情况
            full_tag = match
        else:
            continue
            
        placeholder = f"__HTML_TAG_{i}__"
        protected_parts[placeholder] = full_tag
        text = text.replace(full_tag, placeholder, 1)
    
    return text, protected_parts

def protect_code_blocks(text):
    """保护代码块和特殊内容不被翻译"""
    protected_parts = {}
    
    # 保护 ``` 代码块
    pattern = r'(```[\s\S]*?```|\`[^\`]*\`)'
    matches = re.findall(pattern, text)
    for i, match in enumerate(matches):
        placeholder = f"__CODE_BLOCK_{i}__"
        protected_parts[placeholder] = match
        text = text.replace(match, placeholder, 1)
    
    # 保护HTML标签
    text, html_parts = protect_html_tags(text)
    protected_parts.update(html_parts)
    
    # 保护行内代码 `code`
    inline_pattern = r'`(.*?)`'
    inline_matches = re.findall(inline_pattern, text)
    for i, match in enumerate(inline_matches):
        placeholder = f"__INLINE_CODE_{i}__"
        protected_parts[placeholder] = f"`{match}`"
        text = text.replace(f"`{match}`", placeholder)
    
    return text, protected_parts

def restore_protected_parts(text, protected_parts):
    """恢复受保护的内容"""
    for placeholder, original in protected_parts.items():
        text = text.replace(placeholder, original)
    return text

def split_text(text, max_chars=10000):
    """将文本分割成适当大小的块，保持句子完整性"""
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
    
    # 如果仍有块太大，按句子分割
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

def validate_model(model_name):
    """验证模型名称是否为允许的模型"""
    allowed_models = [
        'qwen3.5-flash-2026-02-23',
        'qwen3.5-plus-2026-02-15',       
        'qwen3.5-plus',
        'qwen3.5-flash',
        'qwen-plus',
        'qwen-max'
    ]
    if model_name not in allowed_models:
        raise ValueError(f"不支持的模型: {model_name}. 支持的模型: {', '.join(allowed_models)}")
    return model_name

def translate_with_qwen_portal(text, source_lang='English', target_lang='Chinese', api_key=None, model='qwen3.5-plus', base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'):
    # 验证模型名称
    model = validate_model(model)
    
    """使用 Qwen Portal 服务进行翻译"""
    if not api_key:
        api_key = os.getenv('QWEN_PORTAL_API_KEY')
        if not api_key:
            print("Qwen Portal API密钥未提供，跳过")
            return None

    print("🔍 开始Qwen Portal翻译流程")
    sys.stdout.flush()
    
    try:
        print(f"📊 原始文本长度: {len(text)} 字符")
        sys.stdout.flush()
        
        print("🛡️ 正在保护代码块和其他特殊内容")
        sys.stdout.flush()
        # 保护代码块和其他特殊内容
        protected_text, protected_parts = protect_code_blocks(text)
        print(f"✅ 代码块保护完成，共有 {len(protected_parts)} 个受保护部分")
        print(f"📊 保护后文本长度: {len(protected_text)} 字符")
        sys.stdout.flush()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        print("📝 准备翻译提示词")
        sys.stdout.flush()
        # 创建翻译提示，特别指示不要翻译代码块
        prompt = f"""请将以下{source_lang}文本翻译为高质量的{target_lang}。翻译时请严格遵守以下要求：
        1. 只翻译普通文本内容，不要翻译代码块、配置项或技术术语
        2. 保留所有代码块（用```包围的内容）、行内代码（用`包围的内容）和配置项不变
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

        print(f"📊 准备发送API请求，提示词长度: {len(prompt)} 字符")
        sys.stdout.flush()
        print(f"📡 正在发送API请求到: {base_url}/chat/completions")
        sys.stdout.flush()
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=180
        )
        print(f"📥 收到API响应，状态码: {response.status_code}")
        sys.stdout.flush()

        if response.status_code == 200:
            print("🔍 解析API响应")
            sys.stdout.flush()
            result = response.json()
            print(f"🔍 API响应解析完成，响应长度: {len(str(result))} 字符")
            sys.stdout.flush()
            if 'choices' in result and len(result['choices']) > 0:
                translated_text = result['choices'][0]['message']['content'].strip()
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
                print(f"⚠️ Qwen Portal响应格式异常: {result}")
                print(f"⚠️ 响应内容预览: {str(result)[:500]}...")  # 显示前500个字符
                sys.stdout.flush()
                return None
        else:
            print(f"❌ Qwen Portal翻译失败: {response.status_code}, {response.text}")
            print(f"❌ 响应内容预览: {response.text[:500]}...")  # 显示前500个字符
            sys.stdout.flush()
            return None
    except Exception as e:
        print(f"❌ Qwen Portal翻译过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()  # 打印详细错误堆栈
        sys.stdout.flush()
        return None

def translate_large_text(text, source_lang='English', target_lang='Chinese', api_key=None, model='qwen3-coder-plus', base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'):
    """翻译大文本，按块分割处理"""
    print(f"📄 检测到大文件 ({len(text)} 字符)，开始分段翻译...")
    
    # 分割文本
    chunks = split_text(text, max_chars=10000)
    print(f"✂️ 文本已分割为 {len(chunks)} 个片段")
    
    translated_chunks = []
    for i, chunk in enumerate(chunks):
        print(f"📝 翻译片段 {i+1}/{len(chunks)} (长度: {len(chunk)} 字符)")
        # 尝试使用主要模型，如果失败则尝试备用模型，使用传入的base_url
        translated_chunk = try_translate_with_fallback(
            chunk, 
            source_lang, 
            target_lang, 
            api_key, 
            base_url  # 使用传入的base_url而不是默认值
        )
        
        if translated_chunk is not None:
            translated_chunks.append(translated_chunk)
            print(f"✅ 片段 {i+1} 翻译完成")
        else:
            print(f"❌ 片段 {i+1} 翻译失败")
            return None
        
        # 避免API调用过于频繁
        time.sleep(1)
    
    # 合并翻译后的片段
    final_text = "\n\n".join(translated_chunks)
    print(f"📦 所有片段合并完成，最终文本长度: {len(final_text)} 字符")
    return final_text

def try_translate_with_fallback(text, source_lang, target_lang, api_key, base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'):
    """尝试使用主要模型翻译，失败时使用备用模型"""
    # 定义模型优先级列表
    model_priority = [
        'qwen3.5-plus',
        'qwen3.5-flash',
        'qwen-plus',
        'qwen-max'
    ]
    
    for i, model in enumerate(model_priority):
        print(f"📝 尝试使用模型: {model} (优先级 {i+1}/{len(model_priority)})")
        result = translate_with_qwen_portal(
            text, 
            source_lang, 
            target_lang, 
            api_key, 
            model,
            base_url  # 使用传入的base_url参数
        )
        
        if result is not None:
            print(f"✅ 模型 {model} 翻译成功")
            return result
        else:
            print(f"⚠️ 模型 {model} 翻译失败，尝试下一个模型...")
            # 短暂延时再尝试下一个模型
            time.sleep(1)
    
    # 所有模型都失败
    print("❌ 所有模型都无法完成翻译")
    return None

def translate_with_ollama(text, source_lang='English', target_lang='Chinese', config=None):
    """使用本地 Ollama 模型进行翻译（OpenAI 兼容接口）。"""
    import requests

    base_url = (config or {}).get('ollama_base_url') or 'http://127.0.0.1:11434/v1'
    model = (config or {}).get('ollama_model') or 'qwen3:8b'

    print(f"🦙 使用 Ollama 本地模型翻译: {model}")
    sys.stdout.flush()

    system_prompt = (
        "You are a professional legal translator. "
        "Translate the provided text from {src} to {tgt} accurately and neutrally. "
        "Preserve names, dates, legal terms, and paragraph structure. "
        "Do not add commentary or omit sensitive details; this is for legal research."
    ).format(src=source_lang, tgt=target_lang)

    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': text},
        ],
        'temperature': 0.2,
    }

    try:
        resp = requests.post(f"{base_url}/chat/completions", json=payload, timeout=600)
        print(f"📥 Ollama API 响应状态码: {resp.status_code}")
        sys.stdout.flush()
        if resp.status_code != 200:
            print(f"❌ Ollama 翻译失败: {resp.status_code}, {resp.text[:500]}...")
            sys.stdout.flush()
            return None
        data = resp.json()
        if 'choices' in data and data['choices']:
            content = data['choices'][0]['message']['content']
            print(f"✅ Ollama 翻译完成，长度: {len(content)} 字符")
            sys.stdout.flush()
            return content
        print(f"⚠️ Ollama 响应格式异常: {data}")
        sys.stdout.flush()
        return None
    except Exception as e:  # noqa: BLE001
        print(f"❌ 调用 Ollama 时出错: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        return None


def translate_with_any_llm(text, source_lang='English', target_lang='Chinese', config=None):
    """使用配置的指定大模型进行翻译，支持备用模型和 Ollama。"""
    if config is None:
        config = {
            'provider': 'qwen-portal',  # 默认使用qwen-portal
            'qwen_portal_api_key': os.getenv('QWEN_PORTAL_API_KEY'),
            'qwen_portal_model': 'qwen-coder-plus-latest',  # 默认使用 qwen-coder-plus-latest
            'qwen_portal_base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1'
        }

    provider = config.get('provider', 'qwen-portal')

    # 如果使用 Ollama，本地模型直接整体交给 Ollama 处理（内部再做分段或一次性翻译）
    if provider == 'ollama':
        print(f"📡 使用 Ollama 提供的本地模型翻译，provider=ollama")
        sys.stdout.flush()
        return translate_with_ollama(text, source_lang, target_lang, config)

    # 否则走原来的 Qwen Portal 路线
    # 检查文件大小，如果大于10KB则分段翻译
    if len(text) > 10000:  # 10KB
        print(f"📏 文本大小 ({len(text)} 字符) 超过 10KB，使用分段翻译")
        result = translate_large_text(
            text,
            source_lang,
            target_lang,
            config['qwen_portal_api_key'],
            config['qwen_portal_model'],
            config['qwen_portal_base_url']
        )
    else:
        print(f"📏 文本大小 ({len(text)} 字符) 在范围内，直接翻译")
        # 使用带备用模型的翻译函数
        result = try_translate_with_fallback(
            text,
            source_lang,
            target_lang,
            config['qwen_portal_api_key'],
            config['qwen_portal_base_url']
        )

    if result is not None:
        return result
    else:
        print("所有模型翻译均失败")
        return None

def translate_file(filepath, source_lang='English', target_lang='Chinese', config=None):
    """翻译单个文件，使用大语言模型"""
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
        # 提取 frontmatter（如果有）
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
        
        # 验证翻译后的内容
        if not translated_content or len(translated_content.strip()) == 0:
            print(f"⚠️ 翻译返回了空内容: {filepath}")
            sys.stdout.flush()
            return None
        
        print(f"✅ 翻译完成，内容长度: {len(translated_content)} 字符")
        sys.stdout.flush()

        print(f"📦 重新组合 frontmatter 和翻译后的内容")
        sys.stdout.flush()
        # 重新组合 frontmatter 和翻译后的内容
        if frontmatter:
            translated_content = f"---\n{frontmatter}\n---\n{translated_content}"

        print(f"✅ 文件处理完成: {filepath}")
        sys.stdout.flush()
        return translated_content
    except Exception as e:
        print(f"❌ 处理文件 {filepath} 时出现错误: {str(e)}")
        import traceback
        traceback.print_exc()  # 打印详细错误堆栈
        sys.stdout.flush()
        return None

def process_directory(src_dir, dest_dir, source_lang='English', target_lang='Chinese', config=None, max_retries=2):
    """处理整个目录，使用大语言模型翻译"""
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)

    # 确保目标目录存在
    dest_path.mkdir(parents=True, exist_ok=True)

    # 找出所有需要处理的文件
    all_files = []
    
    # 检查源目录结构，如果存在 docs 子目录，则在其中搜索
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

    # 统计信息
    stats = {
        'total': len(all_files),
        'translated': 0,
        'copied': 0,
        'failed': 0
    }

    # 需要重试的文件列表
    failed_files = []

    msg = f"🚀 开始处理 {len(all_files)} 个文件..."
    print(msg)
    print("::group::Processing all files")
    processed_count = 0
    # 强制刷新输出缓冲区
    sys.stdout.flush()

    # 第一轮：尝试翻译所有文件
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
            translated_content = translate_file(item, source_lang, target_lang, config)
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
                
                # 立即提交并推送更改到git，实现翻译一个推送一个
                try:
                    import subprocess
                    # 设置git配置
                    subprocess.run(['git', 'config', 'user.email', 'action@github.com'], check=True, capture_output=True, text=True)
                    subprocess.run(['git', 'config', 'user.name', 'GitHub Action'], check=True, capture_output=True, text=True)
                    
                    # 添加当前翻译的文件
                    subprocess.run(['git', 'add', str(dest_item)], check=True, capture_output=True, text=True)
                    
                    # 检查是否有暂存的更改
                    result = subprocess.run(['git', 'diff', '--cached', '--quiet'], check=False, capture_output=True, text=True)
                    if result.returncode != 0:  # 如果有暂存的更改
                        commit_msg = f'Translate: {rel_path} [skip ci]'
                        subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True, text=True)
                        
                        # 立即推送更改到远程仓库
                        try:
                            # 检查原始文件是否存在
                            if os.path.exists(item):
                                # 先将删除操作添加到git（告诉git这个文件被删除了）
                                subprocess.run(['git', 'rm', str(item)], check=True, capture_output=True, text=True)
                                commit_msg = f'Delete: Remove original file after successful translation {rel_path} [skip ci]'
                                subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True, text=True)
                                
                                subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True, text=True)
                                msg = f"🗑️ [{processed_count}/{len(all_files)}] 已删除原始文件并推送更改: {rel_path}"
                                print(msg)
                                
                                # 注意：这里不再调用 os.remove()，因为 git rm 已经处理了删除
                            else:
                                # 文件不存在，但仍推送翻译后的文件
                                subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True, text=True)
                                print(f"📤 [{processed_count}/{len(all_files)}] 已推送 {rel_path} 到远程仓库")
                            
                        except subprocess.CalledProcessError as push_error:
                            print(f"❌ [{processed_count}/{len(all_files)}] 推送 {rel_path} 失败: {push_error.stderr if push_error.stderr else str(push_error)}")
                        
                        print(f"💾 [{processed_count}/{len(all_files)}] 已提交 {rel_path} 到本地git")
                    else:
                        print(f"📊 [{processed_count}/{len(all_files)}] {rel_path} 无更改需要提交")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️ 提交文件 {rel_path} 时出错: {e.stderr if e.stderr else str(e)}")
                    # 提交失败不影响继续处理其他文件
                
                stats['translated'] += 1

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
            
            # 立即提交并推送复制的文件
            try:
                import subprocess
                # 设置git配置
                subprocess.run(['git', 'config', 'user.email', 'action@github.com'], check=True, capture_output=True, text=True)
                subprocess.run(['git', 'config', 'user.name', 'GitHub Action'], check=True, capture_output=True, text=True)
                
                # 添加当前复制的文件
                subprocess.run(['git', 'add', str(dest_item)], check=True, capture_output=True, text=True)
                
                # 检查是否有暂存的更改
                result = subprocess.run(['git', 'diff', '--cached', '--quiet'], check=False, capture_output=True, text=True)
                if result.returncode != 0:  # 如果有暂存的更改
                    commit_msg = f'Copy: {rel_path} [skip ci]'
                    subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True, text=True)
                    
                    # 立即推送更改到远程仓库
                    try:
                        # 检查原始文件是否存在
                        if os.path.exists(item):
                            # 先将删除操作添加到git（告诉git这个文件被删除了）
                            subprocess.run(['git', 'rm', str(item)], check=True, capture_output=True, text=True)
                            commit_msg = f'Delete: Remove original file after successful copy {rel_path} [skip ci]'
                            subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True, text=True)
                            
                            subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True, text=True)
                            msg = f"🗑️ [{processed_count}/{len(all_files)}] 已删除原始文件并推送更改: {rel_path}"
                            print(msg)
                            
                            # 注意：这里不再调用 os.remove()，因为 git rm 已经处理了删除
                        else:
                            # 文件不存在，但仍推送复制后的文件
                            subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True, text=True)
                            print(f"📤 [{processed_count}/{len(all_files)}] 已推送 {rel_path} 到远程仓库")
                        
                    except subprocess.CalledProcessError as push_error:
                        print(f"❌ [{processed_count}/{len(all_files)}] 推送 {rel_path} 失败: {push_error.stderr if push_error.stderr else str(push_error)}")
                    
                    print(f"💾 [{processed_count}/{len(all_files)}] 已提交 {rel_path} 到本地git")
                else:
                    print(f"📊 [{processed_count}/{len(all_files)}] {rel_path} 无更改需要提交")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ 提交文件 {rel_path} 时出错: {e.stderr if e.stderr else str(e)}")
                # 提交失败不影响继续处理其他文件
            
            # 标记此文件待删除
            try:
                os.remove(item)
                msg = f"🗑️ [{processed_count}/{len(all_files)}] 已删除原始文件: {rel_path}"
                print(msg)
            except OSError as e:
                msg = f"⚠️ 删除原始文件 {rel_path} 时出错: {e}"
                print(msg)
            print("::endgroup::")  # GitHub Actions 分组结束
            # 再次强制刷新输出缓冲区
            sys.stdout.flush()

        # 在文件之间稍作延迟，避免过于频繁的API调用
        time.sleep(0.5)
    
    print(f"第一轮处理完成: 总计{len(all_files)}个文件，成功翻译{stats['translated']}个，失败{stats['failed']}个")

    # 重试失败的文件
    retry_count = 0
    while failed_files and retry_count < max_retries:
        retry_count += 1
        print(f"第 {retry_count} 次重试 {len(failed_files)} 个失败的文件...")

        still_failed = []
        for idx, file_info in enumerate(failed_files):
            item = Path(file_info['src'])
            dest_item = Path(file_info['dest'])
            
            # 获取相对路径用于显示
            rel_path = Path(file_info['src']).relative_to(Path(src_dir))

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
                
                # 立即提交并推送重试成功的文件
                try:
                    import subprocess
                    # 设置git配置
                    subprocess.run(['git', 'config', 'user.email', 'action@github.com'], check=True, capture_output=True, text=True)
                    subprocess.run(['git', 'config', 'user.name', 'GitHub Action'], check=True, capture_output=True, text=True)
                    
                    # 添加当前翻译的文件
                    subprocess.run(['git', 'add', str(dest_item)], check=True, capture_output=True, text=True)
                    
                    # 检查是否有暂存的更改
                    result = subprocess.run(['git', 'diff', '--cached', '--quiet'], check=False, capture_output=True, text=True)
                    if result.returncode != 0:  # 如果有暂存的更改
                        commit_msg = f'Retry Translate: {rel_path} [skip ci]'
                        subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True, text=True)
                        
                        # 立即推送更改到远程仓库
                        try:
                            # 检查原始文件是否存在
                            if os.path.exists(item):
                                # 先将删除操作添加到git（告诉git这个文件被删除了）
                                subprocess.run(['git', 'rm', str(item)], check=True, capture_output=True, text=True)
                                commit_msg = f'Delete: Remove original file after successful retry translation {rel_path} [skip ci]'
                                subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True, text=True)
                                
                                subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True, text=True)
                                msg = f"🗑️ [重试 {idx+1}/{len(failed_files)}] 已删除原始文件并推送更改: {rel_path}"
                                print(msg)
                                
                                # 注意：这里不再调用 os.remove()，因为 git rm 已经处理了删除
                            else:
                                # 文件不存在，但仍推送重试后的文件
                                subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True, text=True)
                                print(f"📤 [重试 {idx+1}/{len(failed_files)}] 已推送 {rel_path} 到远程仓库")
                            
                        except subprocess.CalledProcessError as push_error:
                            print(f"❌ [重试 {idx+1}/{len(failed_files)}] 推送 {rel_path} 失败: {push_error.stderr if push_error.stderr else str(push_error)}")
                        
                        print(f"💾 [重试 {idx+1}/{len(failed_files)}] 已提交 {rel_path} 到本地git")
                    else:
                        print(f"📊 [重试 {idx+1}/{len(failed_files)}] {rel_path} 无更改需要提交")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️ 提交文件 {rel_path} 时出错: {e.stderr if e.stderr else str(e)}")
                    # 提交失败不影响继续处理其他文件
                
                stats['translated'] += 1
                stats['failed'] -= 1
                
                # 删除原始文件以避免重复翻译
                try:
                    os.remove(item)
                    msg = f"🗑️ [重试 {idx+1}/{len(failed_files)}] 已删除原始文件: {rel_path}"
                    print(msg)
                except OSError as e:
                    msg = f"⚠️ 删除原始文件 {rel_path} 时出错: {e}"
                    print(msg)
            else:
                # 重试失败，增加尝试次数
                file_info['attempts'] += 1
                if file_info['attempts'] <= max_retries:
                    still_failed.append(file_info)
                else:
                    msg = f"❌ [重试 {idx+1}/{len(failed_files)}] 重试超过 {max_retries} 次，放弃翻译: {rel_path}"
                    print(msg)
            print("::endgroup::")
            # 强制刷新输出缓冲区
            sys.stdout.flush()

        failed_files = still_failed
        
        if still_failed:
            print(f"第 {retry_count} 次重试完成，仍有 {len(still_failed)} 个文件未能翻译")
        else:
            print(f"第 {retry_count} 次重试完成，所有文件均已成功翻译")

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
    parser = argparse.ArgumentParser(description='使用大语言模型翻译文档（支持大文件分段翻译和备用模型）')
    parser.add_argument('--source-dir', default='temp_for_translation', 
                       help='源目录 (默认: temp_for_translation)')
    parser.add_argument('--target-dir', default='docs', 
                       help='目标目录 (默认: docs)')
    parser.add_argument('--source-lang', default='English', 
                       help='源语言 (默认: English)')
    parser.add_argument('--target-lang', default='Chinese', 
                       help='目标语言 (默认: Chinese)')
    parser.add_argument('--provider', choices=['qwen-portal'], default='qwen-portal',
                       help='LLM提供商 (默认: qwen-portal)')
    parser.add_argument('--qwen-portal-api-key', 
                       help='Qwen Portal API密钥')
    parser.add_argument('--qwen-portal-model', default='qwen3-coder-plus',
                       choices=['qwen3-coder-plus', 'qwen-coder-plus-latest', 'qwen-coder-plus-1106', 'qwen-coder-plus', 'qwen-plus'],
                       help='Qwen Portal 模型名称 (默认: qwen3-coder-plus)')
    parser.add_argument('--qwen-portal-base-url', default='https://dashscope.aliyuncs.com/compatible-mode/v1',
                       help='Qwen Portal 服务URL (默认: https://dashscope.aliyuncs.com/compatible-mode/v1)')
    parser.add_argument('--max-retries', type=int, default=2, 
                       help='最大重试次数 (默认: 2)')

    args = parser.parse_args()

    print(f"开始LLM翻译进程...")
    print(f"源目录: {args.source_dir}")
    print(f"目标目录: {args.target_dir}")
    print(f"源语言: {args.source_lang}")
    print(f"目标语言: {args.target_lang}")
    print(f"LLM提供商: {args.provider}")
    print(f"使用模型: {args.qwen_portal_model}")
    
    # 构建配置
    config = {
        'provider': args.provider,
        'qwen_portal_api_key': args.qwen_portal_api_key or os.getenv('QWEN_PORTAL_API_KEY'),
        'qwen_portal_model': args.qwen_portal_model,
        'qwen_portal_base_url': args.qwen_portal_base_url,
    }

    # 检查源目录是否存在
    if not os.path.exists(args.source_dir):
        print(f"错误: 源目录 {args.source_dir} 不存在")
        sys.exit(1)

    # 处理目录
    stats, failed_files = process_directory(
        args.source_dir, 
        args.target_dir, 
        args.source_lang, 
        args.target_lang, 
        config,
        args.max_retries
    )

    print("::endgroup::")  # 结束文件处理分组
    msg = f"\n✅ 翻译完成!"
    print(msg)
    print(f"📊 总计处理文件: {stats['total']}")
    print(f"✅ 成功翻译: {stats['translated']}")
    print(f"📋 直接复制: {stats['copied']}")
    print(f"❌ 翻译失败: {stats['failed']}")

    # 提交所有更改
    try:
        import subprocess
        # 检查 git 配置
        subprocess.run(['git', 'config', 'user.email'], check=True, capture_output=True, text=True)
        subprocess.run(['git', 'config', 'user.name'], check=True, capture_output=True, text=True)
        
        subprocess.run(['git', 'add', 'docs/'], check=True, capture_output=True, text=True)
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], check=False, capture_output=True, text=True)
        if result.returncode != 0:  # 如果有暂存的更改
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
        # 显示失败的文件列表
        for file_info in failed_files:
            src_path = Path(file_info['src'])
            rel_path = src_path.relative_to(src_path.parent.parent)  # 相对于源目录
            print(f"  - {rel_path}")
    else:
        print("🎉 所有文件都已成功处理！")
    
    # 强制刷新输出缓冲区
    sys.stdout.flush()

if __name__ == '__main__':
    main()
