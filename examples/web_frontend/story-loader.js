/**
 * Story Loader
 * Load and play JSON-based story scripts
 *
 * Story Format:
 * {
 *   "start": {
 *     "image": "path/to/image.jpg",
 *     "text": "Story text here...",
 *     "choices": [
 *       { "text": "Choice 1", "goto": "node_id" },
 *       { "text": "Choice 2", "goto": "other_node" }
 *     ]
 *   },
 *   "node_id": { ... }
 * }
 */

class StoryLoader {
  constructor() {
    this.currentStory = null;
    this.currentNode = null;
    this.variables = {};
    this.visitedNodes = new Set();
  }

  /**
   * Load story from JSON file
   * @param {string} url - URL to JSON file
   * @returns {Promise<Object>} Story data
   */
  async loadFromFile(url) {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to load story: ${response.status}`);
    }
    const storyData = await response.json();
    return this.load(storyData);
  }

  /**
   * Load story from object
   * @param {Object} storyData - Story data object
   * @returns {Object} This story loader for chaining
   */
  load(storyData) {
    this.currentStory = storyData;
    this.variables = {};
    this.visitedNodes.clear();
    return this;
  }

  /**
   * Start playing the story from a specific node
   * @param {string} nodeId - Node ID to start from (default: "start")
   */
  play(nodeId = 'start') {
    if (!this.currentStory) {
      console.error('No story loaded');
      return;
    }

    const node = this.currentStory[nodeId];
    if (!node) {
      console.error(`Node "${nodeId}" not found`);
      return;
    }

    this.visitedNodes.add(nodeId);
    this.currentNode = nodeId;
    this.showNode(node, nodeId);
  }

  /**
   * Display a story node
   * @param {Object} node - Node data
   * @param {string} nodeId - Current node ID
   */
  showNode(node, nodeId) {
    // Process text with variables
    const text = this.processText(node.text);

    // Process image (can be conditional)
    const image = this.processImage(node.image);

    // Execute any actions
    if (node.action) {
      this.executeAction(node.action);
    }

    // Check for conditions
    if (node.condition && !this.evaluateCondition(node.condition)) {
      // Skip this node if condition fails
      if (node.else_goto) {
        this.play(node.else_goto);
      }
      return;
    }

    // Build choices
    const choices = node.choices || [];
    const buttons = choices
      .filter(choice => this.shouldShowChoice(choice))
      .map(choice => this.processText(choice.text));

    // Handle end node
    if (node.end) {
      buttons.push('Restart');
    }

    // Show the window
    window.StoryWindow.show({
      image: image,
      text: text,
      buttons: buttons.length > 0 ? buttons : ['Continue'],
      onChoice: (index) => this.handleChoice(node, index, nodeId),
      allowDismiss: node.dismissible !== false
    });
  }

  /**
   * Handle player choice
   * @param {Object} node - Current node
   * @param {number} choiceIndex - Index of chosen option
   * @param {string} currentNodeId - Current node ID
   */
  handleChoice(node, choiceIndex, currentNodeId) {
    // Handle restart from end node
    if (node.end && choiceIndex === node.choices.length) {
      this.play('start');
      return;
    }

    const choices = node.choices.filter(c => this.shouldShowChoice(c));
    const choice = choices[choiceIndex];

    if (!choice) {
      console.error('Invalid choice index');
      return;
    }

    // Execute choice action
    if (choice.action) {
      this.executeAction(choice.action);
    }

    // Go to next node
    if (choice.goto) {
      this.play(choice.goto);
    } else if (choice.goto === null) {
      // Explicit close
      window.StoryWindow.close();
    }
  }

  /**
   * Check if a choice should be shown based on conditions
   * @param {Object} choice - Choice object
   * @returns {boolean} True if choice should be shown
   */
  shouldShowChoice(choice) {
    if (!choice.condition) return true;
    return this.evaluateCondition(choice.condition);
  }

  /**
   * Process text with variable substitution
   * @param {string} text - Text with {variable} placeholders
   * @returns {string} Processed text
   */
  processText(text) {
    if (!text) return '';
    return text.replace(/\{(\w+)\}/g, (match, varName) => {
      return this.variables[varName] !== undefined ? this.variables[varName] : match;
    });
  }

  /**
   * Process image URL (can be conditional or variable)
   * @param {string|Object} image - Image URL or conditional object
   * @returns {string|null} Processed image URL
   */
  processImage(image) {
    if (!image) return null;
    if (typeof image === 'string') {
      return this.processText(image);
    }
    // Handle conditional images
    if (image.condition) {
      return this.evaluateCondition(image.condition) ? image.url : image.else_url;
    }
    return null;
  }

  /**
   * Execute an action (set variable, etc.)
   * @param {Object|string} action - Action to execute
   */
  executeAction(action) {
    if (typeof action === 'string') {
      // Simple string action: "varName=value"
      const [varName, value] = action.split('=').map(s => s.trim());
      this.setVariable(varName, this.parseValue(value));
    } else if (typeof action === 'object') {
      // Object action with multiple operations
      if (action.set) {
        Object.entries(action.set).forEach(([key, value]) => {
          this.setVariable(key, value);
        });
      }
      if (action.increment) {
        Object.entries(action.increment).forEach(([key, amount]) => {
          this.variables[key] = (this.variables[key] || 0) + amount;
        });
      }
      if (action.callback && typeof window[action.callback] === 'function') {
        window[action.callback](this.variables);
      }
    }
  }

  /**
   * Evaluate a condition
   * @param {string|Object} condition - Condition to evaluate
   * @returns {boolean} Result
   */
  evaluateCondition(condition) {
    if (typeof condition === 'string') {
      // Simple condition: "varName>5" or "varName==value"
      const operators = ['>=', '<=', '==', '!=', '>', '<'];
      for (const op of operators) {
        if (condition.includes(op)) {
          const [left, right] = condition.split(op).map(s => s.trim());
          const leftVal = this.getVariable(left);
          const rightVal = this.parseValue(right);

          switch (op) {
            case '>=': return leftVal >= rightVal;
            case '<=': return leftVal <= rightVal;
            case '==': return leftVal == rightVal;
            case '!=': return leftVal != rightVal;
            case '>': return leftVal > rightVal;
            case '<': return leftVal < rightVal;
          }
        }
      }
      // Simple existence check
      return !!this.getVariable(condition);
    } else if (typeof condition === 'object') {
      // Complex condition
      if (condition.visited) {
        return this.visitedNodes.has(condition.visited);
      }
      if (condition.not_visited) {
        return !this.visitedNodes.has(condition.not_visited);
      }
    }
    return false;
  }

  /**
   * Set a variable
   * @param {string} name - Variable name
   * @param {*} value - Variable value
   */
  setVariable(name, value) {
    this.variables[name] = value;
  }

  /**
   * Get a variable
   * @param {string} name - Variable name
   * @returns {*} Variable value
   */
  getVariable(name) {
    return this.variables[name];
  }

  /**
   * Parse a value from string
   * @param {string} value - String value
   * @returns {*} Parsed value (number, boolean, or string)
   */
  parseValue(value) {
    // Try to parse as number
    if (/^-?\d+\.?\d*$/.test(value)) {
      return parseFloat(value);
    }
    // Parse boolean
    if (value === 'true') return true;
    if (value === 'false') return false;
    // Check if it's a variable reference
    if (this.variables[value] !== undefined) {
      return this.variables[value];
    }
    // Return as string
    return value;
  }

  /**
   * Get current story state
   * @returns {Object} Current state
   */
  getState() {
    return {
      currentNode: this.currentNode,
      variables: { ...this.variables },
      visitedNodes: Array.from(this.visitedNodes)
    };
  }

  /**
   * Restore story state
   * @param {Object} state - Saved state
   */
  setState(state) {
    this.currentNode = state.currentNode;
    this.variables = { ...state.variables };
    this.visitedNodes = new Set(state.visitedNodes);
    if (this.currentNode && this.currentStory) {
      this.play(this.currentNode);
    }
  }

  /**
   * Save state to localStorage
   * @param {string} key - Storage key
   */
  save(key = 'storyProgress') {
    const state = this.getState();
    localStorage.setItem(key, JSON.stringify(state));
  }

  /**
   * Load state from localStorage
   * @param {string} key - Storage key
   * @returns {boolean} True if loaded successfully
   */
  loadSave(key = 'storyProgress') {
    const saved = localStorage.getItem(key);
    if (saved) {
      const state = JSON.parse(saved);
      this.setState(state);
      return true;
    }
    return false;
  }
}

// Create global instance
const storyLoader = new StoryLoader();

// Export for ES6 modules
export default StoryLoader;
export { storyLoader };

// Expose globally for non-module usage
if (typeof window !== 'undefined') {
  window.StoryLoader = StoryLoader;
  window.storyLoader = storyLoader;
}
