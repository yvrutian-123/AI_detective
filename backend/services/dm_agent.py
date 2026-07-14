from backend.services.session_manager import (
    get_game_session, update_game_state, add_clue_to_session,
    add_interrogated_suspect, add_dialog_entry, add_player_choice
)

def generate_intro(case_data):
    case_info = case_data['case_info']
    victim = case_info['victim']
    
    intro_text = f"""
【{case_info['case_name']}】

{case_info['background']}

暴雨如注的夜晚，别墅的书房里传来一声闷响。当管家赶到时，{victim['name']}已经倒在了书桌旁，气息全无。

死者信息：
- 姓名：{victim['name']}
- 身份：{victim['identity']}
- 死因：{victim['death_cause']}

书房的窗户从内部反锁，门也没有被撬动的痕迹。现场只有一杯还冒着热气的茶，和一份尚未签署的文件。

你作为一名经验丰富的侦探，受邀前来调查这起案件。现在，你需要决定从哪里开始调查...
    """.strip()
    
    choices = [
        {"id": "action_inspect_body", "text": "查看尸体", "status": "available"},
        {"id": "action_search_villa", "text": "查看别墅布局", "status": "available"},
        {"id": "action_search_书房", "text": "搜查书房", "status": "available"},
        {"id": "action_search_书房书桌", "text": "搜查书房书桌", "status": "available"},
        {"id": "action_interrogate_s3", "text": "询问管家", "status": "available"},
        {"id": "action_list_suspects", "text": "查看嫌疑人名单", "status": "available"},
        {"id": "action_accuse", "text": "指认凶手", "status": "available"}
    ]
    
    return {
        "stage": "intro",
        "text": intro_text,
        "choices": choices
    }

def generate_investigation_response(session_id, player_action):
    session_data = get_game_session(session_id)
    if not session_data:
        return {"error": "会话不存在"}
    
    case_data = session_data['case_data']
    game_state = session_data['game_state']
    
    add_player_choice(session_id, player_action)
    
    if player_action == "action_inspect_body":
        return handle_inspect_body(session_id, case_data, game_state)
    
    elif player_action == "action_search_study":
        return handle_search_location(session_id, case_data, game_state, "书房")
    
    elif player_action == "action_search_villa":
        return handle_search_villa(session_id, case_data, game_state)
    
    elif player_action == "action_ask_butler":
        return handle_interrogate_suspect(session_id, case_data, game_state, "s3")
    
    elif player_action == "action_list_suspects":
        return handle_list_suspects(session_id, case_data, game_state)
    
    elif player_action.startswith("action_search_"):
        location = player_action.replace("action_search_", "")
        return handle_search_location(session_id, case_data, game_state, location)
    
    elif player_action.startswith("action_interrogate_"):
        suspect_id = player_action.replace("action_interrogate_", "")
        return handle_interrogate_suspect(session_id, case_data, game_state, suspect_id)
    
    elif player_action == "action_accuse":
        return handle_accuse_stage(session_id, case_data, game_state)
    
    elif player_action.startswith("action_select_suspect_"):
        suspect_id = player_action.replace("action_select_suspect_", "")
        return handle_accuse_suspect(session_id, case_data, game_state, suspect_id)
    
    elif player_action == "action_check_cup":
        return handle_check_item(session_id, case_data, game_state, "茶杯", ["书房书桌"])
    
    elif player_action == "action_check_document":
        return handle_check_item(session_id, case_data, game_state, "文件", ["书房书桌"])
    
    elif player_action == "action_check_desk":
        return handle_check_item(session_id, case_data, game_state, "书桌", ["书房", "书房书桌"])
    
    elif player_action == "action_back_to_main":
        return handle_back_to_main(session_id, case_data, game_state)
    
    else:
        return handle_custom_action(session_id, case_data, game_state, player_action)

def handle_inspect_body(session_id, case_data, game_state):
    victim = case_data['case_info']['victim']
    
    text = f"""
你走近{victim['name']}的尸体，仔细观察着现场的细节。

尸体特征：
- {victim['name']}倒在书桌旁的椅子上，双手紧握，表情痛苦
- 嘴角有白色泡沫残留，这是氰化物中毒的典型症状
- 身体已经开始僵硬，死亡时间大约在1-2小时前
- 桌上放着一杯半满的茶，旁边是一支钢笔和一份文件

检查完毕后，你注意到书桌上似乎有一些细微的粉末痕迹...
    """.strip()
    
    choices = [
        {"id": "action_check_cup", "text": "检查茶杯", "status": "available"},
        {"id": "action_check_document", "text": "检查文件", "status": "available"},
        {"id": "action_check_desk", "text": "检查书桌", "status": "available"},
        {"id": "action_back_to_main", "text": "返回继续其他调查", "status": "available"}
    ]
    
    add_dialog_entry(session_id, "dm", text)
    update_game_state(session_id, {"current_stage": "inspecting_body"})
    
    return {
        "stage": "inspecting_body",
        "text": text,
        "choices": choices
    }

