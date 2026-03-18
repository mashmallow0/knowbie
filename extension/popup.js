// Knowbie Browser Extension - Popup Script

const DEFAULT_API_URL = 'http://localhost:8000';

let currentType = 'link';
let currentTab = null;

// Initialize popup
document.addEventListener('DOMContentLoaded', async () => {
  // Get current tab info
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  currentTab = tabs[0];
  
  // Pre-fill with page info
  document.getElementById('title').value = currentTab.title;
  document.getElementById('content').value = currentTab.url;
  document.getElementById('tags').value = 'web-clip';
  
  // Focus on title for editing
  document.getElementById('title').select();
});

// Select type
function selectType(type) {
  currentType = type;
  document.querySelectorAll('.type-btn').forEach(btn => {
    btn.classList.toggle('selected', btn.dataset.type === type);
  });
}

// Capture current page
async function capturePage() {
  if (currentTab) {
    document.getElementById('title').value = currentTab.title;
    document.getElementById('content').value = currentTab.url;
    document.getElementById('tags').value = 'bookmark';
    selectType('link');
  }
}

// Capture selection
async function captureSelection() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: () => window.getSelection().toString()
    });
    
    const selection = results[0]?.result;
    if (selection) {
      document.getElementById('title').value = `Note from: ${tab.title}`.substring(0, 200);
      document.getElementById('content').value = selection;
      document.getElementById('tags').value = 'web-clip';
      selectType('note');
    } else {
      showStatus('No text selected on page', 'error');
    }
  } catch (error) {
    showStatus('Could not capture selection', 'error');
  }
}

// Save to Knowbie
async function saveToKnowbie() {
  const title = document.getElementById('title').value.trim();
  const content = document.getElementById('content').value.trim();
  const tags = document.getElementById('tags').value.trim();
  
  if (!title || !content) {
    showStatus('Please fill in title and content', 'error');
    return;
  }
  
  const saveBtn = document.getElementById('save-btn');
  const originalText = saveBtn.innerHTML;
  saveBtn.innerHTML = '<span class="loading"></span>Saving...';
  saveBtn.disabled = true;
  
  const apiUrl = await getApiUrl();
  
  try {
    const response = await fetch(`${apiUrl}/api/knowledge/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        content,
        type: currentType,
        tags,
        source: currentTab?.url || ''
      })
    });
    
    if (response.ok) {
      showStatus('✅ Saved to Knowbie!', 'success');
      // Clear form after successful save
      setTimeout(() => {
        document.getElementById('title').value = '';
        document.getElementById('content').value = '';
        document.getElementById('tags').value = '';
      }, 1500);
    } else {
      throw new Error('Failed to save');
    }
  } catch (error) {
    showStatus('❌ Failed to save. Is Knowbie running?', 'error');
  } finally {
    saveBtn.innerHTML = originalText;
    saveBtn.disabled = false;
  }
}

// Open Knowbie app
async function openKnowbie() {
  const apiUrl = await getApiUrl();
  chrome.tabs.create({ url: apiUrl });
}

// Get API URL from storage
async function getApiUrl() {
  const result = await chrome.storage.sync.get(['knowbieApiUrl']);
  return result.knowbieApiUrl || DEFAULT_API_URL;
}

// Show status message
function showStatus(message, type) {
  const status = document.getElementById('status');
  status.textContent = message;
  status.className = `status ${type}`;
  
  setTimeout(() => {
    status.className = 'status';
  }, 3000);
}