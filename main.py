#python3 -u "/Users/linzezhou/Desktop/DHLSimulator/main.py"
from config import SYSTEM_CONFIG
from DHLpackage import Simulator

def main():
    #adjustable commands according to the needs of the simulation

    # commands = [
    #     {
    #         'task_id': 'task1',
    #         'start_time': 0,
    #         'node_name': 'ComputeNode1',
    #         'ssd_number': 3,
    #         'duration': 1350
    #     },
    #     {
    #         'task_id': 'task2',
    #         'start_time': 100,
    #         'node_name': 'ComputeNode2',
    #         'ssd_number': 25,
    #         'duration': 1350
    #     },
    #     {
    #         'task_id': 'task3',
    #         'start_time': 200,
    #         'node_name': 'ComputeNode3',
    #         'ssd_number': 3,
    #         'duration': 1350
    #     },
    #     {
    #         'task_id': 'task4',
    #         'start_time': 300,
    #         'node_name': 'ComputeNode4',
    #         'ssd_number': 15,
    #         'duration': 1350
    #     }
    # ]

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
    
    print(f"\nsimutation time: {results['total_time']} seconds")
    print(f"total conflicts number: {results['total_conflicts']}")

if __name__ == "__main__":
    main()
