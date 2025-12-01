"""
Quest and Objective System

Tracks player progress through the game with:
- Main story quests
- Side quests
- Objectives with multiple stages
- Rewards
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum
import json


class QuestStatus(Enum):
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class ObjectiveType(Enum):
    KILL = "kill"  # Kill X enemies of type Y
    COLLECT = "collect"  # Collect X items
    REACH = "reach"  # Reach a location
    TALK = "talk"  # Talk to an NPC
    SURVIVE = "survive"  # Survive X turns
    EXPLORE = "explore"  # Visit X locations


@dataclass
class QuestObjective:
    """A single objective within a quest."""
    description: str
    objective_type: ObjectiveType
    target: str  # What to kill/collect/reach/talk to
    required_count: int = 1
    current_count: int = 0
    completed: bool = False
    optional: bool = False  # Optional objectives give bonus rewards

    @property
    def progress_text(self) -> str:
        if self.required_count > 1:
            return f"{self.description} ({self.current_count}/{self.required_count})"
        return self.description

    def update(self, count: int = 1) -> bool:
        """Update progress. Returns True if objective completed."""
        self.current_count = min(self.current_count + count, self.required_count)
        if self.current_count >= self.required_count:
            self.completed = True
        return self.completed

    def check_completion(self) -> bool:
        """Check if objective is complete."""
        return self.current_count >= self.required_count


@dataclass
class QuestReward:
    """Rewards for completing a quest."""
    xp: int = 0
    gold: int = 0
    items: List[str] = field(default_factory=list)
    unlocks_quest: Optional[str] = None
    unlocks_area: Optional[str] = None


@dataclass
class Quest:
    """A quest with objectives and rewards."""
    id: str
    name: str
    description: str
    objectives: List[QuestObjective]
    rewards: QuestReward
    status: QuestStatus = QuestStatus.NOT_STARTED

    # Quest metadata
    level_requirement: int = 1
    is_main_quest: bool = False
    prerequisite_quests: List[str] = field(default_factory=list)

    # Tracking
    started_on_turn: int = 0
    completed_on_turn: int = 0

    @property
    def progress_percent(self) -> float:
        """Get quest completion percentage."""
        required = [o for o in self.objectives if not o.optional]
        if not required:
            return 100.0
        completed = sum(1 for o in required if o.completed)
        return (completed / len(required)) * 100

    @property
    def is_complete(self) -> bool:
        """Check if all required objectives are complete."""
        return all(o.completed for o in self.objectives if not o.optional)

    def get_active_objectives(self) -> List[QuestObjective]:
        """Get objectives that aren't completed yet."""
        return [o for o in self.objectives if not o.completed]

    def update_objective(self, objective_type: ObjectiveType, target: str, count: int = 1) -> List[QuestObjective]:
        """
        Update matching objectives.
        Returns list of newly completed objectives.
        """
        completed = []
        for obj in self.objectives:
            if obj.objective_type == objective_type and obj.target.lower() == target.lower():
                if not obj.completed and obj.update(count):
                    completed.append(obj)
        return completed


