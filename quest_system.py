import logging
import datetime
from typing import List, Dict, Optional, Any
from enum import Enum

logger = logging.getLogger("quest_system")


class QuestStatus(Enum):
    """Status of a quest."""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    AVAILABLE = "available"


class ObjectiveStatus(Enum):
    """Status of a quest objective."""
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"
    FAILED = "failed"


class QuestObjective:
    """Represents a single objective within a quest."""

    def __init__(self, description: str, objective_type: str = "general",
                 target: Optional[str] = None, quantity: int = 1):
        """
        Initialize a quest objective.

        Args:
            description: What needs to be done
            objective_type: Type of objective (defeat, collect, explore, talk, etc.)
            target: The target of the objective (enemy name, item name, location, etc.)
            quantity: How many times the objective must be completed
        """
        self.description = description
        self.objective_type = objective_type
        self.target = target
        self.quantity = quantity
        self.progress = 0
        self.status = ObjectiveStatus.INCOMPLETE

    def update_progress(self, amount: int = 1) -> bool:
        """
        Update objective progress.

        Args:
            amount: Amount to add to progress

        Returns:
            True if objective was completed by this update
        """
        if self.status == ObjectiveStatus.COMPLETE:
            return False

        self.progress = min(self.progress + amount, self.quantity)

        if self.progress >= self.quantity:
            self.status = ObjectiveStatus.COMPLETE
            logger.info(f"Objective completed: {self.description}")
            return True

        logger.info(f"Objective progress: {self.description} ({self.progress}/{self.quantity})")
        return False

    def is_complete(self) -> bool:
        """Check if objective is complete."""
        return self.status == ObjectiveStatus.COMPLETE

    def to_dict(self) -> dict:
        """Convert objective to dictionary."""
        return {
            "description": self.description,
            "type": self.objective_type,
            "target": self.target,
            "quantity": self.quantity,
            "progress": self.progress,
            "status": self.status.value
        }


class Quest:
    """Represents a quest with objectives and rewards."""

    def __init__(self, quest_id: str, title: str, description: str,
                 objectives: List[QuestObjective] = None, rewards: Dict[str, Any] = None):
        """
        Initialize a quest.

        Args:
            quest_id: Unique identifier for the quest
            title: Quest title
            description: Quest description/backstory
            objectives: List of objectives to complete
            rewards: Dictionary of rewards (exp, gold, items, etc.)
        """
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.objectives = objectives or []
        self.rewards = rewards or {"exp": 100, "gold": 50}
        self.status = QuestStatus.ACTIVE
        self.start_time = datetime.datetime.now()
        self.completion_time = None

    def add_objective(self, objective: QuestObjective) -> None:
        """Add an objective to the quest."""
        self.objectives.append(objective)
        logger.info(f"Added objective to {self.title}: {objective.description}")

    def update_objective(self, objective_description: str, progress: int = 1) -> bool:
        """
        Update progress on an objective by description.

        Args:
            objective_description: Description of the objective to update
            progress: Amount of progress to add

        Returns:
            True if the objective was completed
        """
        for objective in self.objectives:
            if objective.description == objective_description:
                return objective.update_progress(progress)
        return False

    def check_completion(self) -> bool:
        """
        Check if all objectives are complete and update quest status.

        Returns:
            True if quest was just completed
        """
        if self.status == QuestStatus.COMPLETED:
            return False

        if all(obj.is_complete() for obj in self.objectives):
            self.status = QuestStatus.COMPLETED
            self.completion_time = datetime.datetime.now()
            logger.info(f"Quest completed: {self.title}")
            return True

        return False

    def get_active_objectives(self) -> List[QuestObjective]:
        """Get list of incomplete objectives."""
        return [obj for obj in self.objectives if not obj.is_complete()]

    def get_progress_summary(self) -> str:
        """Get a summary of quest progress."""
        total = len(self.objectives)
        completed = sum(1 for obj in self.objectives if obj.is_complete())
        return f"{completed}/{total} objectives complete"

    def to_dict(self) -> dict:
        """Convert quest to dictionary."""
        return {
            "quest_id": self.quest_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "rewards": self.rewards,
            "progress_summary": self.get_progress_summary(),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "completion_time": self.completion_time.isoformat() if self.completion_time else None
        }


