import math
import random

class Cart:
    def __init__(self, env, name, config):
        self.env = env
        self.name = name
        self.max_speed = config['max_speed']
        self.acceleration = config['acceleration']
        self.deceleration = config['deceleration']
        self.docking_time = config['docking_time']
        self.mass = config['mass']
        self.ssd_capacity = config['ssd_capacity']
        self.ssd_count = config['ssd_count']
        self.total_capacity = config['total_capacity']
        self.available_ssds = set()  
        self.current_ssd = None
        self.current_node = None
        self.stats = {
            'time_blocked': 0,
            'launches': 0,
            'total_time': 0,
            'distance_traveled': 0,
            'conflicts': 0
        }

    def assign_ssds(self, ssd_numbers):
        self.available_ssds = set(ssd_numbers)

    def has_ssd(self, ssd_number):
        return ssd_number in self.available_ssds

    def get_ssd_location(self, ssd_number):
        if ssd_number in self.available_ssds:
            return self.current_node
        return None

    def calculate_travel_time(self, distance):
        #consider the travel time with acceleration and deceleration
        accel_time = self.max_speed / self.acceleration   #v_t = V_0(0) + a * t
        decel_time = self.max_speed / self.deceleration   #v_t = V_0(max_speed) + a * t
        accel_distance = 0.5 * self.acceleration * accel_time ** 2   #s = V_0(0) * t + (1/2) * a * t^2
        decel_distance = self.max_speed * decel_time - 0.5 * self.deceleration * decel_time ** 2 #s = V_0(max_speed) * t + (1/2) * a * t^2
        if accel_distance + decel_distance >= distance:
            #cannot reach the max speed

            #let t1 is accel_time, t2 is decel_time
            #t1 + t2 = t(total_time)

            #acceleration process
            #s1 = (1/2) * acc * t1^2
            #v_f = acc * t1

            #deceleration process
            #s2 = v_f * t2 - (1/2) * decel * t2^2
            #v_f = 0 = v_f - decel * t2. --> v_f = decel * t2

            #s1 + s2 = distance
            #thus (1/2) * acc * t1^2 + (v_f * t2 - (1/2) * decel * t2^2) = distance
            #--> (1/2) * acc * t1^2 + decel * t2^2 - (1/2) * decel * t2^2 = distance
            #--> (1/2) * acc * t1^2 + (1/2) * decel * t2^2 = distance

            #as a result, we can use the equation "acc * t1 = decel * t2" to solve for t1 and t2
            #t1 = sqrt(2 * distance / (acc + (acc^2/decel))
            #t2 = sqrt(2 * distance / (decel + (decel^2/acc))
            #total time = t1 + t2
            t1 = math.sqrt(2 * distance / (self.acceleration + (self.acceleration**2/self.deceleration)))
            t2 = math.sqrt(2 * distance / (self.deceleration + (self.deceleration**2/self.acceleration)))
            return t1 + t2
        else:
            #can reach the maximum speed
            #total time = accel_time + const_speed_time + decel_time
            const_speed_distance = distance - accel_distance - decel_distance
            const_speed_time = const_speed_distance / self.max_speed
            return accel_time + const_speed_time + decel_time