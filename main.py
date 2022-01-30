# fix boundary collisons
# fix raycast going through some walls

from GameObjects import *
ChangeScreenSize(1000, 800)

import threading
import sys

from mazeGen import *
from rayCast import *


maze = Grid((100, 150, 600, 600), mazeData={}, color=ChangeColorBrightness(white, 5)  , wallColor=white)
p = Player((maze.grid[0][0].pos[0] + cellSize // 2, maze.grid[0][0].pos[1] + cellSize // 2), lightBlue, numOfRays=200, rayLength=maze.rect.w, moveSpeed=4, fov=90)

win = False


timeScore = Label((100, 25, 600, 100), (lightBlack, darkWhite), textData={"fontSize": 64}, drawData={"roundedCorners": True, "roundness": 4})
t = Timer()

debug = False


class HighScores(Label):
	def __init__(self, rect, colors, name="", surface=screen, drawData={}, lists=[allBoxs]):
		super().__init__(rect, colors, text="", name=name, surface=surface, drawData=drawData, textData={"alignText": "top"}, lists=lists)

		self.highScoreFile = "highscores.json"

		self.scollBar = ScollBar((self.rect.x + self.rect.w, self.rect.y + 10, 20, self.rect.h - 20), (lightBlack, darkWhite), buttonData={"activeColor": lightBlue}, scrollObj=self, drawData={"roundedCorners": True, "roundness": 5})

		self.UpdateScores()

	def SaveScore(self, time):
		data = OpenFile(self.highScoreFile)

		# improve
		try:
			for i in range(len(data[str(cellSize)])):
				ID = i + 1
		except KeyError:
			data[str(cellSize)] = {}
			ID = 0

		data[str(cellSize)][str(ID)] = {"value": f"{str(time.seconds // 3600).zfill(2)}:{str(time.seconds // 60).zfill(2)}:{str(time.seconds % 60).zfill(2)}:{str(time.microseconds).zfill(6)}", "achieved": NowFormatted()}
		
		SaveData(self.highScoreFile, data)

		self.UpdateScores()

	def UpdateScores(self):
		scores = OpenFile(self.highScoreFile)\

		def Sort(e):
			time = e["value"].split(":")
			
			return int(time[0]), int(time[1]), int(time[2]), int(time[3])

		values = []

		try:

			for key in scores[str(cellSize)]:
				value = scores[str(cellSize)][key]
				values.append(value)

			values.sort(key=Sort)
			text = ""
			for value in values:
				text += f"Achieved at:\n{value['achieved']}\n{value['value']}\n\n"
			self.UpdateText(text)

		except KeyError:
			self.UpdateText("\nNo high scores found.")


highScores = HighScores((725, 150, 250, 600), (lightBlack, darkWhite), drawData={"roundedCorners": True, "roundness": 15})


def UpdateTimer():
	try:
		while not win:
			diff = t.GetDiff()
			timeScore.UpdateText(f"{str(diff.seconds // 60).zfill(2)} : {str(diff.seconds % 60).zfill(2)} : {str(diff.microseconds).zfill(6)[0:2]}")
	except:
		pass


def CreateBounds():
	for i in range(len(boundaries)):
		boundaries.pop()	

	for j, row in enumerate(maze.grid):
		for i, cell in enumerate(row):
			x, y = cell.pos

			if cell.walls["top"]:
				boundaries.append(Boundary((x - 1, y), (x + cell.size + 2, y), cell.wallColor))
			if cell.walls["right"]:
				boundaries.append(Boundary((x + cell.size , y - 1), (x + cell.size, y + cell.size + 2), cell.wallColor))

			if j == 0:
				if cell.walls["bottom"]:
					boundaries.append(Boundary((x - 1, y + cell.size), (x + cell.size + 2, y + cell.size), cell.wallColor))
			
			if j == len(maze.grid) - 1:
				boundaries.append(Boundary((x - 1, y + cell.size), (x + cell.size + 2, y + cell.size), cell.wallColor))
			
			if i == 0:
				if cell.walls["left"]:
					boundaries.append(Boundary((x, y - 1), (x, y + cell.size + 2), cell.wallColor))


def Win():
	global win
	if not win:
		win = True
		_, _, diff = t.Stop(printResult=False)
		highScores.SaveScore(diff)
		timeScore.UpdateText(f"{str(diff.seconds // 60).zfill(2)} : {str(diff.seconds % 60).zfill(2)} : {str(diff.microseconds).zfill(6)[0:2]}")


def Restart():
	global win
	win = False
	t.Start()
	p.UpdatePos((maze.grid[0][0].pos[0] + cellSize // 2, maze.grid[0][0].pos[1] + cellSize // 2))
	maze.CreatePath()
	CreateBounds()


def DrawLoop():
	screen.fill(darkGray)

	DrawAllGUIObjects()

	maze.Draw()
	p.Draw(cellSize)
	pg.draw.rect(screen, green, (maze.startPoint.pos[0], maze.startPoint.pos[1], maze.startPoint.size, maze.startPoint.size))
	pg.draw.rect(screen, red, (maze.endPoint.pos[0], maze.endPoint.pos[1], maze.endPoint.size, maze.endPoint.size))
	p.lightSource.Draw()

	if debug:
		fpsLabel.Draw()

		for b in boundaries:
			b.Draw()

	pg.display.update()


def HandleEvents(event):
	global debug
	HandleGui(event)
	restartButton.HandleEvent(event)
	p.HandleEvent(event)

	if event.type == pg.KEYDOWN:
		if event.key == pg.K_F3:
			debug = not debug


def Update():
	p.Collide(cellSize)
	p.Update()

	if p.lightSource.x > maze.endPoint.pos[0] and p.lightSource.y > maze.endPoint.pos[1] and p.lightSource.x < maze.endPoint.pos[0] + maze.endPoint.size and p.lightSource.y < maze.endPoint.pos[1] + maze.endPoint.size:
		Win()


threading._start_new_thread(UpdateTimer, ())

restartButton = Button((725, 25, 250, 100), (lightBlack, darkWhite, lightBlue), text="RESTART", onClick=Restart, drawData={"roundedCorners": True, "roundness": 4}, textData={"fontSize": 50})

fpsLabel = Label((0, 0, 50, 25), (lightBlack, darkWhite), textData={"fontSize": 12}, lists=[])


Restart()
while running:
	clock.tick_busy_loop(fps)
	
	fpsLabel.UpdateText(str(round(clock.get_fps(), 1)))

	deltaTime = clock.get_time()
	for event in pg.event.get():
		if event.type == pg.QUIT:
			running = False
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				running = False

		HandleEvents(event)

	Update()
	
	DrawLoop()
