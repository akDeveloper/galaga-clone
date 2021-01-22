from __future__ import annotations
from controls import Input
from pygame import Rect, Surface, draw, mouse
from pygame.sprite import Group, groupcollide
from graphics import Graphics, ImageFactory, SpriteSheet
from tiled_parser import TiledParser
import craft
import enemies
import random
from font import FontFactory


class Game(object):
    SCREEN_WIDTH = 400
    SCREEN_HEIGHT = 300

    def __init__(self, input: Input):
        self.graphics = Graphics(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        screen_rect = Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        mouse.set_visible(0)
        self.input = input
        self.__debug = False
        self.state = PlayGameState(screen_rect)

    def update(self, time: int) -> None:
        """ Get the next state of the game """
        self.state = self.state.get_state()
        """ Update the state of sprites, level, etc """
        self.state.update(time, self.input)

    def render(self) -> None:
        self.state.render(self.graphics.get_surface())
        self.graphics.render()

    def toggle_debug(self) -> None:
        self.state.toggle_debug()


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


class GameState(object):
    def __init__(self):
        raise RuntimeError("Can not instatiate")

    def update(self, time: int, input: Input) -> None:
        raise NotImplementedError("Implement `update` method.")

    def render(self, surface: Surface) -> None:
        raise NotImplementedError("Implement `render` method.")

    def get_state(self) -> GameState:
        raise NotImplementedError("Implement `get_state` method.")


class PlayGameState(GameState):
    def __init__(self, screen: Rect):
        self.screen = screen
        self.actor = None
        self.group = Group()
        self.enemies = None
        self.background: Surface = None
        self.map = TiledParser('resources/levels/level1.json').get_map()
        self.map.set_screen(screen)
        self.limits: list = []
        for platform in self.map.get_platforms():
            self.limits.append(platform.get_rect())
        self.__stars: list = []
        self.__explosion_image_factory = ExplosionImageFactory()
        self.__respawn_counter = 0
        self.__load_background()
        self.__load_actor()
        self.__load_enemies()
        self.__font = FontFactory()

    def update(self, time: int, input: Input) -> None:
        self.__update_actor(time, input)
        self.__update_enemies(time)

    def render(self, surface: Surface) -> None:
        surface.fill((21, 21, 21))
        self.__blit_background(surface)
        self.group.draw(surface)
        self.enemies.draw(surface)
        self.actor.bolts.draw(surface)
        surface.blit(self.__font.get_number(self.actor.get_points()), (168, 0))

    def get_state(self) -> GameState:
        return self

    def toggle_debug(self) -> None:
        pass

    def __load_actor(self) -> None:
        pos = self.map.get_actor().get_items_index(0).get_rect()
        self.actor = craft.factory(self.__explosion_image_factory, pos)
        self.group.add(self.actor)

    def __load_enemies(self) -> None:
        rects: list = []
        enem = self.map.get_enemies()[0]
        for rect in enem.get_items():
            rects.append(rect.get_rect())
        self.enemies = enemies.EnemyGroup(rects, self.__explosion_image_factory)

    def __load_background(self) -> None:
        colors = [(255, 255, 255), (255, 0, 0), (0, 0, 255)]
        for x in range(200):
            random.shuffle(colors)
            self.__stars.append(
                [random.randint(self.left.w, self.right.left), random.randint(0, self.screen.h), colors[0]]
            )

    def __update_actor(self, time, input: Input) -> None:
        self.__respawn_actor(time)
        self.actor.update_input(input.get_user_input(), time)
        self.actor.update(time)
        """ Can only move within stage limits """
        for limit in self.limits:
            if limit.colliderect(self.actor.rect):
                if self.actor.get_vel().x < 0:
                    self.actor.rect.left = limit.right
                else:
                    self.actor.rect.right = limit.left
        """ Destroy enemies when collide with actor's bolts """
        [enemy.destroy(self.actor) for enemy in groupcollide(self.enemies.sprites(), self.actor.bolts, False, True)]

    def __update_enemies(self, time: int) -> None:
        self.enemies.update(time)
        self.enemies.hit_actor(self.actor)

    def __blit_background(self, surface: Surface) -> None:
        for star in self.__stars:
            draw.line(surface, star[2], (star[0], star[1]), (star[0], star[1]))
            star[1] = star[1] + 0.5
            if star[1] > self.screen.h:
                star[1] = 0
                star[0] = random.randint(self.left.w, self.right.left)

    def __respawn_actor(self, time: int) -> None:
        if self.actor.can_respawn():
            self.__respawn_counter += time
        if self.__respawn_counter > 2000:
            self.actor.respawn()
            self.group.add(self.actor)
            self.__respawn_counter = 0
