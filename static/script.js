// script.js - Main application script
import { apiClient } from './api.js';
import { uiManager } from './ui.js';
import { utils } from './utils.js';

class ProjectApp {
    constructor() {
        this.initialized = false;
        this.data = null;
        this.eventHandlers = new Map();
    }

    async init() {
        try {
            await this.setupEventListeners();
            await this.loadInitialData();
            this.initialized = true;
            console.log('ProjectApp initialized successfully');
        } catch (error) {
            console.error('Failed to initialize ProjectApp:', error);
            uiManager.showError('Application initialization failed');
        }
    }

    async setupEventListeners() {
        const events = [
            { selector: '#loadDataBtn', event: 'click', handler: this.handleLoadData.bind(this) },
            { selector: '#submitForm', event: 'submit', handler: this.handleFormSubmit.bind(this) },
            { selector: '#searchInput', event: 'input', handler: this.handleSearch.bind(this) },
            { selector: '#refreshBtn', event: 'click', handler: this.handleRefresh.bind(this) }
        ];

        events.forEach(({ selector, event, handler }) => {
            const element = document.querySelector(selector);
            if (element) {
                element.addEventListener(event, handler);
                this.eventHandlers.set(`${selector}-${event}`, { element, event, handler });
            }
        });

        window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));
    }

    async loadInitialData() {
        uiManager.showLoading();
        
        try {
            this.data = await apiClient.fetchData();
            await uiManager.renderData(this.data);
            uiManager.updateStatus('Data loaded successfully');
        } catch (error) {
            uiManager.showError('Failed to load initial data');
            throw error;
        } finally {
            uiManager.hideLoading();
        }
    }

    async handleLoadData(event) {
        event.preventDefault();
        await this.loadInitialData();
    }

    async handleFormSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData);
        
        if (!this.validateFormData(data)) {
            uiManager.showError('Please fill in all required fields');
            return;
        }

        uiManager.showLoading();
        
        try {
            const response = await apiClient.submitData(data);
            uiManager.showSuccess('Data submitted successfully');
            await this.loadInitialData();
            event.target.reset();
        } catch (error) {
            uiManager.showError('Failed to submit data');
        } finally {
            uiManager.hideLoading();
        }
    }

    async handleSearch(event) {
        const searchTerm = event.target.value.trim();
        
        if (searchTerm.length < 2) {
            if (this.data) {
                await uiManager.renderData(this.data);
            }
            return;
        }

        try {
            const filteredData = await apiClient.searchData(searchTerm);
            await uiManager.renderData(filteredData);
        } catch (error) {
            console.error('Search failed:', error);
        }
    }

    async handleRefresh() {
        await this.loadInitialData();
    }

    validateFormData(data) {
        return Object.values(data).every(value => 
            value !== null && value !== undefined && value.toString().trim() !== ''
        );
    }

    handleBeforeUnload(event) {
        if (this.hasUnsavedChanges()) {
            event.preventDefault();
            event.returnValue = '';
        }
    }

    hasUnsavedChanges() {
        // Implement logic to check for unsaved changes
        return false;
    }

    cleanup() {
        this.eventHandlers.forEach(({ element, event, handler }) => {
            element.removeEventListener(event, handler);
        });
        this.eventHandlers.clear();
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    const app = new ProjectApp();
    await app.init();
    
    // Make app available globally for debugging (optional)
    window.projectApp = app;
});

// Utility functions
const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// Export for module usage
export { ProjectApp, debounce };