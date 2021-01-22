from graphics import ImageFactory, SpriteSheet
from pygame import Surface, SRCALPHA


class FontImageFactory(ImageFactory):
    FILENAME = "resources/sprites/verifier_font_8x8.png"

    def __init__(self):
        self.sheet = SpriteSheet(self.FILENAME)
        self.images = []
        self.__create()

    def __create(self) -> None:
        width = 8
        height = 8
        for x in range(59):
            self.images.append(
                self.sheet.get_image(
                    x * width,
                    0,
                    width,
                    height
                )
            )

    def get_image(self, index: int) -> Surface:
        return self.images[index]


class FontFactory(object):
    def __init__(self):
        self.__factory = FontImageFactory()
        self.__nums = {
            '0': 16,
            '1': 17,
            '2': 18,
            '3': 19,
            '4': 20,
            '5': 21,
            '6': 22,
            '7': 23,
            '8': 24,
            '9': 25
        }

    def get_number(self, num: int) -> Surface:
        self.__image = Surface([64, 8], SRCALPHA).convert_alpha()
        word = str(num)
        word = word.zfill(8)
        chars = [char for char in word]
        for index, char in enumerate(chars):
            n = self.__nums.get(char)
            self.__image.blit(self.__factory.get_image(n), (index * 8, 0))
        return self.__image
