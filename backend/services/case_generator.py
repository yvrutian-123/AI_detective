import uuid
import json
from backend.models.case_model import CaseData, CaseInfo, Victim, Suspect, TrueKiller, Clue

def generate_sample_case():
    case_id = f"case_{uuid.uuid4().hex[:8]}"
    
    case_info = CaseInfo(
        case_name="书房迷案",
        background="现代都市别墅，一场暴雨的夜晚，企业老板被发现死于书房",
        victim=Victim(
            name="张明",
            identity="45岁，某科技公司CEO",
            death_cause="氰化物中毒"
        )
    )
    
    suspects = [
        Suspect(
            id="s1",
            name="李婷",
            motive="丈夫出轨，遗产纠纷",
            alibi="案发时在客厅看电视，管家可以作证",
            secret="私下转移了公司资产"
        ),
        Suspect(
            id="s2",
            name="王强",
            motive="被张明开除，怀恨在心",
            alibi="案发时在自己房间睡觉",
            secret="曾威胁要报复张明"
        ),
        Suspect(
            id="s3",
            name="刘管家",
            motive="长期被克扣工资",
            alibi="案发时在厨房准备夜宵",
            secret="偷偷挪用了家里的钱财"
        ),
        Suspect(
            id="s4",
            name="张小明",
            motive="与父亲关系紧张，争夺公司控制权",
            alibi="案发时在车库修车",
            secret="欠了一大笔赌债"
        )
    ]
    
    true_killer = TrueKiller(
        suspect_id="s1",
        modus_operandi="在张明的茶杯中投放氰化物，趁他不注意时调换了杯子",
        key_flaw="手上残留了微量氰化物，在擦拭杯子时留下了痕迹"
    )
    
    clue_library = [
        Clue(
            id="c1",
            content="死者茶杯中检测到氰化物残留",
            type="critical",
            location="书房书桌",
            related_suspect="s1"
        ),
        Clue(
            id="c2",
            content="李婷房间发现了一包未用完的氰化物粉末",
            type="critical",
            location="李婷的卧室",
            related_suspect="s1"
        ),
        Clue(
            id="c3",
            content="李婷手上有轻微的化学灼伤痕迹",
            type="critical",
            location="李婷的卧室",
            related_suspect="s1"
        ),
        Clue(
            id="c4",
            content="王强房间有一把水果刀，上面没有血迹",
            type="distraction",
            location="王强的卧室",
            related_suspect="s2"
        ),
        Clue(
            id="c5",
            content="王强手机里有威胁张明的短信",
            type="distraction",
            location="王强的卧室",
            related_suspect="s2"
        ),
        Clue(
            id="c6",
            content="刘管家账本上有不明支出",
            type="distraction",
            location="书房保险柜",
            related_suspect="s3"
        ),
        Clue(
            id="c7",
            content="张小明的银行账户有大笔欠款",
            type="distraction",
            location="张小明的卧室",
            related_suspect="s4"
        ),
        Clue(
            id="c8",
            content="书房窗户是从内部反锁的",
            type="background",
            location="书房",
            related_suspect=None
        ),
        Clue(
            id="c9",
            content="案发当晚只有家人和管家在别墅内",
            type="background",
            location="别墅",
            related_suspect=None
        ),
        Clue(
            id="c10",
            content="张明死前正在签署一份股权转让协议",
            type="background",
            location="书房书桌",
            related_suspect=None
        )
    ]
    
    case_data = CaseData(
        case_id=case_id,
        case_info=case_info,
        suspects=suspects,
        true_killer=true_killer,
        clue_library=clue_library
    )
    
    return case_data.dict()

def validate_case(case_data):
    errors = []
    
    suspect_ids = [s['id'] for s in case_data.get('suspects', [])]
    killer_id = case_data.get('true_killer', {}).get('suspect_id')
    
    if killer_id not in suspect_ids:
        errors.append("真凶ID不在嫌疑人列表中")
    
    critical_clues = [c for c in case_data.get('clue_library', []) if c['type'] == 'critical']
    if len(critical_clues) < 3:
        errors.append(f"关键线索数量不足（当前{len(critical_clues)}条，至少需要3条）")
    
    for suspect in case_data.get('suspects', []):
        suspect_clues = [c for c in case_data.get('clue_library', []) if c['related_suspect'] == suspect['id']]
        if len(suspect_clues) == 0:
            errors.append(f"嫌疑人{suspect['name']}没有关联线索")
    
    return errors

def generate_case(topic="悬疑", difficulty="medium", scene="现代都市"):
    case_data = generate_sample_case()
    errors = validate_case(case_data)
    
    if errors:
        return None, errors
    
    return case_data, None