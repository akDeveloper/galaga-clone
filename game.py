from __future__ import annotations
from controls import Input
from pygame import Rect, Surface, draw, mouse
from pygame.sprite import Group, groupcollide
from graphics import Graphics
import craft
import enemies
import random


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
        self.enemies = Group()
        self.background: Surface = None
        self.left = Rect(0, 0, 32, self.screen.h)
        self.right = Rect(368, 0, 32, self.screen.h)
        self.__stars: list = []
        self.__load_background()
        self.__load_actor()
        self.__load_enemies()

    def update(self, time: int, input: Input) -> None:
        self.__update_actor(time, input)
        self.__update_enemies(time)

    def render(self, surface: Surface) -> None:
        surface.fill((21, 21, 21))
        self.__blit_background(surface)
        self.group.draw(surface)
        self.enemies.draw(surface)
        self.actor.bolts.draw(surface)

    def get_state(self) -> GameState:
        return self

    def toggle_debug(self) -> None:
        pass

    def __load_actor(self) -> None:
        self.actor = craft.factory()
        self.group.add(self.actor)

    def __load_enemies(self) -> None:
        # self.enemies.add(enemies.enemy_factory())
        enemies.generate(10, self.enemies)

    def __load_background(self) -> None:
        colors = [(255, 255, 255), (255, 0, 0), (0, 0, 255)]
        for x in range(200):
            random.shuffle(colors)
            self.__stars.append(
                [random.randint(self.left.w, self.right.left), random.randint(0, self.screen.h), colors[0]]
            )

    def __update_actor(self, time, input: Input) -> None:
        self.actor.update_input(input.get_user_input(), time)
        self.actor.update(time)
        if self.left.colliderect(self.actor.rect):
            self.actor.rect.left = self.left.right
        elif self.right.colliderect(self.actor.rect):
            self.actor.rect.right = self.right.left
        [enemy.destroy() for enemy in groupcollide(self.enemies, self.actor.bolts, False, True)]

    def __update_enemies(self, time: int) -> None:
        self.enemies.update(time)

    def __blit_background(self, surface: Surface) -> None:
        for star in self.__stars:
            draw.line(surface, star[2], (star[0], star[1]), (star[0], star[1]))
            star[1] = star[1] + 0.5
            if star[1] > self.screen.h:
                star[1] = 0
                star[0] = random.randint(self.left.w, self.right.left)
