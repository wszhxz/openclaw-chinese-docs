#!/usr/bin/env python3
"""
翻译进度监控脚本
实时显示翻译进度：已翻译数量/总数量
"""

import os
import time
import argparse


def get_translation_progress(source_dir='temp_for_translation', target_dir='docs'):
    """
    获取翻译进度
    :param source_dir: 源目录（待翻译文件）
    :param target_dir: 目标目录（已翻译文件）
    :return: (已翻译数量, 总数量, 待翻译数量)
    """
    # 统计待翻译文件数量
    total_files = 0
    if os.path.exists(source_dir):
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.md'):
                    total_files += 1
    
    # 统计已翻译文件数量
    translated_files = 0
    if os.path.exists(target_dir):
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                if file.endswith('.md') and file != 'README.md':
                    translated_files += 1
    
    remaining = total_files  # 假设初始总数就是待翻译数
    if remaining == 0:
        # 如果没有找到待翻译文件，尝试从另一个角度计算
        original_total = len([f for r, d, fs in os.walk('temp_for_translation_original') for f in fs if f.endswith('.md')]) if os.path.exists('temp_for_translation_original') else 232
        remaining = original_total - translated_files
        total_files = original_total
    
    return translated_files, total_files, remaining


def display_progress_bar(current, total, bar_length=50):
    """
    显示进度条
    :param current: 当前进度
    :param total: 总数
    :param bar_length: 进度条长度
    """
    if total == 0:
        percent = 0
        progress_bar = '[]'
    else:
        percent = round(100 * current / total, 2)
        filled_length = int(bar_length * current // total)
        progress_bar = '[' + '=' * filled_length + '>' + '-' * (bar_length - filled_length - 1) + ']'
    
    print(f'\r翻译进度: {progress_bar} {current}/{total} ({percent}%)', end='', flush=True)


def monitor_translation_progress(source_dir='temp_for_translation', target_dir='docs', interval=5):
    """
    实时监控翻译进度
    :param source_dir: 源目录
    :param target_dir: 目标目录
    :param interval: 刷新间隔（秒）
    """
    print("开始监控翻译进度...")
    print("按 Ctrl+C 停止监控")
    
    try:
        while True:
            translated, total, remaining = get_translation_progress(source_dir, target_dir)
            
            # 如果无法确定总数，使用估算值
            if total == 0:
                # 假设原始文件总数是 232（根据之前的日志）
                total = 232
            
            display_progress_bar(translated, total)
            
            time.sleep(interval)
            
            # 检查是否已完成
            if translated >= total and total > 0:
                print(f"\n✅ 翻译完成！共翻译 {translated} 个文件")
                break
                
    except KeyboardInterrupt:
        print(f"\n\n监控已停止。最终进度: {get_translation_progress(source_dir, target_dir)[0]}/{get_translation_progress(source_dir, target_dir)[1]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='监控翻译进度')
    parser.add_argument('--source-dir', default='temp_for_translation', help='源目录路径 (默认: temp_for_translation)')
    parser.add_argument('--target-dir', default='docs', help='目标目录路径 (默认: docs)')
    parser.add_argument('--interval', type=int, default=5, help='刷新间隔（秒，默认: 5）')
    
    args = parser.parse_args()
    
    monitor_translation_progress(args.source_dir, args.target_dir, args.interval)