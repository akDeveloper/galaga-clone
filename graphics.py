from pygame import Surface, Rect, gfxdraw, SRCALPHA, image, HWSURFACE, DOUBLEBUF, FULLSCREEN
from pygame.sprite import Sprite
from pygame.transform import scale
from pygame.display import set_mode, update


class Graphics(object):
    def __init__(self, width: int, height: int, full: bool = False):
        self.size = (width * 2, height * 2)
        if full:
            self.screen = set_mode(self.size, HWSURFACE | DOUBLEBUF | FULLSCREEN)
        else:
            self.screen = set_mode(self.size)
        """ temp Surface for handling the small graphics """
        self.__surface = Surface((width, height))

    def get_surface(self) -> Surface:
        return self.__surface

    def render(self) -> None:
        self.__surface.convert_alpha()
        # self.screen.blit(self.__surface, (0, 0))
        """ upscale temp surface to screen """
        scale(self.__surface, self.size, self.screen)
        update()


class SpriteSheet(object):

    def __init__(self, filename):
        self.sprite_sheet = image.load(filename)

    def get_image(self, x: int, y: int, width: int, height: int) -> Surface:
        image = Surface([width, height], SRCALPHA).convert_alpha()
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return image


class ImageFactory(object):
    """
    Loads images from a Spritesheet and index them.
    Deliver the image Surface for the given index.
    """
    def __init__(self):
        raise RuntimeError("Can not instatiate")

    def get_image(self, index: int) -> Surface:
        raise NotImplementedError("Implement `get_image` method.")


class TileFactory(object):
    """
    Create a new Sprite for the given geometry.
    Assign an image to this sprite from the ImageFactory.
    """
    def __init__(self, image_factory: ImageFactory):
        self.image_factory = image_factory

    def create(self, name: int, rect: Rect) -> Sprite:
        sprite = Sprite()
        sprite.rect = rect
        sprite.image = self.image_factory.get_image(name)
        return sprite


class TileImageFactory(ImageFactory):
    COLOR = (55, 153, 50)

    def __init__(self):
        rect = Rect(0, 0, 32, 32)
        self.image = Surface(rect.size, SRCALPHA)
        gfxdraw.rectangle(self.image, self.image.get_rect(), self.COLOR)

    def get_image(self, index: int) -> Surface:
        return self.image


class MapImageFactory(ImageFactory):
    FILENAME = "resources/sprites/map.png"

    def __init__(self):
        self.sheet = SpriteSheet(self.FILENAME, (0, 0, 0))
        self.images = []
        self.__create()

    def __create(self) -> None:
        tile = 32
        y = 0
        x = 0
        for i in range(60):
            self.images.append(
                self.sheet.get_image(
                    x * tile, y * tile, tile, tile
                )
            )
            x += 1
            if x > 9:
                x = 0
                y += 1

    def get_image(self, index: int) -> Surface:
        return self.images[index - 1]


class AdventurerImageFactory(ImageFactory):
    FILENAME = "resources/sprites/adventurer.png"

    def __init__(self):
        self.sheet = SpriteSheet(self.FILENAME, (0, 0, 0))
        self.images = []
        self.create()

    def create(self) -> None:
        width = 50
        height = 37
        for y in range(15):
            for x in range(7):
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


class ActorHpImageFactory(ImageFactory):
    FILENAME = "resources/sprites/actor_hp.png"

    def __init__(self):
        self.sheet = SpriteSheet(self.FILENAME, (255, 255, 255))
        self.images = []
        self.create()

    def create(self) -> None:
        width = 18
        height = 16
        offset = 0
        for x in range(3):
            self.images.append(
                self.sheet.get_image(
                    (x * width) + offset,
                    0,
                    width,
                    height
                )
            )
            offset += 1

    def get_image(self, index: int) -> Surface:
        return self.images[index]


class Tile(Sprite):
    COLOR = (55, 153, 50)

    def __init__(self, name: int, rect: Rect, color: tuple, *groups):
        super().__init__(*groups)
        self.name = name
        self.image = Surface(rect.size, SRCALPHA)
        gfxdraw.rectangle(self.image, self.image.get_rect(), color)
        self.rect = self.image.get_rect(topleft=rect.topleft)


class KnightImageFactory(ImageFactory):
    FILENAME = "resources/sprites/knight.png"

    def __init__(self):
        self.sheet = SpriteSheet(self.FILENAME, (0, 0, 0))
        self.images = []
        self.create()

    def create(self) -> None:
        width = 100
        height = 55
        for y in range(9):
            for x in range(10):
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
