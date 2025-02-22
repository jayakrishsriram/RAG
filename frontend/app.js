document.addEventListener('DOMContentLoaded', () => {
    const scrapeBtn = document.getElementById('scrape-btn');
    const scrapeUrlInput = document.getElementById('scrape-url');
    const scrapeResult = document.getElementById('scrape-result');
    const sendBtn = document.getElementById('send-btn');
    const chatInput = document.getElementById('chat-input');
    const chatWindow = document.getElementById('chat-window');

    // Handle website processing
    scrapeBtn.addEventListener('click', () => {
        const url = scrapeUrlInput.value.trim();
        if (!url) return alert('Please enter a URL');
        scrapeResult.textContent = "Processing...";
        fetch('http://localhost:8000/process', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({url})
        })
        .then(response => response.json())
        .then(data => {
            scrapeResult.textContent = data.message;
        })
        .catch(err => {
            scrapeResult.textContent = "Error processing URL.";
            console.error(err);
        });
    });

    // Append a message to chat window
    function appendMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender);
        msgDiv.textContent = text;
        chatWindow.appendChild(msgDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // Handle chat query
    sendBtn.addEventListener('click', () => {
        const query = chatInput.value.trim();
        if (!query) return;
        appendMessage(query, 'user');
        chatInput.value = '';
        fetch('http://localhost:8000/query', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query})
        })
        .then(response => response.json())
        .then(data => {
            appendMessage(data.answer, 'bot');
        })
        .catch(err => {
            appendMessage("Error fetching response.", 'bot');
            console.error(err);
        });
    });

    // Optional: send query on enter key press
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendBtn.click();
    });
});
