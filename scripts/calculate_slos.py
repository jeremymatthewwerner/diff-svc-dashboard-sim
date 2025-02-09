import numpy as np

def calculate_slos():
    # Number of priority levels (0-10)
    n_priorities = 11
    
    # Create exponential distribution for more distinct values
    x = np.arange(n_priorities)
    base = 1.5  # Exponential base for growth
    
    # Calculate distribution
    base_distribution = np.power(base, x)
    scaled_distribution = (base_distribution - base_distribution.min()) / (base_distribution.max() - base_distribution.min())
    
    # Invert so higher priorities (lower numbers) get shorter times
    scaled_distribution = 1 - scaled_distribution
    
    # Scale to our desired range (5 seconds to 180 seconds)
    min_time = 5
    max_time = 180
    waiting_times = min_time + scaled_distribution * (max_time - min_time)
    
    # Ensure strictly increasing times
    waiting_times.sort()
    
    # Calculate other stage times based on waiting times
    stage_multipliers = {
        'WAITING': 1.0,
        'DEFINING': 1.5,
        'SOLVING': 2.0,
        'TRANSFERRING': 1.0,
        'RESOLVING': 1.5,
        'FOLLOWING-UP': 1.5,
        'CLOSED': 0
    }
    
    # Print CSV format
    print("STAGE,WAITING,DEFINING,SOLVING,TRANSFERRING,RESOLVING,FOLLOWING-UP,CLOSED")
    for priority, waiting_time in enumerate(waiting_times):
        times = [str(int(round(waiting_time * stage_multipliers[stage]))) 
                for stage in ['WAITING', 'DEFINING', 'SOLVING', 'TRANSFERRING', 'RESOLVING', 'FOLLOWING-UP', 'CLOSED']]
        print(f"{priority},{','.join(times)}")

if __name__ == "__main__":
    calculate_slos()
