#!/usr/bin/env node

/**
 * Simple test for Decision Matrix MCP Server
 */

const { spawn } = require('child_process');

async function testDecisionMatrixMCP() {
  console.log('🧠 Testing Decision Matrix MCP Server');
  console.log('=' * 50);

  // Test data
  const testData = {
    title: "Technology Stack Decision",
    criteria: [
      {
        name: "Performance",
        weight: 0.4,
        description: "System performance requirements"
      },
      {
        name: "Maintainability",
        weight: 0.3,
        description: "Code maintainability"
      },
      {
        name: "Learning Curve",
        weight: 0.3,
        description: "Team learning curve"
      }
    ],
    options: [
      {
        name: "Python + FastAPI",
        description: "Python with FastAPI framework",
        scores: {
          "Performance": 8.0,
          "Maintainability": 9.0,
          "Learning Curve": 7.0
        }
      },
      {
        name: "Node.js + Express",
        description: "JavaScript with Express framework",
        scores: {
          "Performance": 7.0,
          "Maintainability": 8.0,
          "Learning Curve": 9.0
        }
      }
    ]
  };

  try {
    // Start the MCP server
    const server = spawn('node', ['.mcp-servers/decision-matrix/server.js'], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let output = '';
    let error = '';

    server.stdout.on('data', (data) => {
      output += data.toString();
    });

    server.stderr.on('data', (data) => {
      error += data.toString();
    });

    // Send a test request
    const testRequest = {
      jsonrpc: "2.0",
      id: 1,
      method: "tools/call",
      params: {
        name: "create_decision_matrix",
        arguments: testData
      }
    };

    server.stdin.write(JSON.stringify(testRequest) + '\n');

    // Wait a bit for response
    await new Promise(resolve => setTimeout(resolve, 2000));

    server.kill();

    console.log('Server output:', output);
    if (error) {
      console.log('Server error:', error);
    }

    console.log('✅ MCP server test completed');

  } catch (err) {
    console.error('❌ Test failed:', err);
  }
}

testDecisionMatrixMCP();
