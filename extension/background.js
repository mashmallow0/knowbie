// Knowbie Browser Extension - Background Script
// Handles context menus and background tasks

// Default API configuration
const DEFAULT_API_URL = 'http://localhost:8000';

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  // Create context menus
  chrome.contextMenus.create({
    id: 'knowbie-save-link',
    title: '🔗 Save Link to Knowbie',
    contexts: ['link']
  });

  chrome.contextMenus.create({
    id: 'knowbie-save-selection',
    title: '📝 Save Selection to Knowbie',
    contexts: ['selection']
  });

  chrome.contextMenus.create({
    id: 'knowbie-save-page',
    title: '📄 Save Page to Knowbie',
    contexts: ['page']
  });

  chrome.contextMenus.create({
    id: 'knowbie-separator',
    type: 'separator',
    contexts: ['all']
  });

  chrome.contextMenus.create({
    id: 'knowbie-open',
    title: '🧠 Open Knowbie',
    contexts: ['all']
  });

  console.log('Knowbie extension installed');
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const apiUrl = await getApiUrl();

  switch (info.menuItemId) {
    case 'knowbie-save-link':
      await saveLink(info.linkUrl, info.linkText || info.linkUrl, tab.title, apiUrl);
      break;

    case 'knowbie-save-selection':
      await saveSelection(info.selectionText, tab.title, tab.url, apiUrl);
      break;

    case 'knowbie-save-page':
      await savePage(tab.title, tab.url, apiUrl);
      break;

    case 'knowbie-open':
      chrome.tabs.create({ url: apiUrl });
      break;
  }
});

// Get API URL from storage
async function getApiUrl() {
  const result = await chrome.storage.sync.get(['knowbieApiUrl']);
  return result.knowbieApiUrl || DEFAULT_API_URL;
}

// Save link to Knowbie
async function saveLink(url, linkText, pageTitle, apiUrl) {
  try {
    const response = await fetch(`${apiUrl}/api/knowledge/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: linkText.substring(0, 200),
        content: url,
        type: 'link',
        tags: '',
        source: pageTitle
      })
    });

    if (response.ok) {
      showNotification('Link saved to Knowbie! 🧠', linkText.substring(0, 50) + '...');
    } else {
      throw new Error('Failed to save');
    }
  } catch (error) {
    showNotification('Failed to save link', 'Make sure Knowbie is running on localhost:8000');
  }
}

// Save selection to Knowbie
async function saveSelection(text, pageTitle, pageUrl, apiUrl) {
  try {
    const response = await fetch(`${apiUrl}/api/knowledge/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: `Note from: ${pageTitle}`.substring(0, 200),
        content: text,
        type: 'note',
        tags: 'web-clip',
        source: pageUrl
      })
    });

    if (response.ok) {
      showNotification('Selection saved to Knowbie! 🧠', text.substring(0, 50) + '...');
    } else {
      throw new Error('Failed to save');
    }
  } catch (error) {
    showNotification('Failed to save selection', 'Make sure Knowbie is running on localhost:8000');
  }
}

// Save page to Knowbie
async function savePage(title, url, apiUrl) {
  try {
    const response = await fetch(`${apiUrl}/api/knowledge/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: title.substring(0, 200),
        content: url,
        type: 'link',
        tags: 'bookmark',
        source: url
      })
    });

    if (response.ok) {
      showNotification('Page saved to Knowbie! 🧠', title);
    } else {
      throw new Error('Failed to save');
    }
  } catch (error) {
    showNotification('Failed to save page', 'Make sure Knowbie is running on localhost:8000');
  }
}

// Show browser notification
function showNotification(title, message) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icons/icon128.png',
    title: title,
    message: message
  });
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'saveToKnowbie') {
    saveFromPopup(request.data);
    sendResponse({ success: true });
  }
  return true;
});

// Save from popup
async function saveFromPopup(data) {
  const apiUrl = await getApiUrl();
  try {
    const response = await fetch(`${apiUrl}/api/knowledge/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      showNotification('Saved to Knowbie! 🧠', data.title);
    } else {
      throw new Error('Failed to save');
    }
  } catch (error) {
    showNotification('Failed to save', 'Make sure Knowbie is running');
  }
}