def handle_search_villa(session_id, case_data, game_state):
    text = """
你站在别墅的大厅，环顾四周。这座别墅布局如下：

一楼区域：
- 书房（案发现场）
- 客厅（家人活动区域）
- 厨房（管家工作的地方）
- 车库（停放车辆）

二楼区域：
- 李婷的卧室（死者妻子）
- 王强的卧室（前公司员工）
- 张小明的卧室（死者儿子）
- 客房（空置）

你可以选择前往任何一个房间进行调查。
    """.strip()
    
    choices = generate_next_choices(case_data, game_state)
    
    add_dialog_entry(session_id, "dm", text)
    
    return {
        "stage": "investigation",
        "text": text,
        "choices": choices
    }

def handle_check_item(session_id, case_data, game_state, item_name, locations):
    text = f"""
你仔细检查了{item_name}。

"""
    
    new_clues = []
    for location in locations:
        new_clues.extend(find_clues_by_location(case_data, game_state, location))
    
    if new_clues:
        for clue in new_clues:
            add_clue_to_session(session_id, clue['id'])
            clue_type_text = {
                "critical": "【关键线索】",
                "distraction": "【可疑线索】",
                "background": "【背景信息】"
            }.get(clue['type'], "")
            text += f"{clue_type_text}{clue['content']}\n\n"
    else:
        text += "没有发现新的线索。\n"
    
    searched_locations = game_state.get('searched_locations', [])
    for location in locations:
        if location not in searched_locations:
            searched_locations.append(location)
    update_game_state(session_id, {"searched_locations": searched_locations})
    
    choices = [
        {"id": "action_check_cup", "text": "检查茶杯", "status": "available"},
        {"id": "action_check_document", "text": "检查文件", "status": "available"},
        {"id": "action_check_desk", "text": "检查书桌", "status": "available"},
        {"id": "action_back_to_main", "text": "返回继续其他调查", "status": "available"}
    ]
    
    add_dialog_entry(session_id, "dm", text)
    
    return {
        "stage": "inspecting_body",
        "text": text,
        "choices": choices
    }

def handle_back_to_main(session_id, case_data, game_state):
    text = "你结束了对尸体的检查，回到了别墅大厅。\n"
    
    choices = generate_next_choices(case_data, game_state)
    
    add_dialog_entry(session_id, "dm", text)
    update_game_state(session_id, {"current_stage": "investigation"})
    
    return {
        "stage": "investigation",
        "text": text,
        "choices": choices
    }

def handle_search_location(session_id, case_data, game_state, location):
    text = f"""
你来到{location}，开始仔细搜查这里的每一个角落。

搜索过程中，你发现了一些值得注意的物品：
    """.strip()
    
    new_clues = find_clues_by_location(case_data, game_state, location)
    
    if new_clues:
        for clue in new_clues:
            add_clue_to_session(session_id, clue['id'])
            clue_type_text = {
                "critical": "【关键线索】",
                "distraction": "【可疑线索】",
                "background": "【背景信息】"
            }.get(clue['type'], "")
            text += f"\n\n{clue_type_text}{clue['content']}"
    else:
        text += "\n\n这里似乎没有发现什么新线索..."
    
    searched_locations = game_state.get('searched_locations', [])
    if location not in searched_locations:
        searched_locations.append(location)
        update_game_state(session_id, {"searched_locations": searched_locations})
    
    choices = generate_next_choices(case_data, game_state)
    
    add_dialog_entry(session_id, "dm", text)
    update_game_state(session_id, {"current_stage": "investigation"})
    
    return {
        "stage": "investigation",
        "text": text,
        "choices": choices
    }

