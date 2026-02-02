#!/usr/bin/env python3
"""
使用多种翻译API进行文档翻译的脚本，支持容错和API切换
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

def extract_frontmatter(content):
    """提取并返回 YAML frontmatter（如果有）"""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[1].strip(), parts[2]
    return None, content

def test_libretranslate_api(api_url):
    """测试 LibreTranslate API 是否可用"""
    try:
        response = requests.post(
            f"{api_url}/translate",
            json={
                'q': 'hello world',
                'source': 'en',
                'target': 'zh',
                'format': 'text'
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

def translate_with_libretranslate(text, source_lang='en', target_lang='zh', api_url='https://libretranslate.de', api_token=None):
    """使用 LibreTranslate API 翻译文本"""
    try:
        # 设置请求头
        headers = {'Content-Type': 'application/json'}
        if api_token:
            # 如果提供了API token，使用X-API-Token头（适用于MTranServer等）
            headers['X-API-Token'] = api_token
        elif 'libretranslate.de' in api_url or 'argosopentech.com' in api_url:
            # 公共服务通常不需要认证
            pass
        else:
            # 假设私有部署可能需要Bearer token
            headers['Authorization'] = f'Bearer {api_token}' if api_token else 'Bearer dummy-token'
        
        # 测试API连接
        try:
            response = requests.post(
                f"{api_url}/translate",
                json={
                    'q': 'hello',
                    'source': source_lang,
                    'target': target_lang,
                    'format': 'text'
                },
                headers=headers,
                timeout=10
            )
            if response.status_code != 200:
                print(f"API连接测试失败: {response.status_code}, {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"无法连接到翻译API {api_url}: {str(e)}")
            return None

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
                response = requests.post(
                    f"{api_url}/translate",
                    json={
                        'q': chunk,
                        'source': source_lang,
                        'target': target_lang,
                        'format': 'text'
                    },
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    translated_chunks.append(result['translatedText'])
                else:
                    print(f"LibreTranslate翻译失败: {response.status_code}, {response.text}")
                    return None
                
                # 避免请求过于频繁
                time.sleep(0.1)
        
        return '\n\n'.join(translated_chunks)
    except Exception as e:
        print(f"LibreTranslate翻译过程中出现错误: {str(e)}")
        return None

def translate_with_mymemory(text, source_lang='en', target_lang='zh'):
    """使用 MyMemory API 翻译文本（免费）"""
    try:
        # MyMemory 有单次请求长度限制，需要分割
        max_chunk_size = 500  # MyMemory 推荐长度
        if len(text) <= max_chunk_size:
            chunks = [text]
        else:
            # 按句子分割
            sentences = re.split(r'[.!?]+', text)
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk + sentence) <= max_chunk_size:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
        
        translated_chunks = []
        for chunk in chunks:
            if chunk.strip():
                params = {
                    'q': chunk,
                    'langpair': f'{source_lang}|{target_lang}',
                }
                
                response = requests.get(
                    'https://api.mymemory.translated.net/get',
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'responseData' in result and 'translatedText' in result['responseData']:
                        translated_chunks.append(result['responseData']['translatedText'])
                    else:
                        print(f"MyMemory翻译响应格式异常: {result}")
                        return None
                else:
                    print(f"MyMemory翻译失败: {response.status_code}, {response.text}")
                    return None
                
                # 避免请求过于频繁
                time.sleep(1)
        
        return ' '.join(translated_chunks)
    except Exception as e:
        print(f"MyMemory翻译过程中出现错误: {str(e)}")
        return None

def translate_with_deepl(text, source_lang='EN', target_lang='ZH', auth_key=None):
    """使用 DeepL API 翻译文本"""
    if not auth_key:
        print("DeepL API密钥未提供，跳过")
        return None
        
    try:
        # DeepL 有单次请求长度限制
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
                headers = {
                    'Authorization': f'DeepL-Auth-Key {auth_key}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'text': [chunk],
                    'source_lang': source_lang,
                    'target_lang': target_lang
                }
                
                response = requests.post(
                    'https://api-free.deepl.com/v2/translate',
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'translations' in result and len(result['translations']) > 0:
                        translated_chunks.append(result['translations'][0]['text'])
                    else:
                        print(f"DeepL翻译响应格式异常: {result}")
                        return None
                else:
                    print(f"DeepL翻译失败: {response.status_code}, {response.text}")
                    return None
                
                # 避免请求过于频繁
                time.sleep(0.1)
        
        return '\n\n'.join(translated_chunks)
    except Exception as e:
        print(f"DeepL翻译过程中出现错误: {str(e)}")
        return None

def translate_with_ollama(text, source_lang='English', target_lang='Chinese', model='llama2', ollama_url='http://localhost:11434'):
    """使用本地 Ollama 服务进行翻译"""
    try:
        # 检查是否是OpenAI兼容的API格式 (v1)
        if '/v1' in ollama_url:
            # 使用OpenAI兼容格式
            headers = {
                'Content-Type': 'application/json'
            }
            
            # 创建翻译提示
            prompt = f"""Translate the following {source_lang} text to {target_lang}. 
            Only return the translated text, nothing else:

            {text}"""
            
            data = {
                'model': model,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.3,
                'max_tokens': 2048
            }
            
            response = requests.post(
                f"{ollama_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=180  # 增加超时时间，因为本地模型可能较慢
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content'].strip()
                else:
                    print(f"Ollama(v1)响应格式异常: {result}")
                    return None
            else:
                print(f"Ollama(v1)翻译失败: {response.status_code}, {response.text}")
                return None
        else:
            # 使用传统Ollama格式
            headers = {
                'Content-Type': 'application/json'
            }
            
            # 创建翻译提示
            prompt = f"""Translate the following {source_lang} text to {target_lang}. 
            Only return the translated text, nothing else:

            {text}"""
            
            data = {
                'model': model,
                'prompt': prompt,
                'stream': False
            }
            
            response = requests.post(
                f"{ollama_url}/api/generate",
                headers=headers,
                json=data,
                timeout=180  # 增加超时时间，因为本地模型可能较慢
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'response' in result:
                    return result['response'].strip()
                else:
                    print(f"Ollama响应格式异常: {result}")
                    return None
            else:
                print(f"Ollama翻译失败: {response.status_code}, {response.text}")
                return None
    except Exception as e:
        print(f"Ollama翻译过程中出现错误: {str(e)}")
        return None

def translate_text_multiple_services(text, source_lang='en', target_lang='zh', services_config=None):
    """使用多个翻译服务进行翻译，一个失败则尝试下一个"""
    if services_config is None:
        services_config = {
            'libretranslate_urls': ['https://libretranslate.de', 'https://translate.argosopentech.com'],
            'libretranslate_tokens': {},  # URL到token的映射
            'use_mymemory': True,
            'deepl_auth_key': None,  # 可以配置DeepL密钥
            'use_ollama': False,  # 默认禁用Ollama
            'ollama_model': 'llama2',  # 默认模型
            'ollama_url': 'http://localhost:11434'  # 默认URL
        }
    
    # 尝试 Ollama 服务（如果启用）
    if services_config.get('use_ollama', False):
        print(f"尝试使用 Ollama 服务: {services_config.get('ollama_url')} 模型: {services_config.get('ollama_model')}")
        result = translate_with_ollama(
            text, 
            source_lang.capitalize(), 
            target_lang.capitalize(), 
            services_config.get('ollama_model', 'llama2'),
            services_config.get('ollama_url', 'http://localhost:11434')
        )
        if result is not None:
            return result
        else:
            print("Ollama 服务翻译失败")
    
    # 尝试 LibreTranslate 服务
    libre_urls = services_config.get('libretranslate_urls', [])
    libre_tokens = services_config.get('libretranslate_tokens', {})
    for url in libre_urls:
        print(f"尝试使用 LibreTranslate 服务: {url}")
        if test_libretranslate_api(url):
            print(f"LibreTranslate 服务可用: {url}")
            # 获取特定URL的token，如果没有则使用None
            token = libre_tokens.get(url)
            result = translate_with_libretranslate(text, source_lang, target_lang, url, token)
            if result is not None:
                return result
            else:
                print(f"LibreTranslate 服务 {url} 翻译失败，尝试下一个")
        else:
            print(f"LibreTranslate 服务 {url} 不可用，尝试下一个")
    
    # 尝试 MyMemory 服务
    if services_config.get('use_mymemory', True):
        print("尝试使用 MyMemory 服务")
        result = translate_with_mymemory(text, source_lang, target_lang)
        if result is not None:
            return result
        else:
            print("MyMemory 服务翻译失败")
    
    # 尝试 DeepL 服务
    deepl_key = services_config.get('deepl_auth_key')
    if deepl_key:
        print("尝试使用 DeepL 服务")
        result = translate_with_deepl(text, source_lang.upper(), target_lang.upper(), deepl_key)
        if result is not None:
            return result
        else:
            print("DeepL 服务翻译失败")
    
    print("所有翻译服务都失败了")
    return None

def translate_file(filepath, source_lang='en', target_lang='zh', services_config=None):
    """翻译单个文件，使用多个翻译服务"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取 frontmatter（如果有）
        frontmatter, main_content = extract_frontmatter(content)
        
        print(f"正在翻译文件: {filepath}")
        translated_content = translate_text_multiple_services(main_content, source_lang, target_lang, services_config)
        
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

