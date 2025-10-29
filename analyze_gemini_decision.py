#!/usr/bin/env python3
"""
Standalone decision matrix analysis for Gemini API integration
"""
import json
from typing import Dict, List, Tuple

def calculate_weighted_scores(criteria: List[Dict], options: List[Dict]) -> Dict[str, float]:
    """Calculate weighted scores for each option"""
    results = {}
    for option in options:
        weighted_score = 0.0
        for criterion in criteria:
            if criterion['name'] in option['scores']:
                raw_score = option['scores'][criterion['name']]
                weight = criterion['weight']
                weighted_score += raw_score * weight
        results[option['name']] = weighted_score
    return results

def analyze_decision_matrix():
    """Run the decision matrix analysis"""
    # Load decision matrix JSON
    with open('gemini_integration_decision_matrix.json', 'r') as f:
        matrix_data = json.load(f)

    print("=" * 80)
    print("GEMINI API COOKBOOK INTEGRATION DECISION MATRIX")
    print("=" * 80)
    print()

    # Calculate weighted scores
    print("📊 Calculating weighted scores...")
    weighted_scores = calculate_weighted_scores(matrix_data['criteria'], matrix_data['options'])

    # Sort by score
    ranked_options = sorted(weighted_scores.items(), key=lambda x: x[1], reverse=True)

    print("✓ Analysis complete")
    print()

    # Display weighted scores
    print("📈 WEIGHTED SCORES (out of 10.0):")
    print("-" * 80)
    for option_name, score in ranked_options:
        bar_length = int(score * 4)
        bar = "█" * bar_length
        print(f"  {option_name:45s} {score:6.2f}  {bar}")
    print()

    # Get winner
    winner_name = ranked_options[0][0]
    winner_score = ranked_options[0][1]
    runner_up_score = ranked_options[1][1] if len(ranked_options) > 1 else 0
    score_diff = winner_score - runner_up_score

    confidence = "HIGH" if score_diff > 1.0 else "MEDIUM" if score_diff > 0.5 else "LOW"

    print("🎯 RECOMMENDATION:")
    print("-" * 80)
    print(f"  ✨ Winner: {winner_name}")
    print(f"  📊 Score: {winner_score:.2f}/10.0")
    print(f"  🎲 Confidence: {confidence}")
    print(f"  📏 Score Difference from Runner-up: {score_diff:.2f}")
    print()

    # Find winner option details
    winner_option = next(o for o in matrix_data['options'] if o['name'] == winner_name)

    print("  📝 Description:")
    print(f"     {winner_option['description']}")
    print()

    # Analyze strengths and weaknesses
    strengths = []
    weaknesses = []
    neutral = []

    for criterion in matrix_data['criteria']:
        if criterion['name'] in winner_option['scores']:
            raw_score = winner_option['scores'][criterion['name']]
            weight = criterion['weight']

            if raw_score >= 8.0:
                strengths.append((criterion['name'], raw_score, weight))
            elif raw_score <= 4.0:
                weaknesses.append((criterion['name'], raw_score, weight))
            else:
                neutral.append((criterion['name'], raw_score, weight))

    if strengths:
        print("  ✅ Strengths:")
        for name, score, weight in strengths:
            print(f"     • Excellent {name.replace('_', ' ').title()}")
            print(f"       Score: {score:.1f}/10.0 | Weight: {weight*100:.0f}% | Contribution: {score*weight:.2f}")

    if neutral:
        print()
        print("  ⚖️  Moderate Areas:")
        for name, score, weight in neutral:
            print(f"     • {name.replace('_', ' ').title()}")
            print(f"       Score: {score:.1f}/10.0 | Weight: {weight*100:.0f}% | Contribution: {score*weight:.2f}")

    if weaknesses:
        print()
        print("  ⚠️  Weaknesses:")
        for name, score, weight in weaknesses:
            print(f"     • Poor {name.replace('_', ' ').title()}")
            print(f"       Score: {score:.1f}/10.0 | Weight: {weight*100:.0f}% | Contribution: {score*weight:.2f}")

    print()
    print("=" * 80)
    print("📋 CRITERIA WEIGHTS:")
    print("-" * 80)
    for criterion in sorted(matrix_data['criteria'], key=lambda x: x['weight'], reverse=True):
        weight_bar = "▓" * int(criterion['weight'] * 50)
        print(f"  {criterion['name']:30s} {criterion['weight']*100:5.1f}%  {weight_bar}")
        print(f"    └─ {criterion['description']}")
    print()

    # Display all options with details
    print("=" * 80)
    print("📊 ALL OPTIONS DETAILED BREAKDOWN:")
    print("-" * 80)
    for i, (option_name, option_score) in enumerate(ranked_options, 1):
        option_data = next(o for o in matrix_data['options'] if o['name'] == option_name)

        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."

        print(f"\n{medal} {option_name.upper().replace('_', ' ')}")
        print(f"   Total Score: {option_score:.2f}/10.0")
        print(f"   {option_data['description']}")
        print()
        print("   Criterion Scores:")
        print("   " + "-" * 76)

        for criterion in matrix_data['criteria']:
            if criterion['name'] in option_data['scores']:
                raw_score = option_data['scores'][criterion['name']]
                weighted = raw_score * criterion['weight']

                # Visual indicator
                if raw_score >= 8.0:
                    indicator = "✓✓"
                elif raw_score >= 6.0:
                    indicator = "✓"
                elif raw_score >= 4.0:
                    indicator = "○"
                else:
                    indicator = "✗"

                print(f"   {indicator} {criterion['name']:30s} {raw_score:4.1f}/10  "
                      f"(weight: {criterion['weight']*100:4.0f}% → {weighted:4.2f})")

    print()
    print("=" * 80)
    print("💡 KEY INSIGHTS:")
    print("-" * 80)

    # Generate insights
    print(f"\n1. WINNING STRATEGY: '{winner_name.replace('_', ' ').title()}'")
    print(f"   This approach scored {winner_score:.2f}/10.0, {score_diff:.2f} points ahead of the runner-up.")
    print()

    # Find what makes it win
    max_contribution = 0
    max_criterion = None
    for criterion in matrix_data['criteria']:
        if criterion['name'] in winner_option['scores']:
            contribution = winner_option['scores'][criterion['name']] * criterion['weight']
            if contribution > max_contribution:
                max_contribution = contribution
                max_criterion = criterion['name']

    if max_criterion:
        print(f"2. CRITICAL SUCCESS FACTOR: '{max_criterion.replace('_', ' ').title()}'")
        print(f"   This criterion contributed {max_contribution:.2f} points to the winning score.")
        print()

    # Compare top 2
    if len(ranked_options) >= 2:
        second_name = ranked_options[1][0]
        second_option = next(o for o in matrix_data['options'] if o['name'] == second_name)

        print(f"3. RUNNER-UP COMPARISON: '{second_name.replace('_', ' ').title()}'")
        print(f"   The winner leads in these key areas:")

        for criterion in matrix_data['criteria']:
            if criterion['name'] in winner_option['scores'] and criterion['name'] in second_option['scores']:
                diff = winner_option['scores'][criterion['name']] - second_option['scores'][criterion['name']]
                if diff > 1.0:
                    print(f"   • {criterion['name'].replace('_', ' ').title()}: +{diff:.1f} points")

    print()
    print("=" * 80)

    return winner_name, winner_score, winner_option

if __name__ == "__main__":
    winner, score, details = analyze_decision_matrix()

    print("\n🎯 FINAL RECOMMENDATION:")
    print("=" * 80)
    print(f"Implement: {winner.replace('_', ' ').title().upper()}")
    print(f"Confidence: {'HIGH - Clear winner' if score > 8.0 else 'MEDIUM - Strong contender'}")
    print("=" * 80)

