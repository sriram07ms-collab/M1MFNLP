// API Configuration
const LOCAL_API_BASE_URL = 'http://localhost:8000';
const PRODUCTION_API_BASE_URL = 'https://milestone1mfnlp.onrender.com';
const API_BASE_URL = window.location.hostname === 'localhost'
    ? LOCAL_API_BASE_URL
    : PRODUCTION_API_BASE_URL;

// DOM Elements
const queryInput = document.getElementById('queryInput');
const askButton = document.getElementById('askButton');
const responseSection = document.getElementById('responseSection');
const responseContent = document.getElementById('responseContent');
const responseSources = document.getElementById('responseSources');
const loading = document.getElementById('loading');

// Handle Enter key press
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        askQuestion();
    }
}

// Ask a question
async function askQuestion(questionText = null) {
    const query = questionText || queryInput.value.trim();
    
    if (!query) {
        alert('Please enter a question');
        return;
    }

    // Update UI
    queryInput.value = query;
    showLoading();
    hideResponse();

    try {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                fund_name: null // Can be customized later
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayResponse(data);

    } catch (error) {
        console.error('Error:', error);
        displayError(error.message);
    } finally {
        hideLoading();
    }
}

// Display response
function displayResponse(data) {
    const answer = data.answer || 'No answer available';
    const sources = data.source_urls || [];
    const fallbackUsed = data.fallback_used || false;

    // Format answer
    let formattedAnswer = answer;
    
    // Add fallback note if applicable
    if (fallbackUsed) {
        formattedAnswer += '\n\n[Note: Answer generated from retrieved facts. LLM generation temporarily unavailable.]';
    }

    responseContent.innerHTML = formatAnswer(formattedAnswer);
    
    // Display sources
    if (sources.length > 0) {
        responseSources.innerHTML = `
            <div class="sources-title">Source${sources.length > 1 ? 's' : ''}:</div>
            ${sources.map(url => 
                `<a href="${url}" target="_blank" class="source-link">${getDomainName(url)}</a>`
            ).join('')}
        `;
    } else {
        responseSources.innerHTML = '';
    }

    showResponse();
}

// Format answer text
function formatAnswer(text) {
    // Convert markdown-like formatting to HTML
    let html = text
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Wrap in paragraph tags
    html = '<p>' + html + '</p>';

    // Add fallback note styling if present
    if (text.includes('[Note:')) {
        html = html.replace(
            /\[Note:([^\]]+)\]/g,
            '<div class="fallback-note">$1</div>'
        );
    }

    return html;
}

// Get domain name from URL
function getDomainName(url) {
    try {
        const urlObj = new URL(url);
        return urlObj.hostname.replace('www.', '');
    } catch {
        return url;
    }
}

// Display error
function displayError(errorMessage) {
    responseContent.innerHTML = `
        <p style="color: #DC2626;">
            <strong>Error:</strong> ${errorMessage}
        </p>
        <p style="margin-top: 12px; color: #6B7280;">
            Please make sure the backend server is running on ${API_BASE_URL}
        </p>
    `;
    responseSources.innerHTML = '';
    showResponse();
}

// Show/hide functions
function showLoading() {
    loading.style.display = 'block';
    askButton.disabled = true;
}

function hideLoading() {
    loading.style.display = 'none';
    askButton.disabled = false;
}

function showResponse() {
    responseSection.style.display = 'block';
    responseSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideResponse() {
    responseSection.style.display = 'none';
}

function closeResponse() {
    hideResponse();
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Focus on input
    queryInput.focus();
    
    // Check API health on load
    checkAPIHealth();
});

// Check if API is available
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('API is ready');
        }
    } catch (error) {
        console.warn('API health check failed:', error);
    }
}