def process_directory_with_fallback(src_dir, dest_dir, source_lang='en', target_lang='zh', services_config=None, max_retries=2):
    """处理整个目录，带多重容错机制"""
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
            translated_content = translate_file(item, source_lang, target_lang, services_config)
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
            translated_content = translate_file(item, source_lang, target_lang, services_config)
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
    parser = argparse.ArgumentParser(description='使用多种翻译API翻译文档，支持容错和API切换')
    parser.add_argument('--source-dir', default='temp_for_translation', 
                       help='源目录 (默认: temp_for_translation)')
    parser.add_argument('--target-dir', default='docs', 
                       help='目标目录 (默认: docs)')
    parser.add_argument('--source-lang', default='en', 
                       help='源语言 (默认: en)')
    parser.add_argument('--target-lang', default='zh', 
                       help='目标语言 (默认: zh)')
    parser.add_argument('--libretranslate-urls', nargs='+', 
                       default=['https://libretranslate.de', 'https://translate.argosopentech.com'],
                       help='LibreTranslate API URLs (默认: https://libretranslate.de https://translate.argosopentech.com)')
    parser.add_argument('--libretranslate-tokens', nargs='+',
                       help='对应LibreTranslate API URLs的tokens (格式: url1:token1 url2:token2)')
    parser.add_argument('--enable-ollama', action='store_true',
                       help='启用 Ollama 本地模型服务')
    parser.add_argument('--ollama-model', default='llama2',
                       help='Ollama 模型名称 (默认: llama2)')
    parser.add_argument('--ollama-url', default='http://localhost:11434',
                       help='Ollama 服务URL (默认: http://localhost:11434)')
    parser.add_argument('--disable-mymemory', action='store_true',
                       help='禁用 MyMemory 服务')
    parser.add_argument('--deepl-auth-key', 
                       help='DeepL API 认证密钥')
    parser.add_argument('--max-retries', type=int, default=2, 
                       help='最大重试次数 (默认: 2)')
    
    args = parser.parse_args()
    
    print(f"开始翻译进程...")
    print(f"源目录: {args.source_dir}")
    print(f"目标目录: {args.target_dir}")
    print(f"源语言: {args.source_lang}")
    print(f"目标语言: {args.target_lang}")
    print(f"LibreTranslate URLs: {args.libretranslate_urls}")
    print(f"启用 Ollama: {args.enable_ollama}")
    if args.enable_ollama:
        print(f"Ollama 模型: {args.ollama_model}")
        print(f"Ollama URL: {args.ollama_url}")
    
    # 解析tokens映射
    tokens_map = {}
    if args.libretranslate_tokens:
        for token_pair in args.libretranslate_tokens:
            if ':' in token_pair:
                url, token = token_pair.split(':', 1)
                tokens_map[url] = token
            else:
                print(f"警告: 无效的token格式 '{token_pair}', 应为 'url:token' 格式")
    
    print(f"使用 MyMemory: {not args.disable_mymemory}")
    print(f"使用 DeepL: {'Yes' if args.deepl_auth_key else 'No'}")
    print(f"LibreTranslate Tokens: {list(tokens_map.keys())}")
    print(f"最大重试次数: {args.max_retries}")
    
    # 构建服务配置
    services_config = {
        'libretranslate_urls': args.libretranslate_urls,
        'libretranslate_tokens': tokens_map,
        'use_mymemory': not args.disable_mymemory,
        'deepl_auth_key': args.deepl_auth_key,
        'use_ollama': args.enable_ollama,
        'ollama_model': args.ollama_model,
        'ollama_url': args.ollama_url
    }
    
    # 检查源目录是否存在
    if not os.path.exists(args.source_dir):
        print(f"错误: 源目录 {args.source_dir} 不存在")
        sys.exit(1)
    
    # 处理目录
    stats, failed_files = process_directory_with_fallback(
        args.source_dir, 
        args.target_dir, 
        args.source_lang, 
        args.target_lang, 
        services_config,
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