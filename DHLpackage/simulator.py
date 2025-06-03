import simpy
from .node import Node
from .cart import Cart
import random

class Simulator:
    def __init__(self, config):
        self.env = simpy.Environment()
        self.config = config
        self.nodes = {}
        self.carts = []
        self.events = []
        self.total_conflicts = 0
        self.command_queue = []
        self.cart_status = {} 
        self.setup_system()
        self.initialize_ssd_distribution()

    def setup_system(self):
        for node_type, node_config in self.config['nodes'].items():
            self.nodes[node_config['name']] = Node(self.env, node_config['name'], node_config)

        for i in range(self.config['cart_config']['count']):
            cart = Cart(self.env, f"Cart{i+1}", self.config['cart_config'])
            self.carts.append(cart)
            cart.current_node = 'Library'
            self.cart_status[cart.name] = {
                'busy_until': 0,
                'current_task': None
            }

    def initialize_ssd_distribution(self):
        total_ssds = self.config['dataset_config']['ssd_count']
        ssd_numbers = list(range(1, total_ssds + 1))
        random.shuffle(ssd_numbers)
        
        ssds_per_cart = total_ssds // len(self.carts)
        remaining_ssds = total_ssds % len(self.carts)
        
        start_idx = 0
        for cart in self.carts:
            end_idx = start_idx + ssds_per_cart + (1 if remaining_ssds > 0 else 0)
            cart.assign_ssds(ssd_numbers[start_idx:end_idx])
            start_idx = end_idx
            remaining_ssds -= 1
            
            self.log_event("SSD assignment", 
                          f"{cart.name} assigned SSD: {sorted(cart.available_ssds)}")

    def find_cart_with_ssd(self, ssd_number):
        for cart in self.carts:
            if cart.has_ssd(ssd_number):
                return cart
        return None

    def log_event(self, event_type, details, task_id=None):
        event_details = f"[Task {task_id}] {details}" if task_id else details
        self.events.append((self.env.now, event_type, event_details))

    def execute_command(self, command):
        task_id = command['task_id']
        node_name = command['node_name']
        ssd_number = command['ssd_number']
        duration = command['duration']

        cart = self.find_cart_with_ssd(ssd_number)
        if not cart:
            self.log_event("error", f"SSD {ssd_number} not found in any cart", task_id)
            return

        self.cart_status[cart.name]['current_task'] = task_id
        self.cart_status[cart.name]['busy_until'] = self.env.now

        from_node = cart.current_node
        to_node = node_name

        self.log_event("task started", 
                      f"node {node_name} needs SSD {ssd_number}, assigned to {cart.name}", task_id)

        if from_node == to_node:
            self.log_event("processing started", f"{cart.name} on {to_node} started SSD processing", task_id)
            yield self.env.timeout(duration)
            self.log_event("processing completed", f"{cart.name} on {to_node} completed SSD processing", task_id)
            self.cart_status[cart.name]['current_task'] = None
            self.cart_status[cart.name]['busy_until'] = self.env.now
            return

        total_travel_time = 0
        if from_node != 'Library':
            distance_to_library = self.config['distances'][(from_node, 'Library')]
            total_travel_time += cart.calculate_travel_time(distance_to_library)
        
        distance_to_target = self.config['distances'][('Library', to_node)]
        total_travel_time += cart.calculate_travel_time(distance_to_target)
        
        self.cart_status[cart.name]['busy_until'] = self.env.now + total_travel_time + duration + (cart.docking_time * 3)

        if from_node != 'Library':
            distance = self.config['distances'][(from_node, 'Library')]
            travel_time = cart.calculate_travel_time(distance)
            
            with self.nodes[from_node].docking_stations.request() as req:
                yield req
                self.log_event("docking started", f"{cart.name} on {from_node} started docking", task_id)
                yield self.env.timeout(cart.docking_time)
                self.log_event("docking completed", f"{cart.name} on {from_node} completed docking", task_id)
                
                cart.stats['launches'] += 1
                cart.stats['distance_traveled'] += distance
                cart.stats['total_time'] += travel_time + cart.docking_time
                
                self.log_event("journey started", f"{cart.name} from {from_node} to Library", task_id)
                yield self.env.timeout(travel_time)
                self.log_event("journey completed", f"{cart.name} arrived at Library", task_id)
                cart.current_node = 'Library'

        distance = self.config['distances'][('Library', to_node)]
        travel_time = cart.calculate_travel_time(distance)
        
        cart.stats['launches'] += 1
        cart.stats['distance_traveled'] += distance
        cart.stats['total_time'] += travel_time
        
        self.log_event("journey started", f"{cart.name} from Library to {to_node}", task_id)
        yield self.env.timeout(travel_time)
        self.log_event("journey completed", f"{cart.name} arrived at {to_node}", task_id)
        
        with self.nodes[to_node].docking_stations.request() as req2:
            if self.nodes[to_node].docking_stations.count == 0:
                cart.stats['conflicts'] += 1
                self.total_conflicts += 1
                self.log_event("conflict detected", f"{cart.name} on {to_node} waiting for docking station", task_id)
            
            yield req2
            self.log_event("docking started", f"{cart.name} on {to_node} started docking", task_id)
            yield self.env.timeout(cart.docking_time)
            self.log_event("docking completed", f"{cart.name} on {to_node} completed docking", task_id)
            
            cart.current_node = to_node
            
            if duration > 0:
                self.log_event("processing started", f"{cart.name} on {to_node} started SSD processing", task_id)
                yield self.env.timeout(duration)
                self.log_event("processing completed", f"{cart.name} on {to_node} completed SSD processing", task_id)
        
        self.cart_status[cart.name]['current_task'] = None
        self.cart_status[cart.name]['busy_until'] = self.env.now

    def process_command_queue(self):
        while self.command_queue:
            command = self.command_queue[0]
            task_id = command['task_id']
            
            if command['start_time'] > self.env.now:
                yield self.env.timeout(command['start_time'] - self.env.now)
            
            cart = self.find_cart_with_ssd(command['ssd_number'])
            if not cart:
                self.log_event("error", f"SSD {command['ssd_number']} not found in any cart", task_id)
                self.command_queue.pop(0)
                continue
            
            cart_status = self.cart_status[cart.name]
            if cart_status['current_task'] is not None:
                wait_time = max(0, cart_status['busy_until'] - self.env.now)
                if wait_time > 0:
                    self.log_event("waiting", f"Cart {cart.name} is busy with task {cart_status['current_task']}, waiting {wait_time:.1f} seconds", task_id)
                    yield self.env.timeout(wait_time)
                self.command_queue.append(command)
                self.command_queue.pop(0)
                continue
            
            try:
                yield self.env.process(self.execute_command(command))
            except ValueError as e:
                if "Negative delay" in str(e):
                    self.command_queue.append(command)
                    self.command_queue.pop(0)
                    yield self.env.timeout(1)
                    continue
                else:
                    raise e
            self.command_queue.pop(0)

    def run_simulation(self, commands):
        sorted_commands = sorted(commands, key=lambda x: x['start_time'])
        self.command_queue = sorted_commands
        
        self.env.process(self.process_command_queue())
        self.env.run()
        
        return {
            'carts': [cart.stats for cart in self.carts],
            'total_time': self.env.now,
            'events': self.events,
            'total_conflicts': self.total_conflicts
        } 