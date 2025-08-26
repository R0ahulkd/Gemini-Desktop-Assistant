document.addEventListener('DOMContentLoaded', function() {
    const activateBtn = document.getElementById('activateBtn');
    const testBtn = document.getElementById('testBtn');
    const status = document.getElementById('status');
    
    function updateStatus(message, type = 'info') {
        status.textContent = message;
        status.className = `status ${type}`;
    }
    
    activateBtn.addEventListener('click', function() {
        updateStatus('Activating assistant...', 'info');
        activateBtn.disabled = true;
        
        chrome.runtime.sendMessage({action: 'activate'}, function(response) {
            activateBtn.disabled = false;
            if (chrome.runtime.lastError) {
                updateStatus(`Error: ${chrome.runtime.lastError.message}`, 'error');
            } else if (response && response.status === 'success') {
                updateStatus('Assistant activated successfully!', 'success');
                // Close popup after success
                setTimeout(() => window.close(), 1500);
            } else {
                updateStatus(`Error: ${response ? response.message : 'Unknown error'}`, 'error');
            }
        });
    });
    
    testBtn.addEventListener('click', function() {
        updateStatus('Testing connection...', 'info');
        testBtn.disabled = true;
        
        // Simple test - just try to send a message
        chrome.runtime.sendMessage({action: 'test'}, function(response) {
            testBtn.disabled = false;
            if (chrome.runtime.lastError) {
                updateStatus(`Connection test failed: ${chrome.runtime.lastError.message}`, 'error');
            } else {
                updateStatus('Extension is working!', 'success');
            }
        });
    });
    
    // Check if we can communicate with background script
    chrome.runtime.sendMessage({action: 'ping'}, function(response) {
        if (chrome.runtime.lastError) {
            updateStatus('Background script not responding', 'error');
        } else {
            updateStatus('Ready to connect...', 'info');
        }
    });
});