from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os
from simulation import CustomerServiceSimulation

app = Flask(__name__)

# Initialize simulation
config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
simulation = CustomerServiceSimulation(
    stages_file=os.path.join(config_dir, 'Stages.csv'),
    priorities_file=os.path.join(config_dir, 'Priorities.csv')
)

@app.route('/')
def index():
    """Render the main dashboard"""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_simulation():
    """Start the simulation"""
    simulation.run_simulation()
    return jsonify({'status': 'started'})

@app.route('/api/set_slo_rate', methods=['POST'])
def set_slo_rate():
    """Set the SLO failure rate"""
    rate = request.json.get('rate', 20)
    simulation.slo_failure_rate = rate / 100.0
    return jsonify({'status': 'updated', 'rate': rate})
    """Start the simulation"""
    simulation.run_simulation()
    return jsonify({'status': 'started'})

@app.route('/api/stop', methods=['POST'])
def stop_simulation():
    """Stop the simulation"""
    simulation.stop_simulation()
    return jsonify({'status': 'stopped'})

@app.route('/api/state')
def get_state():
    """Get current simulation state"""
    cases_data = []
    current_time = datetime.now()
    
    for case in simulation.cases.values():
        case_data = {
            'id': case.id,
            'priority': case.priority,
            'creation_time': case.creation_time.isoformat(),
            'current_stage': simulation.stages[case.current_stage_index].name,
            'completed': case.completed,
            'stages': {}
        }
        
        # Add completed stage times
        for stage_name, time_spent in case.stage_times.items():
            stage_index = next((i for i, stage in enumerate(simulation.stages) if stage.name == stage_name), None)
            if stage_index is not None:
                slo_time = simulation.stages[stage_index].slo_times[case.priority]
                case_data['stages'][stage_name] = {
                    'time': time_spent,
                    'slo_time': slo_time,
                    'within_slo': time_spent <= slo_time
                }
        
        # Add current stage time if not completed
        if not case.completed:
            current_stage = simulation.stages[case.current_stage_index].name
            current_time_spent = (current_time - case.stage_start_times[current_stage]).total_seconds()
            slo_time = simulation.stages[case.current_stage_index].slo_times[case.priority]
            case_data['stages'][current_stage] = {
                'time': current_time_spent,
                'slo_time': slo_time,
                'active': True,
                'within_slo': current_time_spent <= slo_time
            }
        
        cases_data.append(case_data)
    
    return jsonify({
        'cases': cases_data,
        'total_cases': simulation.case_counter,
        'stage_stats': simulation.get_stage_statistics()
    })

if __name__ == '__main__':
    app.run(debug=True)
