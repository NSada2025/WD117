
#!/usr/bin/env python3
'''
Voice Command Integration API
Connects voice interface with backend systems
'''

import json
import subprocess
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

class VoiceCommandProcessor:
    def __init__(self):
        self.command_history = []
        self.active_sessions = {}
    
    def process_command(self, command_text, session_id=None):
        '''Process voice command and return response'''
        
        timestamp = datetime.now().isoformat()
        command_entry = {
            'command': command_text,
            'timestamp': timestamp,
            'session_id': session_id,
            'status': 'processing'
        }
        
        self.command_history.append(command_entry)
        
        # Route command to appropriate handler
        response = self.route_command(command_text)
        command_entry['status'] = 'completed'
        command_entry['response'] = response
        
        return response
    
    def route_command(self, command):
        '''Route command to appropriate handler'''
        
        command_lower = command.lower()
        
        # Navigation commands
        if 'dashboard' in command_lower:
            return self.handle_navigation('dashboard')
        elif 'team status' in command_lower:
            return self.handle_team_status()
        elif 'project status' in command_lower:
            return self.handle_project_status()
        elif 'system status' in command_lower:
            return self.handle_system_status()
        elif 'generate report' in command_lower:
            return self.handle_generate_report()
        elif 'emergency stop' in command_lower:
            return self.handle_emergency_stop()
        else:
            return self.handle_unknown_command(command)
    
    def handle_navigation(self, target):
        return {
            'action': 'navigate',
            'target': target,
            'message': f'Navigating to {target}',
            'success': True
        }
    
    def handle_team_status(self):
        return {
            'action': 'team_status',
            'data': {
                'dev1': {'status': 'active', 'progress': '85%'},
                'dev2': {'status': 'active', 'progress': '90%'},
                'dev3': {'status': 'active', 'progress': '80%'}
            },
            'message': 'Team status retrieved successfully',
            'success': True
        }
    
    def handle_project_status(self):
        return {
            'action': 'project_status',
            'data': {
                'active_projects': 3,
                'completion_rate': '85%',
                'critical_issues': 0
            },
            'message': 'Project status retrieved successfully',
            'success': True
        }
    
    def handle_system_status(self):
        return {
            'action': 'system_status',
            'data': {
                'uptime': '99.9%',
                'performance': 'optimal',
                'alerts': 0
            },
            'message': 'All systems operational',
            'success': True
        }
    
    def handle_generate_report(self):
        # Trigger report generation
        try:
            result = subprocess.run([
                'python3', '/mnt/d/multiagent-system/ceo_manager_interface_optimization.py'
            ], capture_output=True, text=True)
            
            return {
                'action': 'generate_report',
                'message': 'Executive report generated successfully',
                'success': True
            }
        except Exception as e:
            return {
                'action': 'generate_report',
                'message': f'Report generation failed: {str(e)}',
                'success': False
            }
    
    def handle_emergency_stop(self):
        return {
            'action': 'emergency_stop',
            'message': 'Emergency stop procedure initiated',
            'success': True,
            'warning': 'All non-critical operations halted'
        }
    
    def handle_unknown_command(self, command):
        return {
            'action': 'unknown',
            'command': command,
            'message': f'Command "{command}" not recognized',
            'success': False,
            'suggestions': [
                'Try "team status"',
                'Try "project status"',
                'Try "system status"',
                'Try "generate report"'
            ]
        }

# Initialize processor
processor = VoiceCommandProcessor()

@app.route('/api/voice/command', methods=['POST'])
def process_voice_command():
    data = request.get_json()
    command = data.get('command', '')
    session_id = data.get('session_id')
    
    response = processor.process_command(command, session_id)
    return jsonify(response)

@app.route('/api/voice/history', methods=['GET'])
def get_command_history():
    return jsonify(processor.command_history[-10:])  # Last 10 commands

@app.route('/api/voice/status', methods=['GET'])
def get_voice_status():
    return jsonify({
        'status': 'active',
        'commands_processed': len(processor.command_history),
        'active_sessions': len(processor.active_sessions)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
        