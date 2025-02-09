import csv
import time
import random
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np

@dataclass
class Stage:
    name: str
    slo_times: Dict[int, int]  # priority -> seconds

@dataclass
class Case:
    id: str
    priority: int
    creation_time: datetime
    current_stage_index: int
    stage_times: Dict[str, float]  # stage_name -> seconds spent
    stage_start_times: Dict[str, datetime]  # stage_name -> start time
    completed: bool = False

class CustomerServiceSimulation:
    def __init__(self, stages_file: str, priorities_file: str, slo_failure_rate: float = 0.2):
        self.stages: List[Stage] = []
        self.priorities: List[int] = []
        self.cases: Dict[str, Case] = {}
        self.case_counter: int = 0
        self.running: bool = False
        self.slo_failure_rate = slo_failure_rate
        self.load_config(stages_file, priorities_file)
        
    def load_config(self, stages_file: str, priorities_file: str):
        # Load priorities
        with open(priorities_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            self.priorities = [int(row[0]) for row in reader]
        
        # Load stages
        with open(stages_file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            stage_names = header[1:]  # Skip STAGE column
            
            # Initialize stages
            self.stages = [Stage(name=name, slo_times={}) for name in stage_names]
            
            # Load SLO times for each priority
            for row in reader:
                priority = int(row[0])
                for i, slo_time in enumerate(row[1:]):
                    self.stages[i].slo_times[priority] = int(slo_time)

    def generate_transition_time(self, slo_time: float) -> float:
        """Generate a random transition time with normal distribution"""
        # Decide if this transition should exceed SLO
        should_exceed = random.random() < self.slo_failure_rate
        
        if should_exceed:
            # Generate a time that exceeds SLO
            mean = slo_time * 1.2  # 20% over SLO on average when failing
            std_dev = slo_time * 0.1
        else:
            # Generate a time within SLO
            mean = slo_time * 0.7  # Target 70% of SLO time when succeeding
            std_dev = slo_time * 0.15
        
        time = np.random.normal(mean, std_dev)
        return max(1, time)  # Ensure positive time

    def create_case(self) -> Case:
        """Create a new case with random priority"""
        self.case_counter += 1
        case_id = f"CASE-{self.case_counter:04d}"
        priority = random.choice(self.priorities)
        case = Case(
            id=case_id,
            priority=priority,
            creation_time=datetime.now(),
            current_stage_index=0,
            stage_times={},
            stage_start_times={self.stages[0].name: datetime.now()}
        )
        self.cases[case_id] = case
        return case

    def advance_case(self, case: Case):
        """Advance a case to the next stage"""
        current_stage = self.stages[case.current_stage_index]
        
        # Calculate time spent in current stage
        start_time = case.stage_start_times[current_stage.name]
        time_spent = (datetime.now() - start_time).total_seconds()
        case.stage_times[current_stage.name] = time_spent

        # Move to next stage if not at end
        if case.current_stage_index < len(self.stages) - 1:
            case.current_stage_index += 1
            next_stage = self.stages[case.current_stage_index]
            case.stage_start_times[next_stage.name] = datetime.now()
        else:
            case.completed = True

    def get_stage_statistics(self) -> Dict[str, Dict[str, float]]:
        """Calculate SLO statistics for each stage"""
        stats = {}
        for stage in self.stages:
            within_slo = 0
            exceeded_slo = 0
            total = 0
            
            for case in self.cases.values():
                if stage.name in case.stage_times:
                    total += 1
                    time_spent = case.stage_times[stage.name]
                    slo_time = stage.slo_times[case.priority]
                    if time_spent <= slo_time:
                        within_slo += 1
                    else:
                        exceeded_slo += 1
            
            if total > 0:
                stats[stage.name] = {
                    'within_slo': (within_slo / total) * 100,
                    'exceeded_slo': (exceeded_slo / total) * 100
                }
            else:
                stats[stage.name] = {'within_slo': 0, 'exceeded_slo': 0}
        
        return stats

    def run_simulation(self):
        """Main simulation loop"""
        self.running = True
        
        def simulation_loop():
            while self.running:
                # Create new case every ~15 seconds
                if random.random() < 0.067:  # ~1/15 chance each second
                    self.create_case()
                
                # Process existing cases
                for case in list(self.cases.values()):
                    if not case.completed:
                        current_stage = self.stages[case.current_stage_index]
                        start_time = case.stage_start_times[current_stage.name]
                        time_spent = (datetime.now() - start_time).total_seconds()
                        
                        # Get SLO time for current stage and priority
                        slo_time = current_stage.slo_times[case.priority]
                        # Randomly advance case based on normal distribution
                        if time_spent >= self.generate_transition_time(slo_time):
                            self.advance_case(case)
                
                time.sleep(1)  # Check every second
        
        threading.Thread(target=simulation_loop, daemon=True).start()

    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False
