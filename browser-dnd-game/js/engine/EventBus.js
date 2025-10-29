/**
 * EventBus - Simple pub/sub system for game events
 * Based on learnings from the existing project
 */
class EventBus {
    constructor() {
        this.events = {};
        this.debug = false;
    }

    /**
     * Subscribe to an event
     * @param {string} event - Event name
     * @param {Function} callback - Callback function
     * @returns {Function} Unsubscribe function
     */
    on(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);

        if (this.debug) {
            console.log(`EventBus: Subscribed to ${event}`);
        }

        // Return unsubscribe function
        return () => this.off(event, callback);
    }

    /**
     * Unsubscribe from an event
     * @param {string} event - Event name
     * @param {Function} callback - Callback function
     */
    off(event, callback) {
        if (!this.events[event]) return;

        const index = this.events[event].indexOf(callback);
        if (index > -1) {
            this.events[event].splice(index, 1);
        }

        if (this.debug) {
            console.log(`EventBus: Unsubscribed from ${event}`);
        }
    }

    /**
     * Emit an event
     * @param {string} event - Event name
     * @param {*} data - Event data
     */
    emit(event, data = null) {
        if (!this.events[event]) return;

        if (this.debug) {
            console.log(`EventBus: Emitting ${event}`, data);
        }

        this.events[event].forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`EventBus: Error in ${event} callback:`, error);
            }
        });
    }

    /**
     * Subscribe to an event once
     * @param {string} event - Event name
     * @param {Function} callback - Callback function
     */
    once(event, callback) {
        const onceCallback = (data) => {
            callback(data);
            this.off(event, onceCallback);
        };
        this.on(event, onceCallback);
    }

    /**
     * Clear all events
     */
    clear() {
        this.events = {};
        if (this.debug) {
            console.log('EventBus: Cleared all events');
        }
    }

    /**
     * Get all registered events
     * @returns {Array} List of event names
     */
    getEvents() {
        return Object.keys(this.events);
    }

    /**
     * Get subscriber count for an event
     * @param {string} event - Event name
     * @returns {number} Number of subscribers
     */
    getSubscriberCount(event) {
        return this.events[event] ? this.events[event].length : 0;
    }
}

// Export for use in other modules
window.EventBus = EventBus;