def handle_interrogate_suspect(session_id, case_data, game_state, suspect_id):
    suspect = next((s for s in case_data['suspects'] if s['id'] == suspect_id), None)
    
    if not suspect:
        return {"error": "嫌疑人不存在"}
    
    add_interrogated_suspect(session_id, suspect_id)
    
    text = f"""
你开始盘问{suspect['name']}。

{suspect['name']}的供词：
"案发时我{suspect['alibi']}。我和{case_data['case_info']['victim']['name']}的关系一直很好，我没有理由伤害他。"

在盘问过程中，你注意到{suspect['name']}的眼神有些闪烁，似乎在隐瞒什么...
    """.strip()
    
    new_clues = find_clues_by_suspect(case_data, game_state, suspect_id)
    for clue in new_clues:
        add_clue_to_session(session_id, clue['id'])
        clue_type_text = {
            "critical": "【关键线索】",
            "distraction": "【可疑线索】",
            "background": "【背景信息】"
        }.get(clue['type'], "")
        text += f"\n\n{clue_type_text}{clue['content']}"
    
    choices = generate_next_choices(case_data, game_state)
    
    add_dialog_entry(session_id, "dm", text)
    update_game_state(session_id, {"current_stage": "investigation"})
    
    return {
        "stage": "investigation",
        "text": text,
        "choices": choices
    }

def handle_list_suspects(session_id, case_data, game_state):
    text = "以下是本案的嫌疑人名单：\n\n"
    
    for suspect in case_data['suspects']:
        status = "已盘问" if suspect['id'] in game_state['interrogated_suspect_ids'] else "未盘问"
        text += f"""【{suspect['name']}】
- 身份：{get_suspect_role(suspect)}
- 动机：{suspect['motive'][:20]}...
- 状态：{status}

"""
    
    choices = generate_next_choices(case_data, game_state)
    
    add_dialog_entry(session_id, "dm", text)
    
    return {
        "stage": "investigation",
        "text": text,
        "choices": choices
    }

def handle_accuse_stage(session_id, case_data, game_state):
    critical_clues = [c for c in case_data['clue_library'] if c['type'] == 'critical']
    unlocked_critical_clues = [c for c in critical_clues if c['id'] in game_state['unlocked_clue_ids']]
    
    if len(unlocked_critical_clues) < 2 and len(game_state['unlocked_clue_ids']) < 5:
        text = "你觉得还需要更多的证据才能做出判断。继续调查吧。"
        choices = generate_next_choices(case_data, game_state)
        add_dialog_entry(session_id, "dm", text)
        return {
            "stage": "investigation",
            "text": text,
            "choices": choices
        }
    
    text = "你决定指认凶手。请选择你认为是凶手的人：\n\n"
    
    choices = []
    for suspect in case_data['suspects']:
        choices.append({
            "id": f"action_select_suspect_{suspect['id']}",
            "text": f"指认 {suspect['name']}"
        })
    
    choices.append({
        "id": "action_cancel_accuse",
        "text": "取消指认，继续调查"
    })
    
    add_dialog_entry(session_id, "dm", text)
    update_game_state(session_id, {"current_stage": "accusation"})
    
    return {
        "stage": "accusation",
        "text": text,
        "choices": choices
    }

def handle_accuse_suspect(session_id, case_data, game_state, suspect_id):
    true_killer_id = case_data['true_killer']['suspect_id']
    suspect = next((s for s in case_data['suspects'] if s['id'] == suspect_id), None)
    true_killer = next((s for s in case_data['suspects'] if s['id'] == true_killer_id), None)
    
    critical_clues = [c for c in case_data['clue_library'] if c['type'] == 'critical']
    unlocked_critical_clues = [c for c in critical_clues if c['id'] in game_state['unlocked_clue_ids']]
    
    if suspect_id == true_killer_id:
        if len(unlocked_critical_clues) >= 3:
            ending_type = "perfect"
            text = f"""
【完美破案！】

你成功指认出真凶——{true_killer['name']}！

{true_killer['name']}在铁证面前终于承认了罪行：
"{case_data['true_killer']['modus_operandi']}"

关键证据：
"""
            for clue in unlocked_critical_clues:
                text += f"- {clue['content']}\n"
            
            text += f"""

案件复盘：
{true_killer['name']}的动机是{true_killer['motive']}。作案后，{true_killer['name']}以为自己做得天衣无缝，但{case_data['true_killer']['key_flaw']}，这成为了破案的关键。

恭喜你完美解决了这起案件！
"""
        else:
            ending_type = "normal"
            text = f"""
【破案成功！】

你指认出了真凶——{true_killer['name']}！

虽然证据链还不够完整，但你的推理是正确的。{true_killer['name']}最终承认了自己的罪行。

案件真相：
{case_data['true_killer']['modus_operandi']}

继续努力，下次可以收集更多线索再做出判断！
"""
    else:
        ending_type = "fail"
        text = f"""
【指认失败】

很遗憾，{suspect['name']}并不是真凶。

真凶是——{true_killer['name']}！

作案手法：{case_data['true_killer']['modus_operandi']}

关键破绽：{case_data['true_killer']['key_flaw']}

不要气馁，下次调查时记得收集更多线索！
"""
    
    choices = [
        {"id": "action_new_game", "text": "开始新游戏"},
        {"id": "action_replay", "text": "重新挑战"}
    ]
    
    add_dialog_entry(session_id, "dm", text)
    update_game_state(session_id, {"current_stage": "ending"})
    
    return {
        "stage": "ending",
        "ending_type": ending_type,
        "text": text,
        "choices": choices
    }

