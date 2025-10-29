#!/usr/bin/env python3
"""
Test script for Decision Matrix MCP Server
"""

import asyncio
import json
from decision_matrix_mcp_server import DecisionMatrixMCP

async def test_decision_matrix_mcp():
    """Test the Decision Matrix MCP Server"""

    print("🧠 DECISION MATRIX MCP SERVER TEST")
    print("=" * 50)

    # Create server instance
    mcp_server = DecisionMatrixMCP()

    # Test data - similar to the Random User API integration decision
    test_matrix = {
        "title": "Random User API Integration Approach",
        "criteria": [
            {
                "name": "Project Alignment",
                "weight": 0.25,
                "description": "How well the approach aligns with project goals"
            },
            {
                "name": "Implementation Complexity",
                "weight": 0.20,
                "description": "How complex the implementation will be"
            },
            {
                "name": "D&D Value",
                "weight": 0.25,
                "description": "Value added to the D&D game experience"
            },
            {
                "name": "Maintenance Overhead",
                "weight": 0.15,
                "description": "Ongoing maintenance requirements"
            },
            {
                "name": "UX Enhancement",
                "weight": 0.15,
                "description": "User experience improvements"
            }
        ],
        "options": [
            {
                "name": "Create Work Effort + Implement",
                "description": "Create structured work effort and implement integration",
                "scores": {
                    "Project Alignment": 9.0,
                    "Implementation Complexity": 8.0,
                    "D&D Value": 9.0,
                    "Maintenance Overhead": 8.0,
                    "UX Enhancement": 9.0
                }
            },
            {
                "name": "Implement Directly",
                "description": "Implement integration without work effort",
                "scores": {
                    "Project Alignment": 8.0,
                    "Implementation Complexity": 7.0,
                    "D&D Value": 8.0,
                    "Maintenance Overhead": 7.0,
                    "UX Enhancement": 8.0
                }
            },
            {
                "name": "No Implementation",
                "description": "Do not implement the integration",
                "scores": {
                    "Project Alignment": 2.0,
                    "Implementation Complexity": 10.0,
                    "D&D Value": 1.0,
                    "Maintenance Overhead": 10.0,
                    "UX Enhancement": 1.0
                }
            }
        ]
    }

    try:
        # Test 1: Create decision matrix
        print("\n1. 📊 Creating Decision Matrix...")
        create_result = await mcp_server.create_decision_matrix(test_matrix)
        print("Create Result:")
        print(create_result[0].text)

        # Extract matrix_id from result
        create_data = json.loads(create_result[0].text)
        matrix_id = create_data["matrix_id"]
        print(f"Matrix ID: {matrix_id}")

        # Test 2: List matrices
        print("\n2. 📋 Listing Decision Matrices...")
        list_result = await mcp_server.list_decision_matrices({})
        print("List Result:")
        print(list_result[0].text)

        # Test 3: Get matrix details
        print("\n3. 🔍 Getting Matrix Details...")
        details_result = await mcp_server.get_decision_matrix_details({"matrix_id": matrix_id})
        print("Details Result:")
        print(details_result[0].text)

        # Test 4: Get recommendation
        print("\n4. 🎯 Getting Recommendation...")
        rec_result = await mcp_server.get_decision_recommendation({
            "matrix_id": matrix_id,
            "include_rationale": True
        })
        print("Recommendation Result:")
        print(rec_result[0].text)

        # Test 5: Update matrix
        print("\n5. ✏️ Updating Matrix...")
        update_result = await mcp_server.update_decision_matrix({
            "matrix_id": matrix_id,
            "title": "Updated: Random User API Integration Approach"
        })
        print("Update Result:")
        print(update_result[0].text)

        # Test 6: Re-analyze after update
        print("\n6. 🔄 Re-analyzing Matrix...")
        analyze_result = await mcp_server.analyze_decision_matrix({"matrix_id": matrix_id})
        print("Analysis Result:")
        print(analyze_result[0].text)

        # Test 7: Get final recommendation
        print("\n7. 🏆 Final Recommendation...")
        final_rec = await mcp_server.get_decision_recommendation({
            "matrix_id": matrix_id,
            "include_rationale": True
        })
        print("Final Recommendation:")
        print(final_rec[0].text)

        print("\n✅ All tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

async def test_multiple_matrices():
    """Test creating and managing multiple decision matrices"""

    print("\n\n🔄 MULTIPLE MATRICES TEST")
    print("=" * 50)

    mcp_server = DecisionMatrixMCP()

    # Test data for different decisions
    test_matrices = [
        {
            "title": "Technology Stack Decision",
            "criteria": [
                {"name": "Performance", "weight": 0.4, "description": "System performance"},
                {"name": "Maintainability", "weight": 0.3, "description": "Code maintainability"},
                {"name": "Learning Curve", "weight": 0.3, "description": "Team learning curve"}
            ],
            "options": [
                {
                    "name": "Python + FastAPI",
                    "description": "Python with FastAPI framework",
                    "scores": {"Performance": 8.0, "Maintainability": 9.0, "Learning Curve": 7.0}
                },
                {
                    "name": "Node.js + Express",
                    "description": "JavaScript with Express framework",
                    "scores": {"Performance": 7.0, "Maintainability": 8.0, "Learning Curve": 9.0}
                }
            ]
        },
        {
            "title": "UI Framework Decision",
            "criteria": [
                {"name": "Developer Experience", "weight": 0.5, "description": "How pleasant it is to develop with"},
                {"name": "Performance", "weight": 0.3, "description": "Runtime performance"},
                {"name": "Ecosystem", "weight": 0.2, "description": "Available libraries and tools"}
            ],
            "options": [
                {
                    "name": "React",
                    "description": "Facebook's React library",
                    "scores": {"Developer Experience": 9.0, "Performance": 8.0, "Ecosystem": 9.0}
                },
                {
                    "name": "Vue.js",
                    "description": "Progressive JavaScript framework",
                    "scores": {"Developer Experience": 8.0, "Performance": 8.0, "Ecosystem": 7.0}
                }
            ]
        }
    ]

    matrix_ids = []

    try:
        # Create multiple matrices
        for i, matrix_data in enumerate(test_matrices):
            print(f"\nCreating matrix {i+1}: {matrix_data['title']}")
            result = await mcp_server.create_decision_matrix(matrix_data)
            data = json.loads(result[0].text)
            matrix_ids.append(data["matrix_id"])
            print(f"Created with ID: {data['matrix_id']}")

        # List all matrices
        print("\nAll matrices:")
        list_result = await mcp_server.list_decision_matrices({})
        print(list_result[0].text)

        # Get recommendations for each
        for matrix_id in matrix_ids:
            print(f"\nRecommendation for {matrix_id}:")
            rec_result = await mcp_server.get_decision_recommendation({
                "matrix_id": matrix_id,
                "include_rationale": True
            })
            print(rec_result[0].text)

        print("\n✅ Multiple matrices test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Multiple matrices test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("DECISION MATRIX MCP SERVER TEST SUITE")
    print("=" * 60)

    # Run tests
    test1_passed = await test_decision_matrix_mcp()
    test2_passed = await test_multiple_matrices()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    tests = [
        ("Basic Decision Matrix", test1_passed),
        ("Multiple Matrices", test2_passed)
    ]

    passed = sum(1 for _, result in tests if result)
    total = len(tests)

    for test_name, result in tests:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Decision Matrix MCP Server is working correctly.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
