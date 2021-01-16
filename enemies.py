from graphics import ImageFactory, SpriteSheet
from pygame.sprite import Sprite, Group
from pygame.math import Vector2
from pygame.transform import flip
from pygame import Rect, Surface
from actions import Action
from enemy_behaviour import HomeBehaviour


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
        self.behaviour = HomeBehaviour((initial_pos[0], initial_pos[1]), (initial_pos[0] + 5, initial_pos[1]))

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
        self.behaviour.update(time)
        self.__vel = self.behaviour.steer.vel
        self.rect.center = self.behaviour.steer.pos
        if self.behaviour.is_completed():
            self.behaviour = self.behaviour.next()


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
