import threading
import time
import random

class TrackSection:
    def __init__(self, id):
        self.id = id
        self.lock = threading.Lock()
        self.occupied_by = None  # Reference to Train object

    def acquire(self, train):
        acquired = self.lock.acquire(timeout=0.1)
        if acquired:
            self.occupied_by = train
        return acquired

    def release(self):
        self.occupied_by = None
        self.lock.release()

class Train(threading.Thread):
    def __init__(self, id, route, speed=1.0, mode="detection"):
        super().__init__(daemon=True)
        self.train_id = id
        self.route = route  # List of TrackSection objects
        self.current_index = -1
        self.speed = speed
        self.mode = mode # "prone", "detection", "prevention"
        self.is_running = True
        self.status = "Waiting"
        self.waiting_for = None # TrackSection we are currently trying to lock

    def run(self):
        while self.is_running:
            # Try to acquire next section in route
            next_index = (self.current_index + 1) % len(self.route)
            next_section = self.route[next_index]
            
            self.waiting_for = next_section
            self.status = f"Waiting for {next_section.id}"
            
            # PREVENTION MODE: Resource Ordering
            # Note: This is a simplified version where trains always acquire in index order.
            # In a real system, we'd sort resources by global ID.
            
            acquired = False
            if self.mode == "prevention":
                # RESOURCE ORDERING: To prevent circular wait, we must always acquire 
                # resources in a strict increasing order of their IDs.
                # In this circular track, 'T7' -> 'T0' is the "wrap around" point.
                # If a train holds T7 and wants T0, it violates the order.
                # However, since each train only holds ONE section at a time (before acquiring next),
                # we can implement this by making the transition from T7 to T0 "atomic" or 
                # by ensuring we don't hold the last if we want the first.
                
                # Simplified robust prevention: Don't hold the "highest" resource if trying to get the "lowest"
                # OR more simply: ensure we don't create a cycle by checking if the next section is free
                # and would not lead to a deadlock.
                
                current_sect = self.route[self.current_index] if self.current_index != -1 else None
                
                # If moving T7 -> T0, we release T7 FIRST (breaking the cycle potential)
                if current_sect and current_sect.id == "T7" and next_section.id == "T0":
                    current_sect.release()
                    self.current_index = -1 # Temporarily outside
                    acquired = next_section.acquire(self)
                else:
                    acquired = next_section.acquire(self)
            else:
                acquired = next_section.acquire(self)

            if acquired:
                self.waiting_for = None
                self.status = f"Moving to {next_section.id}"
                
                # Release previous section if we still hold one
                if self.current_index != -1:
                    prev_section = self.route[self.current_index]
                    prev_section.release()
                
                self.current_index = next_index
                time.sleep(random.uniform(0.5, 1.5) / self.speed)
            else:
                # Could not acquire, sleep and retry
                time.sleep(0.1)

    def stop(self):
        self.is_running = False
        if self.current_index != -1:
            try:
                self.route[self.current_index].release()
            except:
                pass

class DeadlockMonitor:
    def __init__(self, trains, tracks):
        self.trains = trains
        self.tracks = tracks

    def detect_deadlock(self):
        """DFS based cycle detection on Wait-For Graph."""
        # Build Wait-For Graph: Train A -> Train B (A waits for resource held by B)
        graph = {}
        for train in self.trains:
            if train.waiting_for:
                owner = train.waiting_for.occupied_by
                if owner and owner != train:
                    graph[train.train_id] = owner.train_id

        # DFS for cycles
        visited = set()
        path = []
        
        def find_cycle(u, current_path):
            visited.add(u)
            current_path.append(u)
            
            v = graph.get(u)
            if v:
                if v in current_path:
                    # Cycle found!
                    cycle_start_index = current_path.index(v)
                    return current_path[cycle_start_index:]
                if v not in visited:
                    res = find_cycle(v, current_path)
                    if res: return res
            
            current_path.pop()
            return None

        for train_id in list(graph.keys()):
            if train_id not in visited:
                cycle = find_cycle(train_id, [])
                if cycle:
                    return cycle
        return None
