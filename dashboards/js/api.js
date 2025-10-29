/**
 * API Layer Module
 * Handles all HTTP requests to the PixelLab backend
 */

import { apiLogger } from './logger.js';
import { state } from './state.js';

class APIClient {
  constructor() {
    this.baseUrl = state.getConfig('serverUrl');
    apiLogger.info('API Client initialized', { baseUrl: this.baseUrl });
  }

  async request(method, endpoint, data = null) {
    const url = `${this.baseUrl}${endpoint}`;

    apiLogger.apiRequest(method, url, data);

    const options = {
      method,
      headers: {
        'Content-Type': 'application/json'
      }
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    try {
      const startTime = performance.now();
      const response = await fetch(url, options);
      const duration = ((performance.now() - startTime) / 1000).toFixed(3);

      apiLogger.debug(`Request completed in ${duration}s`, {
        url,
        status: response.status
      });

      if (!response.ok) {
        const errorText = await response.text();
        apiLogger.apiResponse(url, response.status, { error: errorText });
        throw new Error(errorText || `HTTP ${response.status}: ${response.statusText}`);
      }

      const responseData = await response.json();
      apiLogger.apiResponse(url, response.status, responseData);

      return responseData;

    } catch (error) {
      apiLogger.error('Request failed', {
        url,
        method,
        error: error.message
      });
      throw error;
    }
  }

  // Generate character sprite
  async generateCharacter(prompt, width, height, seed = null) {
    apiLogger.info('Generating character', { prompt, width, height, seed });

    const payload = { prompt, width, height };
    if (seed) payload.seed = seed;

    return await this.request('POST', '/generate-character', payload);
  }

  // Rotate character to different direction
  async rotateCharacter(imageDataUrl, toDirection, fromDirection = null, width = 64, height = 64) {
    apiLogger.info('Rotating character', { toDirection, fromDirection, width, height });

    const payload = {
      image_data_url: imageDataUrl,
      to_direction: toDirection,
      width,
      height
    };
    if (fromDirection) payload.from_direction = fromDirection;

    return await this.request('POST', '/rotate-character', payload);
  }

  // Check server health and diagnostics
  async checkHealth() {
    apiLogger.debug('Checking server health');

    try {
      const data = await this.request('GET', '/health');

      const diagnostics = {
        server: {
          status: data.status === 'ok' ? 'ok' : 'error',
          message: data.status === 'ok' ? 'Online' : 'Offline'
        },
        api: {
          status: data.api_key_detected ? 'ok' : 'error',
          message: data.api_key_detected ? 'Detected' : 'Missing'
        },
        balance: {
          status: 'warn',
          message: 'Unavailable'
        },
        lastChecked: new Date()
      };

      if (data.balance?.status === 'ok') {
        diagnostics.balance = {
          status: 'ok',
          message: `$${Number(data.balance.usd || 0).toFixed(2)}`
        };
      } else if (data.balance?.status === 'missing') {
        diagnostics.balance = {
          status: 'warn',
          message: 'No key'
        };
      } else if (data.balance?.message) {
        diagnostics.balance = {
          status: 'warn',
          message: data.balance.message
        };
      }

      apiLogger.success('Health check completed', diagnostics);
      return diagnostics;

    } catch (error) {
      apiLogger.error('Health check failed', error);

      return {
        server: { status: 'error', message: 'Offline' },
        api: { status: 'warn', message: 'Unknown' },
        balance: { status: 'warn', message: 'Unavailable' },
        lastChecked: null
      };
    }
  }

  // Get API balance (if separate endpoint exists)
  async getBalance() {
    apiLogger.debug('Fetching balance');

    try {
      return await this.request('GET', '/balance');
    } catch (error) {
      apiLogger.warning('Balance fetch failed', error);
      return null;
    }
  }
}

// Create singleton instance
export const api = new APIClient();

