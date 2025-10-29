/**
 * Main Application Entry Point
 * Initializes and coordinates all modules
 */

import { systemLogger } from './logger.js';
import { state } from './state.js';
import { api } from './api.js';
import { jobQueue } from './jobQueue.js';
import { ui } from './ui.js';

class Application {
  constructor() {
    systemLogger.info('🚀 PixelLab Command Center Starting...');
    this.initialized = false;
  }

  async init() {
    console.log('%c🎮 PixelLab Command Center',
      'font-size: 24px; font-weight: bold; color: #3b82f6; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);');
    console.log('%cModular Architecture v2.0',
      'font-size: 14px; color: #94a3b8; font-style: italic;');
    console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
      'color: #475569;');

    systemLogger.info('Initializing application modules...');

    try {
      // Initialize UI
      systemLogger.info('📱 Initializing UI Manager...');
      ui.init();

      // Perform initial health check
      systemLogger.info('🏥 Performing initial health check...');
      await this.refreshDiagnostics();

      // Setup periodic diagnostics refresh
      systemLogger.info('⏰ Setting up periodic diagnostics refresh (60s interval)...');
      setInterval(() => this.refreshDiagnostics(), 60000);

      // Setup window event listeners
      this.setupWindowListeners();

      this.initialized = true;
      systemLogger.success('✅ Application initialization complete!');

      // Log system info
      this.logSystemInfo();

    } catch (error) {
      systemLogger.error('❌ Application initialization failed', error);
      throw error;
    }
  }

  async refreshDiagnostics() {
    systemLogger.debug('Refreshing diagnostics...');

    try {
      const diagnostics = await api.checkHealth();
      state.updateDiagnostics(diagnostics);
      systemLogger.success('Diagnostics refresh complete');
    } catch (error) {
      systemLogger.error('Diagnostics refresh failed', error);
    }
  }

  setupWindowListeners() {
    systemLogger.debug('Setting up window event listeners');

    // Log when page is about to unload
    window.addEventListener('beforeunload', () => {
      systemLogger.info('Page unloading, cleaning up...');
    });

    // Log visibility changes
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        systemLogger.info('Page hidden');
      } else {
        systemLogger.info('Page visible');
      }
    });

    // Log errors
    window.addEventListener('error', (event) => {
      systemLogger.error('Uncaught error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
      });
    });

    // Log unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      systemLogger.error('Unhandled promise rejection', {
        reason: event.reason,
        promise: event.promise
      });
    });
  }

  logSystemInfo() {
    console.group('%c📊 System Information', 'font-weight: bold; color: #3b82f6;');
    console.log('User Agent:', navigator.userAgent);
    console.log('Platform:', navigator.platform);
    console.log('Language:', navigator.language);
    console.log('Online:', navigator.onLine);
    console.log('Screen:', `${screen.width}×${screen.height}`);
    console.log('Viewport:', `${window.innerWidth}×${window.innerHeight}`);
    console.log('Color Depth:', `${screen.colorDepth}-bit`);
    console.log('Pixel Ratio:', window.devicePixelRatio);

    // Performance info
    if (performance && performance.memory) {
      console.log('Memory:', {
        usedJSHeapSize: `${(performance.memory.usedJSHeapSize / 1048576).toFixed(2)} MB`,
        totalJSHeapSize: `${(performance.memory.totalJSHeapSize / 1048576).toFixed(2)} MB`,
        jsHeapSizeLimit: `${(performance.memory.jsHeapSizeLimit / 1048576).toFixed(2)} MB`
      });
    }

    console.log('Page Load Time:', `${performance.now().toFixed(2)}ms`);
    console.groupEnd();

    // Log configuration
    console.group('%c⚙️ Configuration', 'font-weight: bold; color: #10b981;');
    const config = state.getState().config;
    for (const [key, value] of Object.entries(config)) {
      console.log(`${key}:`, value);
    }
    console.groupEnd();

    // Show helpful console commands
    console.group('%c💡 Helpful Console Commands', 'font-weight: bold; color: #f59e0b;');
    console.log('%capp.getState()%c - View current application state',
      'background: #1e293b; color: #3b82f6; padding: 2px 6px; border-radius: 3px;',
      'color: #94a3b8;');
    console.log('%capp.getMetrics()%c - View job queue metrics',
      'background: #1e293b; color: #3b82f6; padding: 2px 6px; border-radius: 3px;',
      'color: #94a3b8;');
    console.log('%capp.refreshDiagnostics()%c - Manually refresh diagnostics',
      'background: #1e293b; color: #3b82f6; padding: 2px 6px; border-radius: 3px;',
      'color: #94a3b8;');
    console.log('%capp.createTestJob()%c - Create a test job',
      'background: #1e293b; color: #3b82f6; padding: 2px 6px; border-radius: 3px;',
      'color: #94a3b8;');
    console.log('%capp.clearHistory()%c - Clear all jobs and history',
      'background: #1e293b; color: #ef4444; padding: 2px 6px; border-radius: 3px;',
      'color: #94a3b8;');
    console.groupEnd();
  }

  // Public API methods for console access
  getState() {
    const currentState = state.getState();
    console.log('Current State:', currentState);
    return currentState;
  }

  getMetrics() {
    const metrics = jobQueue.getMetrics();
    console.log('Queue Metrics:', metrics);
    return metrics;
  }

  createTestJob() {
    systemLogger.info('Creating test job from console');
    return jobQueue.createJob('test pixel art character', 64, 64);
  }

  setMaxParallelJobs(count) {
    systemLogger.info(`Setting max parallel jobs to ${count}`);
    state.setConfig('maxParallelJobs', count);
  }

  clearHistory() {
    systemLogger.info('Clearing job history from console');
    jobQueue.clearAll();
    console.log('✅ Job history cleared!');
  }
}

// Initialize application when DOM is ready
const app = new Application();

document.addEventListener('DOMContentLoaded', async () => {
  systemLogger.info('DOM Content Loaded');
  await app.init();
});

// Make app available globally for console access
window.app = app;

// Export for module usage
export default app;

