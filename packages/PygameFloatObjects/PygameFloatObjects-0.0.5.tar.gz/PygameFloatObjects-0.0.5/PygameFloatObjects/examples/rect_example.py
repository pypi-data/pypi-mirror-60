from PygameFloatObjects.objects import *


def resize_rect(screen, screen_size, float_rect, float_font, font_text, font_color, ratio):
    # clear screen
    screen.fill((0, 0, 0))

    # set new float rect size
    new_rect_size = (ratio * float_rect.get_float_size()[0], ratio * float_rect.get_float_size()[1])

    # set new top left point
    new_top_left_point = (screen_size[0] / 2 - new_rect_size[0] / 2, 100)

    # update float rect
    float_rect.set_float_size(new_rect_size)
    float_rect.set_float_top_left_point(new_top_left_point)
    float_rect.update()

    # draw float rect
    float_rect.draw()

    # set new float font size
    new_font_size = ratio * float_font.get_float_size()

    # update float font
    float_font.set_float_size(new_font_size)
    float_font.update()

    # create font surface
    font_surface = float_font.get_font().render(font_text, True, font_color)

    # get font surface rect
    font_surface_rect = font_surface.get_rect()

    # position surface rect
    font_surface_rect.center = (int(new_top_left_point[0] + new_rect_size[0] / 2),
                                int(new_top_left_point[1] + new_rect_size[1] / 2))

    # draw font surface
    screen.blit(font_surface, font_surface_rect)

    pygame.display.update()


def rect_example():

    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3

    # create and init display
    pygame.init()
    screen_size = (800, 800)
    screen = pygame.display.set_mode(screen_size)

    # ========== create float rect ==========

    # create float rect size
    rect_size = (600, 200)

    # create top left point
    top_left_point = (screen_size[0] / 2 - rect_size[0] / 2, 100)

    # create object
    float_rect = FloatRect(screen, (255, 0, 255), top_left_point, rect_size)

    # draw object
    float_rect.draw()

    # ========== create float font ==========

    # create initial font size
    font_size = 60

    # create font name
    font_name = "area"

    # create font content
    font_text = "L/R click on this window!"

    # create font color
    font_color = (0, 255, 255)

    # create object
    float_font = FloatFont(font_name, font_size)

    # create font surface
    font_surface = float_font.get_font().render(font_text, True, font_color)

    # get font surface rect
    font_surface_rect = font_surface.get_rect()

    # position surface rect
    font_surface_rect.center = (int(top_left_point[0] + rect_size[0] / 2), int(top_left_point[1] + rect_size[1] / 2))

    # draw font surface
    screen.blit(font_surface, font_surface_rect)

    pygame.display.update()

    loop_exit = False

    # main loop
    while not loop_exit:
        for event in pygame.event.get():

            # quit loop if quit window button is pressed
            if event.type == pygame.QUIT:
                loop_exit = True

            # verify if mouse button is pressed
            if event.type == pygame.MOUSEBUTTONDOWN:

                # verify if mouse button is the left button
                if event.button == LEFT_BUTTON:

                    # increase objects size
                    resize_rect(screen, screen_size, float_rect, float_font, font_text, font_color, 1.1)

                # verify if mouse button is the right button
                if event.button == RIGHT_BUTTON:

                    # decrease objects size
                    resize_rect(screen, screen_size, float_rect, float_font, font_text, font_color, 0.9)

    pygame.quit()


# rect_example()