class QuestTracker:
    """
    Manages all quests in the game.
    """

    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.active_quests: List[str] = []
        self.completed_quests: List[str] = []

        # Callbacks
        self.on_quest_started: Optional[Callable[[Quest], None]] = None
        self.on_quest_completed: Optional[Callable[[Quest], None]] = None
        self.on_objective_completed: Optional[Callable[[Quest, QuestObjective], None]] = None

    def register_quest(self, quest: Quest) -> None:
        """Add a quest to the tracker."""
        self.quests[quest.id] = quest

    def start_quest(self, quest_id: str, current_turn: int = 0) -> bool:
        """
        Start a quest if requirements are met.
        Returns True if quest was started.
        """
        if quest_id not in self.quests:
            return False

        quest = self.quests[quest_id]

        # Check if already active or completed
        if quest.status != QuestStatus.NOT_STARTED:
            return False

        # Check prerequisites
        for prereq_id in quest.prerequisite_quests:
            if prereq_id not in self.completed_quests:
                return False

        # Start quest
        quest.status = QuestStatus.ACTIVE
        quest.started_on_turn = current_turn
        self.active_quests.append(quest_id)

        if self.on_quest_started:
            self.on_quest_started(quest)

        return True

    def complete_quest(self, quest_id: str, current_turn: int = 0) -> Optional[QuestReward]:
        """
        Complete a quest and return rewards.
        """
        if quest_id not in self.active_quests:
            return None

        quest = self.quests[quest_id]

        if not quest.is_complete:
            return None

        quest.status = QuestStatus.COMPLETED
        quest.completed_on_turn = current_turn
        self.active_quests.remove(quest_id)
        self.completed_quests.append(quest_id)

        if self.on_quest_completed:
            self.on_quest_completed(quest)

        # Auto-start unlocked quests
        if quest.rewards.unlocks_quest:
            self.start_quest(quest.rewards.unlocks_quest, current_turn)

        return quest.rewards

    def fail_quest(self, quest_id: str) -> None:
        """Mark a quest as failed."""
        if quest_id in self.active_quests:
            quest = self.quests[quest_id]
            quest.status = QuestStatus.FAILED
            self.active_quests.remove(quest_id)

    def update_objectives(
        self,
        objective_type: ObjectiveType,
        target: str,
        count: int = 1
    ) -> List[tuple]:
        """
        Update all matching objectives across active quests.
        Returns list of (quest, objective) tuples for completed objectives.
        """
        completed = []

        for quest_id in self.active_quests:
            quest = self.quests[quest_id]
            newly_completed = quest.update_objective(objective_type, target, count)

            for obj in newly_completed:
                completed.append((quest, obj))
                if self.on_objective_completed:
                    self.on_objective_completed(quest, obj)

        return completed

    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a quest by ID."""
        return self.quests.get(quest_id)

    def get_active_quests(self) -> List[Quest]:
        """Get all active quests."""
        return [self.quests[qid] for qid in self.active_quests]

    def get_available_quests(self, player_level: int) -> List[Quest]:
        """Get quests that can be started."""
        available = []
        for quest_id, quest in self.quests.items():
            if quest.status != QuestStatus.NOT_STARTED:
                continue
            if quest.level_requirement > player_level:
                continue
            # Check prerequisites
            if all(p in self.completed_quests for p in quest.prerequisite_quests):
                available.append(quest)
        return available

    def to_dict(self) -> dict:
        """Serialize quest tracker to dict for saving."""
        return {
            "active_quests": self.active_quests,
            "completed_quests": self.completed_quests,
            "quest_states": {
                qid: {
                    "status": quest.status.value,
                    "started_on_turn": quest.started_on_turn,
                    "completed_on_turn": quest.completed_on_turn,
                    "objectives": [
                        {
                            "current_count": obj.current_count,
                            "completed": obj.completed
                        }
                        for obj in quest.objectives
                    ]
                }
                for qid, quest in self.quests.items()
                if quest.status != QuestStatus.NOT_STARTED
            }
        }

    def from_dict(self, data: dict) -> None:
        """Load quest tracker state from dict."""
        self.active_quests = data.get("active_quests", [])
        self.completed_quests = data.get("completed_quests", [])

        quest_states = data.get("quest_states", {})
        for qid, state in quest_states.items():
            if qid in self.quests:
                quest = self.quests[qid]
                quest.status = QuestStatus(state["status"])
                quest.started_on_turn = state.get("started_on_turn", 0)
                quest.completed_on_turn = state.get("completed_on_turn", 0)

                for i, obj_state in enumerate(state.get("objectives", [])):
                    if i < len(quest.objectives):
                        quest.objectives[i].current_count = obj_state.get("current_count", 0)
                        quest.objectives[i].completed = obj_state.get("completed", False)


# =============================================================================
# MAIN STORY QUESTS
# =============================================================================

def create_main_story_quests() -> List[Quest]:
    """Create the main story quest line."""
    return [
        Quest(
            id="main_01",
            name="The Goblin Problem",
            description="The village is threatened by goblins. Clear them out!",
            is_main_quest=True,
            objectives=[
                QuestObjective(
                    description="Talk to the Village Elder",
                    objective_type=ObjectiveType.TALK,
                    target="Village Elder"
                ),
                QuestObjective(
                    description="Kill 5 Goblins",
                    objective_type=ObjectiveType.KILL,
                    target="Goblin",
                    required_count=5
                ),
                QuestObjective(
                    description="Find the Goblin Camp",
                    objective_type=ObjectiveType.REACH,
                    target="Goblin Camp"
                ),
            ],
            rewards=QuestReward(
                xp=150,
                gold=50,
                items=["Health Potion", "Health Potion"],
                unlocks_quest="main_02"
            )
        ),
        Quest(
            id="main_02",
            name="Into the Caves",
            description="The goblins came from underground. Explore the caves.",
            is_main_quest=True,
            level_requirement=2,
            prerequisite_quests=["main_01"],
            objectives=[
                QuestObjective(
                    description="Enter the Goblin Caves",
                    objective_type=ObjectiveType.REACH,
                    target="Goblin Caves"
                ),
                QuestObjective(
                    description="Defeat the Goblin Chieftain",
                    objective_type=ObjectiveType.KILL,
                    target="Goblin Chieftain"
                ),
                QuestObjective(
                    description="Find the stolen supplies",
                    objective_type=ObjectiveType.COLLECT,
                    target="Stolen Supplies"
                ),
                QuestObjective(
                    description="Rescue the captured merchant (Optional)",
                    objective_type=ObjectiveType.TALK,
                    target="Captured Merchant",
                    optional=True
                ),
            ],
            rewards=QuestReward(
                xp=300,
                gold=100,
                items=["Steel Sword"],
                unlocks_quest="main_03",
                unlocks_area="Dragon's Lair"
            )
        ),
        Quest(
            id="main_03",
            name="The Dragon's Lair",
            description="A dragon lurks beneath the mountains. End this threat!",
            is_main_quest=True,
            level_requirement=5,
            prerequisite_quests=["main_02"],
            objectives=[
                QuestObjective(
                    description="Descend into the Dragon's Lair",
                    objective_type=ObjectiveType.REACH,
                    target="Dragon's Lair"
                ),
                QuestObjective(
                    description="Defeat Vermithrax the Red",
                    objective_type=ObjectiveType.KILL,
                    target="Vermithrax"
                ),
                QuestObjective(
                    description="Claim the Dragon's Hoard",
                    objective_type=ObjectiveType.COLLECT,
                    target="Dragon's Hoard"
                ),
            ],
            rewards=QuestReward(
                xp=1000,
                gold=500,
                items=["Dragon Slayer", "Dragon Scale Armor"]
            )
        ),
    ]


def create_side_quests() -> List[Quest]:
    """Create optional side quests."""
    return [
        Quest(
            id="side_01",
            name="Rat Infestation",
            description="Giant rats are causing problems. Clear them out.",
            is_main_quest=False,
            objectives=[
                QuestObjective(
                    description="Kill 3 Giant Rats",
                    objective_type=ObjectiveType.KILL,
                    target="Giant Rat",
                    required_count=3
                ),
            ],
            rewards=QuestReward(
                xp=50,
                gold=20,
                items=["Health Potion"]
            )
        ),
        Quest(
            id="side_02",
            name="The Herbalist's Request",
            description="Collect healing herbs from the forest.",
            is_main_quest=False,
            objectives=[
                QuestObjective(
                    description="Collect 5 Healing Herbs",
                    objective_type=ObjectiveType.COLLECT,
                    target="Healing Herb",
                    required_count=5
                ),
                QuestObjective(
                    description="Return to the Herbalist",
                    objective_type=ObjectiveType.TALK,
                    target="Herbalist"
                ),
            ],
            rewards=QuestReward(
                xp=75,
                gold=30,
                items=["Greater Health Potion", "Mana Potion"]
            )
        ),
        Quest(
            id="side_03",
            name="Explorer's Guild",
            description="Map out the dangerous areas.",
            is_main_quest=False,
            level_requirement=3,
            objectives=[
                QuestObjective(
                    description="Visit 5 different locations",
                    objective_type=ObjectiveType.EXPLORE,
                    target="location",
                    required_count=5
                ),
            ],
            rewards=QuestReward(
                xp=200,
                gold=75,
                items=["Strength Elixir"]
            )
        ),
    ]

