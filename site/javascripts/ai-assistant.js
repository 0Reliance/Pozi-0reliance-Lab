// AI Assistant functionality for Homelab Docs
document.addEventListener('DOMContentLoaded', function() {
    // Create AI Assistant UI
    createAIAssistant();
    
    // Load conversation history
    loadConversationHistory();
});

function createAIAssistant() {
    // Create toggle button
    const toggleButton = document.createElement('button');
    toggleButton.className = 'ai-toggle-button';
    toggleButton.innerHTML = '🤖';
    toggleButton.title = 'AI Assistant';
    toggleButton.addEventListener('click', toggleAIChat);
    
    // Create chat container
    const chatContainer = document.createElement('div');
    chatContainer.className = 'ai-chat-container hidden';
    chatContainer.innerHTML = `
        <div class="ai-chat-header">
            <span>🤖 Homelab Assistant</span>
            <button onclick="toggleAIChat()" style="background: none; border: none; color: white; cursor: pointer;">✕</button>
        </div>
        <div class="ai-chat-messages" id="aiChatMessages"></div>
        <div class="ai-chat-input">
            <input type="text" id="aiChatInput" placeholder="Ask about homelab setup..." onkeypress="handleAIChatKeyPress(event)">
            <button onclick="sendAIMessage()" style="margin-left: 10px; padding: 8px 15px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">Send</button>
        </div>
    `;
    
    document.body.appendChild(toggleButton);
    document.body.appendChild(chatContainer);
}

function toggleAIChat() {
    const chatContainer = document.querySelector('.ai-chat-container');
    const toggleButton = document.querySelector('.ai-toggle-button');
    
    if (chatContainer.classList.contains('hidden')) {
        chatContainer.classList.remove('hidden');
        toggleButton.classList.add('hidden');
        document.getElementById('aiChatInput').focus();
    } else {
        chatContainer.classList.add('hidden');
        toggleButton.classList.remove('hidden');
    }
}

function handleAIChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendAIMessage();
    }
}

function sendAIMessage() {
    const input = document.getElementById('aiChatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    addMessage(message, 'user');
    
    // Clear input
    input.value = '';
    
    // Simulate AI response
    setTimeout(() => {
        const response = generateAIResponse(message);
        addMessage(response, 'assistant');
    }, 1000);
}

function addMessage(message, sender) {
    const messagesContainer = document.getElementById('aiChatMessages');
    const messageElement = document.createElement('div');
    messageElement.className = `ai-message ${sender}`;
    messageElement.innerHTML = `
        <strong>${sender === 'user' ? 'You' : 'Assistant'}:</strong><br>
        ${message}
    `;
    
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Save to localStorage
    saveConversationHistory();
}

function generateAIResponse(message) {
    const responses = {
        'docker': 'Docker is a containerization platform that\'s perfect for homelabs. You can run services in isolated containers without affecting your host system. Start by installing Docker CE on your Linux server, then try running some basic containers like nginx or portainer.',
        'network': 'For homelab networking, I recommend setting up VLANs to separate different services (management, production, IoT). A good managed switch and proper firewall configuration are essential. Consider using pfSense or OPNsense for routing and firewall capabilities.',
        'storage': 'ZFS is excellent for homelab storage due to its data integrity features and snapshots. For media storage, consider using TrueNAS or Unraid. Always implement a backup strategy with multiple destinations (local and cloud).',
        'monitoring': 'Prometheus and Grafana form a powerful monitoring stack. Collect metrics from all your services, set up alerts for critical issues, and create informative dashboards. Don\'t forget to monitor network bandwidth, disk usage, and system health.',
        'security': 'Security is crucial in homelabs. Use SSH keys instead of passwords, implement proper firewall rules, keep systems updated, and consider using VPN access. Regular security audits and monitoring are also important.',
        'default': 'That\'s a great question about homelab management! I can help with Docker containers, networking setup, storage solutions, monitoring configurations, or security best practices. What specific aspect would you like to know more about?'
    };
    
    const lowerMessage = message.toLowerCase();
    
    for (const [key, response] of Object.entries(responses)) {
        if (lowerMessage.includes(key)) {
            return response;
        }
    }
    
    return responses.default;
}

function saveConversationHistory() {
    const messages = document.querySelectorAll('.ai-message');
    const conversation = Array.from(messages).map(msg => ({
        sender: msg.classList.contains('user') ? 'user' : 'assistant',
        message: msg.textContent.replace(/^(You|Assistant):\s*/, '')
    }));
    
    localStorage.setItem('aiChatHistory', JSON.stringify(conversation));
}

function loadConversationHistory() {
    const history = localStorage.getItem('aiChatHistory');
    if (!history) return;
    
    try {
        const conversation = JSON.parse(history);
        const messagesContainer = document.getElementById('aiChatMessages');
        
        conversation.forEach(msg => {
            const messageElement = document.createElement('div');
            messageElement.className = `ai-message ${msg.sender}`;
            messageElement.innerHTML = `
                <strong>${msg.sender === 'user' ? 'You' : 'Assistant'}:</strong><br>
                ${msg.message}
            `;
            messagesContainer.appendChild(messageElement);
        });
        
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    } catch (error) {
        console.error('Failed to load conversation history:', error);
    }
}
