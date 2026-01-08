const API_URL = '/api';

// State
let currentUser = null;

// DOM Elements
const views = {
    login: document.getElementById('login-view'),
    dashboard: document.getElementById('dashboard-view')
};

const loginBtn = document.getElementById('login-btn');
const employeeNameInput = document.getElementById('employee-name');
const loginError = document.getElementById('login-error');

const userGreeting = document.getElementById('user-greeting');
const logoutBtn = document.getElementById('logout-btn');

const currentTimeDisplay = document.getElementById('current-time');
const currentDateDisplay = document.getElementById('current-date');

const checkinBtn = document.getElementById('checkin-btn');
const checkoutBtn = document.getElementById('checkout-btn');
const toastMsg = document.getElementById('action-message');
const consoleBody = document.getElementById('system-console');

// Controls
const manualTimeToggle = document.getElementById('manual-time-toggle');
const manualTimeInput = document.getElementById('manual-time-input');
const showHistoryBtn = document.getElementById('show-history-btn');

// Modals
const historyModal = document.getElementById('history-modal');
const historyTableBody = document.querySelector('#history-table tbody');
const closeHistoryBtn = document.getElementById('close-history');

const editModal = document.getElementById('edit-modal');
const closeEditBtn = document.getElementById('close-edit');
const saveEditBtn = document.getElementById('save-edit-btn');
const editDateDisplay = document.getElementById('edit-date-display');
const editTimeInput = document.getElementById('edit-time-input');
const editTypeRadios = document.getElementsByName('edit-type');

// State for Edit
let currentEditRecord = null;

// Functions
function addLog(message) {
    const line = document.createElement('div');
    line.className = 'log-line';
    line.textContent = `> ${message}`;
    consoleBody.appendChild(line);
    consoleBody.scrollTop = consoleBody.scrollHeight;
}

function startLogStream() {
    const eventSource = new EventSource(`${API_URL}/stream-logs`);
    
    eventSource.onopen = () => {
        addLog("Log stream connected.");
    };

    eventSource.onmessage = (event) => {
        addLog(event.data);
    };

    eventSource.onerror = (err) => {
        // console.error("EventSource failed:", err);
        // eventSource.close();
    };
}
function switchView(viewName) {
    Object.values(views).forEach(el => el.classList.remove('active'));
    views[viewName].classList.add('active');
}

function showToast(message) {
    toastMsg.textContent = message;
    toastMsg.classList.add('show');
    setTimeout(() => {
        toastMsg.classList.remove('show');
    }, 3000);
}

function updateTime() {
    const now = new Date();
    currentTimeDisplay.textContent = now.toLocaleTimeString('ko-KR', { hour12: false });
    currentDateDisplay.textContent = now.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' });
}

async function handleLogin() {
    const name = employeeNameInput.value.trim();
    if (!name) {
        loginError.textContent = "이름을 입력해주세요.";
        return;
    }

    loginBtn.textContent = "확인 중...";
    loginError.textContent = "";

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });

        if (!res.ok) {
            throw new Error("직원을 찾을 수 없습니다.");
        }

        const data = await res.json();
        currentUser = data;
        
        // Update Dashboard
        userGreeting.textContent = `반갑습니다, ${currentUser.name}님`;

        switchView('dashboard');
    } catch (err) {
        loginError.textContent = err.message;
    } finally {
        loginBtn.textContent = "입장하기";
    }
}

async function handleCheckIn() {
    if (!currentUser) return;
    
    checkinBtn.disabled = true;
    const isManual = manualTimeToggle.checked;
    const manualTime = isManual ? manualTimeInput.value : null;

    if (isManual && !manualTime) {
        showToast("시간을 입력해주세요.");
        checkinBtn.disabled = false;
        return;
    }

    try {
        const res = await fetch(`${API_URL}/check-in`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: currentUser.name,
                location: currentUser.location,
                employee_id: currentUser.id,
                time: manualTime ? manualTime : null, // Send HH:MM, backend adds random seconds
                date: isManual ? document.getElementById('manual-date-input').value : null
            })
        });

        const data = await res.json();
        if (res.ok) {
            showToast("출근 처리가 완료되었습니다.");
        } else {
            showToast("출근 처리에 실패했습니다: " + data.detail);
        }
    } catch (err) {
        showToast("오류가 발생했습니다.");
    } finally {
        checkinBtn.disabled = false;
    }
}

async function handleCheckOut() {
    if (!currentUser) return;

    checkoutBtn.disabled = true;
    const isManual = manualTimeToggle.checked;
    const manualTime = isManual ? manualTimeInput.value : null;

    if (isManual && !manualTime) {
        showToast("시간을 입력해주세요.");
        checkoutBtn.disabled = false;
        return;
    }

    try {
        const res = await fetch(`${API_URL}/check-out`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: currentUser.name,
                employee_id: currentUser.id,
                time: manualTime ? manualTime : null,
                date: isManual ? document.getElementById('manual-date-input').value : null
            })
        });

        const data = await res.json();
        if (res.ok) {
            showToast("퇴근 처리가 완료되었습니다.");
        } else {
            showToast("퇴근 처리에 실패했습니다: " + data.detail);
        }
    } catch (err) {
        showToast("오류가 발생했습니다.");
    } finally {
        checkoutBtn.disabled = false;
    }
}

