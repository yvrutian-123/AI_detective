const API_BASE = '/api';

let currentSessionId = null;
let currentCaseData = null;
let currentGameState = null;
let dialogHistory = [];
let currentActionId = null;

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('start-game-btn').addEventListener('click', startNewGame);
    document.getElementById('new-game-btn').addEventListener('click', startNewGame);
    document.getElementById('save-btn').addEventListener('click', saveCurrentGame);
    document.getElementById('load-btn').addEventListener('click', openLoadModal);
    document.getElementById('custom-action-btn').addEventListener('click', handleCustomAction);
    document.getElementById('custom-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleCustomAction();
    });
    document.getElementById('back-btn').addEventListener('click', goBack);

    const suspectModal = document.getElementById('suspect-modal');
    const loadModal = document.getElementById('load-modal');
    const closeBtns = document.querySelectorAll('.close');
    
    closeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            suspectModal.style.display = 'none';
            loadModal.style.display = 'none';
        });
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === suspectModal) {
            suspectModal.style.display = 'none';
        }
        if (e.target === loadModal) {
            loadModal.style.display = 'none';
        }
    });
});

async function startNewGame() {
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/new-game`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentSessionId = data.session_id;
            currentCaseData = data.case_data;
            currentGameState = {
                current_stage: 'intro',
                unlocked_clue_ids: [],
                interrogated_suspect_ids: [],
                dialog_history: [],
                player_choices: []
            };
            
            dialogHistory = [];
            
            renderDialog(data.intro.text);
            renderChoices(data.intro.choices);
            renderSuspects();
            renderClues();
            
            updateBackButton();
        } else {
            alert('创建游戏失败: ' + JSON.stringify(data.detail));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('无法连接到服务器，请确保后端服务已启动');
    } finally {
        hideLoading();
    }
}

async function handleChoice(actionId) {
    if (!currentSessionId) {
        alert('请先开始游戏');
        return;
    }

    try {
        const currentDialog = document.getElementById('dialog-content').innerHTML;
        const currentChoices = Array.from(document.getElementById('choices-area').children).map(btn => ({
            id: btn.dataset.actionId,
            text: btn.textContent
        })).filter(c => c.id);
        
        dialogHistory.push({
            dialog: currentDialog,
            choices: currentChoices
        });
        
        if (dialogHistory.length > 50) {
            dialogHistory = dialogHistory.slice(-50);
        }
        
        currentActionId = actionId;
        showLoading();
        
        const response = await fetch(`${API_BASE}/action/${currentSessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ action: actionId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentGameState = data.game_state;
            
            renderDialog(data.response.text);
            renderChoices(data.response.choices);
            renderSuspects();
            renderClues();
            
            updateBackButton();
            
            if (data.response.stage === 'ending') {
                handleEnding(data.response.ending_type);
            }
        } else {
            alert('操作失败: ' + data.detail);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('服务器错误');
    } finally {
        hideLoading();
    }
}

async function handleCustomAction() {
    const input = document.getElementById('custom-input');
    const action = input.value.trim();
    
    if (!action) return;
    if (!currentSessionId) {
        alert('请先开始游戏');
        return;
    }
    
    input.value = '';
    handleChoice(action);
}

