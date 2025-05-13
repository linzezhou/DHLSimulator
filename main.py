#python3 -u "/Users/linzezhou/Desktop/DHLSimulator/main.py"
from config import SYSTEM_CONFIG
from DHLpackage import Simulator

def main():
    #command list
    #command format:(start_time, cart_id, ssd_id, from_node, to_node)
    commands = [
        (0, 0, 3, 'Library', 'ComputeNode'),
        (1, 1, 25, 'Library', 'ComputeNode'),
        (3, 0, 3, 'ComputeNode', 'Library')
    ]
    simulator = Simulator(SYSTEM_CONFIG)
    results = simulator.run_simulation(commands)
    
    #print events
    print("events:")
    print("-"*5,"time | event type | details","-"*5)
    print("-" * 50)
    for time, event_type, details in results['events']:
        print(f"{time:8.1f} | {event_type:<12} | {details}")
    
    #print stats
    print("\nsimulation results:")
    for i, cart_stats in enumerate(results['carts']):
        print(f"\nCart {i+1} statistics:")
        for key, value in cart_stats.items():
            print(f"{key}: {value}")
    print(f"\ntotal simulation time: {results['total_time']} seconds")

if __name__ == "__main__":
    main()
