#!/usr/bin/env python3
"""
实时翻译进度监控脚本
显示当前翻译进度：已翻译数量/估计总数
"""

import os
import time
import subprocess
from pathlib import Path


def get_file_count(directory, extension='.md'):
    """统计目录中指定扩展名的文件数量"""
    if not os.path.exists(directory):
        return 0
    
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extension):
                count += 1
    return count


def get_translated_count(docs_dir='docs'):
    """获取已翻译的文件数量"""
    return get_file_count(docs_dir)


def get_remaining_count(source_dir='temp_for_translation'):
    """获取待翻译的文件数量"""
    return get_file_count(source_dir)


def main():
    print("实时翻译进度监控")
    print("="*50)
    
    try:
        while True:
            # 获取统计数据
            translated = get_translated_count()
            remaining = get_remaining_count()
            estimated_total = translated + remaining  # 估算总数
            
            # 显示进度
            if estimated_total > 0:
                progress_percent = (translated / estimated_total) * 100
                bar_length = 40
                filled_length = int(bar_length * translated // estimated_total)
                progress_bar = '█' * filled_length + '░' * (bar_length - filled_length)
                
                print(f'\r进度: |{progress_bar}| {translated}/{estimated_total} '
                      f'({progress_percent:.1f}%) - 剩余: {remaining}', end='', flush=True)
            else:
                print(f'\r进度: 等待翻译开始... - 已翻译: {translated}, 待翻译: {remaining}', 
                      end='', flush=True)
            
            time.sleep(3)  # 每3秒更新一次
            
    except KeyboardInterrupt:
        print("\n\n监控已停止")
        
        # 显示最终统计
        translated = get_translated_count()
        remaining = get_remaining_count()
        estimated_total = translated + remaining
        
        print(f"最终统计:")
        print(f"- 已翻译文件: {translated}")
        print(f"- 待翻译文件: {remaining}")
        print(f"- 估算总数: {estimated_total}")


if __name__ == "__main__":
    main()