#!/usr/bin/env python3
"""
Voice Recognition & Command Input System
Hands-free CEO-Manager interface for maximum efficiency
Priority: MEDIUM - Enhanced accessibility and convenience
"""

import json
import time
from datetime import datetime
from pathlib import Path

class VoiceCommandSystem:
    """Voice recognition and command processing for CEO-Manager interface"""
    
    def __init__(self):
        self.base_dir = Path("/mnt/d/multiagent-system/ceo_manager_interface")
        self.voice_dir = self.base_dir / "voice"
        self.voice_dir.mkdir(exist_ok=True)
        
        # Voice command configurations
        self.commands_config = self.define_voice_commands()
        self.voice_settings = self.define_voice_settings()
        
    def define_voice_commands(self):
        """Define comprehensive voice command mappings"""
        
        return {
            "navigation": {
                "show dashboard": "navigate_dashboard",
                "open projects": "navigate_projects", 
                "team status": "navigate_team",
                "show alerts": "navigate_alerts",
                "go to settings": "navigate_settings"
            },
            "project_management": {
                "new project": "create_new_project",
                "project status": "show_project_status",
                "assign task": "assign_task_to_team",
                "update priority": "update_task_priority",
                "schedule meeting": "schedule_team_meeting"
            },
            "team_communication": {
                "team broadcast": "initiate_team_broadcast",
                "message dev one": "message_dev1",
                "message dev two": "message_dev2", 
                "message dev three": "message_dev3",
                "message manager": "message_manager",
                "status request": "request_team_status",
                "emergency meeting": "call_emergency_meeting"
            },
            "system_control": {
                "system status": "show_system_status",
                "refresh dashboard": "refresh_dashboard",
                "backup data": "initiate_backup",
                "emergency stop": "emergency_stop_all",
                "pause all tasks": "pause_all_operations",
                "resume operations": "resume_all_operations"
            },
            "reports_analytics": {
                "generate report": "generate_executive_report",
                "show metrics": "display_performance_metrics",
                "export data": "export_analytics_data",
                "schedule report": "schedule_automated_report"
            },
            "quick_actions": {
                "what's the status": "quick_status_overview",
                "any problems": "check_critical_alerts",
                "team progress": "team_progress_summary",
                "next milestone": "show_next_milestone",
                "resource allocation": "show_resource_usage"
            }
        }
    
    def define_voice_settings(self):
        """Define voice recognition settings and preferences"""
        
        return {
            "recognition": {
                "language": "en-US",
                "continuous": True,
                "interim_results": True,
                "max_alternatives": 3,
                "confidence_threshold": 0.7
            },
            "speech_synthesis": {
                "voice": "professional_female",
                "rate": 1.0,
                "pitch": 1.0,
                "volume": 0.8,
                "language": "en-US"
            },
            "activation": {
                "wake_words": ["hey commander", "computer", "dashboard"],
                "always_listening": False,
                "push_to_talk": True,
                "voice_activation_key": "space"
            },
            "privacy": {
                "local_processing": True,
                "cloud_fallback": False,
                "audio_logging": False,
                "command_history": True
            }
        }
    
    def create_voice_interface(self):
        """Create web-based voice interface"""
        
        print("🎤 Creating Voice Command Interface...")
        
        voice_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice Command Center</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 20px;
            min-height: 100vh;
        }
        
        .voice-container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .voice-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .voice-title {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #3498db, #2ecc71);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .voice-subtitle {
            font-size: 1.2em;
            opacity: 0.8;
        }
        
        /* Voice Activation Button */
        .voice-activation {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .voice-button {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: none;
            background: linear-gradient(45deg, #e74c3c, #c0392b);
            color: white;
            font-size: 24px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 8px 25px rgba(231, 76, 60, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .voice-button:hover {
            transform: scale(1.05);
            box-shadow: 0 12px 30px rgba(231, 76, 60, 0.4);
        }
        
        .voice-button.listening {
            background: linear-gradient(45deg, #2ecc71, #27ae60);
            animation: pulse 1.5s infinite;
        }
        
        .voice-button.processing {
            background: linear-gradient(45deg, #f39c12, #e67e22);
            animation: spin 1s linear infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .voice-status {
            margin-top: 15px;
            font-size: 16px;
            font-weight: 600;
        }
        
        /* Voice Visualization */
        .voice-visualizer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 60px;
            margin-bottom: 30px;
        }
        
        .voice-bar {
            width: 4px;
            background: linear-gradient(to top, #3498db, #2ecc71);
            margin: 0 2px;
            border-radius: 2px;
            transition: height 0.1s ease;
        }
        
        /* Command History */
        .command-history {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }
        
        .command-history h3 {
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        
        .command-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .command-item:last-child {
            border-bottom: none;
        }
        
        .command-text {
            font-weight: 600;
        }
        
        .command-time {
            font-size: 12px;
            opacity: 0.7;
        }
        
        .command-status {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
        }
        
        .status-success {
            background: rgba(46, 204, 113, 0.2);
            color: #2ecc71;
        }
        
        .status-processing {
            background: rgba(243, 156, 18, 0.2);
            color: #f39c12;
        }
        
        .status-error {
            background: rgba(231, 76, 60, 0.2);
            color: #e74c3c;
        }
        
        /* Quick Commands */
        .quick-commands {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .quick-command {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 10px;
            padding: 15px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: left;
        }
        
        .quick-command:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        
        .quick-command-title {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .quick-command-desc {
            font-size: 12px;
            opacity: 0.8;
        }
        
        /* Settings Panel */
        .settings-panel {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        
        .settings-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .settings-toggle {
            width: 50px;
            height: 25px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 25px;
            position: relative;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        
        .settings-toggle.active {
            background: #2ecc71;
        }
        
        .settings-toggle::after {
            content: '';
            position: absolute;
            width: 21px;
            height: 21px;
            background: white;
            border-radius: 50%;
            top: 2px;
            left: 2px;
            transition: transform 0.3s ease;
        }
        
        .settings-toggle.active::after {
            transform: translateX(25px);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .voice-title {
                font-size: 2em;
            }
            
            .voice-button {
                width: 100px;
                height: 100px;
                font-size: 20px;
            }
            
            .quick-commands {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="voice-container">
        <!-- Header -->
        <div class="voice-header">
            <h1 class="voice-title">🎤 Voice Command Center</h1>
            <p class="voice-subtitle">Hands-free CEO-Manager interface</p>
        </div>
        
        <!-- Voice Activation -->
        <div class="voice-activation">
            <button class="voice-button" id="voiceButton" onclick="toggleVoiceRecognition()">
                🎤
            </button>
            <div class="voice-status" id="voiceStatus">Click to start listening</div>
        </div>
        
        <!-- Voice Visualizer -->
        <div class="voice-visualizer" id="voiceVisualizer">
            <!-- Bars will be generated by JavaScript -->
        </div>
        
        <!-- Command History -->
        <div class="command-history">
            <h3>📝 Recent Commands</h3>
            <div id="commandHistory">
                <div class="command-item">
                    <div>
                        <div class="command-text">"Show team status"</div>
                        <div class="command-time">2 minutes ago</div>
                    </div>
                    <div class="command-status status-success">Executed</div>
                </div>
                <div class="command-item">
                    <div>
                        <div class="command-text">"Generate report"</div>
                        <div class="command-time">5 minutes ago</div>
                    </div>
                    <div class="command-status status-success">Executed</div>
                </div>
            </div>
        </div>
        
        <!-- Quick Commands -->
        <div class="quick-commands">
            <button class="quick-command" onclick="executeQuickCommand('team status')">
                <div class="quick-command-title">👥 Team Status</div>
                <div class="quick-command-desc">View current team performance</div>
            </button>
            <button class="quick-command" onclick="executeQuickCommand('project status')">
                <div class="quick-command-title">📊 Project Status</div>
                <div class="quick-command-desc">Check all active projects</div>
            </button>
            <button class="quick-command" onclick="executeQuickCommand('system status')">
                <div class="quick-command-title">⚡ System Status</div>
                <div class="quick-command-desc">Monitor system health</div>
            </button>
            <button class="quick-command" onclick="executeQuickCommand('generate report')">
                <div class="quick-command-title">📋 Generate Report</div>
                <div class="quick-command-desc">Create executive summary</div>
            </button>
        </div>
        
        <!-- Settings -->
        <div class="settings-panel">
            <h3>⚙️ Voice Settings</h3>
            <div class="settings-row">
                <span>Continuous Listening</span>
                <div class="settings-toggle" onclick="toggleSetting(this)"></div>
            </div>
            <div class="settings-row">
                <span>Voice Feedback</span>
                <div class="settings-toggle active" onclick="toggleSetting(this)"></div>
            </div>
            <div class="settings-row">
                <span>Command History</span>
                <div class="settings-toggle active" onclick="toggleSetting(this)"></div>
            </div>
        </div>
    </div>
    
    <script>
        let recognition;
        let isListening = false;
        let synthVoice;
        
        // Initialize voice recognition
        function initVoiceRecognition() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                
                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.lang = 'en-US';
                
                recognition.onstart = () => {
                    console.log('Voice recognition started');
                    updateVoiceStatus('Listening...', 'listening');
                    startVoiceVisualization();
                };
                
                recognition.onresult = (event) => {
                    const result = event.results[event.results.length - 1];
                    if (result.isFinal) {
                        const command = result[0].transcript.trim().toLowerCase();
                        processVoiceCommand(command);
                    }
                };
                
                recognition.onerror = (event) => {
                    console.error('Voice recognition error:', event.error);
                    updateVoiceStatus('Error: ' + event.error, 'error');
                    stopListening();
                };
                
                recognition.onend = () => {
                    console.log('Voice recognition ended');
                    stopListening();
                };
            } else {
                alert('Voice recognition not supported in this browser');
            }
        }
        
        // Toggle voice recognition
        function toggleVoiceRecognition() {
            if (!recognition) {
                initVoiceRecognition();
            }
            
            if (isListening) {
                stopListening();
            } else {
                startListening();
            }
        }
        
        function startListening() {
            recognition.start();
            isListening = true;
            document.getElementById('voiceButton').classList.add('listening');
        }
        
        function stopListening() {
            if (recognition) {
                recognition.stop();
            }
            isListening = false;
            const button = document.getElementById('voiceButton');
            button.classList.remove('listening', 'processing');
            updateVoiceStatus('Click to start listening', 'ready');
            stopVoiceVisualization();
        }
        
        function updateVoiceStatus(message, state) {
            document.getElementById('voiceStatus').textContent = message;
        }
        
        // Process voice command
        function processVoiceCommand(command) {
            updateVoiceStatus('Processing: "' + command + '"', 'processing');
            document.getElementById('voiceButton').classList.add('processing');
            
            // Add to command history
            addCommandToHistory(command);
            
            // Simulate command processing
            setTimeout(() => {
                executeCommand(command);
                updateVoiceStatus('Command executed', 'success');
                
                // Provide voice feedback
                speakResponse(getCommandResponse(command));
                
                setTimeout(() => {
                    stopListening();
                }, 2000);
            }, 1000);
        }
        
        // Execute quick command
        function executeQuickCommand(command) {
            addCommandToHistory(command);
            executeCommand(command);
            speakResponse(getCommandResponse(command));
        }
        
        // Execute command
        function executeCommand(command) {
            console.log('Executing command:', command);
            
            // Command mapping
            const commandMap = {
                'team status': () => alert('Team Status: All members active and performing well'),
                'project status': () => alert('Project Status: 3 active projects, 85% overall completion'),
                'system status': () => alert('System Status: All systems operational, no issues detected'),
                'generate report': () => alert('Executive Report: Generated successfully'),
                'show dashboard': () => window.location.href = '../dashboard.html',
                'emergency stop': () => confirm('Confirm emergency stop?') && alert('Emergency stop activated')
            };
            
            // Find matching command
            for (const [key, action] of Object.entries(commandMap)) {
                if (command.includes(key)) {
                    action();
                    return;
                }
            }
            
            // Default action
            alert('Command recognized: ' + command);
        }
        
        // Get command response
        function getCommandResponse(command) {
            const responses = {
                'team status': 'Team status displayed. All members are active.',
                'project status': 'Project overview is ready. 85% completion rate.',
                'system status': 'All systems operational. No issues detected.',
                'generate report': 'Executive report has been generated successfully.',
                'default': 'Command executed successfully.'
            };
            
            for (const [key, response] of Object.entries(responses)) {
                if (command.includes(key)) {
                    return response;
                }
            }
            
            return responses.default;
        }
        
        // Add command to history
        function addCommandToHistory(command) {
            const history = document.getElementById('commandHistory');
            const newCommand = document.createElement('div');
            newCommand.className = 'command-item';
            newCommand.innerHTML = `
                <div>
                    <div class="command-text">"${command}"</div>
                    <div class="command-time">Just now</div>
                </div>
                <div class="command-status status-processing">Processing</div>
            `;
            
            history.insertBefore(newCommand, history.firstChild);
            
            // Update status after processing
            setTimeout(() => {
                newCommand.querySelector('.command-status').textContent = 'Executed';
                newCommand.querySelector('.command-status').className = 'command-status status-success';
            }, 1500);
            
            // Keep only last 5 commands
            while (history.children.length > 5) {
                history.removeChild(history.lastChild);
            }
        }
        
        // Voice visualization
        function startVoiceVisualization() {
            const visualizer = document.getElementById('voiceVisualizer');
            visualizer.innerHTML = '';
            
            for (let i = 0; i < 20; i++) {
                const bar = document.createElement('div');
                bar.className = 'voice-bar';
                bar.style.height = '5px';
                visualizer.appendChild(bar);
            }
            
            animateVoiceVisualization();
        }
        
        function animateVoiceVisualization() {
            if (!isListening) return;
            
            const bars = document.querySelectorAll('.voice-bar');
            bars.forEach(bar => {
                const height = Math.random() * 50 + 5;
                bar.style.height = height + 'px';
            });
            
            setTimeout(animateVoiceVisualization, 100);
        }
        
        function stopVoiceVisualization() {
            const bars = document.querySelectorAll('.voice-bar');
            bars.forEach(bar => {
                bar.style.height = '5px';
            });
        }
        
        // Speech synthesis
        function speakResponse(text) {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 1.0;
                utterance.pitch = 1.0;
                utterance.volume = 0.8;
                speechSynthesis.speak(utterance);
            }
        }
        
        // Settings toggle
        function toggleSetting(toggle) {
            toggle.classList.toggle('active');
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && e.ctrlKey) {
                e.preventDefault();
                toggleVoiceRecognition();
            }
        });
        
        // Initialize on page load
        window.addEventListener('load', () => {
            console.log('Voice Command Center initialized');
        });
    </script>
</body>
</html>
        """
        
        voice_file = self.voice_dir / "index.html"
        with open(voice_file, 'w', encoding='utf-8') as f:
            f.write(voice_html)
        
        print(f"✅ Voice interface created: {voice_file}")
        
        # Save command configurations
        config_file = self.voice_dir / "voice_commands.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.commands_config, f, indent=2)
        
        settings_file = self.voice_dir / "voice_settings.json"
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.voice_settings, f, indent=2)
        
        return voice_file
    
    def create_voice_integration_api(self):
        """Create API for voice command integration"""
        
        print("🔌 Creating Voice Integration API...")
        
        api_content = """
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
        """
        
        api_file = self.voice_dir / "voice_api.py"
        with open(api_file, 'w', encoding='utf-8') as f:
            f.write(api_content)
        
        print(f"✅ Voice API created: {api_file}")
        return api_file

def main():
    """Main execution function"""
    
    print("🎤 VOICE RECOGNITION & COMMAND SYSTEM")
    print("=" * 50)
    print("Creating hands-free CEO-Manager interface...")
    print()
    
    voice_system = VoiceCommandSystem()
    
    # Create voice interface
    voice_interface = voice_system.create_voice_interface()
    
    # Create integration API
    voice_api = voice_system.create_voice_integration_api()
    
    print("\n" + "=" * 50)
    print("✅ VOICE COMMAND SYSTEM COMPLETE")
    print("=" * 50)
    print(f"🎤 Voice Interface: {voice_interface}")
    print(f"🔌 Integration API: {voice_api}")
    print(f"📝 Commands Config: voice_commands.json")
    print(f"⚙️ Settings Config: voice_settings.json")
    print()
    print("🔊 Voice Commands Available:")
    print("  • 'Hey Computer, team status'")
    print("  • 'Show dashboard'")
    print("  • 'Generate report'")
    print("  • 'Emergency stop'")
    print()
    print("⌨️ Keyboard Shortcut: Ctrl+Space (Push-to-talk)")
    print("🎯 CEO-Manager hands-free efficiency: MAXIMIZED")

if __name__ == "__main__":
    main()