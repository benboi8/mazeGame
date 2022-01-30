from GameObjects import *

boundaries = []

drawBounds = False


class Boundary(Line):
	def __init__(self, startPos, endPos, color):
		super().__init__(startPos, endPos, color, 0, 0, True, lists=[])



class Player:
	def __init__(self, startPos, color, rayLength=100, numOfRays=20, moveSpeed=3, fov=120):
		self.color = color
		self.rayLength = rayLength
		self.numOfRays = numOfRays
		self.rays = []

		self.moveSpeed = moveSpeed
		self.direction = [False, False, False, False]
		self.colliding = {"left": False, "right": False, "up": False, "down": False}

		self.lightSource = Point(startPos[0], startPos[1], self.color, 6, lists=[])
		self.rect = pg.Rect(self.lightSource.x - self.moveSpeed * 2, self.lightSource.y - self.moveSpeed * 2, self.moveSpeed * 4, self.moveSpeed * 4)

		self.fov = fov

		self.CreateRays()

	def Draw(self, cellSize):
		for ray in self.rays:
			ray.Draw()

	def Update(self):
		self.ApplyForce(self.moveSpeed, self.direction)
		
		self.CreateRays()

		for ray in self.rays:
			ray.Update((self.lightSource.x, self.lightSource.y))
		
		self.UpdatePos((self.lightSource.x, self.lightSource.y))

	def HandleEvent(self, event):
		if event.type == pg.KEYDOWN:
			# right
			if event.key == pg.K_d:
				self.direction[0] = True
			# left
			if event.key == pg.K_a:
				self.direction[1] = True
			# up
			if event.key == pg.K_w:
				self.direction[2] = True
			# down
			if event.key == pg.K_s:
				self.direction[3] = True

		if event.type == pg.KEYUP:
			# right
			if event.key == pg.K_d:
				self.direction[0] = False
			# left
			if event.key == pg.K_a:
				self.direction[1] = False
			# up
			if event.key == pg.K_w:
				self.direction[2] = False
			# down
			if event.key == pg.K_s:
				self.direction[3] = False
	
	def ApplyForce(self, magnitude, direction):
		# right
		if direction[0]:
			if not self.colliding["right"]:
				self.lightSource.x += magnitude

		# left
		if direction[1]:
			if not self.colliding["left"]:
				self.lightSource.x -= magnitude
		
		# up 
		if direction[2]:
			if not self.colliding["up"]:
				self.lightSource.y -= magnitude
		
		# down
		if direction[3]:
			if not self.colliding["down"]:
				self.lightSource.y += magnitude

	def Collide(self, cellSize):
		self.colliding["left"] = False
		self.colliding["right"] = False
		self.colliding["up"] = False
		self.colliding["down"] = False
	
		for bound in boundaries:
			if pg.Rect(self.lightSource.x - (cellSize // 2) - 2, self.lightSource.y - (cellSize // 2) - 2, cellSize + 2, cellSize + 2).collidepoint(bound.startPos) or pg.Rect(self.lightSource.x - (cellSize // 2), self.lightSource.y - (cellSize // 2), cellSize, cellSize).collidepoint(bound.endPos):

				if bound.endPos[0] - bound.startPos[0] > bound.endPos[1] - bound.startPos[1]:
					rect = pg.Rect(bound.startPos[0], bound.startPos[1] - 3, bound.endPos[0] - bound.startPos[0], 6)
				else:
					rect = pg.Rect(bound.startPos[0] - 3, bound.startPos[1], 6, bound.endPos[1] - bound.startPos[1])

				if self.rect.colliderect(rect):
					if rect.w < rect.h:
						if self.lightSource.x >= rect.x:
							self.colliding["left"] = True

						if self.lightSource.x <= rect.x:
							self.colliding["right"] = True
					else:
						if self.lightSource.y >= rect.y:
							self.colliding["up"] = True

						if self.lightSource.y <= rect.y:
							self.colliding["down"] = True

	def UpdatePos(self, pos):
		self.lightSource.x, self.lightSource.y = pos
		self.rect = pg.Rect(self.lightSource.x - self.moveSpeed * 2, self.lightSource.y - self.moveSpeed * 2, self.moveSpeed * 4, self.moveSpeed * 4)

		for ray in self.rays:
			ray.startPos = (self.lightSource.x, self.lightSource.y)

	def CreateRays(self):
		self.rays = []
		for i in range(1, self.numOfRays + 1):
			p1 = Vec2(self.lightSource.x, self.lightSource.y)
			p2 = Vec2(self.lightSource.x + self.lightSource.radius, self.lightSource.y)
			p3 = Vec2(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])
	
			try:			
				angle = ((self.fov / self.numOfRays) * i) - (degrees(GetAngle(p1, p2, p3)) + (self.fov // 2))
			except ZeroDivisionError:
				angle = radians((self.fov / self.numOfRays) * i)
			
			self.rays.append(Ray((self.lightSource.x, self.lightSource.y), self.color, radians(angle), self.rayLength))


class Ray:
	def __init__(self, startPos, color, angle, length):
		self.startPos = startPos
		self.endPos = startPos
		self.color = color
		self.angle = angle
		self.length = length
		self.c = self.color
		self.draw = False

	def Update(self, pos):
		self.Cast(pos)
		self.Collide()

	def Cast(self, pos):
		self.startPos = pos
		self.endPos = (self.startPos[0] + (self.length * cos(self.angle)), self.startPos[1] + (self.length * sin(self.angle)))

	def Collide(self):
		self.draw = False
		self.c = self.color
		for bound in boundaries:
			x1, y1 = self.startPos
			x2, y2 = self.endPos
			
			if bound.startPos[0] > bound.endPos[0]:
				x3, y3 = bound.endPos
				x4, y4 = bound.startPos
			else:
				x3, y3 = bound.startPos
				x4, y4 = bound.endPos

			den = ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))

			if den != 0:
				t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den

				if 0 <= t <= 1:
					L1 = ((x1 + t * (x2 - x1)), (y1 + t * (y2 - y1)))

					if (L1 > (x3, y3)) and (L1 < (x4, y4)):
						self.endPos = L1
						self.draw = True
						self.c = bound.color

	def Draw(self):
		if self.draw:
			pg.draw.aaline(screen, self.c, self.startPos, self.endPos)
			pg.draw.circle(screen, self.c, self.endPos, 1)

