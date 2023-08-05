import pygame


class FloatRect:
    def __init__(self, screen_display, color, float_top_left_point, float_size, float_width=0):
        self.__screen_display = screen_display
        self.__color = color
        self.__float_top_left_point = float_top_left_point
        self.__float_size = float_size
        self.__float_width = float_width

        # top left point
        self.__round_top_left_point = self.__calculate_round_top_left_point()

        # down left point
        self.__round_down_left_point = self.__calculate_round_down_left_point()

        # top right point
        self.__round_top_right_point = self.__calculate_round_top_right_point()

        # down right point
        self.__round_down_right_point = self.__calculate_round_down_right_point()

    def __calculate_round_top_left_point(self):
        return round(self.__float_top_left_point[0]), \
               round(self.__float_top_left_point[1])

    def __calculate_round_down_left_point(self):
        return round(self.__float_top_left_point[0]), \
               round(self.__float_top_left_point[1] + self.__float_size[1])

    def __calculate_round_top_right_point(self):
        return round(self.__float_top_left_point[0] + self.__float_size[0]), \
               round(self.__float_top_left_point[1])

    def __calculate_round_down_right_point(self):
        return round(self.__float_top_left_point[0] + self.__float_size[0]), \
               round(self.__float_top_left_point[1] + self.__float_size[1])

    def get_float_top_left_point(self):
        return self.__float_top_left_point

    def get_float_size(self):
        return self.__float_size

    def get_float_width(self):
        return self.__float_width

    def set_float_top_left_point(self, new_float_top_left_point):
        self.__float_top_left_point = new_float_top_left_point

    def set_float_size(self, new_float_size):
        self.__float_size = new_float_size

    def set_float_width(self, new_float_width):
        self.__float_width = new_float_width

    def update(self):

        # top left point
        self.__round_top_left_point = self.__calculate_round_top_left_point()

        # down left point
        self.__round_down_left_point = self.__calculate_round_down_left_point()

        # top right point
        self.__round_top_right_point = self.__calculate_round_top_right_point()

        # down right point
        self.__round_down_right_point = self.__calculate_round_down_right_point()

    def draw(self):
        pygame.draw.polygon(self.__screen_display, self.__color,
                            [self.__round_top_left_point,
                             self.__round_down_left_point,
                             self.__round_down_right_point,
                             self.__round_top_right_point], round(self.__float_width))


class FloatCircle:
    def __init__(self, screen, color, float_center, float_radius, width=0):
        self.__screen = screen
        self.__color = color
        self.__float_center = float_center
        self.__float_radius = float_radius
        self.__float_width = width

    def get_float_center(self):
        return self.__float_center

    def get_float_radius(self):
        return self.__float_radius

    def get_float_width(self):
        return self.__float_width

    def set_float_center(self, new_float_center):
        self.__float_center = new_float_center

    def set_float_radius(self, new_float_radius):
        self.__float_radius = new_float_radius

    def set_float_width(self, new_float_width):
        self.__float_width = new_float_width

    def draw(self):
        pygame.draw.circle(self.__screen, self.__color, (int(self.__float_center[0]), int(self.__float_center[1])), int(self.__float_radius), int(self.__float_width))


class FloatFont:
    def __init__(self, name, size, bold=False, italic=False):
        self.__name = name
        self.__size = size
        self.__float_size = size
        self.__bold = bold
        self.__italic = italic
        self.__font = pygame.font.SysFont(self.__name, self.__size, self.__bold, self.__italic)

    def get_name(self):
        return self.__name

    def get_size(self):
        return self.__size

    def get_float_size(self):
        return self.__float_size

    def get_bold(self):
        return self.__bold

    def get_italic(self):
        return self.__italic

    def get_font(self):
        return self.__font

    def set_name(self, name):
        self.__name = name

    def set_size(self, size):
        self.__size = size

    def set_float_size(self, new_float_size):
        self.__float_size = new_float_size

    def set_bold(self, bold):
        self.__bold = bold

    def set_italic(self, italic):
        self.__italic = italic

    def update(self):
        self.__size = int(self.__float_size)
        self.__font = pygame.font.SysFont(self.__name, self.__size, self.__bold, self.__italic)
