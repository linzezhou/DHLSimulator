import simpy
#python3 -u "/Users/linzezhou/Desktop/DHL Simulator/simulator.py"
class Cart:
    def __init__(self, env, name, dispatch_times, station_a, station_b):
        self.env = env
        self.name = name
        self.dispatch_times = dispatch_times
        self.station_a = station_a
        self.station_b = station_b
        self.trip_count = 0
        #start the dispatch controller
        self.process = env.process(self.dispatch())

    def dispatch(self):
        for time in self.dispatch_times:
            yield self.env.timeout(time - self.env.now) #wait till the scheduled time to start
            print(f"[{self.env.now}] {self.name} dispatching from {self.station_a}")
            yield self.env.process(self.travel(self.station_a, self.station_b))
            yield self.env.process(self.travel(self.station_b, self.station_a))

    def travel(self, from_station, to_station):
        print(f"[{self.env.now}] {self.name} traveling from {from_station} to {to_station}")
        travel_time = 5
        yield self.env.timeout(travel_time)
        self.trip_count += 1
        print(f"[{self.env.now}] {self.name} arrived at {to_station}")

#main
schedule = [0, 10, 20, 30]
env = simpy.Environment()
cart1 = Cart(env, "Cart1", schedule, "StationA", "StationB")

#run for 50 seconds
env.run(until=50)
print(f"\nTotal trips completed: {cart1.trip_count}")
