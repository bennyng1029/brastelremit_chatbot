const chatBubble = document.getElementById('chat-bubble');
const chatContainer = document.getElementById('chat-container');
const closeChat = document.getElementById('close-chat');
const sendBtn = document.getElementById('send-btn');
const userInput = document.getElementById('user-input');
const chatMessages = document.getElementById('chat-messages');

// Toggle Chat
chatBubble.addEventListener('click', () => {
    chatContainer.classList.remove('hidden');
    chatBubble.style.display = 'none';
});

closeChat.addEventListener('click', () => {
    chatContainer.classList.add('hidden');
    chatBubble.style.display = 'flex';
});

// Send Message
function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    userInput.value = '';
    
    // Simulate thinking
    setTimeout(() => {
        processQuery(text);
    }, 600);
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

function addMessage(text, sender, isHtml = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    if (isHtml) {
        msgDiv.innerHTML = text;
    } else {
        msgDiv.textContent = text;
    }
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function sendQuickAction(action) {
    addMessage(action, 'user');
    setTimeout(() => processQuery(action), 600);
}

function processQuery(query) {
    // Check for Rate Inquiries (Local check for quick UI feedback)
    const lowerQuery = query.toLowerCase();
    if (lowerQuery.includes('rate') || lowerQuery.includes('how much') || lowerQuery.includes('fee')) {
        // Optional: you can still show a local rate card or wait for LLM
        // For now, let's let the LLM handle it
    }

    // Call the Flask Backend
    fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
    })
    .then(res => res.json())
    .then(data => {
        addMessage(data.answer, 'bot');
    })
    .catch(err => {
        addMessage("Sorry, I'm having trouble connecting to my brain. Is the server running?", 'bot');
    });
}

function showRateCard() {
    const ratesHtml = `
        <div class="rate-card">
            <h4 style="margin-bottom: 8px; color: #004fb6;">Today's Rates (1 JPY)</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.85rem;">
                <div>🇵🇭 PHP: <b>${knowledgeBase.exchange_rates.PHP}</b></div>
                <div>🇻🇳 VND: <b>${knowledgeBase.exchange_rates.VND}</b></div>
                <div>🇮🇩 IDR: <b>${knowledgeBase.exchange_rates.IDR}</b></div>
                <div>🇮🇳 INR: <b>${knowledgeBase.exchange_rates.INR}</b></div>
            </div>
            <p style="margin-top: 10px; font-size: 0.75rem; color: #666;">Fees start from 480 JPY. What amount are you planning to send?</p>
        </div>
    `;
    addMessage(ratesHtml, 'bot', true);
}

function addQuickActions(actions) {
    const container = document.createElement('div');
    container.className = 'quick-actions';
    actions.forEach(action => {
        const btn = document.createElement('button');
        btn.className = 'action-btn';
        btn.textContent = action;
        btn.onclick = () => sendQuickAction(action);
        container.appendChild(btn);
    });
    chatMessages.appendChild(container);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
