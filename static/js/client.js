// Initialize Chart.js for EEG visualization
let eegChart;
let ws;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

document.addEventListener('DOMContentLoaded', () => {
    initializeEEGChart();
    initializeWebSocket();
    setupChatInput();
    updateConnectionStatus('connecting');
});

function initializeEEGChart() {
    const ctx = document.getElementById('eegChart').getContext('2d');
    eegChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array(50).fill(''),
            datasets: [{
                label: 'EEG Signal',
                data: Array(50).fill(0),
                borderColor: '#6C63FF',
                tension: 0.4,
                borderWidth: 2,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 0
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function initializeWebSocket() {
    // Construct WebSocket URL
    const wsProto = location.protocol === 'https:' ? 'wss' : 'ws';
    const wsHost = location.hostname + (location.port ? ':' + location.port : '');
    const wsUrl = `${wsProto}://${wsHost}/ws/neuro/`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
        updateConnectionStatus('connected');
        reconnectAttempts = 0;
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus('disconnected');
        handleReconnection();
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateConnectionStatus('disconnected');
    };
}

function handleWebSocketMessage(data) {
    if (data.type === 'eeg_data') {
        updateEEGChart(data.eeg_data);
    } else if (data.type === 'emotion') {
        updateEmotionDisplay(data.emotion);
    } else if (data.type === 'chat_response') {
        addBotMessage(data.message);
    }
}

function updateEEGChart(newData) {
    eegChart.data.datasets[0].data.push(...newData);
    eegChart.data.datasets[0].data = eegChart.data.datasets[0].data.slice(-50);
    eegChart.update('quiet');
}

function updateEmotionDisplay(emotion) {
    const emotionDisplay = document.getElementById('currentEmotion');
    const emotionIcon = document.getElementById('emotionIcon');
    
    emotionDisplay.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
    
    // Update emotion icon
    const emotionIcons = {
        'happy': '😊',
        'sad': '😢',
        'angry': '😠',
        'neutral': '😐',
        'relaxed': '😌',
        'stressed': '😰'
    };
    
    emotionIcon.textContent = emotionIcons[emotion] || '😐';
}

function setupChatInput() {
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        
        if (message) {
            sendMessage(message);
            addUserMessage(message);
            chatInput.value = '';
        }
    });
}

function sendMessage(message) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'chat_message',
            message: message
        }));
    }
}

function addUserMessage(message) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addBotMessage(message) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateConnectionStatus(status) {
    const statusIndicator = document.getElementById('connectionStatus');
    const statusText = document.getElementById('connectionStatusText');
    
    statusIndicator.className = `status-indicator status-${status}`;
    statusText.textContent = status.charAt(0).toUpperCase() + status.slice(1);
}

function handleReconnection() {
    if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++;
        console.log(`Attempting to reconnect... (${reconnectAttempts}/${maxReconnectAttempts})`);
        updateConnectionStatus('connecting');
        setTimeout(initializeWebSocket, 2000 * reconnectAttempts);
    }
}
