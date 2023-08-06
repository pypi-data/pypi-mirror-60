from PygameFloatObjects.objects import *


class TextButton:
    def __init__(self, position, size, font, screen_display, colors, width=0):
        self._float_position = position
        self._float_size = size
        self._font = font
        self._screen_display = screen_display
        self._colors = colors
        self._width = width
        self._float_width = None

        # if width bigger than 1 then float_width = width integer pixels
        if width > 1:
            self._float_width = width

        self._mouse_over_button = False

        self._mouse_location_changed = False

    def set_float_position(self, new_float_position):
        self._float_position = new_float_position

    def set_float_size(self, new_float_size):
        self._float_size = new_float_size

    def set_font_size(self, size):
        self._font.set_size(size)
        self._font.update()

    def set_font_float_size(self, new_float_size):
        self._font.set_float_size(new_float_size)
        self._font.update()

    def set_screen_display(self, new_screen):
        self._screen_display = new_screen

    def set_colors(self, new_colors):
        self._colors = new_colors

    def set_float_width(self, new_float_width):
        self._float_width = new_float_width

    # set if mouse cursor was inside or outside button area
    def set_mouse_location_changed(self, change):
        self._mouse_location_changed = change

    def get_float_position(self):
        return self._float_position

    def get_float_size(self):
        return self._float_size

    def get_font(self):
        return self._font

    def get_font_size(self):
        return self._font.get_size()

    def get_font_float_size(self):
        return self._font.get_float_size()

    def get_screen_display(self):
        return self._screen_display

    def get_colors(self):
        return self._colors

    def get_float_width(self):
        return self._float_width

    # get if mouse is over button area
    def get_mouse_over_button(self):
        return self._mouse_over_button

    # get if mouse cursor was inside or outside button area
    def get_mouse_location_changed(self):
        return self._mouse_location_changed

    # verify if current mouse cursor is over button area
    def verify_mouse_on_button(self, current_mouse_position):
        self._mouse_over_button = False
        if self._float_position[0] < current_mouse_position[0] < self._float_position[0] + self._float_size[0]:
            if self._float_position[1] < current_mouse_position[1] < self._float_position[1] + self._float_size[1]:
                self._mouse_over_button = True

    def update_float_width(self):
        self._float_width = min(self._float_size) * self._width

    def _draw_font_surface(self, text, font_color):
        # create font surface
        font_surface = self._font.get_font().render(text, True, font_color)

        # get font surface rect
        font_surface_rect = font_surface.get_rect()

        # move rect to center of button
        font_surface_rect.center = (int(self._float_position[0] + self._float_size[0] / 2),
                                    int(self._float_position[1] + self._float_size[1] / 2))

        # draw font surface
        self._screen_display.blit(font_surface, font_surface_rect)

    # draw button on screen
    def draw_button(self, text, state_colors):

        # draw button without width
        if not self._float_width:
            button_rect = FloatRect(self._screen_display, state_colors.get_button(),
                                                self._float_position, self._float_size)
            button_rect.draw()

        # draw button with width
        else:
            # draw button margin
            button_margin_rect = FloatRect(self._screen_display, state_colors.get_width(),
                                                       self._float_position, self._float_size)
            button_margin_rect.draw()

            # draw inside button
            button_rect = FloatRect(self._screen_display, state_colors.get_button(),
                                                (self._float_position[0] + round(self._float_width),
                                                 self._float_position[1] + round(self._float_width)),
                                                (self._float_size[0] - 2 * round(self._float_width),
                                                 self._float_size[1] - 2 * round(self._float_width)))
            button_rect.draw()

        self._draw_font_surface(text, state_colors.get_font())


class RedirectButton(TextButton):
    def __init__(self, font, text, pointer, colors, position=None, size=None, screen_display=None, float_width=0):

        super().__init__(position, size, font, screen_display, colors, float_width)

        self.__text = text

        # location code where button is redirecting to
        self.__pointer = pointer

        # button press state
        self.__pressed = False

    # get redirect location
    def get_next_state(self):
        return self.__pointer

    def get_pressed(self):
        return self.__pressed

    # press button
    def press(self):
        self.__pressed = True

    # release button
    def release(self):
        self.__pressed = False

    # draw button (mouse out button)
    def draw_mouse_out_button(self):
        super().draw_button(self.__text, self._colors.get_mouse_out_button_colors())

    # draw button (mouse over button)
    def draw_mouse_over_button(self):
        super().draw_button(self.__text, self._colors.get_mouse_over_button_colors())


