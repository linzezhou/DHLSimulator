SYSTEM_CONFIG = {
    #set track number
    'track_count': 1,
    #compute node and library
    'nodes':{
        'library': {
            'name': 'Library',
            'docking_stations': 1, 
            'position': (0, 0)  #center
        },
        'compute_node_1': {
            'name': 'ComputeNode1',
            'docking_stations': 1,
            'position': (1000, 0)
        },
        'compute_node_2': {
            'name': 'ComputeNode2',
            'docking_stations': 1,
            'position': (0, 1000)
        },
        'compute_node_3': {
            'name': 'ComputeNode3',
            'docking_stations': 1,
            'position': (-1000, 0)
        },
        'compute_node_4': {
            'name': 'ComputeNode4',
            'docking_stations': 1,
            'position': (0, -1000)
        }
    },
    'cart_config': {
        'count': 3, 
        'max_speed': 300,
        'acceleration': 1000,
        'deceleration': 1000,
        'docking_time': 3,
        'mass': 0.524,
        'ssd_capacity': 8 * 1024,  
        'ssd_count': 64,  
        'total_capacity': 8 * 1024 * 64  
    },
    'dataset_config': {
        'total_data_size': 29 * 1024 * 1024, 
        'ssd_count': 30,
        'ssd_size': 8 * 1024, 
    },
    #distance between nodes in meters
    'distances': {
        ('Library', 'ComputeNode1'): 1000,
        ('Library', 'ComputeNode2'): 1000,
        ('Library', 'ComputeNode3'): 1000,
        ('Library', 'ComputeNode4'): 1000,
        ('ComputeNode1', 'Library'): 1000,
        ('ComputeNode2', 'Library'): 1000,
        ('ComputeNode3', 'Library'): 1000,
        ('ComputeNode4', 'Library'): 1000,
    }
} 