#!/usr/bin/env python3
"""
Comprehensive MCP Server Test Suite
Tests all the MCP servers we've created today
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

class MCPServerTester:
    def __init__(self):
        self.servers = {
            'decision-matrix': 'http://localhost:5002',
            'random-user': 'http://localhost:5003',  # Will be started
            'image-generator': 'http://localhost:5004',  # Will be started
            'dnd-dm': 'http://localhost:5005'  # Will be started
        }
        self.results = {}

    async def test_decision_matrix_server(self):
        """Test the decision matrix server"""
        print("🧠 Testing Decision Matrix Server")
        print("=" * 50)

        try:
            async with aiohttp.ClientSession() as session:
                # Test health endpoint
                async with session.get(f"{self.servers['decision-matrix']}/api/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        print(f"✅ Server is healthy")
                        print(f"   📅 Timestamp: {health_data['timestamp']}")
                        print(f"   🤖 Nano Banana: {'✅ Available' if health_data['nano_banana_available'] else '❌ Not available'}")

                        # Test persona generation
                        test_data = {
                            "numImages": 3,
                            "imageQuality": "balanced",
                            "personaType": "random"
                        }

                        async with session.post(f"{self.servers['decision-matrix']}/api/generate-persona", json=test_data) as response:
                            if response.status == 200:
                                print("✅ Persona generation started successfully")

                                # Poll for completion
                                for i in range(10):
                                    await asyncio.sleep(1)
                                    async with session.get(f"{self.servers['decision-matrix']}/api/generation-status") as status_response:
                                        status = await status_response.json()
                                        print(f"   Progress: {status['progress']}% - {status['current_task']}")

                                        if not status['is_generating'] and status['progress'] == 100:
                                            print("✅ Persona generation completed")
                                            break
                            else:
                                print(f"❌ Persona generation failed: {response.status}")

                        self.results['decision-matrix'] = True
                        return True
                    else:
                        print(f"❌ Health check failed: {response.status}")
                        self.results['decision-matrix'] = False
                        return False
        except Exception as e:
            print(f"❌ Decision Matrix test failed: {e}")
            self.results['decision-matrix'] = False
            return False

    async def test_random_user_server(self):
        """Test the random user MCP server"""
        print("\n👤 Testing Random User MCP Server")
        print("=" * 50)

        try:
            # Test random user generation
            async with aiohttp.ClientSession() as session:
                async with session.get(self.servers['random-user']) as response:
                    if response.status == 200:
                        print("✅ Random User API is accessible")
                        self.results['random-user'] = True
                        return True
                    else:
                        print(f"❌ Random User API failed: {response.status}")
                        self.results['random-user'] = False
                        return False
        except Exception as e:
            print(f"❌ Random User test failed: {e}")
            self.results['random-user'] = False
            return False

    async def test_image_generator_server(self):
        """Test the image generator MCP server"""
        print("\n🎨 Testing Image Generator MCP Server")
        print("=" * 50)

        try:
            # Test Nano Banana availability
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"{self.servers['image-generator']}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status == 200:
                            print("✅ Image Generator server is running")
                            self.results['image-generator'] = True
                            return True
                        else:
                            print(f"❌ Image Generator server failed: {response.status}")
                            self.results['image-generator'] = False
                            return False
                except asyncio.TimeoutError:
                    print("⚠️  Image Generator server not responding (Nano Banana may not be running)")
                    self.results['image-generator'] = False
                    return False
        except Exception as e:
            print(f"❌ Image Generator test failed: {e}")
            self.results['image-generator'] = False
            return False

    async def test_dnd_dm_server(self):
        """Test the D&D DM MCP server"""
        print("\n🎲 Testing D&D DM MCP Server")
        print("=" * 50)

        try:
            # Test campaign creation
            async with aiohttp.ClientSession() as session:
                campaign_data = {
                    "name": "Test Campaign",
                    "setting": "Forgotten Realms",
                    "level_range": "1-10",
                    "tone": "serious"
                }

                async with session.post(f"{self.servers['dnd-dm']}/api/create-campaign", json=campaign_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("✅ Campaign creation successful")
                        print(f"   Campaign ID: {result['campaign_id']}")
                        print(f"   Campaign Name: {result['campaign']['name']}")

                        # Test NPC generation
                        npc_data = {
                            "npc_type": "merchant",
                            "generate_portrait": False
                        }

                        async with session.post(f"{self.servers['dnd-dm']}/api/generate-npc", json=npc_data) as npc_response:
                            if npc_response.status == 200:
                                npc_result = await npc_response.json()
                                print("✅ NPC generation successful")
                                print(f"   NPC Name: {npc_result['npc']['name']}")
                                print(f"   NPC Type: {npc_result['npc']['type']}")

                                self.results['dnd-dm'] = True
                                return True
                            else:
                                print(f"❌ NPC generation failed: {npc_response.status}")
                                self.results['dnd-dm'] = False
                                return False
                    else:
                        print(f"❌ Campaign creation failed: {response.status}")
                        self.results['dnd-dm'] = False
                        return False
        except Exception as e:
            print(f"❌ D&D DM test failed: {e}")
            self.results['dnd-dm'] = False
            return False

    async def run_all_tests(self):
        """Run all MCP server tests"""
        print("🧪 COMPREHENSIVE MCP SERVER TEST SUITE")
        print("=" * 60)
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Test each server
        await self.test_decision_matrix_server()
        await self.test_random_user_server()
        await self.test_image_generator_server()
        await self.test_dnd_dm_server()

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for result in self.results.values() if result)
        total = len(self.results)

        for server, result in self.results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{server.replace('-', ' ').title()}: {status}")

        print(f"\nOverall: {passed}/{total} tests passed")

        if passed == total:
            print("\n🎉 All MCP servers are working correctly!")
            print("\n📋 Available MCP Servers:")
            print("1. Decision Matrix - For complex decision making")
            print("2. Random User - For generating realistic personas")
            print("3. Image Generator - For AI-generated images")
            print("4. D&D DM - Comprehensive Dungeon Master tools")
            print("\n🔧 To use these servers in Cursor:")
            print("1. Restart Cursor to load the new MCP configuration")
            print("2. The servers will be available in your MCP tool list")
            print("3. Use them to enhance your D&D campaigns and development")
            return 0
        else:
            print(f"\n⚠️ {total - passed} server(s) failed.")
            print("\n🔧 Troubleshooting:")
            if not self.results.get('decision-matrix'):
                print("- Check if decision matrix server is running on port 5002")
            if not self.results.get('random-user'):
                print("- Random User API may be down or blocked")
            if not self.results.get('image-generator'):
                print("- Start Nano Banana server for image generation")
            if not self.results.get('dnd-dm'):
                print("- D&D DM server may need to be started")
            return 1

async def main():
    """Main test function"""
    tester = MCPServerTester()
    return await tester.run_all_tests()

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
