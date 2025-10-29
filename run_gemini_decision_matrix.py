#!/usr/bin/env python3
"""
Run decision matrix analysis for Gemini API integration
"""
import json
import asyncio
from decision_matrix_mcp_server import DecisionMatrixMCP, TextContent

async def run_decision_analysis():
    """Run the decision matrix analysis"""
    # Create MCP server instance
    mcp = DecisionMatrixMCP()

    # Load decision matrix JSON
    with open('gemini_integration_decision_matrix.json', 'r') as f:
        matrix_data = json.load(f)

    print("=" * 80)
    print("GEMINI API COOKBOOK INTEGRATION DECISION MATRIX")
    print("=" * 80)
    print()

    # Create decision matrix
    print("📊 Creating decision matrix...")
    result = await mcp.create_decision_matrix(matrix_data)
    creation_result = json.loads(result[0].text)
    matrix_id = creation_result['matrix_id']
    print(f"✓ Created matrix: {matrix_id}")
    print()

    # Get detailed analysis
    print("🔍 Analyzing options...")
    analysis = await mcp.analyze_decision_matrix({"matrix_id": matrix_id})
    analysis_data = json.loads(analysis[0].text)
    print("✓ Analysis complete")
    print()

    # Display weighted scores
    print("📈 WEIGHTED SCORES (out of 10.0):")
    print("-" * 80)
    for option, score in sorted(analysis_data['weighted_scores'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {option:45s} {score:6.2f}")
    print()

    # Get recommendation with rationale
    print("🎯 RECOMMENDATION:")
    print("-" * 80)
    recommendation = await mcp.get_decision_recommendation({
        "matrix_id": matrix_id,
        "include_rationale": True
    })
    rec_data = json.loads(recommendation[0].text)

    print(f"  Winner: {rec_data['recommendation']}")
    print(f"  Score: {rec_data['score']:.2f}")
    print(f"  Confidence: {rec_data['confidence'].upper()}")
    print()

    if 'rationale' in rec_data:
        print("  Rationale:")
        print(f"    Description: {rec_data['rationale']['description']}")
        print()
        if rec_data['rationale']['strengths']:
            print("    Strengths:")
            for strength in rec_data['rationale']['strengths']:
                print(f"      ✓ {strength}")
        print()
        if rec_data['rationale']['weaknesses']:
            print("    Weaknesses:")
            for weakness in rec_data['rationale']['weaknesses']:
                print(f"      ⚠ {weakness}")

    print()
    print("=" * 80)
    print("CRITERIA WEIGHTS:")
    print("-" * 80)
    for criterion in matrix_data['criteria']:
        print(f"  {criterion['name']:30s} {criterion['weight']*100:5.1f}%  - {criterion['description']}")
    print()

    # Display all options with details
    print("=" * 80)
    print("ALL OPTIONS DETAILS:")
    print("-" * 80)
    for i, option in enumerate(analysis_data['ranking'], 1):
        option_name = option[0]
        option_score = option[1]
        option_data = next(o for o in matrix_data['options'] if o['name'] == option_name)

        print(f"\n{i}. {option_name.upper()} (Score: {option_score:.2f})")
        print(f"   {option_data['description']}")
        print()
        print("   Criterion Breakdown:")
        for criterion in matrix_data['criteria']:
            if criterion['name'] in option_data['scores']:
                raw_score = option_data['scores'][criterion['name']]
                weighted = raw_score * criterion['weight']
                print(f"     {criterion['name']:30s} {raw_score:4.1f}/10  (weighted: {weighted:4.2f})")

    print()
    print("=" * 80)

    return rec_data

if __name__ == "__main__":
    result = asyncio.run(run_decision_analysis())

