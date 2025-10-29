#!/usr/bin/env python3
"""
Task Prioritization Algorithm
Impact/Energy Decision Matrix System

Usage:
    python3 task_prioritization.py [config_file.json]

If no config file is provided, uses tasks_config.json by default.
"""

import json
import sys
from pathlib import Path

def calculate_priority_score(
    short_term_impact: int,      # 1-5 stars
    long_term_impact: int,       # 1-5 stars
    energy_cost: int,            # 1-5 hearts
    available_energy: int,       # Current energy level (1-5)
    long_term_weight: float = 1.5  # How much to value long-term
) -> dict:
    """
    Calculate priority score for a task.

    Formula:
    - Base Impact = Short-Term + (Long-Term × Weight)
    - Efficiency = Base Impact / Energy Cost
    - Energy Penalty = Applied if cost > available energy
    - ROI (Return on Investment) = Total Impact / Energy Cost
    - Final Score = Efficiency × Energy Availability Factor

    Returns dict with multiple scoring perspectives.
    """

    # Calculate base impact
    total_impact = short_term_impact + (long_term_impact * long_term_weight)

    # Calculate efficiency (impact per energy spent)
    efficiency = total_impact / energy_cost

    # Energy availability factor
    if energy_cost > available_energy:
        # Penalty for tasks requiring more energy than available
        energy_factor = available_energy / energy_cost * 0.5
    elif energy_cost <= available_energy * 0.5:
        # Bonus for low-cost tasks when we have energy
        energy_factor = 1.2
    else:
        energy_factor = 1.0

    # Final priority score
    priority_score = efficiency * energy_factor

    # ROI calculation
    roi = total_impact / energy_cost

    # Quick wins (high short-term, low cost)
    quick_win_score = short_term_impact / energy_cost

    # Strategic value (high long-term)
    strategic_score = long_term_impact * (1 / energy_cost)

    return {
        'priority_score': round(priority_score, 2),
        'efficiency': round(efficiency, 2),
        'roi': round(roi, 2),
        'quick_win_score': round(quick_win_score, 2),
        'strategic_score': round(strategic_score, 2),
        'total_impact': round(total_impact, 1),
        'energy_factor': round(energy_factor, 2)
    }


def load_config(config_path: str = None) -> dict:
    """Load task configuration from JSON file."""
    if config_path is None:
        # Default to tasks_config.json in same directory as script
        script_dir = Path(__file__).parent
        config_path = script_dir / 'tasks_config.json'
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        print(f"Please create {config_path} or provide a valid config file path.")
        sys.exit(1)

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {config_path}")
        print(f"Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def main(config_path: str = None):
    # Load configuration
    config = load_config(config_path)

    tasks = config.get('tasks', [])
    AVAILABLE_ENERGY = config.get('available_energy', 4)
    long_term_weight = config.get('long_term_weight', 1.5)

    if not tasks:
        print("Error: No tasks defined in configuration")
        sys.exit(1)

    print("=" * 80)
    print("TASK PRIORITIZATION ANALYSIS")
    print("=" * 80)
    print(f"\nCurrent Energy Level: {AVAILABLE_ENERGY}❤️ / 5❤️")
    if config_path:
        print(f"Config File: {config_path}")
    print("\n" + "=" * 80)

    # Calculate scores for all tasks
    results = []
    for task in tasks:
        scores = calculate_priority_score(
            short_term_impact=task['short_term'],
            long_term_impact=task['long_term'],
            energy_cost=task['energy'],
            available_energy=AVAILABLE_ENERGY,
            long_term_weight=long_term_weight
        )
        results.append({
            **task,
            **scores
        })

    # Sort by priority score
    results.sort(key=lambda x: x['priority_score'], reverse=True)

    print("\n📊 DETAILED RANKINGS\n")
    print(f"{'Rank':<6} {'Task':<28} {'Score':<8} {'ROI':<7} {'Quick':<7} {'Impact':<8} {'Energy':<8}")
    print("-" * 80)

    for rank, result in enumerate(results, 1):
        print(f"{rank:<6} {result['name']:<28} {result['priority_score']:<8} "
              f"{result['roi']:<7} {result['quick_win_score']:<7} "
              f"{result['total_impact']:<8} {result['energy']}❤️")

    # Show alternative rankings
    print("\n" + "=" * 80)
    print("📈 ALTERNATIVE PERSPECTIVES\n")

    # Quick wins
    quick_wins = sorted(results, key=lambda x: x['quick_win_score'], reverse=True)[:3]
    print("🎯 TOP QUICK WINS (High short-term impact, low energy):")
    for i, task in enumerate(quick_wins, 1):
        print(f"   {i}. {task['name']} (Score: {task['quick_win_score']})")

    # Strategic value
    strategic = sorted(results, key=lambda x: x['strategic_score'], reverse=True)[:3]
    print("\n🎯 TOP STRATEGIC VALUE (High long-term impact):")
    for i, task in enumerate(strategic, 1):
        print(f"   {i}. {task['name']} (Score: {task['strategic_score']})")

    # Best ROI
    best_roi = sorted(results, key=lambda x: x['roi'], reverse=True)[:3]
    print("\n💰 BEST ROI (Total impact per energy spent):")
    for i, task in enumerate(best_roi, 1):
        print(f"   {i}. {task['name']} (ROI: {task['roi']})")

    # Recommended action plan
    print("\n" + "=" * 80)
    print("🎯 RECOMMENDED ACTION PLAN\n")

    energy_remaining = AVAILABLE_ENERGY
    plan = []

    for task in results:
        if task['energy'] <= energy_remaining:
            plan.append(task)
            energy_remaining -= task['energy']
            if energy_remaining <= 0:
                break

    print(f"Based on your {AVAILABLE_ENERGY}❤️ energy budget, here's the optimal sequence:\n")

    total_impact = 0
    for i, task in enumerate(plan, 1):
        print(f"{i}. {task['name']}")
        print(f"   Impact: {task['short_term']}⭐ short-term + {task['long_term']}⭐ long-term")
        print(f"   Energy: {task['energy']}❤️")
        print(f"   Priority Score: {task['priority_score']}")
        print(f"   → {task['description']}")
        print()
        total_impact += task['total_impact']

    print(f"Total Energy Used: {AVAILABLE_ENERGY - energy_remaining}❤️ / {AVAILABLE_ENERGY}❤️")
    print(f"Total Impact Delivered: {round(total_impact, 1)}⭐")
    print(f"Energy Remaining: {energy_remaining}❤️")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv) > 1 else None
    main(config_file)
