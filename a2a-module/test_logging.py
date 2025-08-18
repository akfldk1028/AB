#!/usr/bin/env python3
"""
Test A2A Logging Functionality
"""
import json
import datetime
import os
from pathlib import Path

def log_a2a_communication_test(agent_port: int, message_data: dict, response_data: dict = None) -> None:
    """Test the A2A logging function"""
    try:
        # Determine agent type by port
        agent_map = {
            8030: "perception",
            8031: "vision", 
            8032: "ux_tts",
            8033: "logger",
            8010: "frontend",
            8021: "backend", 
            8012: "unity"
        }
        
        agent_name = agent_map.get(agent_port, f"unknown_port_{agent_port}")
        
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent / "logs" / "a2a_communications"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.datetime.now()
        log_filename = f"a2a_all_agents_{timestamp.strftime('%Y%m%d')}.log"
        log_file = logs_dir / log_filename
        
        # Extract message content
        message_text = ""
        if message_data and 'params' in message_data:
            message_content = message_data['params'].get('message', {})
            parts = message_content.get('parts', [])
            if parts and len(parts) > 0:
                message_text = parts[0].get('text', '')
        
        # Create log entry
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "datetime": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "agent_name": agent_name,
            "agent_port": agent_port,
            "message_type": "A2A_Communication",
            "request_id": message_data.get('id', 'unknown'),
            "method": message_data.get('method', 'unknown'),
            "message_preview": message_text[:200] + "..." if len(message_text) > 200 else message_text,
            "message_length": len(message_text),
            "has_response": response_data is not None,
            "raw_message": message_data,
            "response": response_data
        }
        
        # Write to log file
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, indent=2, ensure_ascii=False) + "\n")
            f.write("-" * 100 + "\n")
            
        print(f"[A2A Logging] Communication logged for {agent_name}:{agent_port}")
        print(f"[A2A Logging] Log file: {log_file}")
        
    except Exception as e:
        print(f"[A2A Logging] Failed to log communication: {str(e)}")

if __name__ == "__main__":
    # 테스트 메시지 데이터
    test_message = {
        'jsonrpc': '2.0',
        'id': 'test_123',
        'method': 'message/send',
        'params': {
            'message': {
                'role': 'user',
                'parts': [{'kind': 'text', 'text': 'Test A2A logging functionality - this is a test message to verify that all agent communications are being properly logged to the central log file.'}],
                'messageId': 'test_msg_001',
                'kind': 'message'
            }
        }
    }

    print('=' * 80)
    print('Testing A2A Logging Functionality')
    print('=' * 80)
    
    # Test different agents
    for port, agent_name in [(8030, "perception"), (8031, "vision"), (8032, "ux_tts"), (8033, "logger")]:
        print(f"\n🔄 Testing logging for {agent_name} (port {port})...")
        log_a2a_communication_test(port, test_message)
    
    print('\n✅ A2A logging test completed!')
    print('📁 Check logs/a2a_communications/ folder for generated log files')