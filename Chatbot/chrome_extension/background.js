// This script listens for a command or message to launch the native host
chrome.commands.onCommand.addListener((command) => {
  if (command === "launch_assistant") {
    console.log("Hot key command received. Launching assistant...");
    
    // Send a one-time message to the native host
    try {
      chrome.runtime.sendNativeMessage(
        'com.gemini.assistant',
        { action: "trigger_assistant" },
        (response) => {
          if (chrome.runtime.lastError) {
            console.error("Error sending message to native host:", chrome.runtime.lastError.message);
          }
          console.log("Received response from native host:", response);
        }
      );
    } catch (error) {
      console.error("Failed to send message to native host:", error);
    }
  }
});

// A listener for messages from the old popup.js (if you still have it)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "activate") {
        console.log("Popup message received. Launching assistant.");
        chrome.commands.onCommand.dispatch("launch_assistant");
    }
});