#!/usr/bin/env python3
"""
Monitor changes in docs directory
"""
import time
import os
from pathlib import Path
import subprocess

def get_docs_stats():
    """Get current statistics about docs directory"""
    docs_path = Path("docs")
    md_files = list(docs_path.rglob("*.md"))
    total_files = len(md_files)
    
    # Get recent changes
    try:
        result = subprocess.run([
            "git", "log", "--since='1 hour ago'", "--pretty=format:%h %ad %s", 
            "--date=iso", "--name-only", "--no-merges"
        ], capture_output=True, text=True, cwd=docs_path.parent)
        
        if result.returncode == 0:
            recent_commits = result.stdout.strip()
        else:
            recent_commits = "No recent commits found"
    except Exception as e:
        recent_commits = f"Error getting git log: {e}"
    
    return total_files, recent_commits

def monitor_changes():
    print("Monitoring docs/ directory changes...")
    print("="*50)
    
    initial_total, initial_commits = get_docs_stats()
    print(f"Initial MD files count: {initial_total}")
    print(f"Recent commits:\n{initial_commits}")
    print("-"*50)
    
    last_total = initial_total
    
    while True:
        try:
            current_total, _ = get_docs_stats()
            
            if current_total != last_total:
                print(f"[{time.strftime('%H:%M:%S')}] File count changed: {last_total} -> {current_total}")
                if current_total > last_total:
                    print(f"  New files added: {current_total - last_total}")
                else:
                    print(f"  Files removed: {last_total - current_total}")
                last_total = current_total
            
            # Also check for recently modified files
            docs_path = Path("docs")
            recent_files = []
            for f in docs_path.rglob("*.md"):
                if f.stat().st_mtime > time.time() - 300:  # Modified in last 5 minutes
                    recent_files.append((f, f.stat().st_mtime))
            
            if recent_files:
                recent_files.sort(key=lambda x: x[1], reverse=True)
                print(f"[{time.strftime('%H:%M:%S')}] Recently modified files:")
                for file_path, mtime in recent_files[:5]:  # Show top 5
                    print(f"  {file_path} ({time.ctime(mtime)})")
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\nStopping monitor...")
            break
        except Exception as e:
            print(f"Error during monitoring: {e}")
            time.sleep(30)

if __name__ == "__main__":
    monitor_changes()