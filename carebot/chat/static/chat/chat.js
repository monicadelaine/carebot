document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(chatForm);
        
        // insert user message immediately
        const chatMessages = document.getElementById('chat-messages');
        const userMessageDiv = document.createElement('div');
        userMessageDiv.className = 'user-message'; // Adjust this class as needed for styling
        const userMessage = formData.get('query'); // Adjust 'query' based on your form field's name
        userMessageDiv.innerHTML = `<p>${userMessage}</p>`;
        chatMessages.appendChild(userMessageDiv);
        
        // Clear the input field right after pushing button
        const inputField = chatForm.querySelector('input[name="query"]'); // Adjust the selector as needed
        if (inputField) inputField.value = ''; // Clears the text field
        
        // insert loading message
        const loadingMessageDiv = document.createElement('div');
        loadingMessageDiv.className = 'ai-message loading-message'; // Use the same class as AI messages for consistency
        loadingMessageDiv.innerHTML = `<p><span class="dot"></span><span class="dot"></span><span class="dot"></span></p>`;
        chatMessages.appendChild(loadingMessageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll to the latest message
        // Check for SQL message, kept for dev purposes
        //const isSqlCheckbox = document.getElementById('is_sql');
        //formData.append('is_sql', isSqlCheckbox.checked ? 'True' : 'False');
        
        fetch('/chat/', { 
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // remove loading message
            chatMessages.removeChild(loadingMessageDiv);

            // insert AI or system response message
            const aiMessageDiv = document.createElement('div');
            // TODO: set message class based on the message_type value of the Message model
            if (data.response === 'There was an error processing your request. Please try again.') {
                aiMessageDiv.className = 'system-message';
            } else {
                aiMessageDiv.className = 'ai-message'; // Adjust this class as needed for styling
            }
            aiMessageDiv.innerHTML = `<p>${data.response}</p>`;
            chatMessages.appendChild(aiMessageDiv);
        
            chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll to the latest message
        })
        .catch((error) => {
            // optionally handle the loading message in case of error
            chatMessages.removeChild(loadingMessageDiv);
            console.error('Error:', error);
        })
    });
});