def handle_custom_action(session_id, case_data, game_state, action):
    text = f"你决定：{action}\n\n"
    
    new_clues = []
    for clue in case_data['clue_library']:
        if clue['id'] not in game_state['unlocked_clue_ids']:
            if (action in clue['content'] or 
                clue['location'] in action or
                any(s['name'] in action for s in case_data['suspects'])):
                new_clues.append(clue)
    
    if new_clues:
        for clue in new_clues:
            add_clue_to_session(session_id, clue['id'])
            clue_type_text = {
                "critical": "【关键线索】",
                "distraction": "【可疑线索】",
                "background": "【背景信息】"
            }.get(clue['type'], "")
            text += f"{clue_type_text}{clue['content']}\n\n"
    else:
        text += "你的行动没有发现新的线索。\n"
    
    choices = generate_next_choices(case_data, game_state)
    
    add_dialog_entry(session_id, "dm", text)
    
    return {
        "stage": "investigation",
        "text": text,
        "choices": choices
    }

def find_clues_by_location(case_data, game_state, location):
    new_clues = []
    for clue in case_data['clue_library']:
        if clue['id'] not in game_state['unlocked_clue_ids']:
            if clue['location'] == location:
                new_clues.append(clue)
    return new_clues

def find_clues_by_suspect(case_data, game_state, suspect_id):
    new_clues = []
    for clue in case_data['clue_library']:
        if clue['id'] not in game_state['unlocked_clue_ids']:
            if clue['related_suspect'] == suspect_id:
                new_clues.append(clue)
    return new_clues

def generate_next_choices(case_data, game_state):
    choices = []
    
    unlocked_clue_ids = game_state.get('unlocked_clue_ids', [])
    searched_locations = game_state.get('searched_locations', [])
    interrogated_ids = game_state.get('interrogated_suspect_ids', [])
    
    choices.append({
        "id": "action_inspect_body",
        "text": "查看尸体"
    })
    
    choices.append({
        "id": "action_search_villa",
        "text": "查看别墅布局"
    })
    
    all_locations = set(clue['location'] for clue in case_data['clue_library'])
    for location in list(all_locations):
        has_locked_clues = any(clue['location'] == location and clue['id'] not in unlocked_clue_ids for clue in case_data['clue_library'])
        has_unlocked_clues = any(clue['location'] == location and clue['id'] in unlocked_clue_ids for clue in case_data['clue_library'])
        
        if location in searched_locations and not has_locked_clues:
            status_text = "（已搜完）"
            status = "searched"
        elif has_unlocked_clues and not has_locked_clues:
            status_text = "（已搜完）"
            status = "searched"
        else:
            status_text = ""
            status = "available"
        
        choices.append({
            "id": f"action_search_{location}",
            "text": f"搜查{location}{status_text}",
            "status": status
        })
    
    for suspect in case_data['suspects']:
        has_locked_clues = any(clue['related_suspect'] == suspect['id'] and clue['id'] not in unlocked_clue_ids for clue in case_data['clue_library'])
        is_interrogated = suspect['id'] in interrogated_ids
        
        if is_interrogated and not has_locked_clues:
            status_text = "（已盘问）"
            status = "interrogated"
        else:
            status_text = ""
            status = "available"
        
        choices.append({
            "id": f"action_interrogate_{suspect['id']}",
            "text": f"盘问{suspect['name']}{status_text}",
            "status": status
        })
    
    choices.append({
        "id": "action_list_suspects",
        "text": "查看嫌疑人名单"
    })
    
    choices.append({
        "id": "action_accuse",
        "text": "指认凶手"
    })
    
    return choices

def get_suspect_role(suspect):
    name = suspect['name']
    if '妻子' in name:
        return "死者妻子"
    elif '管家' in name:
        return "别墅管家"
    elif '儿子' in name or '小明' in name:
        return "死者儿子"
    else:
        return "公司员工"

def get_unlocked_clues(case_data, game_state):
    return [c for c in case_data['clue_library'] if c['id'] in game_state['unlocked_clue_ids']]