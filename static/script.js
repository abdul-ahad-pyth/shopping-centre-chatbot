function getTime() {
    return new Date().toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' });
}

function addMessage(text, type) {
    const box = document.getElementById('chatbox');
    const group = document.createElement('div');
    group.className = 'msg-group ' + type;

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;

    const time = document.createElement('div');
    time.className = 'msg-time';
    time.textContent = getTime();

    group.appendChild(bubble);
    group.appendChild(time);
    box.appendChild(group);
    box.scrollTop = box.scrollHeight;
}

function showTyping() {
    const box = document.getElementById('chatbox');
    const el  = document.createElement('div');
    el.className = 'typing';
    el.id = 'typing';
    el.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    box.appendChild(el);
    box.scrollTop = box.scrollHeight;
}

function removeTyping() {
    const el = document.getElementById('typing');
    if (el) el.remove();
}

async function sendMessage() {
    const input   = document.getElementById('message');
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    input.value = '';
    showTyping();

    try {
        const res  = await fetch('/chat', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ message: message })
        });
        const data = await res.json();
        removeTyping();
        addMessage(data.reply, 'bot');
    } catch (e) {
        removeTyping();
        addMessage('Something went wrong. Please try again.', 'bot');
    }
}

function quickSend(text) {
    document.getElementById('message').value = text;
    sendMessage();
}

// Add Enter key support
document.getElementById('message').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Focus input on load
document.getElementById('message').focus();