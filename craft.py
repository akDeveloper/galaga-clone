from pygame import Surface, Rect
from pygame.sprite import Sprite, Group
from graphics import ImageFactory, SpriteSheet
from controls import UserInput, State, Direction, Buttons
from actions import Action, Transition
from pygame.math import Vector2
from typing import Optional
from itertools import cycle


def actions() -> dict:
    return {
        "fly": {
            "cls1": [
                (0, 0, 16, 15)
            ],
            "attack": [],
            "frames": [
                {"index": 2, "delay": 4},
                {"index": 7, "delay": 4},
            ],
            "loop": True,
            "wait": False
        },
        "left": {
            "cls1": [
                (0, 0, 16, 15)
            ],
            "attack": [],
            "frames": [
                {"index": 1, "delay": 4},
                {"index": 6, "delay": 4},
                {"index": 0, "delay": 4},
                {"index": 5, "delay": 4},
            ],
            "loop": True,
            "loop_index": 2,
            "wait": False
        },
        "left-restore": {
            "cls1": [
                (0, 0, 16, 15)
            ],
            "attack": [],
            "frames": [
                {"index": 1, "delay": 4},
                {"index": 6, "delay": 4},
            ],
            "loop": False,
            "wait": True
        },
        "right": {
            "cls1": [
                (0, 0, 16, 15)
            ],
            "attack": [],
            "frames": [
                {"index": 3, "delay": 4},
                {"index": 8, "delay": 4},
                {"index": 4, "delay": 4},
                {"index": 9, "delay": 4},
            ],
            "loop": True,
            "loop_index": 2,
            "wait": False
        },
        "right-restore": {
            "cls1": [
                (0, 0, 16, 15)
            ],
            "attack": [],
            "frames": [
                {"index": 3, "delay": 2},
                {"index": 8, "delay": 2},
            ],
            "loop": False,
            "wait": True
        },
        "dead": {
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


class CraftState(object):
    FLY = 'fly'
    LEFT = 'left'
    RIGHT = 'right'
    LEFT_RESTORE = 'left-restore'
    RIGHT_RESTORE = 'right-restore'
    DEAD = 'dead'
    ATTACK1 = 'attack1'

    def get_speed(self) -> int:
        return 2

    def get_transitions(self) -> dict:
        return {
            self.FLY: [self.LEFT, self.RIGHT, self.DEAD],
            self.RIGHT: [self.RIGHT_RESTORE, self.DEAD],
            self.LEFT: [self.LEFT_RESTORE, self.DEAD],
            self.LEFT_RESTORE: [self.FLY],
            self.RIGHT_RESTORE: [self.FLY]
        }

    def to(self, current: str, new: str, action: Action) -> str:
        transitions = self.get_transitions()
        if current in transitions:
            if new in transitions[current]:
                if action.can_interrupt(new):
                    return new
                elif action.is_completed():
                    return new
            if new is CraftState.FLY and current in [CraftState.LEFT, CraftState.RIGHT]:
                if current is CraftState.LEFT:
                    return CraftState.LEFT_RESTORE
                else:
                    return CraftState.RIGHT_RESTORE
            if new in [CraftState.RIGHT, CraftState.LEFT] and \
                    current in [CraftState.LEFT_RESTORE, CraftState.RIGHT_RESTORE]:
                return CraftState.FLY
            if new is CraftState.LEFT and current is CraftState.RIGHT:
                return CraftState.RIGHT_RESTORE
            if new is CraftState.RIGHT and current is CraftState.LEFT:
                return CraftState.LEFT_RESTORE
        return current


class CraftImageFactory(ImageFactory):
    FILENAME = "resources/sprites/ship.png"

    def __init__(self):
        self.sheet = SpriteSheet(self.FILENAME)
        self.images = []
        self.create()

    def create(self) -> None:
        width = 16
        height = 24
        for y in range(2):
            for x in range(5):
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


class BoltImageFactory(ImageFactory):
    FILENAME = "resources/sprites/laser-bolts.png"

    def __init__(self):
        self.sheet = SpriteSheet(self.FILENAME)
        self.images = []
        self.create()

    def create(self) -> None:
        self.images.append(self.sheet.get_image(6, 18, 5, 13))
        self.images.append(self.sheet.get_image(20, 18, 5, 13))

    def get_image(self, index: int) -> Surface:
        return self.images[index]


class Bolt(Sprite):
    def __init__(self, rect: Rect, image_factory: ImageFactory, *groups: tuple):
        super().__init__(groups)
        self.__image_factory = image_factory
        self.rect = rect
        self.__image_index = cycle([0, 1])
        self.__speed = -5

    def update(self, time: int) -> None:
        self.rect.top += self.__speed
        self.image = self.__image_factory.get_image(next(self.__image_index))
        if self.rect.top < 0:
            self.kill()


class CraftControl(object):
    def __init__(self):
        self.last_pressed = None
        self.states = {
            State.IDLE: CraftState.FLY,
            State.UPLEFT: CraftState.LEFT,
            State.UPRIGHT: CraftState.RIGHT,
            State.DOWNLEFT: CraftState.LEFT,
            State.DOWNRIGHT: CraftState.LEFT,
            State.UP: CraftState.FLY,
            State.DOWN: CraftState.FLY,
            State.LEFT: CraftState.LEFT,
            State.RIGHT: CraftState.RIGHT,
            State.X: CraftState.ATTACK1,
            State.Y: CraftState.ATTACK1,
            State.A: CraftState.ATTACK1,
            State.B: CraftState.ATTACK1
        }

    def get_action(self, input: UserInput, current: str = None) -> str:
        if current in [CraftState.DEAD]:
            return current
        motion = self.__get_motion(input.direction)
        button = self.__get_button(input.button)
        if button is None:
            return motion
        return button

    def __get_motion(self, direction: Direction) -> str:
        active = direction.get_active()
        return self.states.get(active)

    def __get_button(
            self,
            buttons: Buttons) -> Optional[str]:
        pressed = buttons.get_pressed()
        if pressed is None:
            self.last_pressed = None
            return None
        """ Check if button is releases before it is pressed again."""
        if self.__is_released(buttons, pressed):
            self.last_pressed = pressed
            return self.states.get(pressed)
        return None

    def __is_released(self, buttons: Buttons, pressed: str = None) -> bool:
        if pressed == self.last_pressed \
                and not buttons.is_released(self.last_pressed):
            return False
        return True


class Craft(Sprite):
    def __init__(self,
                 initial_pos: Rect,
                 actions: list,
                 image_factory: ImageFactory,
                 explosion_image_factory: ImageFactory,
                 *groups: tuple):
        super().__init__(groups)
        self.__state = CraftState()
        self.rect = initial_pos
        self.__image_factory = image_factory
        self.__explosion_image_factory = explosion_image_factory
        self.__control = CraftControl()
        self.__actions = actions
        self.__input: UserInput = None
        self.__action: Action = self.__actions.get(self.__state.FLY)
        self.__vel = Vector2(0, 0)
        self.__speed = self.__state.get_speed()
        self.__bolt_factory = BoltImageFactory()
        self.bolts: Group = Group()
        self.__max_bolts = 3

    def update_input(self, input: UserInput, time: int) -> None:
        self.__input = input

    def is_dead(self) -> bool:
        return self.__action.name is CraftState.DEAD and self.__action.is_completed()

    def update(self, time: int) -> None:
        if self.is_dead():
            self.kill()
        self.__vel.x = 0
        self.__vel.x = self.__input.direction.x * self.__speed
        self.rect.left += self.__vel.x
        action = self.__control.get_action(self.__input, self.__action.name)
        if action is CraftState.ATTACK1:
            self.shoot()
        action = self.__state.to(self.__action.name, action, self.__action)
        new_action: Action = self.__actions.get(action)
        self.__action = Transition(self.__action).to(new_action)
        self.__action.next()
        self.image = self.__image_factory.get_image(self.__action.frame.get_index())
        self.bolts.update(time)

    def shoot(self) -> None:
        if len(self.bolts) >= self.__max_bolts:
            return
        pos = Rect(0, 0, 5, 13)
        pos.center = self.rect.center
        bolt = Bolt(pos, self.__bolt_factory)
        self.bolts.add(bolt)

    def destroy(self) -> None:
        self.__action = self.__actions.get(CraftState.DEAD)
        self.__image_factory = self.__explosion_image_factory


def factory(expl: ImageFactory) -> Craft:
    acts: dict = {}
    rect: Rect = Rect(100, 270, 16, 24)
    for name, data in actions().items():
        acts[name] = (Action(name, data, rect))
    return Craft(rect, acts, CraftImageFactory(), expl)
