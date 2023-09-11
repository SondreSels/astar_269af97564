import pygame
import math
from queue import PriorityQueue
import random
import time

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

acceleration = 100
deceleration = 1
top_speed = 100


class Robot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = RED
		self.path = []
		self.width = width
		self.total_rows = total_rows
		self.is_moving = False
		self.direction = -1
		self.speed = 500
		self.current_move_time = 0

	def move_spot(self, grid):
		if self.path != []:
			grid[self.row][self.col].reset()
			# check if robot is moving in same direction
			if self.direction == get_direction(grid[self.row][self.col], grid[self.path[0][0]][self.path[0][1]]):
				# check if robot is at top speed
				if self.speed > top_speed:
					self.speed -= acceleration
			else:
				# robot is changing direction
				self.speed = 500
			self.direction = get_direction(grid[self.row][self.col], grid[self.path[0][0]][self.path[0][1]])
			self.row = self.path[0][0]
			self.col = self.path[0][1]
			self.path.pop(0)
			grid[self.row][self.col].make_robot()
			self.is_moving = True
			pygame.draw.rect(WIN, self.color, (self.x, self.y, self.width, self.width))
		else:
			self.is_moving = False
	
	def assign_path(self, path):
		self.path = path

	def get_pos(self):
		return self.row, self.col
	
	def get_direction(self):
		return self.direction
	
	def update_blockage(self, grid):
		current = 0
		for i in range(len(self.path)):
			grid[self.path[i][0]][self.path[i][1]].blocked = [current, current + grid[self.path[i][0]][self.path[i][1]].speed]
			current += grid[self.path[i][0]][self.path[i][1]].speed
	

class Spot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows
		self.direction = -1
		self.blocked = [0,0]
		self.speed = 500

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == YELLOW

	def is_open(self):
		return self.color == GREEN

	def is_barrier(self):
		return (self.color == BLACK or self.color == RED)

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == TURQUOISE

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = YELLOW

	def make_open(self):
		self.color = GREEN

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = TURQUOISE

	def make_path(self):
		self.color = PURPLE

	def make_robot(self):
		self.color = RED

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False

def get_direction(current, neighbor):
	direction = -1
	if current.row == neighbor.row:
		# The neighbor is to the left or right
		if current.col < neighbor.col:
			direction = EAST
		else:
			direction = WEST
	else:
		# The neighbor is above or below
		if current.row < neighbor.row:
			direction = SOUTH
		else:
			direction = NORTH
	return direction

def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return (abs(x1 - x2) + abs(y1 - y2)) * 100

	


def reconstruct_path(came_from, current, draw, robot, grid):
	robot_path = [current.get_pos()]
	while current in came_from:
		current = came_from[current]
		robot_path.append(current.get_pos())
		draw()
	robot.assign_path(robot_path[::-1])
	robot.update_blockage(grid)


def algorithm(draw, grid, start, end, robot, current_time):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_pos(), end.get_pos())

	open_set_hash = {start}

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]
		open_set_hash.remove(current)
		# Check where current came from
		direction = -1
		if current == start:
			direction = -1
		else:
			previous = came_from[current]
			if current.row == previous.row:
				# The neighbor is to the left or right
				if current.col < previous.col:
					direction = WEST
				else:
					direction = EAST
			else:
				# The neighbor is above or below
				if current.row < previous.row:
					direction = NORTH
				else:
					direction = SOUTH

		if current == end:
			reconstruct_path(came_from, end, draw, robot, grid)
			end.make_end()
			return True

		for neighbor in current.neighbors:
			# Find the direction between the current node and the neighbor
			neighbor_direction = -1
			speed = current.speed
			if current.row == neighbor.row:
				# The neighbor is to the left or right
				if current.col < neighbor.col:
					neighbor_direction = EAST
				else:
					neighbor_direction = WEST
			else:
				# The neighbor is above or below
				if current.row < neighbor.row:
					neighbor_direction = SOUTH
				else:
					neighbor_direction = NORTH
			if neighbor_direction == direction or direction == -1:
				if speed > top_speed:
					speed -= acceleration
			else:
				speed = 500
			temp_g_score = g_score[current] + speed
			if temp_g_score > neighbor.blocked[0] and temp_g_score < neighbor.blocked[1]:
				temp_g_score = neighbor.blocked[1] + 500

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash:
					count += 1
					neighbor.speed = speed
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()
					draw()
					print(temp_g_score)


		if current != start:
			current.make_closed()

	return False


def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)

	return grid


def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
	win.fill(WHITE)

	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)
	pygame.display.update()


def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col


def main(win, width):
	ROWS = 50
	grid = make_grid(ROWS, width)
	# Percentage of barriers
	percentage = 0
	# make barriers
	for row in grid:
		for spot in row:
			if spot != grid[0][0] and spot != grid[ROWS-1][ROWS-1]:
				if random.random() < percentage:
					spot.make_barrier()
	# Number of robots
	num_robots = 10
	Robots = []
	# make robots
	for i in range(num_robots):
		row = random.randint(0, ROWS-1)
		col = random.randint(0, ROWS-1)
		if grid[row][col] != grid[0][0] and grid[row][col] != grid[ROWS-1][ROWS-1]:
			Robots.append(Robot(row, col, width, ROWS))
			grid[row][col].make_robot()
	
	orders = set()

	run = True
	while run:
		draw(win, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]: # LEFT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				order = spot
				order.make_end()
				orders.add(order)

	

			elif pygame.mouse.get_pressed()[2]: # RIGHT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				spot.make_barrier()
				

			if event.type == pygame.KEYDOWN:
				print(len(orders))
				if event.key == pygame.K_SPACE:
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)
					for i in range(len(orders)):
						min_distance = 100000
						closest_robot = None
						current_time = int(time.time() * 1000)
						for robot in Robots:
							if robot.path == []:
								distance = h(robot.get_pos(), list(orders)[0].get_pos())
								if distance < min_distance:
									min_distance = distance
									closest_robot = robot
						if closest_robot != None:
							algorithm(lambda: draw(win, grid, ROWS, width), grid, grid[closest_robot.row][closest_robot.col], list(orders)[0], closest_robot, current_time)
							# clear order from orders
							orders.remove(list(orders)[0])
					moving = True
					count = 0
					while moving:
						moving = False
						draw(win, grid, ROWS, width)
						current_time = int(time.time() * 1000)
						for robot in Robots:
							if current_time - robot.current_move_time >= robot.speed:
								robot.move_spot(grid)
								robot.current_move_time = current_time
								pygame.display.update()
							if robot.path != []:
								moving = True

				if event.key == pygame.K_c:
					Robots = []
					grid = make_grid(ROWS, width)
					for row in grid:
						for spot in row:
							if spot != grid[0][0] and spot != grid[ROWS-1][ROWS-1]:
								if random.random() < percentage:
									spot.make_barrier()
					for i in range(num_robots):
						row = random.randint(0, ROWS-1)
						col = random.randint(0, ROWS-1)
						if grid[row][col] != grid[0][0] and grid[row][col] != grid[ROWS-1][ROWS-1]:
							Robots.append(Robot(row, col, width, ROWS))
							grid[row][col].make_robot()

	pygame.quit()

main(WIN, WIDTH)