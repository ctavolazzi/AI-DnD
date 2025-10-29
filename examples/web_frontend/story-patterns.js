/**
 * Story Patterns Library
 * Pre-built patterns for common storytelling scenarios
 *
 * Usage:
 *   import StoryPatterns from './story-patterns.js';
 *   StoryPatterns.dialogue(character, "Hello!", () => { ... });
 */

const StoryPatterns = {
  /**
   * Simple dialogue - Character says something with a continue button
   * @param {Object} character - Character object with name and portrait
   * @param {string} text - What the character says
   * @param {Function} onContinue - Callback when player clicks continue
   */
  dialogue(character, text, onContinue) {
    window.StoryWindow.show({
      image: character.portrait || character.image,
      text: `${character.name}: "${text}"`,
      buttons: ['Continue'],
      onChoice: onContinue
    });
  },

  /**
   * Narrator text - No character, just story narration
   * @param {string} text - Narrative text
   * @param {Function} onContinue - Callback when player clicks continue
   */
  narrate(text, onContinue) {
    window.StoryWindow.show({
      text: text,
      buttons: ['Continue'],
      onChoice: onContinue
    });
  },

  /**
   * Yes/No decision
   * @param {string} text - Question or prompt
   * @param {Function} yesCallback - Called when player chooses Yes
   * @param {Function} noCallback - Called when player chooses No
   * @param {string} image - Optional image URL
   */
  yesNo(text, yesCallback, noCallback, image = null) {
    window.StoryWindow.show({
      image: image,
      text: text,
      buttons: ['Yes', 'No'],
      onChoice: (choice) => {
        if (choice === 0) yesCallback();
        else noCallback();
      }
    });
  },

  /**
   * Multiple choice question
   * @param {string} text - Question text
   * @param {Array<{text: string, callback: Function}>} choices - Array of choice objects
   * @param {string} image - Optional image URL
   */
  multipleChoice(text, choices, image = null) {
    const buttons = choices.map(c => c.text);
    window.StoryWindow.show({
      image: image,
      text: text,
      buttons: buttons,
      onChoice: (index) => {
        if (choices[index].callback) {
          choices[index].callback();
        }
      }
    });
  },

  /**
   * Combat encounter interface
   * @param {Object} enemy - Enemy object with name, image, hp, maxHp
   * @param {Function} onAction - Callback with action index (0=Attack, 1=Defend, 2=Item, 3=Flee)
   */
  encounter(enemy, onAction) {
    const hpPercent = Math.round((enemy.hp / enemy.maxHp) * 100);
    window.StoryWindow.show({
      image: enemy.image,
      text: `${enemy.name} appears!\n\nHP: ${enemy.hp}/${enemy.maxHp} (${hpPercent}%)`,
      buttons: ['Attack', 'Defend', 'Item', 'Flee'],
      onChoice: onAction
    });
  },

  /**
   * Shop/merchant interface
   * @param {Object} merchant - Merchant object
   * @param {Array} items - Items for sale
   * @param {Function} onPurchase - Callback with item index
   * @param {Function} onLeave - Callback when player leaves
   */
  shop(merchant, items, onPurchase, onLeave) {
    const itemText = items.map((item, i) =>
      `${i + 1}. ${item.name} - ${item.price} gold`
    ).join('\n');

    const text = `${merchant.name}: "Take a look at my wares!"\n\n${itemText}`;
    const buttons = items.slice(0, 3).map(item => item.name);
    buttons.push('Leave');

    window.StoryWindow.show({
      image: merchant.image,
      text: text,
      buttons: buttons,
      onChoice: (choice) => {
        if (choice === buttons.length - 1) {
          onLeave();
        } else {
          onPurchase(choice);
        }
      }
    });
  },

  /**
   * Item found notification
   * @param {Object} item - Item object with name, image, description
   * @param {Function} onTake - Callback when taken
   * @param {Function} onLeave - Callback when left
   */
  itemFound(item, onTake, onLeave) {
    window.StoryWindow.show({
      image: item.image,
      text: `You found: ${item.name}\n\n${item.description}`,
      buttons: ['Take', 'Leave'],
      onChoice: (choice) => {
        if (choice === 0) onTake();
        else onLeave();
      }
    });
  },

  /**
   * Location description
   * @param {Object} location - Location with name, image, description
   * @param {Array<string>} actions - Available actions
   * @param {Function} onAction - Callback with action index
   */
  location(location, actions, onAction) {
    window.StoryWindow.show({
      image: location.image,
      text: `${location.name}\n\n${location.description}`,
      buttons: actions,
      onChoice: onAction
    });
  },

  /**
   * Character meets character
   * @param {Object} character - Character encountered
   * @param {string} meetingText - Description of meeting
   * @param {Array<string>} responses - Possible responses
   * @param {Function} onResponse - Callback with response index
   */
  meet(character, meetingText, responses, onResponse) {
    window.StoryWindow.show({
      image: character.portrait || character.image,
      text: `You encounter ${character.name}.\n\n${meetingText}`,
      buttons: responses,
      onChoice: onResponse
    });
  },

  /**
   * Quest offer
   * @param {Object} quest - Quest object with title, description, giver
   * @param {Function} onAccept - Callback when accepted
   * @param {Function} onDecline - Callback when declined
   */
  questOffer(quest, onAccept, onDecline) {
    window.StoryWindow.show({
      image: quest.giver?.portrait,
      text: `${quest.title}\n\n${quest.description}\n\nReward: ${quest.reward}`,
      buttons: ['Accept', 'Decline', 'Ask for more details'],
      onChoice: (choice) => {
        if (choice === 0) onAccept();
        else if (choice === 1) onDecline();
        else if (choice === 2 && quest.details) {
          window.StoryWindow.update({
            text: `${quest.title}\n\n${quest.details}`,
            buttons: ['Accept', 'Decline']
          });
        }
      }
    });
  },

  /**
   * Game over / Victory screen
   * @param {boolean} victory - True for victory, false for defeat
   * @param {string} message - End game message
   * @param {Function} onRestart - Callback to restart
   * @param {Function} onQuit - Callback to quit
   */
  gameEnd(victory, message, onRestart, onQuit) {
    window.StoryWindow.show({
      image: victory ? 'images/victory.jpg' : 'images/defeat.jpg',
      text: `${victory ? 'VICTORY!' : 'DEFEAT'}\n\n${message}`,
      buttons: ['Restart', 'Main Menu', 'Quit'],
      onChoice: (choice) => {
        if (choice === 0) onRestart();
        else if (choice === 2) onQuit();
      },
      allowDismiss: false
    });
  },

  /**
   * Confirmation dialog
   * @param {string} action - Action to confirm (e.g., "delete this save")
   * @param {Function} onConfirm - Callback when confirmed
   * @param {Function} onCancel - Callback when cancelled
   */
  confirm(action, onConfirm, onCancel) {
    window.StoryWindow.show({
      text: `Are you sure you want to ${action}?`,
      buttons: ['Confirm', 'Cancel'],
      onChoice: (choice) => {
        if (choice === 0) onConfirm();
        else onCancel();
      },
      allowDismiss: false
    });
  },

  /**
   * Info message (just shows info with OK button)
   * @param {string} text - Information to display
   * @param {string} image - Optional image
   */
  info(text, image = null) {
    window.StoryWindow.show({
      image: image,
      text: text,
      buttons: ['OK']
    });
  }
};

// Export for ES6 modules
export default StoryPatterns;

// Also expose globally for non-module usage
if (typeof window !== 'undefined') {
  window.StoryPatterns = StoryPatterns;
}
