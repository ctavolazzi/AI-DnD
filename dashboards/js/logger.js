/**
 * Comprehensive Logging System
 * Provides detailed console logs for all job lifecycle events
 */

const LogLevel = {
  INFO: 'INFO',
  SUCCESS: 'SUCCESS',
  WARNING: 'WARNING',
  ERROR: 'ERROR',
  DEBUG: 'DEBUG'
};

const LogStyles = {
  INFO: 'background: #3b82f6; color: white; padding: 2px 6px; border-radius: 3px;',
  SUCCESS: 'background: #10b981; color: white; padding: 2px 6px; border-radius: 3px;',
  WARNING: 'background: #f59e0b; color: white; padding: 2px 6px; border-radius: 3px;',
  ERROR: 'background: #ef4444; color: white; padding: 2px 6px; border-radius: 3px;',
  DEBUG: 'background: #8b5cf6; color: white; padding: 2px 6px; border-radius: 3px;'
};

class Logger {
  constructor(module = 'SYSTEM') {
    this.module = module;
    this.startTime = Date.now();
  }

  _log(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const elapsed = ((Date.now() - this.startTime) / 1000).toFixed(3);

    console.groupCollapsed(
      `%c${level}%c [${this.module}] %c+${elapsed}s%c ${message}`,
      LogStyles[level],
      'color: #94a3b8; font-weight: bold;',
      'color: #475569; font-style: italic;',
      'color: #f8fafc;'
    );

    if (data) {
      console.log('📦 Data:', data);
    }

    console.log('🕐 Timestamp:', timestamp);
    console.trace('📍 Stack Trace');
    console.groupEnd();
  }

  info(message, data) {
    this._log(LogLevel.INFO, message, data);
  }

  success(message, data) {
    this._log(LogLevel.SUCCESS, message, data);
  }

  warning(message, data) {
    this._log(LogLevel.WARNING, message, data);
  }

  error(message, data) {
    this._log(LogLevel.ERROR, message, data);
  }

  debug(message, data) {
    this._log(LogLevel.DEBUG, message, data);
  }

  // Special methods for job lifecycle
  jobCreated(job) {
    console.group('%c🆕 JOB CREATED', 'background: #10b981; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;');
    console.log('Job ID:', job.id);
    console.log('Prompt:', job.prompt);
    console.log('Dimensions:', `${job.width}×${job.height}px`);
    console.log('Seed:', job.seed || 'Random');
    console.log('Status:', job.status);
    console.log('Full Job Object:', job);
    console.groupEnd();
  }

  jobQueued(job, queuePosition) {
    console.group('%c📋 JOB QUEUED', 'background: #f59e0b; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;');
    console.log('Job ID:', job.id);
    console.log('Queue Position:', queuePosition);
    console.log('Status:', job.status);
    console.groupEnd();
  }

  jobStarted(job) {
    console.group('%c▶️ JOB STARTED', 'background: #8b5cf6; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;');
    console.log('Job ID:', job.id);
    console.log('Prompt:', job.prompt);
    console.log('Start Time:', new Date(job.startTime).toISOString());
    console.log('Request Payload:', {
      prompt: job.prompt,
      width: job.width,
      height: job.height,
      seed: job.seed
    });
    console.groupEnd();
  }

  jobProgress(job, progress) {
    console.log(
      `%c⏳ JOB PROGRESS%c ${job.id}: ${progress}`,
      'background: #3b82f6; color: white; padding: 2px 6px; border-radius: 3px;',
      'color: #94a3b8;'
    );
  }

  jobCompleted(job) {
    console.group('%c✅ JOB COMPLETED', 'background: #10b981; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;');
    console.log('Job ID:', job.id);
    console.log('Status:', job.status);
    console.log('Duration:', `${job.duration.toFixed(2)}s`);
    console.log('End Time:', new Date(job.endTime).toISOString());
    console.log('Result URL:', job.result);
    console.log('Full Job Object:', job);

    if (job.result) {
      console.log('%c🖼️ Preview Image', 'font-weight: bold; color: #10b981;');
      const img = new Image();
      img.src = job.result;
      img.onload = () => {
        console.log('Image loaded:', {
          width: img.naturalWidth,
          height: img.naturalHeight,
          size: `${(job.result.length / 1024).toFixed(2)} KB`
        });
      };
    }
    console.groupEnd();
  }

  jobFailed(job, error) {
    console.group('%c❌ JOB FAILED', 'background: #ef4444; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;');
    console.log('Job ID:', job.id);
    console.log('Status:', job.status);
    console.log('Duration:', job.duration ? `${job.duration.toFixed(2)}s` : 'N/A');
    console.log('Error Message:', job.error);
    console.error('Error Object:', error);
    console.log('Full Job Object:', job);
    console.groupEnd();
  }

  apiRequest(method, url, payload) {
    console.group('%c🌐 API REQUEST', 'background: #3b82f6; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;');
    console.log('Method:', method);
    console.log('URL:', url);
    console.log('Payload:', payload);
    console.log('Timestamp:', new Date().toISOString());
    console.groupEnd();
  }

  apiResponse(url, status, data) {
    const style = status >= 200 && status < 300 ? LogStyles.SUCCESS : LogStyles.ERROR;
    console.group(`%c📥 API RESPONSE [${status}]`, style);
    console.log('URL:', url);
    console.log('Status:', status);
    console.log('Response Data:', data);
    console.log('Timestamp:', new Date().toISOString());
    console.groupEnd();
  }

  queueStatus(totalJobs, running, completed, failed) {
    console.group('%c📊 QUEUE STATUS', 'background: #475569; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;');
    console.log('Total Jobs:', totalJobs);
    console.log('Running:', running);
    console.log('Completed:', completed);
    console.log('Failed:', failed);
    console.log('Idle/Queued:', totalJobs - running - completed - failed);
    console.groupEnd();
  }

  diagnostics(diagnosticsData) {
    console.group('%c🔧 DIAGNOSTICS UPDATE', 'background: #1e293b; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;');
    console.log('Server Status:', diagnosticsData.server);
    console.log('API Key:', diagnosticsData.api);
    console.log('Balance:', diagnosticsData.balance);
    console.log('Last Checked:', diagnosticsData.lastChecked);
    console.groupEnd();
  }
}

// Create singleton instances for different modules
export const systemLogger = new Logger('SYSTEM');
export const jobLogger = new Logger('JOB');
export const apiLogger = new Logger('API');
export const uiLogger = new Logger('UI');
export const queueLogger = new Logger('QUEUE');

// Export Logger class for custom instances
export { Logger };

