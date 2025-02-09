from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os
from python_project.simulation import CustomerServiceSimulation

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
    
    print(f"Number of cases: {len(simulation.cases)}")
    print(f"Case counter: {simulation.case_counter}")
    
    for case in simulation.cases.values():
        print(f"\nProcessing case {case.id}:")
        print(f"  Priority: {case.priority}")
        print(f"  Current stage index: {case.current_stage_index}")
        print(f"  Completed: {case.completed}")
        
        case_data = {
            'id': case.id,
            'priority': case.priority,
            'creation_time': case.creation_time.isoformat(),
            'stages': {}
        }
        
        # Initialize all stages with empty data
        for stage in simulation.stages:
            case_data['stages'][stage.name] = {
                'time': None,
                'slo_time': stage.slo_times[case.priority],
                'within_slo': False,
                'active': False
            }
        
        # Add completed stage times
        for stage_name, time_spent in case.stage_times.items():
            print(f"  Stage {stage_name}: {time_spent} seconds")
            stage_index = next((i for i, stage in enumerate(simulation.stages) if stage.name == stage_name), None)
            if stage_index is not None:
                slo_time = simulation.stages[stage_index].slo_times[case.priority]
                case_data['stages'][stage_name].update({
                    'time': time_spent,
                    'slo_time': slo_time,
                    'within_slo': time_spent <= slo_time,
                    'active': False
                })
        
        # Add current stage time if not completed
        if not case.completed:
            current_stage = simulation.stages[case.current_stage_index].name
            current_time_spent = (current_time - case.stage_start_times[current_stage]).total_seconds()
            slo_time = simulation.stages[case.current_stage_index].slo_times[case.priority]
            print(f"  Current stage {current_stage}: {current_time_spent} seconds (SLO: {slo_time})")
            case_data['stages'][current_stage].update({
                'time': current_time_spent,
                'slo_time': slo_time,
                'active': True,
                'within_slo': current_time_spent <= slo_time
            })
        
        cases_data.append(case_data)
        print(f"  Final case data: {case_data}")
    
    response = {
        'cases': cases_data,
        'total_cases': simulation.case_counter,
        'stage_stats': simulation.get_stage_statistics()
    }
    print(f"\nFinal response length: {len(response['cases'])} cases")
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
