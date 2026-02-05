#!/usr/bin/env python3
"""
Ollama 翻译进度监控脚本
实时显示翻译进度：已翻译数量/总数量
"""

import os
import time
import argparse
from pathlib import Path


def get_translation_stats(source_dir='temp_for_translation', target_dir='docs'):
    """
    获取翻译统计信息
    :param source_dir: 源目录（待翻译文件）
    :param target_dir: 目标目录（已翻译文件）
    :return: (已翻译数量, 总数量, 待翻译数量)
    """
    # 统计待翻译文件数量
    source_md_files = 0
    source_path = Path(source_dir)
    if source_path.exists():
        source_md_files = len([f for f in source_path.rglob('*.md')])
        # 包括子目录中的文件
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.lower().endswith('.md'):
                    source_md_files += 1
    
    # 重新计算，使用更准确的方法
    if source_path.exists():
        source_md_files = len(list(source_path.rglob('*.md')))
    
    # 统计已翻译文件数量
    target_md_files = 0
    target_path = Path(target_dir)
    if target_path.exists():
        target_md_files = len(list(target_path.rglob('*.md')))
    
    # 总数 = 已翻译 + 待翻译
    total = target_md_files + source_md_files
    
    return target_md_files, total, source_md_files


def display_progress_bar(current, total, bar_length=50):
    """
    显示进度条
    :param current: 当前进度
    :param total: 总数
    :param bar_length: 进度条长度
    """
    if total == 0:
        percent = 0
        progress_bar = '[' + '-' * bar_length + ']'
    else:
        percent = round(100 * current / total, 2)
        filled_length = int(bar_length * current // total)
        progress_bar = '[' + '█' * filled_length + '░' * (bar_length - filled_length) + ']'
    
    print(f'\r翻译进度: {progress_bar} {current}/{total} ({percent}%)', end='', flush=True)


def monitor_translation_progress(source_dir='temp_for_translation', target_dir='docs', interval=3):
    """
    实时监控翻译进度
    :param source_dir: 源目录
    :param target_dir: 目标目录
    :param interval: 刷新间隔（秒）
    """
    print("开始监控 Ollama 翻译进度...")
    print("按 Ctrl+C 停止监控")
    print("="*60)
    
    try:
        while True:
            translated, total, remaining = get_translation_stats(source_dir, target_dir)
            
            if total > 0:
                display_progress_bar(translated, total)
            else:
                print(f'\r等待翻译开始... 已翻译: {translated}, 总计: {total}, 待翻译: {remaining}', end='', flush=True)
            
            time.sleep(interval)
            
            # 检查是否已完成
            if remaining == 0 and translated > 0:
                print(f"\n\n🎉 翻译完成！共翻译 {translated} 个文件")
                break
                
    except KeyboardInterrupt:
        print(f"\n\n⏹️  监控已停止")
        translated, total, remaining = get_translation_stats(source_dir, target_dir)
        print(f"最终统计:")
        print(f"  已翻译文件: {translated}")
        print(f"  总文件数: {total}")
        print(f"  待翻译文件: {remaining}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='监控 Ollama 翻译进度')
    parser.add_argument('--source-dir', default='temp_for_translation', help='源目录路径 (默认: temp_for_translation)')
    parser.add_argument('--target-dir', default='docs', help='目标目录路径 (默认: docs)')
    parser.add_argument('--interval', type=int, default=3, help='刷新间隔（秒，默认: 3）')
    
    args = parser.parse_args()
    
    monitor_translation_progress(args.source_dir, args.target_dir, args.interval)