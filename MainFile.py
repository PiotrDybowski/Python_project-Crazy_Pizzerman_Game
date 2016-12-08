from livewires import games, color
import random
import pygame
import sqlite3
import tkinter

games.init(screen_width=1280, screen_height=720, fps=50)  # tworzenie okna

catchPizzaSound = games.load_sound("sounds\catch.wav")
backgroundSound = games.load_sound("sounds\\main_music.wav")
nextLevelSound = games.load_sound("sounds\\next_lvl.wav")
scoreDB = 0

ifEnd = False
moveX = 2000
ifUpdate1 = True
ifUpdate2 = True
ifUpdate3 = True

ifNextLevel = False
timerNextLevelMod10 = 1
ifLevelMod10 = False
live_counter = 3

Nick = False
displayDatabase = False

class DataBase():

    def createTable(self,score):

        self.connection = sqlite3.connect('game_database.db')
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS player (nick varchar(250) NOT NULL,score INTEGER)""")

        self.players = []
        self.players.append((self.n,score))


        self.cursor.executemany('INSERT INTO player VALUES(?,?)', self.players)
        self.connection.commit()

    def readData(self):
        self.playerList = []
        self.scoreList = []
        self.cursor.execute(
            """
            SELECT nick, score FROM player ORDER BY score DESC
            """)
        self.players = self.cursor.fetchall()
        for gracz in self.players:
            self.playerList.append(str(gracz['nick']))
            self.scoreList.append(str(gracz['score']))
            if len(self.playerList) == 6:
                self.playerList.pop()
                self.scoreList.pop()
                self.players.pop()
        return (self.playerList,self.scoreList)




    def writeDataUser(self):
        self.main = tkinter.Tk()
        self.main.resizable(width=False,height=False)
        self.main.title("Nick")
        self.infoName = tkinter.Label(self.main,text="Podaj swoj nick")
        self.infoName.grid(row = 0, column = 0)
        self.name = tkinter.Entry(self.main)
        self.name.grid(row = 0, column = 1)
        self.buttonName = tkinter.Button(self.main,text="Zapisz",command = self.getNick)
        self.buttonName.grid(row=1, column=1)
        self.main.mainloop()


    def getNick(self):
        self.n = self.name.get()
        self.main.destroy()

class Lives(games.Sprite):
    RED = 1
    BLACK = 2
    heart_color = {RED: games.load_image("image\\live.png"),
                   BLACK: games.load_image("image\\no-live.png")}

    def __init__(self, x, y, color):

        super(Lives, self).__init__(
            image=Lives.heart_color[color],
            x=x,
            y=y)

    def update(self):
        global ifUpdate1
        global ifUpdate2
        global ifUpdate3
        global live_counter
        if ifUpdate1 == True:
            if live_counter == 2:
                self.live3 = Lives(x=100, y=700, color=2)
                games.screen.add(self.live3)
                self.live3.is_collideable = False
                ifUpdate1 = False
        if ifUpdate2 == True:
            if live_counter == 1:
                self.live2 = Lives(x=60, y=700, color=2)
                games.screen.add(self.live2)
                self.live2.is_collideable = False
                ifUpdate2 = False
        if ifUpdate3 == True:
            if live_counter == 0:
                self.live1 = Lives(x=20, y=700, color=2)
                games.screen.add(self.live1)
                self.live1.is_collideable = False
                ifUpdate3 = False

database = DataBase()

class Pizza(games.Sprite):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    GOLD = 4

    images = {SMALL: games.load_image("image\pizza_small.bmp"),
              MEDIUM: games.load_image("image\pizza_medium.bmp"),
              LARGE: games.load_image("image\pizza_large.bmp"),
              GOLD: games.load_image("image\pizza_gold.bmp")
              }

    SPEED = 2

    def __init__(self, x, y, size):


        super(Pizza, self).__init__(
            image=Pizza.images[size],
            x=x,
            y=y,
            dy=Pizza.SPEED)

        self.size = size

    def update(self):
        global ifEnd
        global live_counter

        if ifEnd == True:
            self.dy = 1000
        else:
            self.dy = Pizza.SPEED

        if (self.top > games.screen.height):
            if live_counter - 1 > 0:
                live_counter -= 1
                print(live_counter)
                self.destroy()

            elif live_counter == -1:
                games.screen.clear()
                live_counter = -2

            elif live_counter == -2:

                statImg = LevelStat(image=LevelStat.playerImg, x=300, y=100)
                games.screen.add(statImg)
                scoreImg = LevelStat(image=LevelStat.scoreImg, x=1000, y=100)
                games.screen.add(scoreImg)
                self.end_message()
            else:
                self.destroy()
                live_counter = 0
                self.end_game()
                live_counter = -1

    def destroy_if_catch(self):
        self.destroy()

    def end_message(self):

        global Nick
        if Nick == False:
            global scoreDB
            database.writeDataUser()
            database.createTable(scoreDB)
            Nick = True



        global displayDatabase
        if displayDatabase == False:

            listaP = database.readData()
            strGr = ""
            a = 0
            b = 0
            for i in listaP[0]:
                a += 100
                strGr = str(i)
                m = games.Text(value=strGr, size=100, color=pygame.Color(10,0,229), x=300,
                               y=150 + a)
                games.screen.add(m)

            for i in listaP[1]:
                b += 100
                strGr = str(i)
                m = games.Text(value=strGr, size=100, color=pygame.Color(10,0,229), x = 1000,
                               y=150 + b)
                games.screen.add(m)






    def end_game(self):
        global ifEnd
        ifEnd = True


class LevelStat(games.Sprite):
    playerImg = games.load_image("image\Player.gif")
    scoreImg = games.load_image("image\Score.gif")

class Bowl(games.Sprite):
    image = games.load_image("image\\bowl.bmp")
    pizza_catch = 1
    counter_time = 0

    def __init__(self):
        super(Bowl, self).__init__(image=Bowl.image, x=games.mouse.x, bottom=games.screen.height)
        self.score = games.Text(value=0, size=90, color=color.dark_red, top=5, right=games.screen.width - 10)
        games.screen.add(self.score)
        self.levelText = games.Text(value="Level: ", size=90, color=color.dark_red, top=5, left=10)
        games.screen.add(self.levelText)
        self.levelDisplay = games.Text(value=1, size=90, color=color.dark_red, top=5, left = 200)
        games.screen.add(self.levelDisplay)

    def update(self):
        global ifEnd

        self.x = games.mouse.x

        if self.left < 0:
            self.left = 0

        if self.right > games.screen.width:
            self.right = games.screen.width

        self.check_catch()

    def check_catch(self):
        global ifNextLevel
        global timerNextLevelMod10
        self.counter_time += 1
        if self.counter_time == 750: #minuta = 3000
            self.levelDisplay.value +=1
            Pizza.SPEED +=0.5
            timerNextLevelMod10 +=1
            self.counter_time = 0
            nextLevelSound.play()
            ifNextLevel = True

        for pizza in self.overlapping_sprites:

            global ifEnd

            if ifEnd == True:
                self.score.value +=0
                self.levelDisplay.value +=0

            else:
                if pizza.size == Pizza.SMALL:
                    catchPizzaSound.play()
                    self.pizza_catch += 1
                    self.score.value += 1
                    self.score.right = games.screen.width - 10
                    pizza.destroy_if_catch()
                elif pizza.size == Pizza.MEDIUM:
                    catchPizzaSound.play()
                    self.pizza_catch += 1
                    self.score.value += 5
                    self.score.right = games.screen.width - 10
                    pizza.destroy_if_catch()
                elif pizza.size == Pizza.LARGE:
                    catchPizzaSound.play()
                    self.pizza_catch += 1
                    self.score.value += 10
                    self.score.right = games.screen.width - 10
                    pizza.destroy_if_catch()
                elif pizza.size == Pizza.GOLD:
                    catchPizzaSound.play()
                    self.pizza_catch += 1
                    self.score.value += 100
                    self.score.right = games.screen.width - 10
                    pizza.destroy_if_catch()


                global scoreDB
                scoreDB = self.score.value

class Chef(games.Sprite):
    image = games.load_image("image\kucharz.bmp")
    chefSpeed = 9
    heightNoPizza = 1
    def __init__(self, y=100,odds_change=200):
        super(Chef, self).__init__(image=Chef.image, x=games.screen.width / 2, y=y, dx=Chef.chefSpeed)
        self.odds_change = odds_change
        self.time_till_drop = 0

    def update(self):
        global ifLevelMod10
        global timerNextLevelMod10
        if self.left < 0 or self.right > games.screen.width:
            self.dx = -self.dx
        elif random.randrange(self.odds_change) == 0:  # szansa na zmianę kierunku
            self.dx = -self.dx

        if ifLevelMod10 == True:
            ifLevelMod10 = False
            self.nextChef = Chef()
            games.screen.add(self.nextChef)
            Pizza.SPEED = 2


        if  timerNextLevelMod10 == 10:
            ifLevelMod10 = True
            timerNextLevelMod10 = 1
            Chef.heightNoPizza = 2

        self.check_drop()

    def check_drop(self):
        if self.time_till_drop > 0:
            self.time_till_drop -= 1
        else:
            random_value = random.randrange(300)
            if random_value == 0:
                size = Pizza.GOLD
            elif random_value > 0 and random_value <= 200:
                size = Pizza.SMALL
            elif random_value > 200 and random_value <= 275:
                size = Pizza.MEDIUM
            elif random_value > 275 and random_value <= 290:
                size = Pizza.LARGE

            else:
                size = random.choice([Pizza.SMALL, Pizza.MEDIUM, Pizza.LARGE])
            global ifEnd
            global moveX
            if ifEnd == True:
                new_pizza = Pizza(x=self.x + moveX, y=self.y, size=size)
            else:
                new_pizza = Pizza(x=self.x, y=self.y, size=size)

            games.screen.add(new_pizza)

            self.time_till_drop = int(new_pizza.height * 1.6 * Chef.heightNoPizza / Pizza.SPEED)

class Game(object):

    global live_counter

    def __init__(self):
        self.bowl = Bowl()
        games.screen.add(self.bowl)
        self.chef = Chef()
        games.screen.add(self.chef)

        self.live1 = Lives(x=20, y=700, color=1)
        games.screen.add(self.live1)
        self.live1.is_collideable = False

        self.live2 = Lives(x=60, y=700, color=1)
        games.screen.add(self.live2)
        self.live2.is_collideable = False

        self.live3 = Lives(x=100, y=700, color=1)
        games.screen.add(self.live3)
        self.live3.is_collideable = False

    def play(self):

        backgroundImg = games.load_image("image\wall.jpg")
        games.screen.background = backgroundImg
        backgroundSound.play(-1)
        games.mouse.is_visible = False

        # games.screen.event_grab = True
        games.screen.mainloop()


def startWall():
    pygame.display.set_caption("Crazy Pizzerman")
    startImg = games.load_image("image\\startWall.jpg")
    games.screen.background = startImg
    pygame.time.wait(4000)
    games.screen.remove(startImg)

startWall()
theGame = Game()
theGame.play()


