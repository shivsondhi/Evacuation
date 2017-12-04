from Agent import *

import pygame
from pygame.locals import *
from pygame.color import *
from math import sqrt
import thinkplot
import random

DEBUG = False

class Point():
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.tuple = (x,y)

	def __str__(self):
		return "{}, {}".format(self.x, self.y)

	def __sub__(self, other):
		return Point(self.x - other.x, self.y - other.y)

	def __add__(self, other):
		return Point(self.x + other.x, self.y + other.y)

	def __mul__(self, scalar):
		return Point(self.x * scalar, self.y * scalar)

	def __truediv__(self, scalar):
		return Point(self.x / scalar, self.y / scalar)

	def mag(self):
		return sqrt((self.x**2) + (self.y**2))

	def norm(self):
		return self / self.mag()

class Wall():
	def __init__(self, wallType, **parameters):
		# type: "circle" | "line", points
		# Circle: type='circle' { "center": Point(x,y), "radius": r }
		# Line: type='line'{ "p1": Point(x1,y1), "p2": Point(x2,y2) }
		self.wallType = wallType
		self.parameters = parameters
		self.checkValid()

	def checkValid(self):
		if self.wallType == 'circle':
			assert isinstance(self.parameters["center"], Point), "Circles need a center"
			assert isinstance(self.parameters["radius"], int), "Radius needs to be an int"

		if self.wallType == 'line':
			assert isinstance(self.parameters['p1'], Point)
			assert isinstance(self.parameters['p2'], Point)

class Goal(Wall):
	""" Defines a goal. Currently, only horizontal and vertical lines are supported. """

	def checkValid(self):
		assert self.wallType == 'line'
		assert isinstance(self.parameters['p1'], Point)
		assert isinstance(self.parameters['p2'], Point)
		assert (self.parameters['p1'].x == self.parameters['p2'].x or  self.parameters['p1'].y == self.parameters['p2'].y)


		# p1 should always be smaller than p2
		if (self.parameters['p1'].x == self.parameters['p2'].x):
			if self.parameters['p1'].y > self.parameters['p2'].y:
				p1Temp = self.parameters['p1']
				self.parameters['p1'] = self.paramters['p2']
				self.parameters['p2'] = p1Temp
		elif (self.parameters['p1'].y == self.parameters['p2'].y):
			if self.parameters['p1'].x > self.parameters['p2'].x:
				p1Temp = self.parameters['p1']
				self.parameters['p1'] = self.paramters['p2']
				self.parameters['p2'] = p1Temp

class Environment():
	conditions = { 'k': 1.2 * 10**5, 'ka': 2.4 * 10**5 }

	def __init__(self, N, walls, goals, agents, conditions, instruments):
		self.N = N
		self.walls = walls
		self.goals = goals
		self.agents = agents
		self.instruments = instruments
		# Conditions: Agent force, Agent repulsive distance, acceleration time, step length,
		self.conditions.update(conditions)


	def step(self):
		for agent in self.agents:
			print(agent.desiredDirection)
		self.updateInstruments()

	def updateInstruments(self):
		for instrument in self.instruments:
			instrument.update(self)

	def plot(self, num):
		self.instruments[num].plot()



class EnvironmentViewer():
	BG_COLOR = Color(0,0,0)

	BLACK  = Color(0, 0, 0)
	WHITE  = Color(255, 255, 255)
	YELLOW = Color(255, 233, 0)
	RED    = Color(203, 20, 16)
	GOAL   = Color(252, 148, 37)

	def __init__(self, environment):
		self.env = environment
		self.screen = pygame.display.set_mode((1000,1000))

	def draw(self):
		self.screen.fill(self.BG_COLOR)

		for agent in self.env.agents:
			self.drawAgent(agent)

		for wall in self.env.walls:
			self.drawWall(wall)

		for goal in self.env.goals:
			self.drawGoal(goal)

		pygame.display.update()

	def drawAgent(self, agent):
		# Draw agent
		pygame.draw.circle(self.screen, self.YELLOW, agent.pos.tuple, agent.size)
		# Draw desired vector
		pygame.draw.line(self.screen, self.YELLOW, agent.pos.tuple, (agent.pos + (agent.desiredDirection*30)).tuple)
		if(DEBUG): print("drew agent at ", agent.pos)

	def drawWall(self, wall, color=WHITE):
		if wall.wallType == 'circle':
			pygame.draw.circle(self.screen, color, wall.parameters['center'].tuple, wall.parameters['radius'])
			if(DEBUG): print("drew wall at {}".format(wall.parameters['center']))

		if wall.wallType == 'line':
			pygame.draw.line(self.screen, color, wall.parameters['p1'].tuple, wall.parameters['p2'].tuple, 10)
			if(DEBUG): print("drew wall between {} and {}".format(wall.parameters['p1'], wall.parameters['p2']))

	def drawGoal(self, goal):
		self.drawWall(goal, color=self.GOAL)


class Instrument():
	""" Instrument that logs the state of the environment"""
	def __init__(self):
		self.metric = []

	def plot(self, **options):
		thinkplot.plot(self.metric, **options)
		thinkplot.show()


class ReachedGoal(Instrument):
	""" Logs the number of agents that have escaped """
	def update(self, env):
		self.metric.append(self.countReachedGoal(env))

	def countReachedGoal(self, env):
		num_escaped = 0

		for agent in env.agents:
			if agent.pos.x > agent.goal.parameters['p1'].x:
				num_escaped += 1
		return num_escaped



if __name__ == '__main__':
	roomHeight = 600
	roomWidth = 400
	doorWidth = 100
	walls = []
	walls.append(Wall('circle', **{ 'center': Point(600,600), 'radius': 50 }))

	walls.append(Wall('line', **{ 'p1': Point(0,0), 'p2': Point(roomWidth, 0) })) # Top
	walls.append(Wall('line', **{ 'p1': Point(0,0), 'p2': Point(0, roomHeight) })) # Left
	walls.append(Wall('line', **{ 'p1': Point(0,roomHeight), 'p2': Point(roomWidth, roomHeight) })) # Bottom

	walls.append(Wall('line', **{ 'p1': Point(roomWidth,0), 'p2': Point(roomWidth, roomHeight/2 - doorWidth/2) })) # Top Doorway
	walls.append(Wall('line', **{ 'p1': Point(roomWidth, roomHeight/2 + doorWidth/2), 'p2': Point(roomWidth, roomHeight) })) # Bottom Doorway



	goals = []
	goals.append(Goal('line', **{ 'p1': Point(roomWidth, roomHeight/2 - doorWidth/2), 'p2': Point(roomWidth, roomHeight/2 + doorWidth/2) }))

	instruments = []
	instruments.append(ReachedGoal())

	maxSize = 20
	agents = []
	for _ in range(10):
		# Agent(size, mass, pos, goal, desiredSpeed = 4))
		size = random.randint(10,maxSize)
		mass = 50
		pos = Point(random.randint(maxSize/2,roomWidth-maxSize/2), random.randint(maxSize/2,roomHeight-maxSize/2))
		goal = goals[0]

		agents.append(Agent(size, mass, pos, goal))

	env = Environment(100, walls, goals, agents, {}, instruments)
	viewer = EnvironmentViewer(env)

	viewer.draw()
	env.step()

	# Run until all agents have escaped
	while env.instruments[0].metric[-1] < len(env.agents):
		env.step()

	env.plot(0)
