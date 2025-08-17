import subprocess
import os

def call_sub_agent(agent_type: str, task: str) -> str:
    agent_configs = {
        'frontend': {
            'directory': 'agents/claude_cli/frontend',
            'description': 'Frontend Developer expert specializing in React, Vue, and modern web technologies'
        }
    }
    
    config = agent_configs.get(agent_type)
    if not config:
        return f'Unknown agent type: {agent_type}'
    
    current_dir = os.getcwd()
    target_dir = os.path.join(current_dir, config['directory'])
    
    system_prompt = f'You are a {agent_type} development expert. Do not route tasks to other agents. Focus only on {agent_type} development work.'
    cmd = ['claude', '--print', '--permission-mode', 'bypassPermissions', '--append-system-prompt', system_prompt, task]
    
    try:
        agent_name = f'{agent_type.capitalize()} Agent'
        print(f'\n[{agent_name}] Subprocess call initiated')
        print(f'[{agent_name}] Working Directory: {target_dir}')
        print(f'[{agent_name}] Task: {task}')
        print(f'[{agent_name}] ' + '-' * 60)
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=600,
            cwd=target_dir,
            encoding='utf-8'
        )
        
        print(f'[{agent_name}] Subprocess completed')
        print(f'[{agent_name}] Exit Code: {result.returncode}')
        print(f'[{agent_name}] ' + '-' * 60)
        print(result.stdout)
        
        return result.stdout
    except subprocess.TimeoutExpired:
        return f'Agent {agent_type} timed out'
    except Exception as e:
        return f'Error calling {agent_type} agent: {str(e)}'

# Call Frontend Agent
task = "Create a simple user information display component in React. The component should display user name, email, and profile picture."
response = call_sub_agent('frontend', task)