async function saveCurrentGame() {
    if (!currentSessionId) {
        alert('请先开始游戏');
        return;
    }

    const saveName = prompt('请输入存档名称:', '书房迷案-调查中');
    if (!saveName) return;

    try {
        const response = await fetch(`${API_BASE}/save/${currentSessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                user_id: 'default_user',
                save_name: saveName 
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('保存成功！存档ID: ' + data.save_id);
        } else {
            alert('保存失败: ' + data.detail);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('保存失败');
    }
}

function renderDialog(text) {
    const dialogContent = document.getElementById('dialog-content');
    dialogContent.innerHTML = `<div class="dialog-text">${text}</div>`;
    
    const dialogBox = document.getElementById('dialog-box');
    dialogBox.scrollTop = dialogBox.scrollHeight;
}

function renderChoices(choices) {
    const choicesArea = document.getElementById('choices-area');
    choicesArea.innerHTML = '';
    
    if (!choices || choices.length === 0) {
        choicesArea.innerHTML = '<p class="empty-text">暂无可用行动</p>';
        return;
    }
    
    choices.forEach(choice => {
        const btn = document.createElement('button');
        btn.className = 'choice-btn';
        
        if (choice.status === 'searched') {
            btn.classList.add('status-searched');
        } else if (choice.status === 'interrogated') {
            btn.classList.add('status-interrogated');
        }
        
        if (currentActionId === choice.id) {
            btn.classList.add('current-action');
        }
        
        btn.textContent = choice.text;
        btn.dataset.actionId = choice.id;
        btn.onclick = () => handleChoice(choice.id);
        choicesArea.appendChild(btn);
    });
}

function renderSuspects() {
    const suspectList = document.getElementById('suspect-list');
    suspectList.innerHTML = '';
    
    if (!currentCaseData || !currentCaseData.suspects) {
        suspectList.innerHTML = '<p class="empty-text">暂无嫌疑人信息</p>';
        return;
    }
    
    currentCaseData.suspects.forEach(suspect => {
        const isInterrogated = currentGameState && 
            currentGameState.interrogated_suspect_ids &&
            currentGameState.interrogated_suspect_ids.includes(suspect.id);
        
        const item = document.createElement('div');
        item.className = `suspect-item ${isInterrogated ? 'interrogated' : ''}`;
        item.onclick = () => showSuspectDetail(suspect);
        
        item.innerHTML = `
            <div class="suspect-name">${suspect.name}</div>
            <div class="suspect-status">${isInterrogated ? '已盘问' : '未盘问'}</div>
        `;
        
        suspectList.appendChild(item);
    });
}

function renderClues() {
    const clueList = document.getElementById('clue-list');
    clueList.innerHTML = '';
    
    if (!currentCaseData || !currentCaseData.clue_library) {
        clueList.innerHTML = '<p class="empty-text">暂无线索</p>';
        return;
    }
    
    const unlockedClueIds = currentGameState ? currentGameState.unlocked_clue_ids || [] : [];
    
    const unlockedClues = currentCaseData.clue_library.filter(clue => 
        unlockedClueIds.includes(clue.id)
    );
    
    if (unlockedClues.length === 0) {
        clueList.innerHTML = '<p class="empty-text">暂无线索</p>';
        return;
    }
    
    unlockedClues.forEach(clue => {
        const item = document.createElement('div');
        item.className = `clue-item ${clue.type}`;
        
        const typeText = {
            'critical': '关键线索',
            'distraction': '干扰线索',
            'background': '背景信息'
        }[clue.type] || '线索';
        
        item.innerHTML = `
            <div class="clue-type">${typeText}</div>
            <div class="clue-content">${clue.content}</div>
        `;
        
        clueList.appendChild(item);
    });
}

function showSuspectDetail(suspect) {
    const modal = document.getElementById('suspect-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    
    modalTitle.textContent = suspect.name;
    
    const unlockedClueIds = currentGameState ? currentGameState.unlocked_clue_ids || [] : [];
    const suspectClues = currentCaseData.clue_library.filter(clue => 
        clue.related_suspect === suspect.id && unlockedClueIds.includes(clue.id)
    );
    
    let cluesHtml = '';
    if (suspectClues.length > 0) {
        cluesHtml = `
            <div class="suspect-clues-title">关联线索</div>
            <div class="suspect-clues">
                ${suspectClues.map(clue => `
                    <div class="clue-item ${clue.type}" style="margin-bottom: 8px;">
                        <div class="clue-type">${getClueTypeText(clue.type)}</div>
                        <div class="clue-content">${clue.content}</div>
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        cluesHtml = '<p style="color: #666;">暂无关联线索</p>';
    }
    
    modalBody.innerHTML = `
        <div class="suspect-detail">
            <label>身份</label>
            <value>${getSuspectRole(suspect)}</value>
        </div>
        <div class="suspect-detail">
            <label>动机</label>
            <value>${suspect.motive}</value>
        </div>
        <div class="suspect-detail">
            <label>不在场证明</label>
            <value>${suspect.alibi}</value>
        </div>
        ${cluesHtml}
    `;
    
    modal.style.display = 'block';
}

function getClueTypeText(type) {
    return {
        'critical': '关键线索',
        'distraction': '干扰线索',
        'background': '背景信息'
    }[type] || '线索';
}

function getSuspectRole(suspect) {
    const name = suspect.name;
    if (name.includes('妻子')) return '死者妻子';
    if (name.includes('管家')) return '别墅管家';
    if (name.includes('儿子') || name.includes('小明')) return '死者儿子';
    return '公司员工';
}

function handleEnding(endingType) {
    console.log('游戏结束:', endingType);
    document.getElementById('back-btn').style.display = 'none';
}

function showLoading() {
    const dialogContent = document.getElementById('dialog-content');
    dialogContent.innerHTML = '<div style="text-align: center; padding: 40px;">加载中...</div>';
}

function hideLoading() {
}

function getGameState() {
    return currentGameState;
}

function updateBackButton() {
    const backBtn = document.getElementById('back-btn');
    if (dialogHistory.length > 0) {
        backBtn.style.display = 'flex';
    } else {
        backBtn.style.display = 'none';
    }
}

function goBack() {
    if (dialogHistory.length === 0) {
        alert('已经是最早的记录了');
        return;
    }
    
    const previousState = dialogHistory.pop();
    
    const dialogContent = document.getElementById('dialog-content');
    if (previousState.dialog && previousState.dialog.includes('加载中')) {
        dialogContent.innerHTML = '<div class="dialog-text">返回上一页</div>';
    } else {
        dialogContent.innerHTML = previousState.dialog || '<div class="dialog-text">返回上一页</div>';
    }
    
    const choicesArea = document.getElementById('choices-area');
    choicesArea.innerHTML = '';
    
    if (previousState.choices && previousState.choices.length > 0) {
        previousState.choices.forEach(choice => {
            const btn = document.createElement('button');
            btn.className = 'choice-btn';
            btn.textContent = choice.text;
            btn.dataset.actionId = choice.id;
            btn.onclick = () => handleChoice(choice.id);
            choicesArea.appendChild(btn);
        });
    } else {
        choicesArea.innerHTML = '<p class="empty-text">暂无可用行动</p>';
    }
    
    updateBackButton();
}

async function openLoadModal() {
    const modal = document.getElementById('load-modal');
    const body = document.getElementById('load-body');
    modal.style.display = 'block';
    body.innerHTML = '<p>加载中...</p>';
    
    try {
        const response = await fetch(`${API_BASE}/saves/default_user`);
        const saves = await response.json();
        
        if (saves.length === 0) {
            body.innerHTML = '<p class="empty-text">暂无存档</p>';
            return;
        }
        
        body.innerHTML = '';
        saves.forEach(save => {
            const saveItem = document.createElement('div');
            saveItem.className = 'save-item';
            saveItem.innerHTML = `
                <h4>${save.save_name}</h4>
                <p>存档ID: ${save.save_id}</p>
                <p>创建时间: ${save.create_time}</p>
                <p>更新时间: ${save.update_time}</p>
                <div style="display: flex; gap: 10px;">
                    <button class="btn-primary" onclick="loadSave('${save.save_id}')">加载</button>
                    <button class="btn-danger" onclick="deleteSave('${save.save_id}')">删除</button>
                </div>
            `;
            body.appendChild(saveItem);
        });
    } catch (error) {
        console.error('Error:', error);
        body.innerHTML = '<p class="empty-text">加载存档失败</p>';
    }
}

async function loadSave(save_id) {
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/load/${save_id}`);
        const data = await response.json();
        
        if (response.ok) {
            currentSessionId = data.session_id;
            currentCaseData = data.case_data;
            currentGameState = data.game_state;
            dialogHistory = [];
            
            document.getElementById('start-game-btn').style.display = 'none';
            
            const lastDialog = data.game_state.dialog_history && data.game_state.dialog_history.length > 0 
                ? data.game_state.dialog_history[data.game_state.dialog_history.length - 1].content 
                : '欢迎回到游戏';
            
            renderDialog(lastDialog);
            renderSuspects();
            renderClues();
            
            const choices = generateChoicesFromState();
            renderChoices(choices);
            
            document.getElementById('back-btn').style.display = 'block';
            document.getElementById('save-btn').style.display = 'inline-block';
            
            document.getElementById('load-modal').style.display = 'none';
            alert('存档加载成功！');
        } else {
            alert('加载失败: ' + data.detail);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('服务器错误');
    } finally {
        hideLoading();
    }
}

async function deleteSave(save_id) {
    if (!confirm('确定要删除这个存档吗？')) return;
    
    try {
        const response = await fetch(`${API_BASE}/save/${save_id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            openLoadModal();
        } else {
            alert('删除失败');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('服务器错误');
    }
}

function generateChoicesFromState() {
    if (!currentCaseData || !currentGameState) return [];
    
    const choices = [];
    choices.push({ id: 'action_inspect_body', text: '查看尸体', status: 'available' });
    choices.push({ id: 'action_search_villa', text: '查看别墅布局', status: 'available' });
    
    const unlockedClues = currentGameState.unlocked_clue_ids || [];
    const searchedLocations = currentGameState.searched_locations || [];
    const interrogatedIds = currentGameState.interrogated_suspect_ids || [];
    
    const allLocations = new Set(currentCaseData.clue_library.map(clue => clue.location));
    allLocations.forEach(location => {
        const hasLockedClues = currentCaseData.clue_library.some(
            clue => clue.location === location && !unlockedClues.includes(clue.id)
        );
        
        let status = 'available';
        let statusText = '';
        if (searchedLocations.includes(location) && !hasLockedClues) {
            status = 'searched';
            statusText = '（已搜完）';
        }
        
        choices.push({ 
            id: `action_search_${location}`, 
            text: `搜查${location}${statusText}`, 
            status: status 
        });
    });
    
    currentCaseData.suspects.forEach(suspect => {
        const hasLockedClues = currentCaseData.clue_library.some(
            clue => clue.related_suspect === suspect.id && !unlockedClues.includes(clue.id)
        );
        const isInterrogated = interrogatedIds.includes(suspect.id);
        
        let status = 'available';
        let statusText = '';
        if (isInterrogated && !hasLockedClues) {
            status = 'interrogated';
            statusText = '（已盘问）';
        }
        
        choices.push({ 
            id: `action_interrogate_${suspect.id}`, 
            text: `盘问${suspect.name}${statusText}`, 
            status: status 
        });
    });
    
    choices.push({ id: 'action_list_suspects', text: '查看嫌疑人名单', status: 'available' });
    choices.push({ id: 'action_accuse', text: '指认凶手', status: 'available' });
    
    return choices;
}