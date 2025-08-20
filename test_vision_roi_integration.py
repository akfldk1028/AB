"""
Integration test for Vision Agent with ROI Processing
Demonstrates A2A communication for ROI analysis
"""

import asyncio
import sys
from pathlib import Path
import json
import numpy as np

# Add module path
sys.path.append(str(Path(__file__).parent / 'a2a-module'))

from agents.claude_cli.vision.agent import VisionCLIAgent
from agents.claude_cli.vision.roi_processor import (
    ROIProcessor, 
    ROICoordinates, 
    ROIAnalysisMode
)
from agents.claude_cli.vision.android_xr_utils import AndroidXRBridge


async def test_vision_agent_roi_integration():
    """Test Vision Agent with ROI processing integration"""
    
    print("=" * 70)
    print("Vision Agent + ROI Processing Integration Test")
    print("A2A Protocol Communication Demo")
    print("=" * 70)
    
    # Initialize components
    vision_agent = VisionCLIAgent()
    bridge = AndroidXRBridge()
    roi_processor = ROIProcessor(bridge=bridge)
    
    # Your specific ROI
    roi = ROICoordinates(x=100, y=200, width=300, height=400)
    
    print(f"\n1. Testing Vision Agent with ROI Analysis Request")
    print(f"   ROI: {roi.to_dict()}")
    
    # Create a query that includes ROI information
    roi_query = f"""
    Analyze the following ROI (Region of Interest) for XR interaction:
    - Coordinates: x={roi.x}, y={roi.y}, width={roi.width}, height={roi.height}
    - Task: Identify interactive elements and gestures
    - Mode: Object detection and scene understanding
    - Context: Android XR application with A2A protocol
    
    Please provide:
    1. Object classification for the ROI
    2. Interaction possibilities (tap, pinch, grab)
    3. Depth estimation if applicable
    4. Any text or UI elements present
    """
    
    print("\n2. Sending ROI Analysis Query to Vision Agent...")
    
    # Invoke Vision Agent
    try:
        response = await vision_agent.invoke_async(roi_query, "roi_test_session")
        
        print("\n3. Vision Agent Response:")
        print("-" * 50)
        if response.get('is_task_complete'):
            content = response.get('content', '')
            # Limit output for readability
            if len(content) > 500:
                print(content[:500] + "...")
            else:
                print(content)
        else:
            print(f"Task incomplete: {response.get('content')}")
        print("-" * 50)
        
    except Exception as e:
        print(f"Error invoking Vision Agent: {e}")
    
    # Simulate ROI processing pipeline
    print("\n4. Processing ROI through AI Analysis Pipeline:")
    
    # Create dummy image
    test_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
    
    # Process with multiple modes
    modes = [
        ROIAnalysisMode.OBJECT_DETECTION,
        ROIAnalysisMode.GESTURE_RECOGNITION,
        ROIAnalysisMode.SCENE_UNDERSTANDING
    ]
    
    results = []
    for mode in modes:
        result = await roi_processor.process_roi(test_image, roi, mode)
        results.append(result)
        print(f"   - {mode.value}: {result.labels[0] if result.labels else 'unknown'} ({result.confidence:.0%})")
    
    # Create A2A message combining Vision Agent and ROI processing
    print("\n5. Creating A2A Protocol Message:")
    
    a2a_message = {
        "protocol": "A2A",
        "version": "1.0",
        "sender": "vision_agent",
        "receiver": "android_xr",
        "message_type": "roi_analysis_complete",
        "data": {
            "session_id": "roi_test_session",
            "roi": roi.to_dict(),
            "vision_agent": {
                "status": "completed" if response.get('is_task_complete') else "pending",
                "confidence": 0.95
            },
            "ai_analysis": [result.to_a2a_format() for result in results[:2]],  # Include first 2 results
            "recommendations": {
                "interaction_type": "tap",
                "priority": "high",
                "requires_depth": False
            }
        },
        "timestamp": asyncio.get_event_loop().time()
    }
    
    print(json.dumps(a2a_message, indent=2)[:800] + "...")
    
    # Send to Android XR bridge
    print("\n6. Sending to Android XR Bridge:")
    bridge.send_to_android('roi_analysis_complete', a2a_message)
    print(f"   - Messages in queue: {len(bridge.message_queue)}")
    
    # Simulate receiving response from Android
    print("\n7. Simulating Android XR Response:")
    
    android_response = json.dumps({
        "type": "roi_confirmation",
        "data": {
            "roi_id": "roi_100_200",
            "received": True,
            "action_taken": "highlight",
            "user_feedback": "positive"
        }
    })
    
    processed_response = bridge.process_android_message(android_response)
    if processed_response:
        print(f"   - Received confirmation: {processed_response.get('data', {}).get('action_taken')}")
    
    # Test streaming capability
    print("\n8. Testing Vision Agent Streaming:")
    stream_query = f"Stream analysis for ROI at position ({roi.x}, {roi.y})"
    
    async for chunk in vision_agent.stream(stream_query, "stream_session"):
        if chunk.get('content'):
            print(f"   - Stream chunk: {chunk['content'][:100]}...")
            break  # Just show first chunk
    
    print("\n" + "=" * 70)
    print("Integration Test Complete!")
    print("A2A Communication Successfully Demonstrated")
    print("=" * 70)


