import logging

class GameEventManager:
    """
    Event manager for the game that enables real-time updates to Obsidian files.
    Publishes events and updates run_data and Current Run.md in real-time.
    """
    def __init__(self, obsidian_logger, run_data, dungeon_master=None):
        self.obsidian = obsidian_logger
        self.run_data = run_data
        self.subscribers = {}
        self.logger = logging.getLogger("game_event_manager")
        self.dungeon_master = dungeon_master  # Store reference to the DungeonMaster instance

    def publish(self, event_type, event_data):
        """
        Publish an event which updates run_data and Current Run.md immediately.

        Args:
            event_type: Type of event (e.g. "character_created", "location_created")
            event_data: Data associated with the event
        """
        # Log the event
        self.logger.debug(f"Event published: {event_type} - {event_data.get('name', '')}")

        # Update run_data based on event type
        self._update_run_data(event_type, event_data)

        # Update Current Run.md immediately
        try:
            # First try to use the direct reference to DungeonMaster instance
            if self.dungeon_master and hasattr(self.dungeon_master, 'update_current_run'):
                self.logger.debug(f"Updating Current Run.md via direct DungeonMaster reference after {event_type}")
                self.dungeon_master.update_current_run()
            else:
                # Import here to avoid circular imports
                # This is a fallback for direct usage of the EventManager
                try:
                    # Try to find a DungeonMaster instance to update the run
                    import sys
                    dm_found = False
                    for module in sys.modules.values():
                        if hasattr(module, 'DungeonMaster'):
                            for obj_name in dir(module):
                                obj = getattr(module, obj_name)
                                if isinstance(obj, module.DungeonMaster) and hasattr(obj, 'update_current_run'):
                                    self.logger.debug(f"Found DungeonMaster instance, updating Current Run.md after {event_type}")
                                    obj.update_current_run()
                                    self.dungeon_master = obj  # Save for future use
                                    dm_found = True
                                    break

                    if not dm_found:
                        self.logger.warning(f"No DungeonMaster instance found to update Current Run.md after {event_type}")
                except Exception as e:
                    self.logger.error(f"Failed to find DungeonMaster: {e}")
                    # Fallback to direct update
                    try:
                        from run_game import update_current_run
                        self.logger.debug(f"Using fallback update_current_run after {event_type}")
                        update_current_run(self.obsidian, self.run_data)
                    except Exception as inner_e:
                        self.logger.error(f"Fallback update also failed: {inner_e}")
        except Exception as e:
            self.logger.error(f"Failed to update Current Run.md: {e}")

        # Notify subscribers if needed
        self._notify_subscribers(event_type, event_data)

    def _update_run_data(self, event_type, event_data):
        """
        Update the run_data based on the event type. This ensures Current Run.md shows
        real-time game state even before a turn is completed.

        Args:
            event_type: Type of event (e.g. "character_created", "location_created")
            event_data: Data associated with the event
        """
        try:
            # Handle character events
            if event_type == "character_created":
                if "characters" not in self.run_data:
                    self.run_data["characters"] = []
                # Ensure we're only adding new characters, no duplicates
                if event_data["name"] not in self.run_data["characters"]:
                    self.run_data["characters"].append(event_data["name"])
                    self.logger.debug(f"Added character {event_data['name']} to run_data")

            elif event_type == "character_updated":
                # No change to run_data needed, as the character is already tracked
                pass

            # Handle location events
            elif event_type == "location_created":
                if "locations" not in self.run_data:
                    self.run_data["locations"] = []
                # Ensure we're only adding new locations, no duplicates
                if event_data["name"] not in self.run_data["locations"]:
                    self.run_data["locations"].append(event_data["name"])
                    self.logger.debug(f"Added location {event_data['name']} to run_data")

            elif event_type == "location_updated":
                # No change to run_data needed, as the location is already tracked
                pass

            # Handle game events
            elif event_type == "event_occurred":
                if "events" not in self.run_data:
                    self.run_data["events"] = []
                self.run_data["events"].append(event_data["name"])
                self.logger.debug(f"Added event {event_data['name']} to run_data")

            elif event_type == "quest_created":
                self.run_data["quest"] = event_data["name"]
                self.logger.debug(f"Set quest to {event_data['name']} in run_data")

            elif event_type == "quest_updated":
                # No change to run_data needed, as the quest is already set
                pass

            elif event_type == "item_created" or event_type == "item_updated":
                # Currently not tracking items in run_data
                # Consider adding if needed for Current Run.md display
                pass

            elif event_type == "combat_started":
                if "combat" not in self.run_data:
                    self.run_data["combat"] = []
                if event_data["name"] not in self.run_data["combat"]:
                    self.run_data["combat"].append(event_data["name"])
                    self.logger.debug(f"Added combat {event_data['name']} to run_data")

            elif event_type == "session_created":
                self.run_data["session"] = event_data["name"]
                self.logger.debug(f"Set session to {event_data['name']} in run_data")

            elif event_type == "relationship_changed":
                # Currently not tracking relationships in run_data
                # Consider adding if needed for Current Run.md display
                pass
        except Exception as e:
            self.logger.error(f"Error updating run_data for {event_type}: {e}")
            # Print full traceback for debugging
            import traceback
            self.logger.error(traceback.format_exc())

    def subscribe(self, event_type, callback):
        """Subscribe a callback to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        self.logger.debug(f"Subscribed to event type: {event_type}")

    def _notify_subscribers(self, event_type, event_data):
        """Notify all subscribers of an event"""
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(event_data)
                except Exception as e:
                    self.logger.error(f"Error in subscriber callback: {e}")

    def unsubscribe(self, event_type, callback):
        """Unsubscribe a callback from an event type"""
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            self.logger.debug(f"Unsubscribed from event type: {event_type}")

    def get_event_types(self):
        """Get all registered event types"""
        return list(self.subscribers.keys())