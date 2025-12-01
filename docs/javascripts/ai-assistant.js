// AI Assistant functionality for Homelab Docs
document.addEventListener('DOMContentLoaded', function() {
    // Always create the AI Assistant UI - auth check happens when user interacts
    createAIAssistant();
    
    // Only load conversation history if authenticated
    if (checkAuthentication()) {
        loadConversationHistory();
    }
});

// Rate limiting configuration
const RATE_LIMIT = 10; // requests per minute
const rateLimiter = new Map();

function checkAuthentication() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        return false;
    }
    
    // Basic token validation (JWT format check)
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const now = Date.now() / 1000;
        return payload.exp > now;
    } catch (e) {
        return false;
    }
}

function redirectToLogin() {
    window.location.href = '/admin/login';
}

// Show login prompt inside the AI chat container (not as popup toast)
function showLoginPromptInChat() {
    const messagesContainer = document.getElementById('aiChatMessages');
    if (!messagesContainer) return;
    
    messagesContainer.innerHTML = `
        <div style="padding: 20px; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 15px;">🔐</div>
            <h3 style="margin: 0 0 10px 0; color: #333;">Login Required</h3>
            <p style="color: #666; margin-bottom: 15px;">Please login to use the AI Assistant features.</p>
            <a href="/admin/login" style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">Login to Continue</a>
        </div>
    `;
}

function checkRateLimit(userId) {
    const now = Date.now();
    const userRequests = rateLimiter.get(userId) || [];
    const recentRequests = userRequests.filter(time => now - time < 60000);
    
    if (recentRequests.length >= RATE_LIMIT) {
        throw new Error('Rate limit exceeded. Please wait before sending another message.');
    }
    
    recentRequests.push(now);
    rateLimiter.set(userId, recentRequests);
}

function validateAIInput(message) {
    // Length validation
    if (message.length > 1000) {
        throw new Error('Message too long. Maximum 1000 characters allowed.');
    }
    
    if (message.length < 1) {
        throw new Error('Message cannot be empty.');
    }
    
    // Content validation - prevent XSS and injection
    const blockedPatterns = [
        /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
        /javascript:/gi,
        /data:text\/html/gi,
        /on\w+\s*=/gi,
        /eval\s*\(/gi,
        /exec\s*\(/gi
    ];
    
    for (const pattern of blockedPatterns) {
        if (pattern.test(message)) {
            throw new Error('Invalid content detected. Please remove any script tags or JavaScript code.');
        }
    }
    
    return message;
}

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
        <div class="ai-chat-status" id="aiChatStatus" style="display: none; padding: 10px; background: #f8f9fa; border-top: 1px solid #dee2e6; font-size: 12px; color: #6c757d;"></div>
        <div class="ai-chat-input">
            <input type="text" id="aiChatInput" placeholder="Ask about homelab setup..." onkeypress="handleAIChatKeyPress(event)" maxlength="1000">
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
        
        // Check auth when opening chat - show login prompt if not authenticated
        if (!checkAuthentication()) {
            showLoginPromptInChat();
        } else {
            document.getElementById('aiChatInput').focus();
        }
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

function showStatus(message, type = 'info') {
    const statusElement = document.getElementById('aiChatStatus');
    statusElement.style.display = 'block';
    statusElement.className = `ai-chat-status ai-status-${type}`;
    
    const colors = {
        'info': '#6c757d',
        'error': '#dc3545',
        'success': '#28a745',
        'warning': '#ffc107'
    };
    
    statusElement.style.color = colors[type] || colors['info'];
    statusElement.textContent = message;
    
    if (type === 'info') {
        setTimeout(() => {
            statusElement.style.display = 'none';
        }, 3000);
    }
}

async function sendAIMessage() {
    const input = document.getElementById('aiChatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Check authentication before sending
    if (!checkAuthentication()) {
        showLoginPromptInChat();
        return;
    }
    
    const token = localStorage.getItem('access_token');
    
    try {
        // Rate limiting
        const userId = JSON.parse(atob(token.split('.')[1])).sub;
        checkRateLimit(userId);
        
        // Input validation
        const validatedMessage = validateAIInput(message);
        
        // Add user message
        addMessage(validatedMessage, 'user');
        
        // Clear input and show typing indicator
        input.value = '';
        showStatus('🤔 Thinking...', 'info');
        addTypingIndicator();
        
        // Make actual API call
        const response = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ 
                message: validatedMessage,
                context: getWindowContext()
            })
        });
        
        removeTypingIndicator();
        
        if (!response.ok) {
            if (response.status === 429) {
                throw new Error('Rate limit exceeded. Please wait before sending another message.');
            } else if (response.status === 401) {
                throw new Error('Authentication expired. Please login again.');
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Add AI response
        addMessage(data.response, 'assistant');
        showStatus('✓ Response received', 'success');
        
    } catch (error) {
        removeTypingIndicator();
        showStatus(`❌ ${error.message}`, 'error');
        console.error('AI Assistant Error:', error);
        
        // Add error message to chat
        addMessage(`Error: ${error.message}`, 'system');
    }
}

function getWindowContext() {
    // Extract relevant context from the current page
    const title = document.title;
    const url = window.location.pathname;
    const headings = Array.from(document.querySelectorAll('h1, h2, h3')).map(h => h.textContent).join('\n');
    
    return {
        page_title: title,
        page_url: url,
        headings: headings.substring(0, 500), // Limit context length
        timestamp: new Date().toISOString()
    };
}

function addTypingIndicator() {
    const messagesContainer = document.getElementById('aiChatMessages');
    const typingElement = document.createElement('div');
    typingElement.className = 'ai-message assistant ai-typing';
    typingElement.innerHTML = `
        <strong>Assistant:</strong><br>
        <span class="typing-dots">
            <span class="dot">.</span>
            <span class="dot">.</span>
            <span class="dot">.</span>
        </span>
    `;
    
    messagesContainer.appendChild(typingElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeTypingIndicator() {
    const typingElement = document.querySelector('.ai-typing');
    if (typingElement) {
        typingElement.remove();
    }
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