// History Functions
async function loadHistory() {
    if (!currentUser) return;
    historyTableBody.innerHTML = '<tr><td colspan="4">로딩 중...</td></tr>';
    
    try {
        const res = await fetch(`${API_URL}/history/${currentUser.id}`);
        const records = await res.json();
        
        historyTableBody.innerHTML = '';
        if (records.length === 0) {
            historyTableBody.innerHTML = '<tr><td colspan="4">기록이 없습니다.</td></tr>';
            return;
        }

        records.forEach(record => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${record.date}</td>
                <td>${record.checkin_time || '-'}</td>
                <td>${record.checkout_time || '-'}</td>
                <td>
                    <button class="action-icon-btn edit-rec-btn" data-date="${record.date}">✏️</button>
                    <button class="action-icon-btn del-rec-btn" data-date="${record.date}">🗑️</button>
                </td>
            `;
            historyTableBody.appendChild(tr);
        });

        // Add listeners to dynamic buttons
        document.querySelectorAll('.edit-rec-btn').forEach(btn => {
            btn.addEventListener('click', (e) => openEditModal(e.target.dataset.date));
        });
        document.querySelectorAll('.del-rec-btn').forEach(btn => {
            btn.addEventListener('click', (e) => confirmDelete(e.target.dataset.date));
        });

    } catch (err) {
        historyTableBody.innerHTML = '<tr><td colspan="4">불러오기 실패</td></tr>';
    }
}

async function confirmDelete(date) {
    if (!confirm(`${date} 기록을 정말 삭제하시겠습니까?`)) return;
    
    try {
        const res = await fetch(`${API_URL}/record`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                employee_id: currentUser.id,
                date: date
            })
        });
        
        if (res.ok) {
            showToast("삭제되었습니다.");
            loadHistory();
        } else {
            showToast("삭제 실패");
        }
    } catch (err) {
        showToast("오류 발생");
    }
}

function openEditModal(date) {
    currentEditRecord = { date };
    editDateDisplay.textContent = date;
    editModal.classList.add('active');
}

async function saveEdit() {
    if (!currentEditRecord) return;
    
    const type = Array.from(editTypeRadios).find(r => r.checked).value;
    const timeVal = editTimeInput.value;
    
    if (!timeVal) {
        alert("시간을 입력해주세요.");
        return;
    }

    try {
         const res = await fetch(`${API_URL}/record`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                employee_id: currentUser.id,
                date: currentEditRecord.date,
                field: type,
                value: timeVal.length === 5 ? timeVal + ":00" : timeVal // Only append :00 if HH:MM
            })
        });
        
        if (res.ok) {
            showToast("수정되었습니다.");
            editModal.classList.remove('active');
            loadHistory();
        } else {
            showToast("수정 실패");
        }
    } catch (err) {
        showToast("오류 발생");
    }
}

// UI Event Listeners
// UI Event Listeners
manualTimeToggle.addEventListener('change', (e) => {
    const isManual = e.target.checked;
    const manualDateInput = document.getElementById('manual-date-input');
    
    if (isManual) {
        manualTimeInput.classList.remove('hidden');
        manualDateInput.classList.remove('hidden');
        // Set default date to today
        const today = new Date().toISOString().split('T')[0];
        manualDateInput.value = today;
    } else {
        manualTimeInput.classList.add('hidden');
        manualDateInput.classList.add('hidden');
        manualTimeInput.value = '';
        manualDateInput.value = '';
    }
});

showHistoryBtn.addEventListener('click', () => {
    historyModal.classList.add('active');
    loadHistory();
});

closeHistoryBtn.addEventListener('click', () => historyModal.classList.remove('active'));
closeEditBtn.addEventListener('click', () => editModal.classList.remove('active'));
saveEditBtn.addEventListener('click', saveEdit);

// Close modals on outside click
window.addEventListener('click', (e) => {
    if (e.target === historyModal) historyModal.classList.remove('active');
    if (e.target === editModal) editModal.classList.remove('active');
});


// Event Listeners
loginBtn.addEventListener('click', handleLogin);
employeeNameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleLogin();
});

logoutBtn.addEventListener('click', () => {
    currentUser = null;
    employeeNameInput.value = '';
    switchView('login');
});

checkinBtn.addEventListener('click', handleCheckIn);
checkoutBtn.addEventListener('click', handleCheckOut);

// Init
setInterval(updateTime, 1000);
updateTime();
startLogStream();
