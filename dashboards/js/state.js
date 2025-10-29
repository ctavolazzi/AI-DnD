/**
 * State Management Module
 * Centralized state with event-driven updates
 */

import { systemLogger } from './logger.js';

class StateManager {
  constructor() {
    this.STORAGE_KEY = 'pixellab_jobs_v1';

    // Load persisted jobs from localStorage
    const persistedJobs = this.loadFromStorage();

    this.state = {
      jobs: persistedJobs.jobs || [],
      diagnostics: {
        server: { status: 'warn', message: 'Checking...' },
        api: { status: 'warn', message: 'Validating...' },
        balance: { status: 'warn', message: '—' },
        lastChecked: null
      },
      config: {
        maxParallelJobs: 3,
        serverUrl: 'http://127.0.0.1:8787'
      },
      stats: {
        total: 0,
        running: 0,
        completed: 0,
        failed: 0
      }
    };

    this.listeners = new Map();
    this.jobIdCounter = persistedJobs.lastJobId || 1;

    // Restore stats after loading jobs
    this.updateStats();

    systemLogger.info('State Manager initialized', {
      loadedJobs: this.state.jobs.length,
      lastJobId: this.jobIdCounter
    });
  }

  // Load jobs from server (with localStorage fallback)
  loadFromStorage() {
    try {
      // Try localStorage first for instant load
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        const data = JSON.parse(stored);
        systemLogger.info('Loaded jobs from localStorage cache', {
          count: data.jobs?.length || 0
        });

        // Async load from server to sync
        this.loadFromServer();

        return data;
      }

      return { jobs: [], lastJobId: 1 };
    } catch (error) {
      systemLogger.error('Failed to load jobs from localStorage', error);
      return { jobs: [], lastJobId: 1 };
    }
  }

  // Load jobs from server
  async loadFromServer() {
    try {
      const response = await fetch(`${this.state.config.serverUrl}/load-jobs`);
      if (!response.ok) {
        systemLogger.warning('Server load failed, using localStorage');
        return;
      }

      const data = await response.json();

      if (data.status === 'ok' && data.jobs.length > 0) {
        systemLogger.info('Loaded jobs from server', {
          count: data.jobs.length,
          savedAt: data.savedAt
        });

        // Update state with server data if newer
        if (data.jobs.length !== this.state.jobs.length) {
          this.state.jobs = data.jobs;
          this.jobIdCounter = data.lastJobId || 1;
          this.updateStats();

          // Update localStorage cache
          this.saveToLocalStorage();

          // Emit events to update UI
          this.emit('jobs:restored', data.jobs);
          this.emit('state:updated', this.state);
        }
      }
    } catch (error) {
      systemLogger.error('Failed to load jobs from server', error);
    }
  }

  // Save to localStorage only
  saveToLocalStorage() {
    try {
      const data = {
        jobs: this.state.jobs,
        lastJobId: this.jobIdCounter,
        savedAt: new Date().toISOString()
      };

      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));

      systemLogger.debug('Saved jobs to localStorage', {
        count: this.state.jobs.length
      });
    } catch (error) {
      systemLogger.error('Failed to save jobs to localStorage', error);
    }
  }

  // Save jobs to server and localStorage
  async saveToStorage() {
    // Save to localStorage immediately
    this.saveToLocalStorage();

    // Save to server async
    try {
      const data = {
        jobs: this.state.jobs,
        lastJobId: this.jobIdCounter
      };

      const response = await fetch(`${this.state.config.serverUrl}/save-jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        systemLogger.warning('Server save failed, localStorage only');
        return;
      }

      const result = await response.json();

      if (result.status === 'ok') {
        systemLogger.info('Saved jobs to server', {
          count: this.state.jobs.length,
          fileSize: result.fileSize
        });
      }
    } catch (error) {
      systemLogger.error('Failed to save jobs to server', error);
    }
  }

  // Subscribe to state changes
  subscribe(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);

    systemLogger.debug(`Subscribed to event: ${event}`, {
      totalListeners: this.listeners.get(event).length
    });
  }

  // Emit state change events
  emit(event, data) {
    systemLogger.debug(`Emitting event: ${event}`, data);

    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          systemLogger.error(`Error in event listener for ${event}`, error);
        }
      });
    }
  }

  // Get next job ID
  getNextJobId() {
    return `job-${this.jobIdCounter++}`;
  }

  // Add job to state
  addJob(job) {
    this.state.jobs.push(job);
    this.updateStats();
    this.saveToStorage();  // Persist to localStorage
    this.emit('job:added', job);
    this.emit('state:updated', this.state);

    systemLogger.info('Job added to state', {
      jobId: job.id,
      totalJobs: this.state.jobs.length
    });
  }

  // Update job in state
  updateJob(jobId, updates) {
    const job = this.state.jobs.find(j => j.id === jobId);
    if (job) {
      Object.assign(job, updates);
      this.updateStats();
      this.saveToStorage();  // Persist to localStorage
      this.emit('job:updated', job);
      this.emit('state:updated', this.state);

      systemLogger.debug('Job updated', {
        jobId,
        updates,
        newStatus: job.status
      });
    } else {
      systemLogger.warning(`Job not found for update: ${jobId}`);
    }
  }

  // Remove job from state
  removeJob(jobId) {
    const index = this.state.jobs.findIndex(j => j.id === jobId);
    if (index > -1) {
      const job = this.state.jobs[index];
      this.state.jobs.splice(index, 1);
      this.updateStats();
      this.saveToStorage();  // Persist to localStorage
      this.emit('job:removed', job);
      this.emit('state:updated', this.state);

      systemLogger.info('Job removed from state', {
        jobId,
        remainingJobs: this.state.jobs.length
      });
    }
  }

  // Clear all jobs
  clearAllJobs() {
    const count = this.state.jobs.length;
    this.state.jobs = [];
    this.updateStats();
    this.saveToStorage();  // Persist to localStorage
    this.emit('jobs:cleared');
    this.emit('state:updated', this.state);

    systemLogger.info(`Cleared all jobs`, { clearedCount: count });
  }

  // Get job by ID
  getJob(jobId) {
    return this.state.jobs.find(j => j.id === jobId);
  }

  // Get all jobs with specific status
  getJobsByStatus(status) {
    return this.state.jobs.filter(j => j.status === status);
  }

  // Update diagnostics
  updateDiagnostics(diagnostics) {
    this.state.diagnostics = { ...this.state.diagnostics, ...diagnostics };
    this.emit('diagnostics:updated', this.state.diagnostics);
    this.emit('state:updated', this.state);

    systemLogger.debug('Diagnostics updated', diagnostics);
  }

  // Update stats
  updateStats() {
    this.state.stats = {
      total: this.state.jobs.length,
      running: this.state.jobs.filter(j => j.status === 'running').length,
      completed: this.state.jobs.filter(j => j.status === 'success').length,
      failed: this.state.jobs.filter(j => j.status === 'error').length
    };

    this.emit('stats:updated', this.state.stats);
  }

  // Get current state
  getState() {
    return this.state;
  }

  // Get config value
  getConfig(key) {
    return this.state.config[key];
  }

  // Set config value
  setConfig(key, value) {
    this.state.config[key] = value;
    this.emit('config:updated', { key, value });

    systemLogger.info(`Config updated: ${key} = ${value}`);
  }
}

// Create singleton instance
export const state = new StateManager();

