# Decision Matrix MCP Server

A Model Context Protocol (MCP) server that provides decision-making tools for AI agents using weighted criteria analysis.

## Overview

The Decision Matrix MCP Server allows AI agents to create, analyze, and manage decision matrices for complex decision-making scenarios. It provides tools for:

- Creating decision matrices with weighted criteria
- Analyzing options against criteria
- Getting recommendations with rationale
- Managing multiple decision matrices
- Updating and deleting matrices

## Features

### Core Functionality
- **Weighted Criteria Analysis**: Define criteria with importance weights
- **Option Scoring**: Score options against each criterion (0-10 scale)
- **Automatic Analysis**: Calculate weighted scores and rankings
- **Recommendations**: Get top recommendations with detailed rationale
- **Matrix Management**: Create, update, delete, and list matrices

### Decision Matrix Tools
1. `create_decision_matrix` - Create a new decision matrix
2. `analyze_decision_matrix` - Analyze and calculate weighted scores
3. `get_decision_recommendation` - Get recommendation with rationale
4. `list_decision_matrices` - List all created matrices
5. `get_decision_matrix_details` - Get detailed matrix information
6. `update_decision_matrix` - Update existing matrix
7. `delete_decision_matrix` - Delete a matrix

## Installation

### Prerequisites
- Python 3.8+
- MCP framework

### Setup
1. **Install dependencies:**
   ```bash
   pip install -r decision_matrix_requirements.txt
   ```

2. **Make server executable:**
   ```bash
   chmod +x decision_matrix_mcp_server.py
   ```

3. **Configure MCP client:**
   Add to your MCP configuration file:
   ```json
   {
     "mcpServers": {
       "decision-matrix": {
         "command": "python3",
         "args": ["/path/to/decision_matrix_mcp_server.py"],
         "env": {}
       }
     }
   }
   ```

## Usage

### Basic Example

```python
# Create a decision matrix
matrix_data = {
    "title": "Technology Stack Decision",
    "criteria": [
        {
            "name": "Performance",
            "weight": 0.4,
            "description": "System performance requirements"
        },
        {
            "name": "Maintainability",
            "weight": 0.3,
            "description": "Code maintainability"
        },
        {
            "name": "Learning Curve",
            "weight": 0.3,
            "description": "Team learning curve"
        }
    ],
    "options": [
        {
            "name": "Python + FastAPI",
            "description": "Python with FastAPI framework",
            "scores": {
                "Performance": 8.0,
                "Maintainability": 9.0,
                "Learning Curve": 7.0
            }
        },
        {
            "name": "Node.js + Express",
            "description": "JavaScript with Express framework",
            "scores": {
                "Performance": 7.0,
                "Maintainability": 8.0,
                "Learning Curve": 9.0
            }
        }
    ]
}

# Create matrix (auto-analyzes)
result = await create_decision_matrix(matrix_data)
matrix_id = result["matrix_id"]

# Get recommendation
recommendation = await get_decision_recommendation({
    "matrix_id": matrix_id,
    "include_rationale": True
})
```

### Advanced Features

#### Weighted Scoring
Criteria weights must sum to 1.0:
```json
{
    "criteria": [
        {"name": "Cost", "weight": 0.4},
        {"name": "Quality", "weight": 0.4},
        {"name": "Speed", "weight": 0.2}
    ]
}
```

#### Option Scoring
Score options on 0-10 scale for each criterion:
```json
{
    "scores": {
        "Cost": 8.0,
        "Quality": 9.0,
        "Speed": 6.0
    }
}
```

#### Detailed Recommendations
Include rationale for recommendations:
```python
recommendation = await get_decision_recommendation({
    "matrix_id": "matrix_1",
    "include_rationale": True
})
```

## API Reference

### create_decision_matrix
Creates a new decision matrix with criteria and options.

**Parameters:**
- `title` (string): Title of the decision matrix
- `criteria` (array): List of criteria with name, weight, and description
- `options` (array): List of options with name, description, and scores

**Returns:**
- `matrix_id`: Unique identifier for the matrix
- `status`: Creation status

### analyze_decision_matrix
Analyzes a decision matrix and calculates weighted scores.

**Parameters:**
- `matrix_id` (string): ID of the matrix to analyze

**Returns:**
- `weighted_scores`: Scores for each option
- `ranking`: Options ranked by score
- `recommendation`: Top recommendation
- `score_difference`: Difference between top options

### get_decision_recommendation
Gets a recommendation with optional rationale.

**Parameters:**
- `matrix_id` (string): ID of the matrix
- `include_rationale` (boolean): Include detailed rationale

**Returns:**
- `recommendation`: Recommended option
- `score`: Recommendation score
- `confidence`: High/medium confidence level
- `rationale`: Detailed analysis (if requested)

### list_decision_matrices
Lists all created decision matrices.

**Returns:**
- `total_matrices`: Number of matrices
- `matrices`: List of matrix summaries

### get_decision_matrix_details
Gets detailed information about a specific matrix.

**Parameters:**
- `matrix_id` (string): ID of the matrix

**Returns:**
- Complete matrix details including criteria, options, and results

### update_decision_matrix
Updates an existing decision matrix.

**Parameters:**
- `matrix_id` (string): ID of the matrix to update
- `title` (string, optional): New title
- `criteria` (array, optional): New criteria
- `options` (array, optional): New options

**Returns:**
- Update status and note about results clearing

### delete_decision_matrix
Deletes a decision matrix.

**Parameters:**
- `matrix_id` (string): ID of the matrix to delete

**Returns:**
- Deletion confirmation

## Testing

Run the test suite:
```bash
python3 test_decision_matrix_mcp.py
```

The test suite includes:
- Basic decision matrix creation and analysis
- Multiple matrix management
- Recommendation generation
- Matrix updates and deletions

## Error Handling

The server includes comprehensive error handling for:
- Invalid criteria weights (must sum to 1.0)
- Missing matrix IDs
- Invalid option scores
- Analysis errors

## Use Cases

### AI Agent Decision Making
- Technology stack selection
- Feature prioritization
- Resource allocation
- Project approach selection

### Business Decision Support
- Vendor selection
- Investment decisions
- Strategic planning
- Risk assessment

### Personal Decision Making
- Career choices
- Purchase decisions
- Life planning
- Goal prioritization

## Architecture

### Core Components
- `DecisionMatrixMCP`: Main server class
- `Criterion`: Represents decision criteria
- `Option`: Represents decision options
- `DecisionMatrix`: Complete matrix with results

### Data Flow
1. Create matrix with criteria and options
2. Auto-analyze to calculate weighted scores
3. Get recommendations with rationale
4. Update or delete as needed

### Scoring Algorithm
```
Weighted Score = Σ(Criterion Score × Criterion Weight)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check the test suite for examples
2. Review the API reference
3. Create an issue with detailed description

## Changelog

### v1.0.0
- Initial release
- Core decision matrix functionality
- MCP server implementation
- Comprehensive test suite
- Full API documentation
