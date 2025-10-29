/**
 * Job Queue Manager
 * Handles job lifecycle, queuing, and parallel execution
 */

import { jobLogger, queueLogger } from './logger.js';
import { state } from './state.js';
import { api } from './api.js';

class Job {
  constructor(prompt, width, height, seed = null) {
    this.id = state.getNextJobId();
    this.prompt = prompt;
    this.width = width;
    this.height = height;
    this.seed = seed;
    this.status = 'idle'; // idle, queued, running, success, error
    this.result = null;
    this.error = null;
    this.startTime = null;
    this.endTime = null;
    this.duration = null;
    this.createdAt = Date.now();

    jobLogger.jobCreated(this);
  }

  get statusLabel() {
    return this.status.toUpperCase();
  }

  get statusEmoji() {
    const emojis = {
      idle: '⚪',
      queued: '🟡',
      running: '🔵',
      success: '🟢',
      error: '🔴'
    };
    return emojis[this.status] || '⚪';
  }
}

class JobQueue {
  constructor() {
    this.maxParallelJobs = state.getConfig('maxParallelJobs');
    queueLogger.info('Job Queue initialized', {
      maxParallelJobs: this.maxParallelJobs
    });

    // Listen for config changes
    state.subscribe('config:updated', ({ key, value }) => {
      if (key === 'maxParallelJobs') {
        this.maxParallelJobs = value;
        queueLogger.info('Max parallel jobs updated', { newValue: value });
      }
    });
  }

  // Create and add a new job
  createJob(promptOrConfig, width, height, seed = null) {
    // Support both old API (prompt, width, height, seed) and new API (config object)
    let config;
    if (typeof promptOrConfig === 'object') {
      config = promptOrConfig;
    } else {
      config = { prompt: promptOrConfig, width, height, seed };
    }

    queueLogger.info('Creating new job', config);

    const job = new Job(config.prompt, config.width, config.height, config.seed);

    // Add rotation data if present
    if (config.isRotation) {
      job.isRotation = true;
      job.rotationData = config.rotationData;
    }

    state.addJob(job);

    // Attempt to process queue
    this.processQueue();

    return job;
  }

  // Create multiple jobs
  createMultipleJobs(count, prompt, width, height) {
    queueLogger.info(`Creating ${count} jobs`, { prompt, width, height });

    const jobs = [];
    for (let i = 0; i < count; i++) {
      const job = new Job(prompt, width, height, null);
      state.addJob(job);
      jobs.push(job);
    }

    // Attempt to process queue
    this.processQueue();

    return jobs;
  }

  // Process the job queue
  processQueue() {
    const runningJobs = state.getJobsByStatus('running');
    const idleJobs = state.getJobsByStatus('idle');

    queueLogger.debug('Processing queue', {
      running: runningJobs.length,
      idle: idleJobs.length,
      maxParallel: this.maxParallelJobs
    });

    const slotsAvailable = this.maxParallelJobs - runningJobs.length;

    if (slotsAvailable > 0 && idleJobs.length > 0) {
      queueLogger.info(`${slotsAvailable} slots available, starting jobs`, {
        idleCount: idleJobs.length
      });

      for (let i = 0; i < Math.min(slotsAvailable, idleJobs.length); i++) {
        this.runJob(idleJobs[i]);
      }
    } else if (slotsAvailable === 0) {
      queueLogger.debug('All slots occupied, waiting for completion');
    } else {
      queueLogger.debug('No idle jobs to process');
    }

    // Log current queue status
    this.logQueueStatus();
  }

