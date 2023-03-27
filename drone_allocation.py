from random import randrange

import pygame
import os

class MissionCycle():
	def __init__(self, start_time):
		self.start_time = start_time

		self.flight_duration = randrange(15, 25) # Arbitrary flight duration
		self.charge_duration = randrange(2, 5) # Arbitrary charge duration

		self.time_to_return = self.est_time_to_return()
		self.time_to_bingo_fuel = self.flight_duration

		self.manual_mode = False

		self.status = "waiting"
		self.modes = ["ready", "flying", "charging", "waiting"]
		#self.available = True

	def set_status(self, new_status):
		if new_status in self.modes:
			self.status = new_status
		else:
			print(f"Status '{new_status}' is not in the list of mission modes!")

	def est_time_to_return(self):
		return randrange(2, 7)

	def on_begin_flying(self):
		### Assign path here!
		#print("Assign a flight path!")
		pass

	def on_done_flying(self):
		self.manual_mode = False

	def on_done_charging(self, current_time):
		self.start_time = current_time

	def invoke_callback(self, callback_fn, *args, **kwargs):
		# Status change!
	    if not args and not kwargs:
	        callback_fn()
	    elif args and not kwargs:
	        callback_fn(*args)
	    elif kwargs and not args:
	        callback_fn(**kwargs)
	    else:
	        callback_fn(*args, **kwargs)

	def update_status(self, current_time):
		if current_time >= self.start_time:
			if self.status == "ready":
				self.invoke_callback(self.on_begin_flying)
				self.set_status("flying")

		if current_time >= self.start_time + self.flight_duration:
			if self.status == "flying":
				self.invoke_callback(self.on_done_flying)
				self.set_status("charging")

		if current_time >= self.start_time + self.flight_duration + self.charge_duration:
			if self.status == "charging":
				self.invoke_callback(self.on_done_charging, current_time)
				self.set_status("waiting")

	def is_available(self, current_time):
		pass
		#if self.status == "waiting":
		#	return True # Drone is available
		#if self.status == "flying":
		#	if current_time >= self.start_time + self.time_to_bingo_fuel - self.time_to_return:
		#		return True # Path is available???
		#return False

	def update(self, current_time):
		self.time_to_bingo_fuel = self.flight_duration - current_time
		self.update_status(current_time)

	def __str__(self):
		repr_s = ""
		if self.status == "ready":
			repr_s += "R"
		elif self.status == "flying":
			repr_s += "F-->"
			if not self.manual_mode: 
				repr_s += "\t -A"
		elif self.status == "charging":
			repr_s += "C..."
		elif self.status == "waiting":
			repr_s += "X-"

		if self.manual_mode:
			repr_s += "\t ||M"

		return repr_s


class Mission():
	def __init__(self, num_drones, greedy=False):
		self.cycles = [MissionCycle(0) for i in range(num_drones)]
		self.num_drones = num_drones

		self.manual_mode = False
		self.manual_drones = []
		self.num_allocated_manual = 1

		self.greedy = greedy

	def available_cycles(self):
		cycles = []
		for cycle in self.cycles:
			if cycle.status == "waiting":
				cycles.append(cycle)
		return cycles

	def update_manual_drones_status(self):
		self.manual_drones = [drone for drone in self.manual_drones if drone.manual_mode]

	def toggle_manual_mode(self):
		self.manual_mode = not self.manual_mode

	def get_target_num_available(self, has_all_manual):
		# Return the number of drones to reserve for manual mode.
		if has_all_manual and self.greedy:
			# In greedy allocation, reserve one less drone for manual mode
			# if it already has the correct number of manual drones.
			return self.num_allocated_manual - 1
		return self.num_allocated_manual


	def update(self, current_time):
		self.update_manual_drones_status()
		has_all_manual = len(self.manual_drones) == self.num_allocated_manual

		# Find all available cycles
		available_cycles = self.available_cycles()

		num_available = self.get_target_num_available(has_all_manual)
		# Assign allowed number of drones (leave some for the manual mode)
		while len(available_cycles) > num_available:
			cycle = available_cycles.pop()
			cycle.status = "ready"

		# Assign manual drones until the number of assigned drones is equal to the target number of manual drones
		if self.manual_mode:
			if not has_all_manual:
				available_cycles = self.available_cycles()
				if available_cycles:
					available_cycle = available_cycles.pop()
					available_cycle.manual_mode = True
					available_cycle.status = "ready"
					self.manual_drones.append(available_cycle)
				else:
					print("Awaiting available cycle for manual mode!")

		# Update cycles
		for cycle in self.cycles:
			cycle.update(current_time)

	def __str__(self):
		repr_s = ""
		manual_status = "ON" if self.manual_mode else "OFF"
		for cycle in self.cycles:
			repr_s += str(cycle)
			if cycle is self.cycles[0]: # First cycle
				repr_s += f"\t\t Manual mode: {manual_status}, Num allocated: {self.num_allocated_manual}, Greedy: {self.greedy}"
			repr_s += "\n"
		repr_s += "\n"
		return repr_s	

def main():
	pygame.display.set_mode((100, 100))
	NUM_DRONES = 10
	GREEDY = False
	mission = Mission(NUM_DRONES, GREEDY)
	t = 0

	while True:
		time = int(t)
		mission.update(time)
		os.system('cls')
		print(f"{time=}")
		print(str(mission))

		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_m:
					mission.toggle_manual_mode()
				if event.key == pygame.K_w:
					mission.num_allocated_manual += 1
				if event.key == pygame.K_s:
					if mission.num_allocated_manual > 1:
						mission.num_allocated_manual -= 1

		t += 0.08

if __name__ == '__main__':
	main()