"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
import random


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )


class DemoEnemy(Enemy):
    """
    Demo enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill='red')

    def update(self) -> None:
        self.x += 1
        self.y += 1
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size,
                           self.y + self.size)

    def delete(self) -> None:
        pass


class RandomWalkEnemy(Enemy):
    """
    RandomWalkEnemy will walk randomly on the screen.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 speed = 1):
        super().__init__(game, size, color)
        self.__id = None
        self.__stateX = self.moving_right
        self.__stateY = self.moving_down
        self.__speed = speed

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill='cyan')

    def update(self) -> None:
        self.__stateX()
        self.__stateY()
        if self.hits_player():
            self.game.game_over_lose()

    def moving_right(self):
        self.x += 5 * self.__speed
        if self.x > self.canvas.winfo_width():
            self.__stateX = self.moving_left

    def moving_left(self):
        self.x += -5 * self.__speed
        if self.x < 0:
            self.__stateX = self.moving_right

    def moving_up(self):
        self.y += 5 * self.__speed
        if self.y > self.canvas.winfo_height():
            self.__stateY = self.moving_down

    def moving_down(self):
        self.y += -5 * self.__speed
        if self.y < 0:
            self.__stateY = self.moving_up

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        pass


class ChasingEnemy(Enemy):
    """
    ChasingEnemy will try chasing the player.
    Try not to move this enemy too fast, otherwise the player will have no chance to win.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 speed=1.0):
        super().__init__(game, size, color)
        self.__id = None
        self.__speed = speed

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill='red')

    def update(self) -> None:
        if self.x > self.game.player.x:
            self.x += -2 * self.__speed
        if self.x < self.game.player.x:
            self.x += 2 * self.__speed
        if self.y > self.game.player.y:
            self.y += -2 * self.__speed
        if self.y < self.game.player.y:
            self.y += 2 * self.__speed
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        pass


class FencingEnemy(Enemy):
    """
    FencingEnemy will walk around the home in a square-like pattern.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill='black')

    def update(self) -> None:
        size = self.game.home.size
        if self.x >= self.game.home.x - (size/2) - 8 and self.y == self.game.home.y + (size/2) + 3:
            self.x += -2
        if self.x == self.game.home.x - (size/2) - 7 and self.y >= self.game.home.y - (size/2) - 8:
            self.y += -2
        if self.x <= self.game.home.x + (size/2) + 4 and self.y == self.game.home.y - (size/2) - 7:
            self.x += 2
        if self.x == self.game.home.x + (size/2) + 3 and self.y <= self.game.home.y + (size/2) + 3:
            self.y += 2
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size,
                           self.y + self.size)

    def delete(self) -> None:
        pass


class CrossShooterEnemy(Enemy):
    """
        FencingEnemy will walk around the home in a square-like pattern.
        """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 speed=0.5):
        super().__init__(game, size, color)
        self.__id = None
        self.__stateX = self.moving_right
        self.__stateY = self.moving_down
        self.__speed = speed
        # self.__shooting = self.shooting
        # print('here')

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill='yellow')

    def update(self) -> None:
        self.__stateX()
        self.__stateY()
        # self.__shooting()
        if self.hits_player():
            self.game.game_over_lose()

    def moving_right(self):
        self.x += 1 * self.__speed
        if self.x > self.canvas.winfo_width():
            self.__stateX = self.moving_left

    def moving_left(self):
        self.x += -1 * self.__speed
        if self.x < 0:
            self.__stateX = self.moving_right

    def moving_up(self):
        self.y += 1 * self.__speed
        if self.y > self.canvas.winfo_height():
            self.__stateY = self.moving_down

    def moving_down(self):
        self.y += -1 * self.__speed
        if self.y < 0:
            self.__stateY = self.moving_up

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        pass


class Bullet(Enemy):
    """
    CrossShooter Bullets
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 direction=(1, 0)):
        super().__init__(game, size, color)
        self.__id = None
        self.__direction = direction

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill='black')

    def update(self) -> None:
        self.x += self.__direction[0] * 3
        self.y += self.__direction[1] * 3
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def delete(self) -> None:
        pass


class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """
    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level

        self.__game.after(100, self.create_enemy)
        self.__game.after(200, self.create_chasing_enemy)
        self.__game.after(100, self.create_fencing_enemy)
        self.__game.after(300, self.create_shooter_enemy)
        self.__game.after(1000, self.level_increment)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAdvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def level_increment(self):
        self.__level += 0.1
        self.__game.after(5000, self.level_increment)

    def create_enemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        new_enemy = RandomWalkEnemy(self.__game, 20, "cyan", self.__level)
        new_enemy.x = random.randrange(0, self.game.canvas.winfo_width())
        new_enemy.y = random.randrange(0, self.game.canvas.winfo_height())
        self.game.add_element(new_enemy)

        self.__game.after(2000, self.create_enemy)

    def create_chasing_enemy(self) -> None:
        new_enemy = ChasingEnemy(self.__game, 20, "red", 0.5 + self.__level/2)
        new_enemy.x = random.randrange(0, self.game.canvas.winfo_width())
        new_enemy.y = random.randrange(0, self.game.canvas.winfo_height())
        self.game.add_element(new_enemy)

        self.__game.after(4000, self.create_chasing_enemy)

    def create_fencing_enemy(self) -> None:
        new_enemy = FencingEnemy(self.__game, 6, "black")
        new_enemy.x = self.game.home.x + (self.game.home.size / 2) + 3
        new_enemy.y = self.game.home.y + (self.game.home.size / 2) + 3
        self.game.add_element(new_enemy)

        self.__game.after(6000, self.create_fencing_enemy)

    def create_shooter_enemy(self) -> None:
        new_enemy = CrossShooterEnemy(self.__game, 30, "yellow")
        new_enemy.x = random.randrange(0, self.game.canvas.winfo_width())
        new_enemy.y = random.randrange(0, self.game.canvas.winfo_height())
        self.game.add_element(new_enemy)
        self.__game.after(100, self.create_bullet, new_enemy)
        self.__game.after(5000, self.create_shooter_enemy)

    def create_bullet(self, target):
        bullet = Bullet(self.__game, 7, "black", (0, -1))
        bullet.x = target.x
        bullet.y = target.y - target.size/2
        self.game.add_element(bullet)

        bullet2 = Bullet(self.__game, 7, "black", (0, 1))
        bullet2.x = target.x
        bullet2.y = target.y + target.size/2
        self.game.add_element(bullet2)

        bullet3 = Bullet(self.__game, 7, "black", (-1, 0))
        bullet3.x = target.x - target.size/2
        bullet3.y = target.y
        self.game.add_element(bullet3)

        bullet4 = Bullet(self.__game, 7, "black", (1, 0))
        bullet4.x = target.x + target.size/2
        bullet4.y = target.y
        self.game.add_element(bullet4)

        self.__game.after(1000, self.create_bullet, target)


class TurtleAdventureGame(Game):  # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
