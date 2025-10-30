#!/usr/bin/env python3
"""
Decision Matrix MCP Server
Provides decision-making tools for AI agents using weighted criteria analysis
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, CallToolResult, ListResourcesRequest, ListResourcesResult,
    ReadResourceRequest, ReadResourceResult
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Criterion:
    """Represents a decision criterion with weight and description"""
    name: str
    weight: float  # 0.0 to 1.0, should sum to 1.0 across all criteria
    description: str

@dataclass
class Option:
    """Represents a decision option with scores for each criterion"""
    name: str
    description: str
    scores: Dict[str, float]  # criterion_name -> score (0.0 to 10.0)

@dataclass
class DecisionMatrix:
    """Complete decision matrix with criteria, options, and results"""
    title: str
    criteria: List[Criterion]
    options: List[Option]
    results: Optional[Dict[str, float]] = None  # option_name -> weighted_score

class DecisionMatrixMCP:
    """Decision Matrix MCP Server implementation"""

    def __init__(self):
        self.server = Server("decision-matrix")
        self.matrices: Dict[str, DecisionMatrix] = {}
        self.setup_handlers()

    def setup_handlers(self):
        """Set up MCP server handlers"""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available decision matrix tools"""
            return [
                Tool(
                    name="create_decision_matrix",
                    description="Create a new decision matrix with criteria and options",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the decision matrix"
                            },
                            "criteria": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "weight": {"type": "number", "minimum": 0, "maximum": 1},
                                        "description": {"type": "string"}
                                    },
                                    "required": ["name", "weight", "description"]
                                },
                                "description": "List of criteria with weights (should sum to 1.0)"
                            },
                            "options": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "description": {"type": "string"},
                                        "scores": {
                                            "type": "object",
                                            "description": "Scores for each criterion (0-10 scale)"
                                        }
                                    },
                                    "required": ["name", "description", "scores"]
                                },
                                "description": "List of options with scores for each criterion"
                            }
                        },
                        "required": ["title", "criteria", "options"]
                    }
                ),
                Tool(
                    name="analyze_decision_matrix",
                    description="Analyze a decision matrix and calculate weighted scores",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "matrix_id": {
                                "type": "string",
                                "description": "ID of the decision matrix to analyze"
                            }
                        },
                        "required": ["matrix_id"]
                    }
                ),
                Tool(
                    name="get_decision_recommendation",
                    description="Get a recommendation based on decision matrix analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "matrix_id": {
                                "type": "string",
                                "description": "ID of the decision matrix"
                            },
                            "include_rationale": {
                                "type": "boolean",
                                "description": "Include detailed rationale for the recommendation",
                                "default": True
                            }
                        },
                        "required": ["matrix_id"]
                    }
                ),
                Tool(
                    name="list_decision_matrices",
                    description="List all created decision matrices",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_decision_matrix_details",
                    description="Get detailed information about a specific decision matrix",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "matrix_id": {
                                "type": "string",
                                "description": "ID of the decision matrix"
                            }
                        },
                        "required": ["matrix_id"]
                    }
                ),
                Tool(
                    name="update_decision_matrix",
                    description="Update an existing decision matrix",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "matrix_id": {
                                "type": "string",
                                "description": "ID of the decision matrix to update"
                            },
                            "title": {"type": "string"},
                            "criteria": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "weight": {"type": "number", "minimum": 0, "maximum": 1},
                                        "description": {"type": "string"}
                                    },
                                    "required": ["name", "weight", "description"]
                                }
                            },
                            "options": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "description": {"type": "string"},
                                        "scores": {
                                            "type": "object",
                                            "description": "Scores for each criterion (0-10 scale)"
                                        }
                                    },
                                    "required": ["name", "description", "scores"]
                                }
                            }
                        },
                        "required": ["matrix_id"]
                    }
                ),
                Tool(
                    name="delete_decision_matrix",
                    description="Delete a decision matrix",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "matrix_id": {
                                "type": "string",
                                "description": "ID of the decision matrix to delete"
                            }
                        },
                        "required": ["matrix_id"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "create_decision_matrix":
                    return await self.create_decision_matrix(arguments)
                elif name == "analyze_decision_matrix":
                    return await self.analyze_decision_matrix(arguments)
                elif name == "get_decision_recommendation":
                    return await self.get_decision_recommendation(arguments)
                elif name == "list_decision_matrices":
                    return await self.list_decision_matrices(arguments)
                elif name == "get_decision_matrix_details":
                    return await self.get_decision_matrix_details(arguments)
                elif name == "update_decision_matrix":
                    return await self.update_decision_matrix(arguments)
                elif name == "delete_decision_matrix":
                    return await self.delete_decision_matrix(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def create_decision_matrix(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create a new decision matrix"""
        title = args["title"]
        criteria_data = args["criteria"]
        options_data = args["options"]

        # Validate criteria weights sum to 1.0
        total_weight = sum(c["weight"] for c in criteria_data)
        if abs(total_weight - 1.0) > 0.01:
            return [TextContent(type="text", text=f"Error: Criteria weights must sum to 1.0, got {total_weight}")]

        # Create criteria objects
        criteria = [
            Criterion(
                name=c["name"],
                weight=c["weight"],
                description=c["description"]
            )
            for c in criteria_data
        ]

        # Create options objects
        options = [
            Option(
                name=o["name"],
                description=o["description"],
                scores=o["scores"]
            )
            for o in options_data
        ]

        # Create matrix
        matrix_id = f"matrix_{len(self.matrices) + 1}"
        matrix = DecisionMatrix(
            title=title,
            criteria=criteria,
            options=options
        )

        self.matrices[matrix_id] = matrix

        # Auto-analyze the matrix
        await self.analyze_decision_matrix({"matrix_id": matrix_id})

        result = {
            "matrix_id": matrix_id,
            "title": title,
            "criteria_count": len(criteria),
            "options_count": len(options),
            "status": "created_and_analyzed"
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def analyze_decision_matrix(self, args: Dict[str, Any]) -> List[TextContent]:
        """Analyze a decision matrix and calculate weighted scores"""
        matrix_id = args["matrix_id"]

        if matrix_id not in self.matrices:
            return [TextContent(type="text", text=f"Error: Matrix {matrix_id} not found")]

        matrix = self.matrices[matrix_id]

        # Calculate weighted scores for each option
        results = {}
        for option in matrix.options:
            weighted_score = 0.0
            for criterion in matrix.criteria:
                if criterion.name in option.scores:
                    weighted_score += option.scores[criterion.name] * criterion.weight
            results[option.name] = weighted_score

        # Update matrix with results
        matrix.results = results

        # Sort options by score (highest first)
        sorted_options = sorted(results.items(), key=lambda x: x[1], reverse=True)

        analysis = {
            "matrix_id": matrix_id,
            "title": matrix.title,
            "weighted_scores": results,
            "ranking": sorted_options,
            "recommendation": sorted_options[0][0] if sorted_options else None,
            "score_difference": sorted_options[0][1] - sorted_options[1][1] if len(sorted_options) > 1 else 0
        }

        return [TextContent(type="text", text=json.dumps(analysis, indent=2))]

    async def get_decision_recommendation(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get a recommendation based on decision matrix analysis"""
        matrix_id = args["matrix_id"]
        include_rationale = args.get("include_rationale", True)

        if matrix_id not in self.matrices:
            return [TextContent(type="text", text=f"Error: Matrix {matrix_id} not found")]

        matrix = self.matrices[matrix_id]

        if not matrix.results:
            return [TextContent(type="text", text="Error: Matrix not analyzed yet. Run analyze_decision_matrix first.")]

        # Get ranking
        sorted_options = sorted(matrix.results.items(), key=lambda x: x[1], reverse=True)

        if not sorted_options:
            return [TextContent(type="text", text="Error: No options to recommend")]

        recommendation = sorted_options[0]
        recommendation_name = recommendation[0]
        recommendation_score = recommendation[1]

        result = {
            "matrix_id": matrix_id,
            "title": matrix.title,
            "recommendation": recommendation_name,
            "score": recommendation_score,
            "confidence": "high" if len(sorted_options) == 1 or (recommendation_score - sorted_options[1][1]) > 1.0 else "medium"
        }

        if include_rationale:
            # Find the option object for detailed rationale
            option_obj = next((o for o in matrix.options if o.name == recommendation_name), None)
            if option_obj:
                rationale = {
                    "description": option_obj.description,
                    "strengths": [],
                    "weaknesses": []
                }

                # Analyze strengths and weaknesses
                for criterion in matrix.criteria:
                    if criterion.name in option_obj.scores:
                        score = option_obj.scores[criterion.name]
                        weight = criterion.weight
                        contribution = score * weight

                        if score >= 8.0:
                            rationale["strengths"].append(f"Excellent {criterion.name} (score: {score}, weight: {weight:.1%})")
                        elif score <= 4.0:
                            rationale["weaknesses"].append(f"Poor {criterion.name} (score: {score}, weight: {weight:.1%})")

                result["rationale"] = rationale

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def list_decision_matrices(self, args: Dict[str, Any]) -> List[TextContent]:
        """List all created decision matrices"""
        matrices_list = []
        for matrix_id, matrix in self.matrices.items():
            matrices_list.append({
                "matrix_id": matrix_id,
                "title": matrix.title,
                "criteria_count": len(matrix.criteria),
                "options_count": len(matrix.options),
                "analyzed": matrix.results is not None
            })

        result = {
            "total_matrices": len(self.matrices),
            "matrices": matrices_list
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def get_decision_matrix_details(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get detailed information about a specific decision matrix"""
        matrix_id = args["matrix_id"]

        if matrix_id not in self.matrices:
            return [TextContent(type="text", text=f"Error: Matrix {matrix_id} not found")]

        matrix = self.matrices[matrix_id]

        details = {
            "matrix_id": matrix_id,
            "title": matrix.title,
            "criteria": [asdict(c) for c in matrix.criteria],
            "options": [asdict(o) for o in matrix.options],
            "results": matrix.results,
            "analyzed": matrix.results is not None
        }

        return [TextContent(type="text", text=json.dumps(details, indent=2))]

    async def update_decision_matrix(self, args: Dict[str, Any]) -> List[TextContent]:
        """Update an existing decision matrix"""
        matrix_id = args["matrix_id"]

        if matrix_id not in self.matrices:
            return [TextContent(type="text", text=f"Error: Matrix {matrix_id} not found")]

        matrix = self.matrices[matrix_id]

        # Update fields if provided
        if "title" in args:
            matrix.title = args["title"]

        if "criteria" in args:
            criteria_data = args["criteria"]
            total_weight = sum(c["weight"] for c in criteria_data)
            if abs(total_weight - 1.0) > 0.01:
                return [TextContent(type="text", text=f"Error: Criteria weights must sum to 1.0, got {total_weight}")]

            matrix.criteria = [
                Criterion(
                    name=c["name"],
                    weight=c["weight"],
                    description=c["description"]
                )
                for c in criteria_data
            ]

        if "options" in args:
            options_data = args["options"]
            matrix.options = [
                Option(
                    name=o["name"],
                    description=o["description"],
                    scores=o["scores"]
                )
                for o in options_data
            ]

        # Clear results since matrix was updated
        matrix.results = None

        result = {
            "matrix_id": matrix_id,
            "title": matrix.title,
            "status": "updated",
            "note": "Results cleared due to update. Run analyze_decision_matrix to recalculate."
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def delete_decision_matrix(self, args: Dict[str, Any]) -> List[TextContent]:
        """Delete a decision matrix"""
        matrix_id = args["matrix_id"]

        if matrix_id not in self.matrices:
            return [TextContent(type="text", text=f"Error: Matrix {matrix_id} not found")]

        deleted_title = self.matrices[matrix_id].title
        del self.matrices[matrix_id]

        result = {
            "matrix_id": matrix_id,
            "title": deleted_title,
            "status": "deleted"
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="decision-matrix",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

def main():
    """Main entry point"""
    mcp_server = DecisionMatrixMCP()
    import asyncio
    asyncio.run(mcp_server.run())

if __name__ == "__main__":
    main()
