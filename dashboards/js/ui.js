/**
 * UI Rendering Module
 * Handles all DOM updates and user interactions
 */

import { uiLogger } from './logger.js';
import { state } from './state.js';
import { jobQueue } from './jobQueue.js';

class UIManager {
  constructor() {
    this.elements = {};
    uiLogger.info('UI Manager initialized');
  }

  // Initialize UI and cache element references
  init() {
    uiLogger.info('Initializing UI elements');

    this.elements = {
      jobsGrid: document.getElementById('jobs-grid'),
      statTotal: document.getElementById('stat-total'),
      statRunning: document.getElementById('stat-running'),
      statSuccess: document.getElementById('stat-success'),
      statError: document.getElementById('stat-error'),
      diagServer: document.getElementById('diag-server'),
      diagApi: document.getElementById('diag-api'),
      diagBalance: document.getElementById('diag-balance'),
      promptInput: document.getElementById('prompt'),
      widthInput: document.getElementById('width'),
      heightInput: document.getElementById('height'),
      seedInput: document.getElementById('seed'),
      addJobBtn: document.getElementById('add-job'),
      addMultipleBtn: document.getElementById('add-multiple'),
      clearAllBtn: document.getElementById('clear-all'),
      rotationJobSelect: document.getElementById('rotation-job-select'),
      rotationFrom: document.getElementById('rotation-from'),
      rotationTo: document.getElementById('rotation-to'),
      rotateCharacterBtn: document.getElementById('rotate-character'),
      rotateAll8Btn: document.getElementById('rotate-all-8')
    };

    // Verify all elements exist
    for (const [key, element] of Object.entries(this.elements)) {
      if (!element) {
        uiLogger.error(`Element not found: ${key}`);
      }
    }

    this.setupEventListeners();
    this.subscribeToState();
    this.restoreJobs();  // Restore persisted jobs

    uiLogger.success('UI initialization complete');
  }

  // Restore jobs from state (loaded from localStorage)
  restoreJobs() {
    const jobs = state.getState().jobs;

    if (jobs.length > 0) {
      uiLogger.info(`Restoring ${jobs.length} persisted jobs`);

      // Render each job (newest first, so reverse)
      jobs.slice().reverse().forEach(job => {
        this.renderJob(job);
      });

      // Update stats
      const stats = state.getState().stats;
      this.updateStats(stats);

      uiLogger.success(`Restored ${jobs.length} jobs from history`);
    } else {
      uiLogger.info('No jobs to restore');
    }
  }

