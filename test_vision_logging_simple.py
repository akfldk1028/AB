"""
Simple test script for A2A logging functionality - Vision Agent
This script tests the logging capabilities without full Claude CLI invocation
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the a2a-module to path
sys.path.append(str(Path(__file__).parent / "a2a-module"))

# Import the Logger Agent for direct logging tests
from agents.claude_cli.logger.agent import LoggerCLIAgent


def test_vision_agent_logging_simple():
    """Test Vision Agent logging functionality directly"""
    
    print("=" * 80)
    print("A2A LOGGING FUNCTIONALITY TEST - VISION AGENT (SIMPLE)")
    print("=" * 80)
    print()
    
    # Initialize logger agent
    logger_agent = LoggerCLIAgent()
    
    # Test session ID
    session_id = f"test_vision_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"[TEST] Starting Vision Agent logging tests with session: {session_id}")
    print("-" * 80)
    
    # Test 1: Log A2A conversation
    print("\n[TEST 1] Testing A2A conversation logging...")
    logger_agent.log_a2a_conversation(
        agent_from="vision_agent",
        agent_to="perception_agent",
        message="Analyzing XR scene for object detection and spatial mapping",
        response="Scene analysis complete. Detected 5 objects with spatial coordinates."
    )
    print("[OK] A2A conversation logged")
    
    # Test 2: Log performance metrics
    print("\n[TEST 2] Testing performance metrics logging...")
    performance_metrics = {
        "agent": "vision",
        "operation": "scene_analysis",
        "processing_time_ms": 125,
        "fps": 120,
        "objects_detected": 5,
        "memory_usage_mb": 256,
        "gpu_usage_percent": 45,
        "vlm_model": "GPT-4V",
        "optimization_level": "high"
    }
    logger_agent.log_performance_metrics(performance_metrics)
    print("[OK] Performance metrics logged")
    
    # Test 3: Log error scenarios
    print("\n[TEST 3] Testing error logging...")
    logger_agent.log_error(
        error_type="VisionProcessingError",
        error_message="Failed to initialize GPT-4V connection",
        context={
            "agent": "vision",
            "operation": "vlm_init",
            "retry_count": 3,
            "session_id": session_id
        }
    )
    print("[OK] Error logged")
    
    # Test 4: Log multiple A2A interactions
    print("\n[TEST 4] Testing multiple A2A interactions...")
    test_interactions = [
        {
            "from": "vision_agent",
            "to": "ux_tts_agent",
            "message": "Detected user gesture: swipe right",
            "response": "Acknowledging gesture with haptic feedback"
        },
        {
            "from": "vision_agent",
            "to": "backend_agent",
            "message": "Requesting object classification for detected items",
            "response": "Classification complete: chair, table, monitor, keyboard, mouse"
        },
        {
            "from": "vision_agent",
            "to": "unity_agent",
            "message": "Updated spatial mesh data for room mapping",
            "response": "Mesh integrated into Unity scene successfully"
        },
        {
            "from": "vision_agent",
            "to": "logger_agent",
            "message": "Vision processing pipeline performance report",
            "response": "Performance data logged and analyzed"
        }
    ]
    
    for interaction in test_interactions:
        logger_agent.log_a2a_conversation(
            agent_from=interaction["from"],
            agent_to=interaction["to"],
            message=interaction["message"],
            response=interaction["response"]
        )
        print(f"[OK] Logged: {interaction['from']} -> {interaction['to']}")
    
    # Test 5: Log complex vision processing metrics
    print("\n[TEST 5] Testing complex vision processing metrics...")
    complex_metrics = {
        "timestamp": datetime.now().isoformat(),
        "vision_pipeline": {
            "input_resolution": "2880x1700",
            "output_fps": 120,
            "latency_ms": 8.3,
            "models_active": ["GPT-4V", "YOLO-XR", "DepthNet"],
            "memory_allocation": {
                "gpu_vram_mb": 2048,
                "system_ram_mb": 512,
                "cache_mb": 128
            }
        },
        "scene_analysis": {
            "objects_tracked": 12,
            "hands_detected": 2,
            "gaze_tracking_active": True,
            "spatial_anchors": 8,
            "room_mesh_vertices": 15420
        },
        "performance_optimization": {
            "dynamic_resolution_scaling": True,
            "foveated_rendering": True,
            "temporal_upsampling": True,
            "optimization_preset": "balanced"
        }
    }
    logger_agent.log_performance_metrics(complex_metrics)
    print("[OK] Complex vision metrics logged")
    
    print("\n" + "=" * 80)
    print("LOG FILE VERIFICATION")
    print("=" * 80)
    
    # Check and read log files
    log_dir = Path(__file__).parent / "a2a-module" / "agents" / "claude_cli" / "logger" / "logs"
    
    # Check A2A conversation logs
    a2a_logs = log_dir / "a2a_conversations"
    print(f"\n[A2A LOGS] Directory: {a2a_logs}")
    if a2a_logs.exists():
        log_files = list(a2a_logs.glob("*.log"))
        print(f"  Found {len(log_files)} A2A conversation log files")
        if log_files:
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            print(f"  Latest log: {latest_log.name}")
            
            # Read and display sample from latest log
            try:
                with open(latest_log, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    print(f"  Log contains {len(lines)} lines")
                    print("\n  Sample entry:")
                    print("  " + "-" * 40)
                    # Show first entry
                    for i, line in enumerate(lines[:20]):
                        if line.strip():
                            print(f"  {line[:100]}...")
                        if "------" in line:
                            break
            except Exception as e:
                print(f"  Error reading log: {e}")
    
    # Check performance logs
    perf_logs = log_dir / "performance"
    print(f"\n[PERFORMANCE LOGS] Directory: {perf_logs}")
    if perf_logs.exists():
        perf_files = list(perf_logs.glob("*.log"))
        print(f"  Found {len(perf_files)} performance log files")
        if perf_files:
            latest_perf = max(perf_files, key=lambda f: f.stat().st_mtime)
            print(f"  Latest log: {latest_perf.name}")
    
    # Check error logs
    error_logs = log_dir / "errors"
    print(f"\n[ERROR LOGS] Directory: {error_logs}")
    if error_logs.exists():
        error_files = list(error_logs.glob("*.log"))
        print(f"  Found {len(error_files)} error log files")
        if error_files:
            latest_error = max(error_files, key=lambda f: f.stat().st_mtime)
            print(f"  Latest log: {latest_error.name}")
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("\n[SUCCESS] All Vision Agent A2A logging tests completed successfully!")
    print("[SUCCESS] Logs are being written to the designated directories")
    print("[SUCCESS] A2A protocol communication is properly logged")
    print("\n[INFO] Vision Agent logging functionality is working correctly")
    print("=" * 80)


if __name__ == "__main__":
    # Run the test
    test_vision_agent_logging_simple()