// Configuration for different environments
const CONFIG = {
    // Change this to your deployed backend URL
    BACKEND_URL: 'https://your-bedtime-story-app.herokuapp.com',
    // For local development, use: 'http://localhost:5000'
    // For deployed backend, use: 'https://your-app.herokuapp.com'
    
    // Auto-detect environment
    getApiUrl: function() {
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:5000';
        } else {
            return this.BACKEND_URL;
        }
    }
};

// Generate Story with Backend API
async function generateStory() {
    const request = storyRequest.value.trim();
    
    if (!request) {
        showNotification('Please enter a story request!', 'error');
        storyRequest.focus();
        return;
    }

    // Show loading state
    showLoading(true);
    generateBtn.disabled = true;
    
    try {
        // Make API call to backend
        const apiUrl = CONFIG.getApiUrl();
        const response = await fetch(`${apiUrl}/api/generate-story`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                request: request,
                mode: selectedMode
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayStory(result);
            showNotification('Story generated successfully!', 'success');
        } else {
            throw new Error(result.error || 'Failed to generate story');
        }
        
    } catch (error) {
        console.error('Error generating story:', error);
        showNotification(`Error: ${error.message}`, 'error');
        
        // Fallback to demo mode if backend is not available
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            showNotification('Backend not available, showing demo mode', 'warning');
            // You could add demo functionality here
        }
    } finally {
        showLoading(false);
        generateBtn.disabled = false;
    }
}

// Rest of your existing JavaScript code...
// (Include all the other functions from script.js)
