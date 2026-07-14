import uuid
import time
from backend.utils.database import save_session, get_session, save_case, get_case, save_game_save, get_game_save
from backend.services.case_generator import generate_case
from backend.models.case_model import GameState

def create_new_game(topic="悬疑", difficulty="medium", scene="现代都市"):
    case_data, errors = generate_case(topic, difficulty, scene)
    if errors:
        return None, errors
    
    save_case(case_data['case_id'], case_data)
    
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    game_state = GameState(
        current_stage="intro",
        unlocked_clue_ids=[],
        interrogated_suspect_ids=[],
        dialog_history=[],
        player_choices=[]
    )
    
    save_session(session_id, case_data['case_id'], game_state.dict())
    
    return {
        'session_id': session_id,
        'case_id': case_data['case_id'],
        'case_data': case_data,
        'game_state': game_state.dict()
    }, None

def get_game_session(session_id):
    session = get_session(session_id)
    if not session:
        return None
    
    case_data = get_case(session['case_id'])
    if not case_data:
        return None
    
    return {
        'session_id': session['session_id'],
        'case_id': session['case_id'],
        'case_data': case_data,
        'game_state': session['game_state']
    }

def update_game_state(session_id, updates):
    session = get_session(session_id)
    if not session:
        return False
    
    game_state = session['game_state']
    
    if 'current_stage' in updates:
        game_state['current_stage'] = updates['current_stage']
    
    if 'unlocked_clue_ids' in updates:
        game_state['unlocked_clue_ids'] = updates['unlocked_clue_ids']
    
    if 'interrogated_suspect_ids' in updates:
        game_state['interrogated_suspect_ids'] = updates['interrogated_suspect_ids']
    
    if 'dialog_history' in updates:
        game_state['dialog_history'] = updates['dialog_history']
    
    if 'player_choices' in updates:
        game_state['player_choices'] = updates['player_choices']
    
    save_session(session_id, session['case_id'], game_state)
    return True

def add_clue_to_session(session_id, clue_id):
    session = get_session(session_id)
    if not session:
        return False
    
    game_state = session['game_state']
    
    if clue_id not in game_state['unlocked_clue_ids']:
        game_state['unlocked_clue_ids'].append(clue_id)
        save_session(session_id, session['case_id'], game_state)
    
    return True

def add_interrogated_suspect(session_id, suspect_id):
    session = get_session(session_id)
    if not session:
        return False
    
    game_state = session['game_state']
    
    if suspect_id not in game_state['interrogated_suspect_ids']:
        game_state['interrogated_suspect_ids'].append(suspect_id)
        save_session(session_id, session['case_id'], game_state)
    
    return True

def add_dialog_entry(session_id, role, content):
    session = get_session(session_id)
    if not session:
        return False
    
    game_state = session['game_state']
    
    game_state['dialog_history'].append({
        'role': role,
        'content': content,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })
    
    if len(game_state['dialog_history']) > 20:
        game_state['dialog_history'] = game_state['dialog_history'][-20:]
    
    save_session(session_id, session['case_id'], game_state)
    return True

def add_player_choice(session_id, choice):
    session = get_session(session_id)
    if not session:
        return False
    
    game_state = session['game_state']
    
    game_state['player_choices'].append({
        'choice': choice,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })
    
    save_session(session_id, session['case_id'], game_state)
    return True

def save_game(session_id, user_id, save_name):
    session = get_session(session_id)
    if not session:
        return None
    
    case_data = get_case(session['case_id'])
    if not case_data:
        return None
    
    save_id = f"save_{uuid.uuid4().hex[:8]}"
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    
    save_data = {
        'save_id': save_id,
        'user_id': user_id,
        'create_time': now,
        'update_time': now,
        'save_name': save_name,
        'case_data': case_data,
        'game_state': session['game_state']
    }
    
    save_game_save(save_data)
    return save_data

def load_game(save_id):
    save_data = get_game_save(save_id)
    if not save_data:
        return None
    
    new_session_id = str(uuid.uuid4())
    case_data = save_data['case_data']
    game_state = save_data['game_state']
    
    save_case(case_data['case_id'], case_data)
    save_session(new_session_id, case_data['case_id'], game_state)
    
    return {
        'session_id': new_session_id,
        'case_data': case_data,
        'game_state': game_state,
        'save_name': save_data['save_name']
    }