class StatesButton(TextButton):
    def __init__(self, font, states_text_list, colors, position=None, size=None, screen_display=None, float_width=0):

        super().__init__(position, size, font, screen_display, colors, float_width)

        # list of strings that can appear on button when button is pressed
        self.__states_text_list = states_text_list

        # initial index
        self.__current_state_text_index = 0

    # increment text index
    def add_state_text_index(self):
        self.__current_state_text_index += 1
        self.__current_state_text_index = self.__current_state_text_index % len(self.__states_text_list)

    # draw button (mouse out button)
    def draw_mouse_out_button(self):
        super().draw_button(self.__states_text_list[self.__current_state_text_index],
                            self._colors.get_mouse_out_button_colors())

    # draw button (mouse over button)
    def draw_mouse_over_button(self):
        super().draw_button(self.__states_text_list[self.__current_state_text_index],
                            self._colors.get_mouse_over_button_colors())


class SlideButton(TextButton):
    def __init__(self, font, bar_width, range_items, colors, position=None, size=None, screen_display=None,
                 float_width=0):

        super().__init__(position, size, font, screen_display, colors, float_width)

        self.__bar_float_width = bar_width

        # list of all items that can be displayed on button
        self.__range_items = range_items

        # initial item
        self.__current_item_float_index = 0
        self.__current_item = range_items[0]

        # initial bar position
        self.__current_float_bar_position = None

        # bar pressed state
        self.__bar_pressed = False

    def get_bar_is_pressed(self):
        return self.__bar_pressed

    def get_current_item(self):
        return self.__current_item

    def get_bar_float_width(self):
        return self.__bar_float_width

    def set_bar_float_width(self, new_bar_float_width):
        self.__bar_float_width = new_bar_float_width

    def update_bar_position(self):
        self.calculate_float_bar_position_by_current_item_float_index()

    def press_bar(self):
        self.__bar_pressed = True

    def release_bar(self):
        self.__bar_pressed = False

    def calculate_float_bar_position_by_current_mouse_position(self, current_mouse_position):

        # mouse position exceed button right limit
        if current_mouse_position[0] > \
                self._float_position[0] + self._float_size[0] - round(self._float_width) - self.__bar_float_width / 2:
            self.__current_float_bar_position = (self._float_position[0] +
                                                self._float_size[0] - round(self._float_width) - self.__bar_float_width,
                                                self._float_position[1] + round(self._float_width))

        # mouse position exceed button left limit
        elif current_mouse_position[0] < self._float_position[0] + self._float_width + self.__bar_float_width / 2:
            self.__current_float_bar_position = (self._float_position[0] + round(self._float_width),
                                                self._float_position[1] + round(self._float_width))

        # mouse position on button
        else:
            self.__current_float_bar_position = (current_mouse_position[0] - self.__bar_float_width / 2,
                                                self._float_position[1] + round(self._float_width))

    def __calculate_current_item_float_index(self):
        self.__current_item_float_index = \
            (self.__current_float_bar_position[0] - self._float_position[0] - round(self._float_width)) * \
            ((len(self.__range_items) - 1) / (self._float_size[0] - 2 * round(self._float_width) - self.__bar_float_width))

    def calculate_current_item(self):
        self.__calculate_current_item_float_index()
        self.__current_item = self.__range_items[round(self.__current_item_float_index)]

    def calculate_float_bar_position_by_current_item_float_index(self):
        self.__current_float_bar_position = \
            (self._float_position[0] + round(self._float_width) + self.__current_item_float_index /
             ((len(self.__range_items) - 1) / (self._float_size[0] - 2 * round(self._float_width) - self.__bar_float_width)),

             self._float_position[1] + round(self._float_width))

    def draw_mouse_over_button(self):
        self.__draw_slide_button(self._colors.get_mouse_over_button_colors())

    def draw_mouse_out_button(self):
        self.__draw_slide_button(self._colors.get_mouse_out_button_colors())

    def __draw_slide_button(self, colors):

        # draw button without width
        if not self._float_width:
            # draw button rectangle
            button_rect = FloatRect(self._screen_display, colors.get_button(),
                                                self._float_position, self._float_size)
            button_rect.draw()

            # draw bar (mouse over button)
            bar_rect = FloatRect(self._screen_display, colors.get_bar(), self.__current_float_bar_position,
                                             (self.__bar_float_width, self._float_size[1]))
            bar_rect.draw()

        # draw button with width
        else:

            # draw button margin
            button_margin_rect = FloatRect(self._screen_display, colors.get_width(), self._float_position,
                                                       self._float_size)
            button_margin_rect.draw()

            # draw button rectangle
            button_rect = FloatRect(self._screen_display, colors.get_button(),
                                                (self._float_position[0] + round(self._float_width),
                                                 self._float_position[1] + round(self._float_width)),
                                                (self._float_size[0] - 2 * round(self._float_width),
                                                 self._float_size[1] - 2 * round(self._float_width)))
            button_rect.draw()

            # draw bar
            bar_rect = FloatRect(self._screen_display, colors.get_bar(), self.__current_float_bar_position,
                                             (self.__bar_float_width, self._float_size[1] - 2 * round(self._float_width)))
            bar_rect.draw()

        # draw text
        self._draw_font_surface(str(self.__current_item), colors.get_font())
