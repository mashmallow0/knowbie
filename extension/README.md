# Knowbie Browser Extension

A Chrome/Firefox extension for quickly saving content to your Knowbie knowledge manager.

## Features

- 🔗 **Save Links**: Right-click on any link to save it
- 📝 **Save Selection**: Highlight text and save it as a note
- 📄 **Save Pages**: Save the current page as a bookmark
- 💨 **Quick Capture**: Use the popup to quickly add knowledge
- 🎯 **Type Selection**: Choose between link, note, code, or idea

## Installation

### Chrome

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `extension` folder
5. The extension icon will appear in your toolbar

### Firefox

1. Open Firefox and navigate to `about:debugging`
2. Click "This Firefox"
3. Click "Load Temporary Add-on"
4. Select the `manifest.json` file in the extension folder

## Configuration

1. Click the extension icon → "Options" (or right-click → Options)
2. Set your Knowbie API URL (default: `http://localhost:8000`)
3. Save settings

## Usage

### Context Menu
- Right-click on a link → "🔗 Save Link to Knowbie"
- Right-click on selected text → "📝 Save Selection to Knowbie"
- Right-click on any page → "📄 Save Page to Knowbie"

### Popup
- Click the 🧠 icon in your toolbar
- Fill in the details or use quick capture buttons
- Click "Save"

### Keyboard Shortcuts
- The extension works through the context menu - no keyboard shortcuts needed!

## Requirements

- Knowbie must be running locally (default: http://localhost:8000)
- Chrome 88+ or Firefox 109+ (Manifest V3 support)

## Troubleshooting

**"Failed to save" error:**
- Make sure Knowbie is running on localhost:8000
- Check the API URL in extension options
- Check that CORS is enabled in Knowbie

**Extension not appearing:**
- Make sure Developer mode is enabled (Chrome)
- Try reloading the extension

## Files

- `manifest.json` - Extension configuration
- `background.js` - Service worker for context menus
- `popup.html/js` - Extension popup interface
- `options.html` - Settings page
- `icons/` - Extension icons