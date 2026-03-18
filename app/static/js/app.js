/**
 * Knowbie - Knowledge Manager SPA
 * Main Application JavaScript
 */

const app = {
    // State
    items: [],
    tags: [],
    currentFilter: '',
    currentTypeFilter: '',
    currentItem: null,
    searchTimeout: null,

    // Type configurations
    typeConfig: {
        link: { icon: '🔗', color: 'bg-purple-100 text-purple-800', gradient: 'from-purple-100 to-purple-50' },
        code: { icon: '💻', color: 'bg-emerald-100 text-emerald-800', gradient: 'from-emerald-100 to-emerald-50' },
        note: { icon: '📝', color: 'bg-amber-100 text-amber-800', gradient: 'from-amber-100 to-amber-50' },
        image: { icon: '🖼️', color: 'bg-pink-100 text-pink-800', gradient: 'from-pink-100 to-pink-50' },
        file: { icon: '📎', color: 'bg-rose-100 text-rose-800', gradient: 'from-rose-100 to-rose-50' },
        idea: { icon: '💡', color: 'bg-indigo-100 text-indigo-800', gradient: 'from-indigo-100 to-indigo-50' }
    },

    // Initialize app
    init() {
        this.loadData();
        this.setupKeyboardShortcuts();
        this.updateStats();
    },

    // Load all data
    async loadData() {
        this.showLoading(true);
        
        try {
            // Load items
            const itemsResponse = await fetch('/api/knowledge/');
            this.items = await itemsResponse.json();
            
            // Load tags
            const tagsResponse = await fetch('/api/knowledge/tags');
            this.tags = await tagsResponse.json();
            
            this.renderTags();
            this.renderItems();
        } catch (error) {
            console.error('Error loading data:', error);
            this.showToast('Error loading data. Please refresh.', 'error');
        } finally {
            this.showLoading(false);
        }
    },

    // Show/hide loading state
    showLoading(show) {
        document.getElementById('loading-state').classList.toggle('hidden', !show);
        document.getElementById('knowledge-grid').classList.toggle('hidden', show);
    },

    // Render tag filters
    renderTags() {
        const container = document.getElementById('tag-filters');
        container.innerHTML = `
            <button onclick="app.filterByTag('')" 
                    class="tag-btn ${this.currentFilter === '' ? 'active' : 'px-4 sm:px-5 py-2 bg-white border border-gray-200 text-gray-600 rounded-full text-sm font-medium'}"
                    style="${this.currentFilter !== '' ? '' : ''}"
            >All</button>
        `;
        
        this.tags.forEach(tag => {
            const isActive = this.currentFilter === tag;
            const btn = document.createElement('button');
            btn.className = `tag-btn px-4 sm:px-5 py-2 rounded-full text-sm font-medium ${
                isActive 
                    ? 'active' 
                    : 'bg-white border border-gray-200 text-gray-600 hover:border-primary hover:text-primary'
            }`;
            btn.textContent = tag;
            btn.onclick = () => this.filterByTag(tag);
            container.appendChild(btn);
        });
    },

    // Render knowledge items
    renderItems() {
        const container = document.getElementById('knowledge-grid');
        
        // Filter items
        let filtered = this.items;
        if (this.currentFilter) {
            filtered = filtered.filter(item => 
                item.tags && item.tags.toLowerCase().includes(this.currentFilter.toLowerCase())
            );
        }
        if (this.currentTypeFilter) {
            filtered = filtered.filter(item => item.type === this.currentTypeFilter);
        }
        
        // Show empty state if needed
        if (filtered.length === 0) {
            container.classList.add('hidden');
            document.getElementById('empty-state').classList.remove('hidden');
            return;
        }
        
        document.getElementById('empty-state').classList.add('hidden');
        container.classList.remove('hidden');
        
        // Render cards
        container.innerHTML = filtered.map(item => this.renderCard(item)).join('');
        
        // Initialize code highlighting
        document.querySelectorAll('pre code').forEach(block => {
            if (window.hljs) {
                hljs.highlightElement(block);
            }
        });
    },

    // Render a single card
    renderCard(item) {
        const config = this.typeConfig[item.type] || this.typeConfig.note;
        const timeAgo = this.formatTimeAgo(item.updated_at);
        
        return `
            <div class="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 card-hover cursor-pointer animate-fade-in"
                 onclick="app.viewItem('${item.id}')"
            >
                <div class="h-24 bg-gradient-to-br ${config.gradient} p-5 flex justify-between items-start">
                    <span class="text-3xl">${config.icon}</span>
                    <span class="${config.color} text-xs font-medium px-3 py-1 rounded-full capitalize">${item.type}</span>
                </div>
                <div class="p-5">
                    <h3 class="font-semibold text-gray-800 mb-2 line-clamp-1">${this.escapeHtml(item.title)}</h3>
                    <p class="text-sm text-gray-500 mb-4 line-clamp-2">${this.getContentPreview(item)}</p>
                    <div class="flex items-center justify-between">
                        <span class="text-xs text-primary">${timeAgo}</span>
                        ${item.tags ? `
                            <span class="text-xs text-gray-400">${item.tags.split(',')[0]}</span>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    },

    // Get content preview based on type
    getContentPreview(item) {
        if (item.type === 'code') {
            return item.content.substring(0, 80).replace(/\n/g, ' ') + '...';
        }
        if (item.type === 'link') {
            try {
                const url = new URL(item.content);
                return url.hostname;
            } catch {
                return item.content.substring(0, 60);
            }
        }
        return item.content.substring(0, 80);
    },

    // Filter by tag
    filterByTag(tag) {
        this.currentFilter = tag;
        this.renderTags();
        this.renderItems();
    },

    // Show add modal
    showAddModal() {
        document.getElementById('add-modal').classList.remove('hidden');
        document.getElementById('add-modal').classList.add('flex');
        document.getElementById('item-title').focus();
    },

    // Hide add modal
    hideAddModal() {
        document.getElementById('add-modal').classList.add('hidden');
        document.getElementById('add-modal').classList.remove('flex');
        document.getElementById('add-form').reset();
        this.clearTypeSelection();
    },

    // Select type in modal
    selectType(type) {
        document.getElementById('item-type').value = type;
        document.querySelectorAll('.type-btn').forEach(btn => {
            btn.classList.remove('selected');
            if (btn.dataset.type === type) {
                btn.classList.add('selected');
            }
        });
    },

    // Clear type selection
    clearTypeSelection() {
        document.querySelectorAll('.type-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
    },

    // Save new knowledge
    async saveKnowledge(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData);
        
        if (!data.type) {
            this.showToast('Please select a type', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/knowledge/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showToast('Knowledge saved successfully!');
                this.hideAddModal();
                this.loadData();
                
                // Index for search
                this.indexForSearch(result);
            } else {
                this.showToast('Error saving knowledge', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showToast('Error saving knowledge', 'error');
        }
    },

    // Index item for semantic search
    async indexForSearch(item) {
        try {
            await fetch('/api/search/index/' + item.id, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: item.title,
                    content: item.content,
                    type: item.type,
                    tags: item.tags
                })
            });
        } catch (e) {
            console.log('Indexing not available');
        }
    },

    // View item details
    async viewItem(id) {
        const item = this.items.find(i => i.id === id);
        if (!item) return;
        
        this.currentItem = item;
        const config = this.typeConfig[item.type] || this.typeConfig.note;
        
        document.getElementById('view-type-icon').textContent = config.icon;
        document.getElementById('view-type-badge').className = `${config.color} px-3 py-1 rounded-full text-xs font-medium capitalize`;
        document.getElementById('view-type-badge').textContent = item.type;
        
        const contentDiv = document.getElementById('view-content');
        
        if (item.type === 'code') {
            contentDiv.innerHTML = `
                <h2 class="text-xl font-bold text-gray-800 mb-4">${this.escapeHtml(item.title)}</h2>
                <pre><code class="language-${this.detectLanguage(item.content)}">${this.escapeHtml(item.content)}</code></pre>
                ${item.tags ? `<div class="mt-4 flex flex-wrap gap-2">${this.renderTagsPills(item.tags)}</div>` : ''}
            `;
        } else if (item.type === 'link') {
            contentDiv.innerHTML = `
                <h2 class="text-xl font-bold text-gray-800 mb-4">${this.escapeHtml(item.title)}</h2>
                <a href="${item.content}" target="_blank" rel="noopener" 
                   class="link-preview block p-4 bg-gray-50 rounded-xl text-primary hover:underline break-all">
                    🔗 ${item.content}
                </a>
                <p class="mt-4 text-gray-600">${this.escapeHtml(item.source || '')}</p>
                ${item.tags ? `<div class="mt-4 flex flex-wrap gap-2">${this.renderTagsPills(item.tags)}</div>` : ''}
            `;
        } else if (item.type === 'image') {
            contentDiv.innerHTML = `
                <h2 class="text-xl font-bold text-gray-800 mb-4">${this.escapeHtml(item.title)}</h2>
                <img src="${item.content}" alt="${item.title}" class="max-w-full rounded-xl">
                ${item.tags ? `<div class="mt-4 flex flex-wrap gap-2">${this.renderTagsPills(item.tags)}</div>` : ''}
            `;
        } else {
            contentDiv.innerHTML = `
                <h2 class="text-xl font-bold text-gray-800 mb-4">${this.escapeHtml(item.title)}</h2>
                <p class="text-gray-600 whitespace-pre-wrap">${this.escapeHtml(item.content)}</p>
                ${item.tags ? `<div class="mt-4 flex flex-wrap gap-2">${this.renderTagsPills(item.tags)}</div>` : ''}
            `;
        }
        
        document.getElementById('view-modal').classList.remove('hidden');
        document.getElementById('view-modal').classList.add('flex');
        
        // Highlight code if present
        contentDiv.querySelectorAll('pre code').forEach(block => {
            if (window.hljs) {
                hljs.highlightElement(block);
            }
        });
    },

    // Hide view modal
    hideViewModal() {
        document.getElementById('view-modal').classList.add('hidden');
        document.getElementById('view-modal').classList.remove('flex');
        this.currentItem = null;
    },

    // Edit current item
    editCurrentItem() {
        if (!this.currentItem) return;
        this.hideViewModal();
        // TODO: Implement edit functionality
        this.showToast('Edit coming soon!');
    },

    // Delete current item
    async deleteCurrentItem() {
        if (!this.currentItem) return;
        
        if (!confirm('Are you sure you want to delete this item?')) return;
        
        try {
            const response = await fetch(`/api/knowledge/${this.currentItem.id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.showToast('Item deleted');
                this.hideViewModal();
                this.loadData();
            } else {
                this.showToast('Error deleting item', 'error');
            }
        } catch (error) {
            this.showToast('Error deleting item', 'error');
        }
    },

    // Show search modal
    showSearchModal() {
        document.getElementById('search-modal').classList.remove('hidden');
        document.getElementById('search-modal').classList.add('flex');
        document.getElementById('search-input').focus();
        document.getElementById('search-input').value = '';
        document.getElementById('search-results').innerHTML = `
            <div class="p-8 text-center text-gray-400">Type to search your knowledge base...</div>
        `;
    },

    // Hide search modal
    hideSearchModal() {
        document.getElementById('search-modal').classList.add('hidden');
        document.getElementById('search-modal').classList.remove('flex');
    },

    // Perform semantic search
    async performSearch(query) {
        if (!query.trim()) {
            document.getElementById('search-results').innerHTML = `
                <div class="p-8 text-center text-gray-400">Type to search your knowledge base...</div>
            `;
            return;
        }
        
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(async () => {
            try {
                const response = await fetch('/api/search/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query, limit: 10 })
                });
                
                const data = await response.json();
                this.renderSearchResults(data.results || []);
            } catch (error) {
                // Fallback to local search
                this.performLocalSearch(query);
            }
        }, 300);
    },

    // Local search fallback
    performLocalSearch(query) {
        const q = query.toLowerCase();
        const results = this.items.filter(item => 
            item.title.toLowerCase().includes(q) ||
            item.content.toLowerCase().includes(q) ||
            (item.tags && item.tags.toLowerCase().includes(q))
        ).slice(0, 10);
        
        this.renderSearchResults(results.map(r => ({...r, score: 1})));
    },

    // Render search results
    renderSearchResults(results) {
        const container = document.getElementById('search-results');
        
        if (results.length === 0) {
            container.innerHTML = `<div class="p-8 text-center text-gray-400">No results found</div>`;
            return;
        }
        
        container.innerHTML = results.map(item => {
            const config = this.typeConfig[item.type] || this.typeConfig.note;
            return `
                <div class="p-4 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-0"
                     onclick="app.viewItemFromSearch('${item.id}')"
                >
                    <div class="flex items-center gap-3 mb-2">
                        <span class="text-lg">${config.icon}</span>
                        <span class="font-medium text-gray-800">${this.escapeHtml(item.title)}</span>
                        <span class="ml-auto text-xs text-gray-400">${Math.round((item.score || 1) * 100)}%</span>
                    </div>
                    <p class="text-sm text-gray-500 line-clamp-1 pl-8">${this.getContentPreview(item)}</p>
                </div>
            `;
        }).join('');
    },

    // View item from search
    viewItemFromSearch(id) {
        this.hideSearchModal();
        this.viewItem(id);
    },

    // Show tags view
    showTags() {
        // TODO: Implement tags page
        this.showToast('Tags view coming soon!');
    },

    // Show stats view
    showStats() {
        // TODO: Implement stats page
        this.showToast('Stats view coming soon!');
    },

    // Show home
    showHome() {
        this.currentFilter = '';
        this.renderTags();
        this.renderItems();
    },

    // Update stats footer
    async updateStats() {
        try {
            const response = await fetch('/api/knowledge/stats');
            const stats = await response.json();
            document.getElementById('stats-footer').textContent = 
                `${stats.total_items} items • ${stats.total_tags} tags • Last updated: Just now`;
        } catch (e) {
            console.log('Stats update failed');
        }
    },

    // Render tags as pills
    renderTagsPills(tags) {
        return tags.split(',').map(tag => `
            <span class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">${tag.trim()}</span>
        `).join('');
    },

    // Detect programming language for syntax highlighting
    detectLanguage(code) {
        if (code.includes('import ') && code.includes('from ')) return 'python';
        if (code.includes('function') || code.includes('const') || code.includes('let')) return 'javascript';
        if (code.includes('<!DOCTYPE') || code.includes('<html')) return 'html';
        if (code.includes('{') && code.includes('}') && code.includes(':')) return 'json';
        if (code.includes('docker') || code.includes('FROM ') || code.includes('RUN ')) return 'dockerfile';
        return 'plaintext';
    },

    // Format time ago
    formatTimeAgo(dateString) {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);
        
        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
        return date.toLocaleDateString();
    },

    // Escape HTML
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // Show toast notification
    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        document.getElementById('toast-message').textContent = message;
        
        if (type === 'error') {
            toast.classList.remove('bg-gray-800');
            toast.classList.add('bg-red-600');
        } else {
            toast.classList.remove('bg-red-600');
            toast.classList.add('bg-gray-800');
        }
        
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    },

    // Keyboard shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // ⌘K or Ctrl+K for search
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                this.showSearchModal();
            }
            
            // ESC to close modals
            if (e.key === 'Escape') {
                this.hideAddModal();
                this.hideViewModal();
                this.hideSearchModal();
            }
            
            // N for new item
            if (e.key === 'n' && !e.metaKey && !e.ctrlKey && !e.altKey) {
                const activeElement = document.activeElement;
                if (activeElement.tagName !== 'INPUT' && activeElement.tagName !== 'TEXTAREA') {
                    e.preventDefault();
                    this.showAddModal();
                }
            }
        });
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});