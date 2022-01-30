from GameObjects import *


cellSize = 50


class Cell:
	def __init__(self, pos, size, data):
		self.pos = pos
		self.size = size
		self.maze = data["maze"]

		self.walls = {
			"top": True,
			"bottom": True,
			"left": True,
			"right": True
		}

		self.visited = False
		self.wallColor = data["wallColor"]
		self.backgroundColor = data["color"]
		self.inPath = False

	def Draw(self):
		x, y = self.pos
		if self == self.maze.startPoint:
			backgroundColor = green
		elif self == self.maze.endPoint:
			backgroundColor = red
		elif self == self.maze.current:
			backgroundColor = blue
		else:
			backgroundColor = self.backgroundColor

		pg.draw.rect(screen, backgroundColor, (x + 2, y + 2, self.size - 4, self.size - 4))

		if self.walls["top"]:
			pg.draw.line(screen, self.wallColor, (x, y), (x + self.size, y), 3)
		if self.walls["bottom"]:
			pg.draw.line(screen, self.wallColor, (x, y + self.size), (x + self.size, y + self.size), 3)
		if self.walls["left"]:
			pg.draw.line(screen, self.wallColor, (x, y), (x, y + self.size), 3)
		if self.walls["right"]:
			pg.draw.line(screen, self.wallColor, (x + self.size, y), (x + self.size, y + self.size), 3)

	def CheckNeighbors(self):
		neighbors = []

		i, j = self.maze.GetIndexFromPos(self.pos[0], self.pos[1])

		if j - 1 >= 0:
			neighbors.append(self.maze.grid[j - 1][i]) if not self.maze.grid[j - 1][i].visited else None

		if j + 1 < len(self.maze.grid):
			neighbors.append(self.maze.grid[j + 1][i]) if not self.maze.grid[j + 1][i].visited else None
		
		if i - 1 >= 0:
			neighbors.append(self.maze.grid[j][i - 1]) if not self.maze.grid[j][i - 1].visited else None
		
		if i + 1 < len(self.maze.grid[0]):
			neighbors.append(self.maze.grid[j][i + 1]) if not self.maze.grid[j][i + 1].visited else None

		return neighbors[randint(0, len(neighbors) - 1)] if len(neighbors) > 0 else None


class Grid(World):
	def __init__(self, rect=(0, 0, width, height), size=cellSize, color=lightBlack, mazeData={}, wallColor=lightBlue):
		super().__init__(rect, size, cellData={"cell": Cell, "wallColor": wallColor, "color": lightBlack, "maze": self})
		self.color = color
		self.mazeData = mazeData

		self.startPoint = self.grid[self.mazeData.get("start", [0, 0])[0]][self.mazeData.get("start", [0, 0])[1]]
		self.endPoint = self.grid[self.mazeData.get("end", [-1, -1])[0]][self.mazeData.get("end", [-1, -1])[1]]


	def Draw(self):
		pg.draw.rect(screen, self.color, self.rect)

		DrawRectOutline(darkWhite, self.rect, 2)

	def CreatePath(self):
		self.CreateGrid()
		self.current = self.startPoint
		self.path = []
		self.stack = []
		self.endReached = False
		self.finished = False

		while not self.finished:
			nextNeighbor = self.current.CheckNeighbors()

			self.current.visited = True
			if nextNeighbor != None:
				self.current.visited = True
				nextNeighbor.visited = True
				self.stack.append(self.current)
				self.path.append(self.current)

				self.RemoveWalls(self.current, nextNeighbor)

				self.current = nextNeighbor
				if self.path[-1] == self.endPoint:
					self.endReached = True
					self.path.append(self.endPoint)

				if self.endReached:
					self.path.pop()

			elif len(self.stack) > 0:
				self.current = self.stack.pop()

				if not self.endReached:
					self.path.pop()

			elif len(self.stack) == 0:
				self.finished = True

	def RemoveWalls(self, a, b):
		x = a.pos[0] - b.pos[0]
		if x == self.size:
			a.walls["left"] = False
			b.walls["right"] = False
		elif x == -self.size:
			a.walls["right"] = False
			b.walls["left"] = False

		y = a.pos[1] - b.pos[1]
		if y == self.size:
			a.walls["top"] = False
			b.walls["bottom"] = False
		elif y == -self.size:
			a.walls["bottom"] = False
			b.walls["top"] = False