class QuestManager:
    """Manages all quests in the game."""

    def __init__(self):
        """Initialize the quest manager."""
        self.quests: Dict[str, Quest] = {}
        self.quest_counter = 0
        self.logger = logging.getLogger("quest_manager")

    def create_quest(self, title: str, description: str,
                    objectives: List[QuestObjective] = None,
                    rewards: Dict[str, Any] = None) -> Quest:
        """
        Create a new quest.

        Args:
            title: Quest title
            description: Quest description
            objectives: List of objectives
            rewards: Dictionary of rewards

        Returns:
            The created quest
        """
        self.quest_counter += 1
        quest_id = f"quest_{self.quest_counter:03d}"

        quest = Quest(quest_id, title, description, objectives, rewards)
        self.quests[quest_id] = quest

        self.logger.info(f"Created quest: {title} (ID: {quest_id})")
        return quest

    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a quest by ID."""
        return self.quests.get(quest_id)

    def get_active_quests(self) -> List[Quest]:
        """Get all active quests."""
        return [q for q in self.quests.values() if q.status == QuestStatus.ACTIVE]

    def get_completed_quests(self) -> List[Quest]:
        """Get all completed quests."""
        return [q for q in self.quests.values() if q.status == QuestStatus.COMPLETED]

    def update_quest_progress(self, quest_id: str, objective_description: str,
                            progress: int = 1) -> bool:
        """
        Update progress on a quest objective.

        Args:
            quest_id: ID of the quest to update
            objective_description: Description of the objective
            progress: Amount of progress to add

        Returns:
            True if the quest was completed
        """
        quest = self.get_quest(quest_id)
        if not quest:
            self.logger.warning(f"Quest not found: {quest_id}")
            return False

        quest.update_objective(objective_description, progress)
        return quest.check_completion()

    def generate_starter_quest(self, location: str, characters: List[str]) -> Quest:
        """
        Generate a simple starter quest based on context.

        Args:
            location: Current location
            characters: List of character names

        Returns:
            Generated quest
        """
        # Create a simple starter quest
        objectives = [
            QuestObjective("Explore the current area", "explore", location, 1),
            QuestObjective("Defeat enemies in combat", "defeat", "enemies", 3),
            QuestObjective("Make decisions to progress the story", "general", None, 2)
        ]

        quest = self.create_quest(
            title="The Beginning of an Adventure",
            description=f"You and your companions have arrived at {location}. Explore the area, face challenges, and begin your journey.",
            objectives=objectives,
            rewards={"exp": 200, "gold": 100}
        )

        return quest

    def check_objective_triggers(self, event_type: str, event_data: dict) -> List[str]:
        """
        Check if an event triggers any quest objective updates.

        Args:
            event_type: Type of event (combat, exploration, dialogue, etc.)
            event_data: Event data dictionary

        Returns:
            List of quest IDs that were updated
        """
        updated_quests = []

        for quest in self.get_active_quests():
            for objective in quest.get_active_objectives():
                # Check if objective matches event
                if self._objective_matches_event(objective, event_type, event_data):
                    quest.update_objective(objective.description, 1)
                    if quest.check_completion():
                        updated_quests.append(quest.quest_id)

        return updated_quests

    def _objective_matches_event(self, objective: QuestObjective,
                                 event_type: str, event_data: dict) -> bool:
        """Check if an objective matches an event."""
        # Combat-related objectives
        if objective.objective_type == "defeat" and event_type == "combat_victory":
            return True

        # Exploration objectives
        if objective.objective_type == "explore" and event_type == "location_entered":
            if objective.target and objective.target in event_data.get("location", ""):
                return True

        # General objectives triggered by various actions
        if objective.objective_type == "general" and event_type in ["player_action", "choice_made"]:
            return True

        return False

    def get_all_active_objectives(self) -> List[tuple]:
        """
        Get all active objectives from all active quests.

        Returns:
            List of tuples (quest_title, objective)
        """
        active_objectives = []
        for quest in self.get_active_quests():
            for objective in quest.get_active_objectives():
                active_objectives.append((quest.title, objective))
        return active_objectives


