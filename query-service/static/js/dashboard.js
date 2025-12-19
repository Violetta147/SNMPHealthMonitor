/**
 * dashboard.js - SPA style
 * Main controller: orchestrates WebSocket, DataProcessor, and topic dashboard
 */
import { WebSocketManager } from './websocket-manager.js';
import { DataProcessor } from '/static/js/data-processor.js';

export class Dashboard {
    constructor(sysname, topic) {
        console.log(`[Dashboard] Initializing dashboard for ${sysname}, topic: ${topic}`);
        this.sysname = sysname;
        this.topic = topic || 'systemstatus';

        this.wsManager = new WebSocketManager(sysname, this.topic);
        this.wsManager.connect();
        this.dataProcessor = new DataProcessor();

        // Load initial topic
        this.loadTopicPartial(this.topic);

        // Cleanup on destroy
        this._destroyCallbacks = [];
    }

    async loadTopicPartial(topic) {
        console.log(`[Dashboard] Loading topic partial: ${topic}`);
        try {
            const response = await fetch(`/web/dashboard/partial/${topic}?sysname=${this.sysname}&partial=true`);
            if (!response.ok) throw new Error(`Failed to fetch partial: ${response.statusText}`);

            const html = await response.text();
            const container = document.getElementById('dashboard-main');
            if (!container) throw new Error('Dashboard main container not found');

            // Inject HTML
            container.innerHTML = html;

            // Update body data-topic
            document.body.dataset.topic = topic;
            // If topic changed, ask wsManager to subscribe to the new topic
            const previousTopic = this.topic;
            this.topic = topic;
            if (this.wsManager && previousTopic !== topic) {
                try {
                    this.wsManager.subscribe(topic);
                } catch (e) {
                    console.warn('[Dashboard] Error subscribing to new topic, falling back to reconnect', e);
                    // fallback: recreate connection
                    try { this.wsManager.disconnect(); } catch (_) {}
                    this.wsManager = new WebSocketManager(this.sysname, this.topic);
                    this.wsManager.connect();
                }
            }

            // Import topic-specific JS
            await this.loadTopicModule(topic);

        } catch (err) {
            console.error('[Dashboard] Error loading topic partial:', err);
            container.innerHTML = `<p class="error">Failed to load topic: ${topic}</p>`;
        }
    }

    async loadTopicModule(topic) {
        try {
            let modulePath;
            switch (topic) {
                case 'systemstatus':
                    modulePath = '/static/js/dashboard/systemstatus.js';
                    break;
                case 'network':
                    modulePath = '/static/js/dashboard/network.js';
                    break;
                case 'disk':
                    modulePath = '/static/js/dashboard/disk.js';
                    break;
                case 'diskio':
                    modulePath = '/static/js/dashboard/diskio.js';
                    break;
                default:
                    console.warn('[Dashboard] Unknown topic, falling back to systemstatus');
                    modulePath = 'static/js/dashboard/systemstatus.js';
            }
            console.log(`[Dashboard] Importing module: ${modulePath}`);
            const module = await import(modulePath);
            if (module && typeof module.initTopicDashboard === 'function') {
                if (this.topicDashboard?.destroy) this.topicDashboard.destroy();
                this.topicDashboard = module.initTopicDashboard(this.sysname, topic, this.wsManager, this.dataProcessor);
            }
        } catch (err) {
            console.error('[Dashboard] Error importing topic module:', err);
        }
    }

    registerDestroyCallback(fn) {
        if (typeof fn === 'function') this._destroyCallbacks.push(fn);
    }

    destroy() {
        console.log('[Dashboard] Destroying dashboard');
        this.wsManager.disconnect();
        if (this.topicDashboard?.destroy) this.topicDashboard.destroy();
        this._destroyCallbacks.forEach(fn => fn());
    }
}

/**
 * SPA navigation helper
 * Call this function on nav-item click to load partial & JS for topic
 */
export async function loadTopicPartial(topic) {
    if (window.dashboard) {
        await window.dashboard.loadTopicPartial(topic);
    }
}

// ---------------------------
// Initialize dashboard on DOM
// ---------------------------
document.addEventListener('DOMContentLoaded', () => {
    const sysname = document.body.dataset.sysname || 'default';
    const topic = document.body.dataset.topic || 'systemstatus';

    console.log(`[Dashboard] Initializing SPA: sysname=${sysname}, topic=${topic}`);
    document.getElementById('server-name').textContent = sysname;

    window.dashboard = new Dashboard(sysname, topic);

    // SPA nav: intercept menu clicks
    document.querySelectorAll('.nav-item').forEach(el => {
        el.addEventListener('click', e => {
            e.preventDefault();
            const topic = el.dataset.topic;
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            el.classList.add('active');
            loadTopicPartial(topic);
        });
    });

    window.addEventListener('beforeunload', () => window.dashboard.destroy());
});
