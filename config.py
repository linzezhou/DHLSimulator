SYSTEM_CONFIG = {
    #set track number
    'track_count': 1,
    #compute node and library
    'nodes':{
        'compute_node': {
            'name': 'ComputeNode',
            'docking_stations': 2,  #docking station number
            'processing_time': 50,  #SSD processing time (in seconds)
        },
        'library': {
            'name': 'Library',
            'docking_stations': 2,
            'processing_time': 0,  #library doesn't need processing time
        }
    },
    'cart_config': {
        'count': 2,
        'max_speed': 200,  #meter/second
        'acceleration': 1000,  #meter/second squared
        'deceleration': 1000,  #meter/second squared
        'docking_time': 10,  #docking time (in seconds)
    },
    'dataset_config': {
        'ssd_count': 30,
        'ssd_size': 100,  #assume GB for now
    },
    #distance between nodes (in meters)
    'distances': {
        ('ComputeNode', 'Library'): 500,
        ('Library', 'ComputeNode'): 500,
    }
} 