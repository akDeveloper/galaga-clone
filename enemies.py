from graphics import ImageFactory, SpriteSheet
from pygame.sprite import Sprite, Group
from pygame.math import Vector2
from random import randint, uniform
from pygame.transform import flip
from pygame import Rect, Surface
from actions import Action


def actions() -> dict:
    return {
        "fly": {
            "cls1": [
                (0, 0, 16, 16)
            ],
            "attack": [],
            "frames": [
                {"index": 0, "delay": 6},
                {"index": 1, "delay": 6},
            ],
            "loop": True,
            "wait": False
        },
        "explode": {
            "cls1": [],
            "attack": [],
            "frames": [
                {"index": 0, "delay": 6},
                {"index": 1, "delay": 6},
                {"index": 2, "delay": 6},
                {"index": 3, "delay": 6},
            ],
            "loop": False,
            "wait": False
        }
    }


def bresenham(x0, y0, x1, y1):
    """
    https://github.com/encukou/bresenham/blob/master/bresenham.py
    Yield integer coordinates on the line from (x0, y0) to (x1, y1).
    Input coordinates should be integers.
    The result will contain both the start and the end point.
    """
    dx = x1 - x0
    dy = y1 - y0

    xsign = 1 if dx > 0 else -1
    ysign = 1 if dy > 0 else -1

    dx = abs(dx)
    dy = abs(dy)

    if dx > dy:
        xx, xy, yx, yy = xsign, 0, 0, ysign
    else:
        dx, dy = dy, dx
        xx, xy, yx, yy = 0, ysign, xsign, 0

    D = 2*dy - dx
    y = 0

    for x in range(dx + 1):
        yield x0 + x*xx + y*yx, y0 + x*xy + y*yy
        if D >= 0:
            y += 1
            D -= 2*dx
        D += 2*dy


class ExplosionImageFactory(ImageFactory):
    FILENAME = "resources/sprites/explosion.png"

    def __init__(self):
        self.sheet = SpriteSheet(self.FILENAME)
        self.images = []
        self.create()

    def create(self) -> None:
        width = 16
        height = 16
        for y in range(1):
            for x in range(4):
                self.images.append(
                    self.sheet.get_image(
                        x * width,
                        y * height,
                        width,
                        height
                    )
                )

    def get_image(self, index: int) -> Surface:
        return self.images[index]


class EnemyImageFactory(ImageFactory):
    FILENAME = "resources/sprites/enemy-small.png"

    def __init__(self):
        self.sheet = SpriteSheet(self.FILENAME)
        self.images = []
        self.create()

    def create(self) -> None:
        width = 16
        height = 16
        for y in range(1):
            for x in range(2):
                self.images.append(
                    self.sheet.get_image(
                        x * width,
                        y * height,
                        width,
                        height
                    )
                )

    def get_image(self, index: int) -> Surface:
        return self.images[index]


class EnemySteer(object):
    def __init__(self, pos: tuple):
        self.max_speed = 3
        self.max_force = 0.1
        self.approach_radius = 30
        self.pos = Vector2(pos[0], pos[1])
        self.vel = Vector2(self.max_speed, 0).rotate(uniform(0, 360))
        self.acc = Vector2(0, 0)
        self.dist = 0

    def seek_with_approach(self, target: tuple):
        self.desired = (target - self.pos)
        dist = self.desired.length()
        self.desired.normalize_ip()
        if dist < self.approach_radius:
            self.desired *= dist / self.approach_radius * self.max_speed
        else:
            self.desired *= self.max_speed
        steer = (self.desired - self.vel)
        if steer.length() > self.max_force:
            steer.scale_to_length(self.max_force)
        self.dist = dist
        return steer

    def update(self, target: tuple):
        self.acc = self.seek_with_approach(target)
        # equations of motion
        self.vel += self.acc
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        self.pos += self.vel
        """
        if self.pos.x > 400:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = 400
        if self.pos.y > 300:
            self.pos.y = 0
        if self.pos.y < 0:
            self.pos.y = 300
        """


class Enemy(Sprite):
    FLY = 'fly'
    EXPLODE = 'explode'

    def __init__(self,
                 initial_pos: Rect,
                 actions: list,
                 image_factory: ImageFactory,
                 explosion_image_factory: ImageFactory,
                 *groups: tuple):
        super().__init__(groups)
        self.__actions = actions
        self.__image_factory = image_factory
        self.__explosion_image_factory = explosion_image_factory
        self.initial = (initial_pos.left, initial_pos.top)
        self.rect = initial_pos
        self.__action: Action = self.__actions.get(self.FLY)
        self.__vel: Vector2 = Vector2(0, 0)
        self.steer = EnemySteer(initial_pos.center)
        self.dive_time = 1000
        self.dive_counter = 0
        self.steer_target = self.initial
        self.is_diving = False

    def update(self, time: int) -> None:
        self.__move(time)
        if self.__action.name is self.EXPLODE and self.__action.is_completed():
            self.kill()
        self.__action.next()
        self.image = self.__image_factory.get_image(self.__action.frame.get_index())
        if self.__vel.y < 0:
            self.image = flip(self.image, False, True)

    def destroy(self) -> None:
        self.__action = self.__actions.get(self.EXPLODE)
        self.__image_factory = self.__explosion_image_factory

    def __move(self, time: int) -> None:
        if self.__action.name is self.EXPLODE:
            return
        self.steer.update(self.steer_target)
        self.__vel = self.steer.vel
        self.rect.center = self.steer.pos
        self.dive_counter += time
        if self.steer.pos == self.initial and self.is_diving is True:
            self.dive_counter = 0
            self.is_diving = False
        if self.dive_counter > self.dive_time and self.is_diving is False:
            self.is_diving = True
            self.steer_target = (randint(32, 368), 200)
        if self.steer.pos == self.steer_target and self.steer_target != self.initial and self.is_diving is True:
            self.steer_target = self.initial


def enemy_factory(rect: Rect = None) -> Enemy:
    rect: Rect = Rect(100, 50, 16, 16) if rect is None else rect
    acts: dict = {}
    for name, data in actions().items():
        acts[name] = (Action(name, data, rect))
    return Enemy(rect, acts, EnemyImageFactory(), ExplosionImageFactory())


def generate(count: int, group: Group) -> None:
    for i in range(count):
        rect = Rect(64 + (i * 26), 20, 16, 16)
        group.add(enemy_factory(rect))
