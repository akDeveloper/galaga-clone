from random import randint, uniform
from pygame.math import Vector2


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


class Behaviour(object):
    def __init__(self):
        raise RuntimeError("Can not instatiate `Behaviour`")

    def is_completed(self) -> bool:
        raise NotImplementedError("Implement `is_completed` method.")

    def next(self) -> bool:
        raise NotImplementedError("Implement `next` method.")

    def update(self, time: int) -> bool:
        raise NotImplementedError("Implement `update` method.")


class HomeBehaviour(Behaviour):
    def __init__(self, source: tuple, target: tuple):
        self.steer = EnemySteer(source)
        self.source = source
        self.target = target

    def is_completed(self) -> bool:
        return self.steer.pos == self.target

    def next(self) -> Behaviour:
        target = (randint(32, 368), 330)
        return DiveBehaviour(self.steer.pos, target, self.target)

    def update(self, time: int) -> None:
        self.steer.update(self.target)


class DiveBehaviour(Behaviour):
    def __init__(self, source: tuple, target: tuple, home: tuple):
        self.steer = EnemySteer(source)
        self.source = source
        self.target = target
        self.home = home

    def is_completed(self) -> bool:
        return self.steer.desired.length() < 0.5

    def next(self) -> Behaviour:
        return HomeBehaviour(self.steer.pos, self.home)

    def update(self, time: int) -> None:
        self.steer.update(self.target)


class EnemySteer(object):
    def __init__(self, pos: tuple):
        self.desired = None
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
