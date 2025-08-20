"""
Test script for A2A logging functionality - Vision Agent
This script tests the logging capabilities of the Vision Agent in the A2A protocol
"""
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the a2a-module to path
sys.path.append(str(Path(__file__).parent / "a2a-module"))

# Import the Vision Agent and Logger Agent
from agents.claude_cli.vision.agent import VisionCLIAgent
from agents.claude_cli.logger.agent import LoggerCLIAgent


async def test_vision_agent_logging():
    """Test Vision Agent with A2A logging functionality"""
    
    print("=" * 80)
    print("A2A LOGGING FUNCTIONALITY TEST - VISION AGENT")
    print("=" * 80)
    print()
    
    # Initialize agents
    vision_agent = VisionCLIAgent()
    logger_agent = LoggerCLIAgent()
    
    # Test session ID
    session_id = f"test_vision_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Test cases for Vision Agent
    test_queries = [
        {
            "query": "Initialize GPT-4V integration for Android XR real-time object detection",
            "description": "Test VLM initialization and setup"
        },
        {
            "query": "Analyze XR scene for spatial understanding and object recognition",
            "description": "Test scene analysis capabilities"
        },
        {
            "query": "Optimize vision processing pipeline for 120 FPS XR performance",
            "description": "Test performance optimization features"
        },
        {
            "query": "Implement multimodal understanding for hand gestures and voice commands",
            "description": "Test multimodal integration"
        }
    ]
    
    print(f"[TEST] Starting Vision Agent tests with session: {session_id}")
    print("-" * 80)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n[TEST {i}] {test_case['description']}")
        print(f"Query: {test_case['query'][:100]}...")
        
        try:
            # Test Vision Agent
            print("\n[VISION AGENT] Processing query...")
            vision_response = await vision_agent.invoke_async(
                test_case['query'],
                session_id
            )
            
            # Log the interaction using Logger Agent
            log_message = f"""
            A2A Communication Log:
            From: Test Script
            To: Vision Agent
            Query: {test_case['query']}
            Response Status: {vision_response.get('is_task_complete')}
            Response Preview: {str(vision_response.get('content', ''))[:200]}
            """
            
            print("\n[LOGGER AGENT] Logging A2A communication...")
            logger_response = await logger_agent.invoke_async(
                log_message,
                f"logger_{session_id}"
            )
            
            # Manually log to demonstrate A2A conversation logging
            logger_agent.log_a2a_conversation(
                agent_from="test_script",
                agent_to="vision_agent",
                message=test_case['query'],
                response=str(vision_response.get('content', ''))[:500]
            )
            
            # Log performance metrics
            performance_metrics = {
                "test_case": i,
                "agent": "vision",
                "query_length": len(test_case['query']),
                "response_length": len(str(vision_response.get('content', ''))),
                "is_complete": vision_response.get('is_task_complete'),
                "requires_input": vision_response.get('require_user_input'),
                "test_description": test_case['description']
            }
            logger_agent.log_performance_metrics(performance_metrics)
            
            # Display results
            print(f"\n[RESULT] Test {i} - {test_case['description']}")
            print(f"  Task Complete: {vision_response.get('is_task_complete')}")
            print(f"  Requires Input: {vision_response.get('require_user_input')}")
            print(f"  Response Length: {len(str(vision_response.get('content', '')))} chars")
            
            if not vision_response.get('is_task_complete'):
                # Log error if task wasn't completed
                logger_agent.log_error(
                    error_type="TaskIncomplete",
                    error_message=f"Test {i} did not complete successfully",
                    context={
                        "test_case": i,
                        "query": test_case['query'],
                        "response": vision_response
                    }
                )
            
        except Exception as e:
            print(f"\n[ERROR] Test {i} failed: {str(e)}")
            
            # Log the error
            logger_agent.log_error(
                error_type="TestFailure",
                error_message=str(e),
                context={
                    "test_case": i,
                    "query": test_case['query'],
                    "session_id": session_id
                }
            )
        
        print("-" * 80)
    
    # Test streaming functionality
    print("\n[TEST] Testing Vision Agent streaming capability...")
    try:
        stream_query = "Stream real-time vision analysis for XR environment"
        print(f"Stream Query: {stream_query}")
        
        async for stream_response in vision_agent.stream(stream_query, session_id):
            print(f"[STREAM] Response chunk received")
            print(f"  Content preview: {str(stream_response.get('content', ''))[:100]}...")
            
            # Log streaming event
            logger_agent.log_a2a_conversation(
                agent_from="test_script",
                agent_to="vision_agent",
                message=f"STREAM: {stream_query}",
                response=f"CHUNK: {str(stream_response.get('content', ''))[:200]}"
            )
    except Exception as e:
        print(f"[ERROR] Streaming test failed: {str(e)}")
        logger_agent.log_error(
            error_type="StreamingFailure",
            error_message=str(e),
            context={"session_id": session_id}
        )
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    # Check log files
    log_dir = Path(__file__).parent / "a2a-module" / "agents" / "claude_cli" / "logger" / "logs"
    a2a_logs = log_dir / "a2a_conversations"
    perf_logs = log_dir / "performance"
    error_logs = log_dir / "errors"
    
    print(f"\n[LOGS] A2A Conversation logs directory: {a2a_logs}")
    if a2a_logs.exists():
        log_files = list(a2a_logs.glob("*.log"))
        print(f"  Found {len(log_files)} A2A conversation log files")
        if log_files:
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            print(f"  Latest log: {latest_log.name}")
    
    print(f"\n[LOGS] Performance logs directory: {perf_logs}")
    if perf_logs.exists():
        perf_files = list(perf_logs.glob("*.log"))
        print(f"  Found {len(perf_files)} performance log files")
    
    print(f"\n[LOGS] Error logs directory: {error_logs}")
    if error_logs.exists():
        error_files = list(error_logs.glob("*.log"))
        print(f"  Found {len(error_files)} error log files")
    
    print("\n[TEST] Vision Agent A2A logging test completed!")
    print("=" * 80)


if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_vision_agent_logging())