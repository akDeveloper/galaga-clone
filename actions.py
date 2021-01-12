from pygame import Rect
from enum import Enum
from typing import Optional


class CollisionType(Enum):
    CLS = 'cls'
    ATTACK = 'attack'


class CollisionItem(object):
    def __init__(self, rect: Rect, ctype: CollisionType):
        self.__rect: Rect = rect
        self.__type: CollisionType = ctype
        self.__offset: tuple = rect.topleft

    def get_type(self) -> CollisionType:
        return self.__type

    def get_rect(self) -> Rect:
        return self.__rect

    def get_offset_x(self) -> int:
        return self.__offset[0]

    def get_offset_y(self) -> int:
        return self.__offset[1]


class MoveAxis(object):
    '''
    Define the axis that allowed to move the sprite in the current frame.
    '''
    def __init__(self, x: bool = True, y: bool = True):
        self.x = x
        self.y = y


class Frame(object):
    def __init__(self, citems: list, index: int, delay: int, move: MoveAxis):
        self.__index = index
        self.__delay = delay
        self.__move = move
        self.__items = citems
        self.__cls = self.__get_item(CollisionType.CLS)
        self.__attack = self.__get_item(CollisionType.ATTACK)

    def get_index(self) -> int:
        return self.__index

    def get_delay(self) -> int:
        return self.__delay

    def get_collision_item(self) -> Optional[CollisionItem]:
        return self.__cls

    def get_attack_item(self) -> Optional[CollisionItem]:
        return self.__attack

    def get_items(self) -> list:
        return self.__items

    def allow_horizontal_move(self) -> bool:
        return self.__move.x

    def allow_vertical_move(self) -> bool:
        return self.__move.y

    def align(self, source: Rect, inverted: bool = False) -> None:
        """
        Align all collision rects of frame.
        The alignement is placed against the source rect, the Character.
        It computes the new collision position when Character sprite is
        facing the opposite side.
        """
        for cls in self.__items:
            offset_x = cls.get_offset_x()
            if inverted:
                offset_x = source.width - cls.get_rect().width - cls.get_offset_x()
            cls.get_rect().left = source.left + offset_x
            cls.get_rect().top = source.top + cls.get_offset_y()

    def receive(self, source: Rect, inverted: bool = False) -> None:
        """
        Calculate and apply the new position for the source rect.
        """
        cls: CollisionItem = self.get_collision_item()
        if cls is None:
            return
        offset_x = cls.get_offset_x()
        if inverted:
            offset_x = (source.width - cls.get_rect().width - cls.get_offset_x())
        source.left = cls.get_rect().left - offset_x
        source.top = cls.get_rect().top - cls.get_offset_y()

    def __get_item(self, ctype: CollisionType) -> Optional[CollisionItem]:
        for item in self.__items:
            if item.get_type() is ctype:
                return item
        return None


class Action(object):
    def __init__(self, name: str, data: dict, initial: Rect):
        self.name = name
        self.data = data
        self.initial = initial
        self.frames = []
        self.loop = self.data.get('loop')
        self.loop_index = self.data.get('loop_index', 0)
        self.wait = self.data.get('wait')
        self.interrupt_from = self.data.get('interrupt_from') or []
        """ Default collistion rects for action """
        self.cls = []
        """ Default attack rects for action """
        self.attack = []
        self.tick = 0
        self.index = 0
        self.completed = False
        self.__build()
        self.frame = self.frames[self.index]

    def __build(self) -> None:
        self.__build_global_collisions()
        self.__build_frames()

    def next(self) -> Frame:
        self.tick += 1
        if self.tick > self.frames[self.index].get_delay():
            self.index = self.__next_index()
            self.tick = 0
        self.frame = self.frames[self.index]
        return self.frame

    def __next_index(self) -> int:
        index = self.index + 1
        if index > len(self.frames) - 1:
            self.completed = True
            if self.loop:
                index = self.loop_index
            else:
                index = len(self.frames) - 1
        return index

    def reset(self) -> None:
        self.index = 0
        self.completed = False

    def is_completed(self) -> bool:
        return self.completed

    def can_interrupt(self, state: str) -> bool:
        if self.wait is True and self.completed is False \
                and state not in self.interrupt_from:
            return False
        return True

    def align_frames(self, source: Rect, inverted: bool = False) -> None:
        for f in self.frames:
            f.align(source, inverted)

    def __build_global_collisions(self) -> None:
        if len(self.data.get('attack')):
            self.__build_rects(self.data.get('attack'),
                               CollisionType.ATTACK,
                               self.attack)
        if len(self.data.get('cls1')):
            self.__build_rects(self.data.get('cls1'),
                               CollisionType.CLS,
                               self.cls)

    def __build_frames(self) -> None:
        for f in self.data.get('frames'):
            citems = []
            if 'cls' in f:
                self.__build_rects(f.get('cls'), CollisionType.CLS, citems)
            if len(citems) == 0:
                citems.extend(self.cls)
            if 'attack' in f:
                self.__build_rects(f.get('attack'), CollisionType.ATTACK, citems)
            if len(citems) == 0:
                citems.extend(self.attack)
            self.frames.append(
                Frame(citems, f.get('index'), f.get('delay'), self.__get_move_axis(self.data)))

    def __build_rects(self, items: list, ctype: CollisionType, appendee: list) -> None:
        for entry in items:
            appendee.append(CollisionItem(Rect(entry), ctype))

    def __get_move_axis(self, data: dict) -> MoveAxis:
        default = MoveAxis(True, True)
        if 'move_x' in data:
            default.x = data.get('move_x')
        if 'move_y' in data:
            default.x = data.get('move_y')
        return default


class Transition(object):
    def __init__(self, source: Action = None):
        self.__source = source

    def to(self, dest: Action) -> Action:
        if self.__source is None:
            return dest
        if dest is None:
            return self.__source
        if dest is not self.__source:
            if self.__source.can_interrupt(dest.name) or self.__source.is_completed():
                self.__source.reset()
                return dest
            else:
                return self.__source
        else:
            return self.__source
