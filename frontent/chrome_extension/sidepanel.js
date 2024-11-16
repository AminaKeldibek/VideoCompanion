const chatLog = document.getElementById('chat-log');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const API_URL = "http://127.0.0.1:8000/search_video"; // Your API URL

// Function to extract video ID from YouTube URL
function extractVideoId(url) {
  const standardYouTubePattern = /(?:\?v=|&v=)([^&]+)/;
  const shortYouTubePattern = /youtu\.be\/([^?&]+)/;

  if (url.match(standardYouTubePattern)) {
    return url.match(standardYouTubePattern)[1];
  } else if (url.match(shortYouTubePattern)) {
    return url.match(shortYouTubePattern)[1];
  }
  return null;
}

// Function to navigate to timestamp in current YouTube tab
async function navigateToTimestamp(timestamp) {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  // Extract video ID from current tab's URL
  const videoId = extractVideoId(tab.url);

  if (!videoId) {
    chatLog.innerHTML += `<p><strong>AI:</strong> Unable to extract video ID from the current YouTube URL.</p>`;
    return;
  }

  // Construct YouTube URL with timestamp
  const youtubeUrl = `https://www.youtube.com/watch?v=${videoId}&t=${timestamp}s`;

  // Update the current tab with the new URL
  chrome.tabs.update(tab.id, { url: youtubeUrl });

  // Inform the user that the video is jumping to the timestamp
  chatLog.innerHTML += `<p><strong>AI:</strong> Jumping to ${timestamp} seconds!</p>`;
}

// Function to send message and get timestamp from API
async function sendMessage() {
  const userMessage = userInput.value;

  if (userMessage.trim() === '') {
    return;
  }

  // Display user's message in the chat log
  chatLog.innerHTML += `<p><strong>You:</strong> ${userMessage}</p>`;

  // Get the current tab and extract the video ID
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const videoId = extractVideoId(tab.url);

  if (!videoId) {
    chatLog.innerHTML += `<p><strong>AI:</strong> Unable to extract video ID from the current YouTube URL.</p>`;
    return;
  }

  // Prepare data to send to the API
  const requestData = {
    video_id: videoId,
    query: userMessage,
    user_id: 'user789'
  };

  try {
    // Send the POST request to the API
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData)
    });

    const responseData = await response.json();

    if (response.ok) {
      const { timestamp } = responseData;

      // Jump to the timestamp in the current tab
      navigateToTimestamp(timestamp);
    } else {
      chatLog.innerHTML += `<p><strong>AI:</strong> Error: Unable to fetch timestamp.</p>`;
    }
  } catch (error) {
    chatLog.innerHTML += `<p><strong>AI:</strong> Error: ${error.message}</p>`;
  }

  userInput.value = '';
  chatLog.scrollTop = chatLog.scrollHeight;
}

// Event listeners
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', function(event) {
  if (event.key === 'Enter') {
    sendMessage();
  }
});