  // Run a single job
  async runJob(job) {
    jobLogger.info(`Starting job execution: ${job.id}`);

    // Mark as running
    job.status = 'running';
    job.startTime = Date.now();
    state.updateJob(job.id, { status: 'running', startTime: job.startTime });

    jobLogger.jobStarted(job);

    try {
      jobLogger.debug(`Sending API request for job ${job.id}`);

      let result;

      // Check if this is a rotation job
      if (job.isRotation && job.rotationData) {
        // Call rotation API
        result = await api.rotateCharacter(
          job.rotationData.imageDataUrl,
          job.rotationData.toDirection,
          job.rotationData.fromDirection,
          job.width,
          job.height
        );
      } else {
        // Call character generation API
        result = await api.generateCharacter(
          job.prompt,
          job.width,
          job.height,
          job.seed
        );
      }

      jobLogger.debug(`API response received for job ${job.id}`, result);

      // Update job with success
      job.status = 'success';
      job.result = result;  // Store full result object now
      job.endTime = Date.now();
      job.duration = (job.endTime - job.startTime) / 1000;

      state.updateJob(job.id, {
        status: 'success',
        result: job.result,
        endTime: job.endTime,
        duration: job.duration
      });

      jobLogger.jobCompleted(job);

    } catch (error) {
      jobLogger.error(`Job ${job.id} failed`, error);

      // Update job with error
      job.status = 'error';
      job.error = error.message;
      job.endTime = Date.now();
      job.duration = (job.endTime - job.startTime) / 1000;

      state.updateJob(job.id, {
        status: 'error',
        error: job.error,
        endTime: job.endTime,
        duration: job.duration
      });

      jobLogger.jobFailed(job, error);
    }

    // Process next jobs in queue
    queueLogger.info(`Job ${job.id} finished, processing queue`);
    this.processQueue();
  }

  // Manually trigger a job to run (for "Run" button)
  triggerJob(jobId) {
    const job = state.getJob(jobId);

    if (!job) {
      queueLogger.warning(`Job not found: ${jobId}`);
      return;
    }

    if (job.status === 'running') {
      queueLogger.warning(`Job ${jobId} already running`);
      return;
    }

    jobLogger.info(`Manually triggering job: ${jobId}`);

    // Reset job to idle and let queue process it
    job.status = 'idle';
    job.error = null;
    job.result = null;
    job.startTime = null;
    job.endTime = null;
    job.duration = null;

    state.updateJob(jobId, {
      status: 'idle',
      error: null,
      result: null,
      startTime: null,
      endTime: null,
      duration: null
    });

    this.processQueue();
  }

  // Remove a job
  removeJob(jobId) {
    const job = state.getJob(jobId);

    if (!job) {
      queueLogger.warning(`Job not found for removal: ${jobId}`);
      return;
    }

    jobLogger.info(`Removing job: ${jobId}`, { status: job.status });

    state.removeJob(jobId);

    // If it was running, process queue to start next job
    if (job.status === 'running') {
      queueLogger.info('Removed running job, processing queue');
      this.processQueue();
    }
  }

  // Clear all jobs
  clearAll() {
    const jobs = state.getState().jobs;
    const runningCount = jobs.filter(j => j.status === 'running').length;

    queueLogger.info('Clearing all jobs', {
      total: jobs.length,
      running: runningCount
    });

    state.clearAllJobs();
  }

  // Log queue status
  logQueueStatus() {
    const stats = state.getState().stats;
    queueLogger.queueStatus(
      stats.total,
      stats.running,
      stats.completed,
      stats.failed
    );
  }

  // Get queue metrics
  getMetrics() {
    const jobs = state.getState().jobs;
    const completedJobs = jobs.filter(j => j.status === 'success');

    const totalDuration = completedJobs.reduce((sum, job) => sum + (job.duration || 0), 0);
    const avgDuration = completedJobs.length > 0 ? totalDuration / completedJobs.length : 0;

    return {
      total: jobs.length,
      running: state.getJobsByStatus('running').length,
      completed: completedJobs.length,
      failed: state.getJobsByStatus('error').length,
      totalDuration: totalDuration.toFixed(2),
      avgDuration: avgDuration.toFixed(2)
    };
  }
}

// Create singleton instance
export const jobQueue = new JobQueue();
export { Job };