  // Setup event listeners
  setupEventListeners() {
    uiLogger.debug('Setting up event listeners');

    // Preset buttons
    document.querySelectorAll('.preset-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const preset = e.target.dataset.preset;
        uiLogger.info(`Preset clicked: ${preset}`);
        this.applyPreset(preset);
      });
    });

    // Add job button
    this.elements.addJobBtn.addEventListener('click', () => {
      uiLogger.info('Add Job button clicked');
      this.addJob();
    });

    // Add multiple jobs button
    this.elements.addMultipleBtn.addEventListener('click', () => {
      uiLogger.info('Add Multiple Jobs button clicked');
      this.addMultipleJobs(3);
    });

    // Clear all button
    this.elements.clearAllBtn.addEventListener('click', () => {
      uiLogger.info('Clear All button clicked');
      this.clearAllJobs();
    });

    // Rotation buttons
    this.elements.rotateCharacterBtn.addEventListener('click', () => {
      uiLogger.info('Rotate Character button clicked');
      this.rotateCharacter();
    });

    this.elements.rotateAll8Btn.addEventListener('click', () => {
      uiLogger.info('Rotate All 8 Directions button clicked');
      this.rotateAll8Directions();
    });

    uiLogger.success('Event listeners setup complete');
  }

  // Subscribe to state changes
  subscribeToState() {
    uiLogger.debug('Subscribing to state changes');

    state.subscribe('job:added', (job) => {
      uiLogger.debug('State event: job:added', job);
      this.renderJob(job);
    });

    state.subscribe('job:updated', (job) => {
      uiLogger.debug('State event: job:updated', job);
      this.updateJobUI(job);
      // Update rotation dropdown when job completes
      if (job.status === 'success') {
        this.updateRotationDropdown();
      }
    });

    state.subscribe('job:removed', (job) => {
      uiLogger.debug('State event: job:removed', job);
      this.removeJobUI(job);
    });

    state.subscribe('jobs:cleared', () => {
      uiLogger.debug('State event: jobs:cleared');
      this.clearAllJobsUI();
    });

    state.subscribe('stats:updated', (stats) => {
      uiLogger.debug('State event: stats:updated', stats);
      this.updateStats(stats);
    });

    state.subscribe('diagnostics:updated', (diagnostics) => {
      uiLogger.debug('State event: diagnostics:updated', diagnostics);
      this.updateDiagnostics(diagnostics);
    });
  }

  // Apply preset values
  applyPreset(presetName) {
    const presets = {
      knight: { prompt: 'heroic knight with glowing sword, blue cape, ready stance', width: 64, height: 64 },
      mage: { prompt: 'cyberpunk mage with neon circuits, levitating spellbook', width: 64, height: 64 },
      dragon: { prompt: 'adorable pixel dragon companion, bright scales, tiny wings', width: 64, height: 64 },
      warrior: { prompt: 'battle-worn warrior with massive axe, scar across eye', width: 64, height: 64 },
      wizard: { prompt: 'wise old wizard with long beard, staff with glowing crystal', width: 64, height: 64 }
    };

    const preset = presets[presetName];
    if (!preset) {
      uiLogger.warning(`Unknown preset: ${presetName}`);
      return;
    }

    uiLogger.info(`Applying preset: ${presetName}`, preset);

    this.elements.promptInput.value = preset.prompt;
    this.elements.widthInput.value = preset.width;
    this.elements.heightInput.value = preset.height;
    this.elements.seedInput.value = '';
  }

  // Add a new job
  addJob() {
    const prompt = this.elements.promptInput.value.trim();
    const width = parseInt(this.elements.widthInput.value) || 64;
    const height = parseInt(this.elements.heightInput.value) || 64;
    const seed = this.elements.seedInput.value.trim() || null;

    if (!prompt) {
      uiLogger.warning('Add job failed: No prompt provided');
      alert('Please enter a prompt');
      return;
    }

    uiLogger.info('Adding new job', { prompt, width, height, seed });

    jobQueue.createJob(prompt, width, height, seed);
  }

  // Add multiple jobs
  addMultipleJobs(count) {
    const prompt = this.elements.promptInput.value.trim();
    const width = parseInt(this.elements.widthInput.value) || 64;
    const height = parseInt(this.elements.heightInput.value) || 64;

    if (!prompt) {
      uiLogger.warning('Add multiple jobs failed: No prompt provided');
      alert('Please enter a prompt');
      return;
    }

    uiLogger.info(`Adding ${count} jobs`, { prompt, width, height });

    jobQueue.createMultipleJobs(count, prompt, width, height);
  }

  // Clear all jobs
  clearAllJobs() {
    if (!confirm('Clear all jobs?')) {
      uiLogger.info('Clear all jobs cancelled by user');
      return;
    }

    uiLogger.info('Clearing all jobs');
    jobQueue.clearAll();
  }

  // Render a new job box
  renderJob(job) {
    uiLogger.debug(`Rendering job UI: ${job.id}`);

    const box = document.createElement('div');
    box.className = `job-box status-${job.status}`;
    box.id = job.id;
    box.innerHTML = `
      <div class="job-header">
        <div class="job-id">${job.id}</div>
        <div class="job-status ${job.status}">${job.statusEmoji} ${job.statusLabel}</div>
      </div>

      <div class="job-prompt">${job.prompt}</div>

      <div class="job-meta">
        <div class="job-meta-item">
          <span>Dimensions:</span>
          <span class="job-meta-value">${job.width}×${job.height}px</span>
        </div>
        <div class="job-meta-item">
          <span>Duration:</span>
          <span class="job-meta-value" data-field="duration">—</span>
        </div>
      </div>

      <div class="job-result">
        <div class="placeholder">Waiting to start...</div>
      </div>

      <div class="job-actions">
        <button class="job-btn job-btn-primary" data-action="run">▶️ Run</button>
        <button class="job-btn job-btn-secondary" data-action="remove">🗑️ Remove</button>
      </div>
    `;

    // Add event listeners to job buttons
    box.querySelector('[data-action="run"]').addEventListener('click', () => {
      uiLogger.info(`Run button clicked for job: ${job.id}`);
      jobQueue.triggerJob(job.id);
    });

    box.querySelector('[data-action="remove"]').addEventListener('click', () => {
      uiLogger.info(`Remove button clicked for job: ${job.id}`);
      jobQueue.removeJob(job.id);
    });

    this.elements.jobsGrid.insertBefore(box, this.elements.jobsGrid.firstChild);

    uiLogger.success(`Job UI rendered: ${job.id}`);
  }

  // Update existing job UI
  updateJobUI(job) {
    const box = document.getElementById(job.id);
    if (!box) {
      uiLogger.warning(`Job box not found for update: ${job.id}`);
      return;
    }

    uiLogger.debug(`Updating job UI: ${job.id}`, { status: job.status });

    // Update status class and badge
    box.className = `job-box status-${job.status}`;
    const statusBadge = box.querySelector('.job-status');
    statusBadge.className = `job-status ${job.status}`;
    statusBadge.textContent = `${job.statusEmoji} ${job.statusLabel}`;

    // Update duration
    const durationEl = box.querySelector('[data-field="duration"]');
    if (job.duration !== null) {
      durationEl.textContent = `${job.duration.toFixed(2)}s`;
    }

    // Update result area
    const resultArea = box.querySelector('.job-result');

    // Remove any existing error messages
    const existingError = box.querySelector('.error-message');
    if (existingError) {
      existingError.remove();
    }

    if (job.status === 'running') {
      resultArea.innerHTML = '<div class="spinner"></div>';
    } else if (job.status === 'success' && job.result) {
      // Handle result as either string (old format) or object (new format)
      const imageUrl = typeof job.result === 'string' ? job.result : job.result.image_data_url;
      resultArea.innerHTML = `<img src="${imageUrl}" alt="Result">`;
    } else if (job.status === 'error') {
      resultArea.innerHTML = '<div class="placeholder">Generation failed</div>';

      // Add error message
      const errorDiv = document.createElement('div');
      errorDiv.className = 'error-message';
      errorDiv.textContent = job.error || 'Unknown error occurred';
      box.querySelector('.job-actions').insertAdjacentElement('beforebegin', errorDiv);
    } else {
      resultArea.innerHTML = '<div class="placeholder">Waiting to start...</div>';
    }

    // Update run button state
    const runBtn = box.querySelector('[data-action="run"]');
    runBtn.disabled = job.status === 'running';
  }

  // Remove job UI
  removeJobUI(job) {
    const box = document.getElementById(job.id);
    if (!box) {
      uiLogger.warning(`Job box not found for removal: ${job.id}`);
      return;
    }

    uiLogger.debug(`Removing job UI: ${job.id}`);

    box.style.opacity = '0';
    box.style.transform = 'scale(0.95)';

    setTimeout(() => {
      box.remove();
      uiLogger.success(`Job UI removed: ${job.id}`);
    }, 300);
  }

  // Clear all job UIs
  clearAllJobsUI() {
    uiLogger.info('Clearing all job UIs');
    this.elements.jobsGrid.innerHTML = '';
  }

  // Update stats display
  updateStats(stats) {
    uiLogger.debug('Updating stats display', stats);

    this.elements.statTotal.textContent = stats.total;
    this.elements.statRunning.textContent = stats.running;
    this.elements.statSuccess.textContent = stats.completed;
    this.elements.statError.textContent = stats.failed;
  }

  // Update diagnostics display
  updateDiagnostics(diagnostics) {
    uiLogger.debug('Updating diagnostics display', diagnostics);

    // Server status
    this.elements.diagServer.textContent = diagnostics.server.message;
    this.elements.diagServer.className = `diag-value ${diagnostics.server.status}`;

    // API status
    this.elements.diagApi.textContent = diagnostics.api.message;
    this.elements.diagApi.className = `diag-value ${diagnostics.api.status}`;

    // Balance status
    this.elements.diagBalance.textContent = diagnostics.balance.message;
    this.elements.diagBalance.className = `diag-value ${diagnostics.balance.status}`;
  }

  // Update rotation dropdown with completed jobs
  updateRotationDropdown() {
    const jobs = state.getState().jobs;
    const completedJobs = jobs.filter(j => j.status === 'success' && j.result?.image_data_url);

    uiLogger.debug(`Updating rotation dropdown with ${completedJobs.length} completed jobs`);

    const select = this.elements.rotationJobSelect;
    const currentValue = select.value;

    // Clear options except first
    select.innerHTML = '<option value="">-- Select a completed job --</option>';

    // Add options for completed jobs (newest first)
    completedJobs.slice().reverse().forEach(job => {
      const option = document.createElement('option');
      option.value = job.id;
      option.textContent = `${job.id}: ${job.prompt.substring(0, 50)}...`;
      select.appendChild(option);
    });

    // Restore previous selection if still valid
    if (currentValue && completedJobs.some(j => j.id === currentValue)) {
      select.value = currentValue;
    }
  }

  // Rotate a character
  async rotateCharacter() {
    const jobId = this.elements.rotationJobSelect.value;
    const fromDirection = this.elements.rotationFrom.value || null;
    const toDirection = this.elements.rotationTo.value;

    if (!jobId) {
      alert('Please select a completed character first');
      return;
    }

    if (!toDirection) {
      alert('Please select a target direction');
      return;
    }

    const job = state.getJob(jobId);
    if (!job || !job.result?.image_data_url) {
      alert('Selected job has no image data');
      return;
    }

    uiLogger.info(`Rotating ${jobId} to ${toDirection}`);

    // Create a new job for the rotation
    const rotationPrompt = `${job.prompt} (rotated to ${toDirection})`;
    const rotationJob = jobQueue.createJob({
      prompt: rotationPrompt,
      width: job.width,
      height: job.height,
      isRotation: true,
      rotationData: {
        sourceJobId: jobId,
        imageDataUrl: job.result.image_data_url,
        toDirection,
        fromDirection
      }
    });

    uiLogger.info(`Created rotation job: ${rotationJob.id}`);
  }

  // Rotate to all 8 directions
  async rotateAll8Directions() {
    const jobId = this.elements.rotationJobSelect.value;

    if (!jobId) {
      alert('Please select a completed character first');
      return;
    }

    const job = state.getJob(jobId);
    if (!job || !job.result?.image_data_url) {
      alert('Selected job has no image data');
      return;
    }

    const directions = ['north', 'north-east', 'east', 'south-east', 'south', 'south-west', 'west', 'north-west'];

    uiLogger.info(`Creating 8-direction sprite sheet for ${jobId}`);

    // Create rotation jobs for all 8 directions
    directions.forEach(direction => {
      const rotationPrompt = `${job.prompt} (${direction})`;
      jobQueue.createJob({
        prompt: rotationPrompt,
        width: job.width,
        height: job.height,
        isRotation: true,
        rotationData: {
          sourceJobId: jobId,
          imageDataUrl: job.result.image_data_url,
          toDirection: direction,
          fromDirection: null
        }
      });
    });

    uiLogger.success(`Created 8 rotation jobs for sprite sheet`);
  }
}

// Create singleton instance
export const ui = new UIManager();