async def test_multi_agent_roi_collaboration():
    """Test multiple agents collaborating on ROI analysis"""
    
    print("\n" + "=" * 70)
    print("Multi-Agent ROI Collaboration Test")
    print("=" * 70)
    
    # Initialize components
    vision_agent = VisionCLIAgent()
    roi_processor = ROIProcessor()
    
    # Multiple ROIs for different agents to analyze
    rois = [
        ROICoordinates(x=100, y=200, width=300, height=400),  # Your original ROI
        ROICoordinates(x=500, y=100, width=200, height=300),  # Second ROI
        ROICoordinates(x=800, y=400, width=250, height=250)   # Third ROI
    ]
    
    print(f"\nProcessing {len(rois)} ROIs with specialized agents:")
    
    # Assign different analysis modes to different ROIs
    roi_assignments = [
        (rois[0], ROIAnalysisMode.GESTURE_RECOGNITION, "Gesture Agent"),
        (rois[1], ROIAnalysisMode.TEXT_RECOGNITION, "Text Agent"),
        (rois[2], ROIAnalysisMode.FACE_ANALYSIS, "Face Agent")
    ]
    
    # Create dummy image
    test_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
    
    # Process each ROI with its assigned agent
    collaboration_results = []
    
    for roi, mode, agent_name in roi_assignments:
        print(f"\n{agent_name} analyzing ROI at ({roi.x}, {roi.y}):")
        
        # Process ROI
        result = await roi_processor.process_roi(test_image, roi, mode)
        
        # Create agent-specific message
        agent_message = {
            "agent": agent_name,
            "roi": roi.to_dict(),
            "analysis": {
                "mode": mode.value,
                "confidence": result.confidence,
                "findings": result.labels[:2] if result.labels else []
            }
        }
        
        collaboration_results.append(agent_message)
        print(f"  - Found: {', '.join(result.labels[:2]) if result.labels else 'nothing'}")
        print(f"  - Confidence: {result.confidence:.0%}")
    
    # Aggregate results
    print("\nAggregated Multi-Agent Analysis:")
    print(json.dumps({
        "collaboration_id": "multi_agent_roi_001",
        "total_rois": len(rois),
        "agents_involved": [r["agent"] for r in collaboration_results],
        "results": collaboration_results
    }, indent=2)[:600] + "...")
    
    print("\nMulti-Agent Collaboration Complete!")


if __name__ == "__main__":
    print("Starting Vision Agent + ROI Integration Test...\n")
    
    # Run integration test
    asyncio.run(test_vision_agent_roi_integration())
    
    # Run multi-agent collaboration test
    asyncio.run(test_multi_agent_roi_collaboration())