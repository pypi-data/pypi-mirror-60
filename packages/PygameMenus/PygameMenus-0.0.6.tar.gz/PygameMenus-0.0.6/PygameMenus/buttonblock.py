class Block:
    def __init__(self, size, buttons_matrix, vertical_margin, horizontal_margin, position=None, screen_display=None):
        self.__float_size = size
        self.__buttons_matrix = buttons_matrix
        self.__float_vertical_margin = vertical_margin
        self.__float_horizontal_margin = horizontal_margin
        self.__float_position = position
        self.__screen_display = screen_display

        # separate buttons by type
        self.__text_buttons = []
        self.__separate_buttons_type()

        # separate text buttons by type
        self.__redirect_buttons, self.__press_buttons, self.__slide_buttons = [], [], []
        self.__separate_text_buttons_type()

    def set_float_position(self, new_position):
        self.__float_position = new_position

    def set_screen_display(self, new_screen):
        self.__screen_display = new_screen

    def set_float_size(self, new_float_size):
        self.__float_size = new_float_size

    def set_float_vertical_margin(self, new_float_vertical_margin):
        self.__float_vertical_margin = new_float_vertical_margin

    def set_float_horizontal_margin(self, new_float_horizontal_margin):
        self.__float_horizontal_margin = new_float_horizontal_margin

    def get_buttons(self):
        return self.get_redirect_buttons() + self.get_press_buttons() + self.get_slide_buttons()

    def get_text_buttons(self):
        return self.__text_buttons

    def get_redirect_buttons(self):
        return self.__redirect_buttons

    def get_press_buttons(self):
        return self.__press_buttons

    def get_slide_buttons(self):
        return self.__slide_buttons

    def get_float_size(self):
        return self.__float_size

    def get_float_position(self):
        return self.__float_position

    def get_float_vertical_margin(self):
        return self.__float_vertical_margin

    def get_float_horizontal_margin(self):
        return self.__float_horizontal_margin

    def __separate_buttons_type(self):
        for buttons_row in self.__buttons_matrix:
            for button in buttons_row:
                try:
                    button.get_font()
                except AttributeError:
                    pass
                else:
                    # store text button
                    self.__text_buttons.append(button)

    def __separate_text_buttons_type(self):
        for button in self.__text_buttons:
            if type(button).__name__ == "RedirectButton":
                self.__redirect_buttons.append(button)

            elif type(button).__name__ == "PressButton":
                self.__press_buttons.append(button)

            elif type(button).__name__ == "SlideButton":
                self.__slide_buttons.append(button)

    def __calculate_buttons_float_width_current_row(self, current_buttons_row):
        return (self.__float_size[0] -
                self.__float_horizontal_margin * (len(current_buttons_row) - 1)) / len(current_buttons_row)

    def __calculate_buttons_float_height(self):
        return (self.__float_size[1] -
                self.__float_vertical_margin * (len(self.__buttons_matrix) - 1)) / len(self.__buttons_matrix)

    def set_slide_buttons_bar_width(self, new_bar_float_width):
        for button in self.__slide_buttons:
            button.set_bar_float_width(new_bar_float_width)

    # set buttons new position, size and screen display
    def update_buttons_appearance_in_block(self):

        current_float_position = self.__float_position

        # get height of all buttons
        buttons_float_height = self.__calculate_buttons_float_height()

        for row_buttons in self.__buttons_matrix:

            # get width of all buttons in the row
            buttons_float_width = self.__calculate_buttons_float_width_current_row(row_buttons)

            for button in row_buttons:
                if button is not None:
                    button.set_float_position(current_float_position)
                    button.set_float_size((buttons_float_width, buttons_float_height))
                    button.set_screen_display(self.__screen_display)
                    button.update_float_width()

                    # when slide button position is changed we have to update bar position
                    if type(button).__name__ == "SlideButton":
                        button.update_bar_position()

                # move position to the right
                current_float_position = (current_float_position[0] + buttons_float_width + self.__float_horizontal_margin,
                                         current_float_position[1])

            # move position x to initial position
            current_float_position = (self.__float_position[0], current_float_position[1])

            # move position to down
            current_float_position = (current_float_position[0],
                                     current_float_position[1] + buttons_float_height + self.__float_vertical_margin)
