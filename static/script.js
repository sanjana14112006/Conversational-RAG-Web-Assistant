// static/script.js
document.getElementById('userInput').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') sendMessage();
});
document.getElementById('sendBtn').addEventListener('click', sendMessage);

// Generate a random session string identifier to secure this unique conversation's history lanes
const uniqueSessionID = "session_" + Math.random().toString(36).substr(2, 9);

function sendMessage() {
    const inputEl = document.getElementById('userInput');
    const messageText = inputEl.value.trim();
    if (!messageText) return;

    // Instantly append user's text bubble to UI log frame workspace canvas
    appendMessage(messageText, 'user-message');
    inputEl.value = '';

    // Create a temporary "Thinking..." bubble placeholder indicator text
    const loadingDiv = appendMessage("Assistant is reading context...", 'bot-message');

    // Send payload straight to our local Flask API server endpoint route port
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageText, session_id: uniqueSessionID })
    })
    .then(res => res.json())
    .then(data => {
        loadingDiv.remove(); // Drop the placeholder loading line bubble
        if (data.answer) {
            appendMessage(data.answer, 'bot-message');
        } else {
            appendMessage("I ran into an internal document parsing error.", 'bot-message');
        }
    })
    .catch(err => {
        loadingDiv.remove();
        appendMessage("Could not communicate with the backend application server.", 'bot-message');
    });
}

function appendMessage(text, className) {
    const chatBody = document.getElementById('chatBody');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${className}`;
    
    // Check if the message is from the bot and contains links
    if (className === 'bot-message') {
        // Regular expression to discover URLs starting with http:// or https://
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        
        // Convert text URLs into HTML <a> tags natively
        let formattedText = text.replace(urlRegex, function(url) {
            // Clean up trailing punctuation if the regex caught a period at the end of a sentence
            let cleanUrl = url.replace(/[.,]$/, "");
            return `<a href="${cleanUrl}" target="_blank" style="color: #4F46E5; text-decoration: underline; font-weight: 600;">${cleanUrl}</a>`;
        });
        
        // Convert newlines (\n) to HTML line breaks (<br>) so spacing looks beautiful
        msgDiv.innerHTML = formattedText.replace(/\n/g, "<br>");
    } else {
        // For the user, keep it as pure safe text string
        msgDiv.innerText = text;
    }
    
    chatBody.appendChild(msgDiv);
    chatBody.scrollTop = chatBody.scrollHeight; // Auto scroll down
    return msgDiv;
}