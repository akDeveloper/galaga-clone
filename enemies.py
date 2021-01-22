from graphics import ImageFactory, SpriteSheet
from pygame.sprite import Sprite, Group, spritecollide
from pygame.math import Vector2
from pygame.transform import flip
from pygame import Rect, Surface
from actions import Action
from enemy_behaviour import HomeBehaviour, Behaviour, DiveBehaviour
from itertools import cycle
from random import randint


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


class EnemyBulletFactory(ImageFactory):
    FILENAME = "resources/sprites/laser-bolts.png"

    def __init__(self):
        self.sheet = SpriteSheet(self.FILENAME)
        self.images = []
        self.create()

    def create(self) -> None:
        self.images.append(self.sheet.get_image(6, 7, 5, 5))
        self.images.append(self.sheet.get_image(20, 7, 5, 5))

    def get_image(self, index: int) -> Surface:
        return self.images[index]


class EnemyBullet(Sprite):
    def __init__(self, rect: Rect, image_factory: ImageFactory, *groups: tuple):
        super().__init__(groups)
        self.__image_factory = image_factory
        self.rect = rect
        self.__image_index = cycle([0, 1])
        self.__speed = 1

    def update(self, time: int) -> None:
        self.rect.top += self.__speed
        self.image = self.__image_factory.get_image(next(self.__image_index))
        if self.rect.top > 300:
            self.kill()


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
                 bullet_factory: ImageFactory,
                 bullets_group: Group,
                 *groups: tuple):
        super().__init__(groups)
        self.points = 50
        self.__actions = actions
        self.__image_factory = image_factory
        self.__explosion_image_factory = explosion_image_factory
        self.initial = (initial_pos.left, initial_pos.top)
        self.rect = initial_pos
        self.__action: Action = self.__actions.get(self.FLY)
        self.__vel: Vector2 = Vector2(0, 0)
        self.__bullet_factory = bullet_factory
        self.bullets = bullets_group
        self.behaviour = HomeBehaviour((0, -20), (initial_pos[0], initial_pos[1]))

    def update(self, time: int) -> None:
        self.__move(time)
        if self.__action.name is self.EXPLODE and self.__action.is_completed():
            self.kill()
        self.__action.next()
        self.image = self.__image_factory.get_image(self.__action.frame.get_index())
        if self.__vel.y < 0:
            self.image = flip(self.image, False, True)

    def in_home(self) -> bool:
        return isinstance(self.behaviour, HomeBehaviour)

    def set_behaviour(self, behaviour: Behaviour) -> None:
        self.behaviour = behaviour

    def get_behaviour(self) -> Behaviour:
        return self.behaviour

    def shoot(self) -> None:
        pos = Rect(0, 0, 5, 5)
        pos.center = self.rect.center
        bullet = EnemyBullet(pos, self.__bullet_factory)
        self.bullets.add(bullet)

    def destroy(self, actor: Sprite) -> None:
        if self.__action.name == self.EXPLODE:
            return
        actor.add_points(self.points)
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


class EnemyGroup(object):
    DIVE_TIME = 4000
    SHOOT_TIME = 700

    def __init__(self, pos: list, expl: ImageFactory):
        image_factory = EnemyImageFactory()
        bullet_factory = EnemyBulletFactory()
        self.__bullet_group = Group()
        self.__enemies = Group()
        self.__shoot_counter = 0
        self.__dive_counter = 0
        for rect in pos:
            self.__enemies.add(enemy_factory(self.__bullet_group, expl, image_factory, bullet_factory, rect))

    def update(self, time: int) -> None:
        self.__enemies.update(time)
        self.__dive(time)
        self.__shoot(time)
        self.__bullet_group.update(time)

    def draw(self, surface: Surface) -> None:
        self.__enemies.draw(surface)
        self.__bullet_group.draw(surface)

    def hit_actor(self, actor: Sprite) -> None:
        if not actor.is_alive():
            return
        bullets = spritecollide(actor, self.__bullet_group, True)
        if len(bullets) > 0 and not actor.is_invincible():
            actor.destroy()

    def sprites(self) -> Group:
        return self.__enemies

    def count(self) -> int:
        return len(self.__enemies.sprites())

    def get_home_sprites(self) -> list:
        return list(filter(lambda e: e.in_home() is True, self.__enemies.sprites()))

    def get_dive_sprites(self) -> list:
        return list(filter(lambda e: e.in_home() is False, self.__enemies.sprites()))

    def __dive(self, time: int) -> None:
        if len(self.get_home_sprites()) == 0:
            return
        self.__dive_counter += time
        if self.__dive_counter > self.DIVE_TIME:
            self.__dive_counter = 0
            indexes = [randint(0, len(self.get_home_sprites()) - 1) for i in range(2)]
            for i, enemy in enumerate(self.get_home_sprites()):
                if i in indexes:
                    b = enemy.get_behaviour()
                    target = (randint(32, 368), 330)
                    n = DiveBehaviour(b.steer.pos, target, enemy.initial)
                    enemy.set_behaviour(n)

    def __shoot(self, time: int) -> None:
        if len(self.get_dive_sprites()) == 0:
            return
        self.__shoot_counter += time
        if self.__shoot_counter > self.SHOOT_TIME:
            self.__shoot_counter = 0
            indexes = [randint(0, len(self.get_dive_sprites()) - 1) for i in range(4)]
            for i, enemy in enumerate(self.get_dive_sprites()):
                if i in indexes:
                    enemy.shoot()


def enemy_factory(bullet_group: Group,
                  expl: ImageFactory,
                  img: ImageFactory,
                  bullet_factory: ImageFactory,
                  rect: Rect) -> Enemy:
    acts: dict = {}
    for name, data in actions().items():
        acts[name] = (Action(name, data, rect))
    return Enemy(rect, acts, img, expl, bullet_factory, bullet_group)
