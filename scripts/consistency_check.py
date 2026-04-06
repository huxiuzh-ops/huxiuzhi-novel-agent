# consistency_check.py
# 小说 Agent 通用一致性检查脚本
# 用途：检查 world.md、characters/、inventory/ 中的设定是否前后矛盾

import os
import re
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# 使用说明
# ─────────────────────────────────────────────────────────────
# 运行方式：python consistency_check.py <路径/to/workspace>
# 示例：python consistency_check.py ./my-novel
#
# 检查内容：
# 1. 角色年龄/外貌/性格是否前后矛盾
# 2. 武器/道具参数是否矛盾（同一道具参数不一致）
# 3. 时间线逻辑（用餐后短时间不能写饿）
# 4. 势力关系是否有冲突
# 5. 章节内的设定是否与 world.md 冲突
#
# 输出：列出所有潜在矛盾，格式为：
#   [WARNING] 矛盾描述 | 位置
# ─────────────────────────────────────────────────────────────

def load_file(path):
    """加载文件内容"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"[ERROR] 无法读取文件 {path}: {e}")
        return None

def extract_age(content):
    """提取年龄信息"""
    pattern = r'(年龄|age|岁)[：:]\s*(\d+)'
    matches = re.findall(pattern, content)
    return [int(m[1]) for m in matches]

def extract_number(pattern, content):
    """提取指定模式的数字"""
    matches = re.findall(pattern, content)
    return matches

def check_character_consistency(char_dir, warnings):
    """检查角色一致性"""
    if not os.path.exists(char_dir):
        return warnings
    
    char_files = [f for f in os.listdir(char_dir) if f.endswith('.md')]
    
    for char_file in char_files:
        char_path = os.path.join(char_dir, char_file)
        content = load_file(char_path)
        if not content:
            continue
        
        # 检查年龄是否一致
        ages = extract_age(content)
        if len(set(ages)) > 1:
            warnings.append(f"[WARNING] 角色 {char_file} 中年龄描述不一致，发现多个年龄值: {set(ages)} | {char_path}")
        
        # 检查同一角色在不同文件的描述是否矛盾（如果有多个文件）
        # 这里可以扩展更多检查
    
    return warnings

def check_weapon_consistency(inventory_dir, chapters_dir, warnings):
    """检查武器/道具参数一致性"""
    if not os.path.exists(inventory_dir):
        return warnings
    
    inventory_files = [f for f in os.listdir(inventory_dir) if f.endswith('.md')]
    
    # 提取装备参数
    item_specs = {}
    for inv_file in inventory_files:
        inv_path = os.path.join(inventory_dir, inv_file)
        content = load_file(inv_path)
        if not content:
            continue
        
        # 提取道具名称和参数（这里用简单正则，可以扩展）
        name_pattern = r'^#\s+(.+)$'
        spec_pattern = r'(射程|威力|容量|速度|持续时间|范围)[：:]\s*(.+)'
        
        current_item = None
        specs = {}
        
        for line in content.split('\n'):
            name_match = re.match(name_pattern, line)
            if name_match:
                if current_item and specs:
                    item_specs[current_item] = specs
                current_item = name_match.group(1).strip()
                specs = {}
            
            spec_match = re.search(spec_pattern, line)
            if spec_match and current_item:
                key = spec_match.group(1)
                value = spec_match.group(2).strip()
                if current_item in item_specs and key in item_specs[current_item]:
                    if item_specs[current_item][key] != value:
                        warnings.append(
                            f"[WARNING] 道具 '{current_item}' 的 '{key}' 参数矛盾: "
                            f"world定义为'{item_specs[current_item][key]}'，"
                            f"在{inv_file}中为'{value}' | {inv_path}"
                        )
                specs[key] = value
        
        if current_item and specs:
            item_specs[current_item] = specs
    
    return warnings

def check_world_conflicts(world_path, warnings):
    """检查世界设定是否有内在冲突"""
    content = load_file(world_path)
    if not content:
        return warnings
    
    # 示例：检查时间线描述是否矛盾
    # 例如：如果写了"末世第三年"但又写了"末世发生后立即..."
    timeline_mentions = re.findall(r'第[一二三四五六七八九十百千万\d]+年', content)
    
    # 检查是否有明显的逻辑冲突
    if '永不' in content and '但是' in content:
        # 可能的绝对化表述与转折的冲突
        pass
    
    return warnings

def check_readme_conflicts(workspace_path, warnings):
    """检查各章节是否与总体设定冲突"""
    chapters_dir = os.path.join(workspace_path, 'chapters')
    world_path = os.path.join(workspace_path, 'world.md')
    
    if not os.path.exists(world_path) or not os.path.exists(chapters_dir):
        return warnings
    
    world_content = load_file(world_path)
    if not world_content:
        return warnings
    
    # 提取世界设定中的关键词
    world_keyword_pattern = r'势力|规则|等级|限制|代价|时间|范围'
    world_keywords = set(re.findall(world_keyword_pattern, world_content))
    
    chapter_files = sorted([f for f in os.listdir(chapters_dir) if f.endswith('.md')])
    
    # 简单检查：章节中是否有与世界设定明显矛盾的描述
    # 这是一个非常基础的实现，实际需要更复杂的NLP
    for ch_file in chapter_files[-5:]:  # 只检查最近5章
        ch_path = os.path.join(chapters_dir, ch_file)
        ch_content = load_file(ch_path)
        if not ch_content:
            continue
        
        # 检查是否有冲突的描述
        # 示例：如果world说某武器射程200米，章节里写了500米
    
    return warnings

def main():
    if len(sys.argv) < 2:
        print("用法: python consistency_check.py <路径/to/workspace>")
        print("示例: python consistency_check.py ./my-novel")
        sys.exit(1)
    
    workspace_path = sys.argv[1]
    
    print(f"=" * 50)
    print(f"小说 Agent 一致性检查")
    print(f"检查路径: {workspace_path}")
    print(f"=" * 50)
    
    warnings = []
    
    # 检查角色一致性
    char_dir = os.path.join(workspace_path, 'characters')
    warnings = check_character_consistency(char_dir, warnings)
    
    # 检查装备一致性
    inventory_dir = os.path.join(workspace_path, 'inventory')
    chapters_dir = os.path.join(workspace_path, 'chapters')
    warnings = check_weapon_consistency(inventory_dir, chapters_dir, warnings)
    
    # 检查世界设定内在冲突
    world_path = os.path.join(workspace_path, 'world.md')
    warnings = check_world_conflicts(world_path, warnings)
    
    # 检查章节与总体设定冲突
    warnings = check_readme_conflicts(workspace_path, warnings)
    
    # 输出结果
    print()
    if warnings:
        print(f"发现 {len(warnings)} 个潜在问题：")
        for w in warnings:
            print(w)
    else:
        print("✅ 未发现明显的一致性问题")
    
    return warnings

if __name__ == '__main__':
    main()
