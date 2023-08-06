class MousePositionButtonColors:
    def __init__(self, button=(0, 0, 0), font=(0, 0, 0), bar=(0, 0, 0), width=(0, 0, 0)):
        self.__button = button
        self.__font = font
        self.__bar = bar
        self.__width = width

    def set_button(self, new_button):
        self.__button = new_button

    def set_font(self, new_font):
        self.__font = new_font

    def set_bar(self, new_bar):
        self.__bar = new_bar

    def set_width(self, new_width):
        self.__width = new_width

    def get_button(self):
        return self.__button

    def get_font(self):
        return self.__font

    def get_bar(self):
        return self.__bar

    def get_width(self):
        return self.__width


class ButtonColors:
    def __init__(self, mouse_over_button_colors, mouse_out_button_colors):
        self.__mouse_over_button_colors = mouse_over_button_colors
        self.__mouse_out_button_colors = mouse_out_button_colors

    def set_mouse_over_button_colors(self, new_state):
        self.__mouse_over_button_colors = new_state

    def set_mouse_out_button_colors(self, new_state):
        self.__mouse_out_button_colors = new_state

    def get_mouse_over_button_colors(self):
        return self.__mouse_over_button_colors

    def get_mouse_out_button_colors(self):
        return self.__mouse_out_button_colors
