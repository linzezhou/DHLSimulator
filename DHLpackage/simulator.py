import simpy
from .node import Node
from .cart import Cart

class Simulator:
    def __init__(self, config):
        self.env = simpy.Environment()
        self.config = config
        self.nodes = {}  #dictionary
        self.carts = []
        self.events = [] 
        self.setup_system()

    def setup_system(self):
        #create nodes(compute_node and library) and add them to the nodes dictionary
        for node_type, node_config in self.config['nodes'].items():
            self.nodes[node_config['name']] = Node(self.env, node_config['name'], node_config)

        #create carts
        for i in range(self.config['cart_config']['count']):
            cart = Cart(self.env, f"Cart{i+1}", self.config['cart_config'])
            self.carts.append(cart)

    def log_event(self, event_type, details):
        self.events.append((self.env.now, event_type, details)) #append the event as a tuple to the list

    def execute_command(self, command):
        #command format:(time, cart_id, ssd_id, from_node, to_node)
        time, cart_id, ssd_id, from_node, to_node = command
        #wait for the specified time to come
        yield self.env.timeout(time - self.env.now)

        cart = self.carts[cart_id]
        start_time = self.env.now
        self.log_event("Command Start", f"Cart {cart_id+1} starting from {from_node} to {to_node} with SSD {ssd_id}")
        #check if the source node has available docking stations
        with self.nodes[from_node].docking_stations.request() as req:
            yield req
            self.log_event("Docking Start", f"Cart {cart_id+1} docking at {from_node}")
            #docking time
            yield self.env.timeout(cart.docking_time)
            self.log_event("Docking Complete", f"Cart {cart_id+1} finished docking at {from_node}")
            
            #calculate the travel time
            distance = self.config['distances'][(from_node, to_node)]
            travel_time = cart.calculate_travel_time(distance)
            
            #update statistics
            cart.stats['launches'] += 1
            cart.stats['distance_traveled'] += distance
            cart.stats['total_time'] += travel_time + cart.docking_time
            
            #simulate the travel
            self.log_event("Travel Start", f"Cart {cart_id+1} starting travel from {from_node} to {to_node}")
            yield self.env.timeout(travel_time)
            self.log_event("Travel Complete", f"Cart {cart_id+1} arrived at {to_node}")
            
            #dock at the destinition node
            with self.nodes[to_node].docking_stations.request() as req2:
                yield req2
                self.log_event("Docking Start", f"Cart {cart_id+1} docking at {to_node}")
                yield self.env.timeout(cart.docking_time)
                self.log_event("Docking Complete", f"Cart {cart_id+1} finished docking at {to_node}")
                
                #if the destination node is a compute node, simulate data reading from the SSD
                if self.nodes[to_node].processing_time > 0:
                    self.log_event("Processing Start", f"Cart {cart_id+1} starting SSD processing at {to_node}")
                    yield self.env.timeout(self.nodes[to_node].processing_time)
                    self.log_event("Processing Complete", f"Cart {cart_id+1} finished SSD processing at {to_node}")

    def run_simulation(self, commands):
        #create processes for each command and add these processes to the event list
        #process execution order follows FIFO(the order of the commands) 
        #and will get suspended when yield is called
        for command in commands:
            self.env.process(self.execute_command(command))
        #run simulation(fake parallel), start handling the events(processes) in chronological order
        self.env.run()
        #return the data
        return { #dictionary
            'carts': [cart.stats for cart in self.carts], #list of dictionaries containing each cart's stats
            'total_time': self.env.now,
            'events': self.events  #(time, event_type, details)
        } 