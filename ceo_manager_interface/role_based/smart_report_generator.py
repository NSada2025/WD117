
#!/usr/bin/env python3
'''
Smart Report Generator with Role-Based Optimization
Prevents output overload through intelligent summarization
'''

import json
from datetime import datetime

class SmartReportGenerator:
    def __init__(self, role):
        self.role = role
        self.output_budget = self.get_output_budget(role)
        self.current_usage = 0
        
    def get_output_budget(self, role):
        budgets = {
            'dev1': 4000,
            'dev2': 6000,
            'dev3': 2500  # Strict limit for dev3
        }
        return budgets.get(role, 3000)
    
    def generate_report(self, data, report_type='standard'):
        '''Generate role-optimized report'''
        
        if self.role == 'dev3':
            return self.generate_executive_summary(data)
        elif self.role == 'dev2':
            return self.generate_technical_summary(data)
        else:
            return self.generate_balanced_report(data)
    
    def generate_executive_summary(self, data):
        '''Ultra-concise executive summary for dev3'''
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'type': 'executive_summary',
            'key_points': []
        }
        
        # Extract only top 3 critical items
        if 'achievements' in data:
            summary['key_points'].append(f"✓ Top achievement: {data['achievements'][0]}")
        
        if 'issues' in data:
            summary['key_points'].append(f"⚠ Critical issue: {data['issues'][0] if data['issues'] else 'None'}")
        
        if 'next_steps' in data:
            summary['key_points'].append(f"→ Next priority: {data['next_steps'][0]}")
        
        # Add visual indicator
        summary['visual_health'] = self.generate_mini_visualization(data)
        
        # Ensure output stays under budget
        summary['output_length'] = len(str(summary))
        summary['budget_used'] = f"{(summary['output_length'] / self.output_budget * 100):.1f}%"
        
        return summary
    
    def generate_technical_summary(self, data):
        '''Technical summary for dev2'''
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'type': 'technical_summary',
            'implementation_status': data.get('status', 'active'),
            'code_metrics': {
                'lines_added': data.get('lines_added', 0),
                'functions_created': data.get('functions', 0),
                'performance': data.get('performance', 'optimal')
            },
            'next_tasks': data.get('next_steps', [])[:3]
        }
        
        return summary
    
    def generate_balanced_report(self, data):
        '''Balanced report for dev1'''
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'type': 'balanced_report',
            'analysis_summary': data.get('analysis', {}),
            'findings': data.get('findings', [])[:5],
            'recommendations': data.get('recommendations', [])[:3],
            'data_quality': data.get('quality_score', 'good')
        }
        
        return report
    
    def generate_mini_visualization(self, data):
        '''Generate text-based mini visualization'''
        
        # Simple ASCII chart for minimal output
        health_score = data.get('health_score', 85)
        bars = int(health_score / 10)
        
        return f"[{'█' * bars}{'░' * (10 - bars)}] {health_score}%"
    
    def check_output_health(self):
        '''Monitor output usage'''
        
        usage_percent = (self.current_usage / self.output_budget) * 100
        
        if usage_percent > 90:
            return 'critical'
        elif usage_percent > 75:
            return 'warning'
        else:
            return 'healthy'

# Auto-compact prevention wrapper
class OutputGuard:
    def __init__(self, role):
        self.role = role
        self.buffer = []
        self.chunk_size = 500 if role == 'dev3' else 1000
        
    def safe_output(self, content):
        '''Safely output content with chunking'''
        
        if len(content) > self.chunk_size:
            # Break into chunks
            chunks = [content[i:i+self.chunk_size] 
                     for i in range(0, len(content), self.chunk_size)]
            return {
                'chunked': True,
                'total_chunks': len(chunks),
                'first_chunk': chunks[0],
                'remaining': len(chunks) - 1
            }
        else:
            return {
                'chunked': False,
                'content': content
            }

if __name__ == '__main__':
    # Example usage
    dev3_reporter = SmartReportGenerator('dev3')
    dev3_guard = OutputGuard('dev3')
    
    sample_data = {
        'achievements': ['CEO-Manager interface optimized', 'Stability enhanced'],
        'issues': [],
        'next_steps': ['Monitor performance', 'Gather feedback'],
        'health_score': 92
    }
    
    report = dev3_reporter.generate_report(sample_data)
    safe_output = dev3_guard.safe_output(json.dumps(report, indent=2))
    
    print(json.dumps(safe_output, indent=2))
        