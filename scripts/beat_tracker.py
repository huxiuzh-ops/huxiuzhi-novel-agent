# beat_tracker.py
# 小说 Agent 通用伏笔追踪脚本
# 用途：检查 beats/TRACKING.md 中的伏笔状态，标记逾期未回收项

import os
import re
import sys
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# 使用说明
# ─────────────────────────────────────────────────────────────
# 运行方式：python beat_tracker.py <路径/to/workspace> [当前章节号]
# 示例：python beat_tracker.py ./my-novel 50
#   当前写到第50章，检查伏笔状态
#
# 功能：
# 1. 读取 beats/TRACKING.md
# 2. 检查每个伏笔的状态
# 3. 标记逾期未回收的伏笔（当前章节 > 计划回收章节）
# 4. 标记已触发的伏笔
# 5. 检查是否需要回收
#
# 输出格式：
#   [OK] 伏笔状态良好
#   [WARNING] 伏笔 B001 已逾期（计划ch050，当前ch070）
#   [INFO] 伏笔 B003 已在 ch055 触发，等待正式回收
# ─────────────────────────────────────────────────────────────

def load_tracking_file(beats_dir):
    """加载伏笔追踪表"""
    tracking_path = os.path.join(beats_dir, 'TRACKING.md')
    try:
        with open(tracking_path, 'r', encoding='utf-8') as f:
            return f.read(), tracking_path
    except FileNotFoundError:
        return None, tracking_path
    except Exception as e:
        print(f"[ERROR] 无法读取伏笔追踪文件: {e}")
        return None, None

def parse_beats_table(content):
    """解析伏笔总表，提取各伏笔信息"""
    beats = []
    
    # 找到表格（Markdown 表格格式）
    lines = content.split('\n')
    in_table = False
    header_found = False
    
    for i, line in enumerate(lines):
        # 跳过标题和说明部分
        if line.startswith('#'):
            continue
        
        # 检测表格开始
        if '| ID |' in line or '|ID|' in line:
            in_table = True
            header_found = True
            continue
        
        # 检测表格结束（空行或非表格行）
        if in_table and not line.strip():
            in_table = False
            continue
        
        if not in_table or not header_found:
            continue
        
        # 解析表格行
        cells = [c.strip() for c in line.split('|')]
        cells = [c for c in cells if c]  # 去掉空单元格
        
        if len(cells) >= 6:
            beat_id = cells[0]
            beat_type = cells[1]
            description = cells[2]
            planted_ch = cells[3].replace('ch', '').strip()
            planned_ch = cells[4].replace('ch', '').strip()
            status = cells[5].lower().strip()
            
            try:
                planted_num = int(planted_ch) if planted_ch.isdigit() else 0
                planned_num = int(planned_ch) if planned_ch.isdigit() else 0
            except ValueError:
                planted_num = 0
                planned_num = 0
            
            beats.append({
                'id': beat_id,
                'type': beat_type,
                'description': description,
                'planted_ch': planted_ch,
                'planned_ch': planned_ch,
                'planned_num': planned_num,
                'status': status,
                'line_num': i + 1
            })
    
    return beats

def check_beat_status(beats, current_chapter):
    """检查伏笔状态"""
    warnings = []
    infos = []
    
    for beat in beats:
        status = beat['status']
        planned = beat['planned_num']
        
        if status == 'resolved':
            # 已回收，检查是否在计划章节内
            infos.append(f"[OK] 伏笔 {beat['id']} 已回收 ✅")
        
        elif status == 'triggered':
            # 已触发但未正式回收
            infos.append(f"[INFO] 伏笔 {beat['id']} 已在 ch{beat['planted_ch']} 触发，等待正式回收 ⏳")
        
        elif status == 'pending':
            if planned > 0 and current_chapter > planned:
                # 逾期
                overdue_by = current_chapter - planned
                warnings.append(
                    f"[WARNING] 伏笔 {beat['id']} 已逾期！"
                    f"计划回收 ch{planned}，当前 ch{current_chapter}（已超过 {overdue_by} 章）| {beat['description'][:50]}..."
                )
            elif planned > 0 and current_chapter >= planned - 3 and current_chapter <= planned + 2:
                # 临近回收窗口
                infos.append(f"[INFO] 伏笔 {beat['id']} 临近回收窗口（计划 ch{planned}，当前 ch{current_chapter}）⚠️")
            else:
                infos.append(f"[OK] 伏笔 {beat['id']} 状态正常 | {beat['description'][:40]}...")
        
        else:
            warnings.append(f"[WARNING] 伏笔 {beat['id']} 状态未知: '{beat['status']}' | 第{beat['line_num']}行")
    
    return warnings, infos

def main():
    if len(sys.argv) < 2:
        print("用法: python beat_tracker.py <路径/to/workspace> [当前章节号]")
        print("示例: python beat_tracker.py ./my-novel 50")
        sys.exit(1)
    
    workspace_path = sys.argv[1]
    current_chapter = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    print(f"=" * 50)
    print(f"小说 Agent 伏笔追踪检查")
    print(f"检查路径: {workspace_path}")
    if current_chapter > 0:
        print(f"当前章节: ch{current_chapter}")
    print(f"=" * 50)
    print()
    
    # 加载伏笔追踪表
    content, tracking_path = load_tracking_file(os.path.join(workspace_path, 'beats'))
    
    if content is None:
        print(f"[ERROR] 未找到伏笔追踪文件: {tracking_path}")
        print("请确保 beats/TRACKING.md 存在")
        sys.exit(1)
    
    # 解析伏笔表
    beats = parse_beats_table(content)
    
    if not beats:
        print("[INFO] 伏笔追踪表中暂无登记的伏笔")
        print("在 TRACKING.md 中添加伏笔后，此脚本会自动追踪")
        return
    
    print(f"共追踪 {len(beats)} 个伏笔")
    print()
    
    # 检查状态
    warnings, infos = check_beat_status(beats, current_chapter)
    
    # 输出结果
    if warnings:
        print("⚠️ 需要关注的伏笔：")
        for w in warnings:
            print(w)
        print()
    
    if infos:
        print("伏笔状态总览：")
        for info in infos:
            print(info)
    
    print()
    if not warnings:
        print("✅ 没有严重问题")
    else:
        print(f"发现 {len(warnings)} 个需要关注的问题")

if __name__ == '__main__':
    main()
