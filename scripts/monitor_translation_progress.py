#!/usr/bin/env python3
"""
监控翻译进度的脚本
实时报告翻译进度百分比
"""

import os
import sys
import time
import threading
from pathlib import Path


class TranslationProgressMonitor:
    def __init__(self, source_dir, target_dir):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.source_files = []
        self.completed_files = []
        self.lock = threading.Lock()
        
    def get_file_list(self):
        """获取源目录中的所有文件"""
        if not self.source_dir.exists():
            return []
        
        files = []
        for root, dirs, filenames in os.walk(self.source_dir):
            for filename in filenames:
                if filename.endswith(('.md', '.txt', '.html', '.htm')):
                    files.append(Path(root) / filename)
        return files
    
    def get_completion_percentage(self):
        """计算完成百分比"""
        with self.lock:
            total = len(self.source_files)
            completed = len(self.completed_files)
            
            if total == 0:
                return 0, 0, 0
            
            return (completed / total) * 100, completed, total
    
    def update_completed_files(self):
        """更新已完成文件列表"""
        if not self.target_dir.exists():
            return
        
        completed = []
        for root, dirs, filenames in os.walk(self.target_dir):
            for filename in filenames:
                if filename.endswith(('.md', '.txt', '.html', '.htm')):
                    completed.append(filename)
        
        with self.lock:
            self.completed_files = completed
    
    def start_monitoring(self, interval=2):
        """开始监控翻译进度"""
        print(f"开始监控翻译进度...")
        print(f"源目录: {self.source_dir}")
        print(f"目标目录: {self.target_dir}")
        print("-" * 50)
        
        while True:
            self.source_files = self.get_file_list()
            self.update_completed_files()
            
            percentage, completed, total = self.get_completion_percentage()
            
            print(f"\r进度: {percentage:.1f}% ({completed}/{total} 文件)", end="", flush=True)
            
            if completed >= total and total > 0:
                print(f"\n\n✅ 翻译完成！{completed}/{total} 文件已翻译")
                break
                
            time.sleep(interval)


def main():
    if len(sys.argv) < 3:
        print("使用方法: python monitor_translation_progress.py <源目录> <目标目录>")
        print("例如: python monitor_translation_progress.py temp_for_translation docs")
        return
    
    source_dir = sys.argv[1]
    target_dir = sys.argv[2]
    
    monitor = TranslationProgressMonitor(source_dir, target_dir)
    monitor.start_monitoring()


if __name__ == "__main__":
    main()