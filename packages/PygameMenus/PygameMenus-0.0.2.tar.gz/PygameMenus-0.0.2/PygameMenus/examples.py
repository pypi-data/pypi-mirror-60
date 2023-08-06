from PygameMenus.button import *
from PygameMenus.title import *
from PygameMenus.buttonblock import *
from PygameMenus.menu import *
from PygameMenus.buttoncolors import *
from PygameFloatObjects.objects import *


def example_1():

    # create display
    pygame.init()
    screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
    screen.fill((255, 255, 255))
    pygame.display.update()





    # ==================== Main Menu ====================
    # --- Title ---

    # define title color
    main_title_color = (0, 0, 0)

    # define title font
    main_title_font = FloatFont("Arial", 150)

    # create title
    main_title = Title(main_title_font, main_title_color, "Main Menu")



    # --- Slide buttons ---

    # create slide buttons colors when mouse is outside button
    main_slide_1_mouse_out_colors = MousePositionButtonColors(button=(0, 255, 255), font=(0, 0, 255), bar=(200, 200, 255))
    main_slide_2_mouse_out_colors = MousePositionButtonColors(button=(0, 255, 255), font=(0, 0, 255), bar=(200, 200, 255))
    main_slide_3_mouse_out_colors = MousePositionButtonColors(button=(0, 255, 255), font=(0, 0, 255), bar=(200, 200, 255))

    # create slide buttons colors when mouse is over button
    main_slide_1_mouse_over_colors = MousePositionButtonColors(button=(255, 255, 0), font=(255, 0, 0), bar=(255, 165, 0))
    main_slide_2_mouse_over_colors = MousePositionButtonColors(button=(255, 255, 0), font=(255, 0, 0), bar=(255, 165, 0))
    main_slide_3_mouse_over_colors = MousePositionButtonColors(button=(255, 255, 0), font=(255, 0, 0), bar=(255, 165, 0))

    # create slide buttons colors
    main_slide_1_colors = ButtonColors(main_slide_1_mouse_over_colors, main_slide_1_mouse_out_colors)
    main_slide_2_colors = ButtonColors(main_slide_2_mouse_over_colors, main_slide_2_mouse_out_colors)
    main_slide_3_colors = ButtonColors(main_slide_3_mouse_over_colors, main_slide_3_mouse_out_colors)

    # create slide buttons fonts
    main_slide_1_font = FloatFont("Arial", 70)
    main_slide_2_font = FloatFont("Arial", 70)
    main_slide_3_font = FloatFont("Arial", 70)

    # create slide buttons ranges
    main_slide_1_range = range(101)
    main_slide_2_range = ["a", "e", "i", "o", "u"]
    main_slide_3_range = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

    # define slide buttons bar width
    main_slide_bar_width = 10

    # create slide buttons
    main_slide_1 = SlideButton(main_slide_1_font, main_slide_bar_width, main_slide_1_range, main_slide_1_colors)
    main_slide_2 = SlideButton(main_slide_2_font, main_slide_bar_width, main_slide_2_range, main_slide_2_colors)
    main_slide_3 = SlideButton(main_slide_3_font, main_slide_bar_width, main_slide_3_range, main_slide_3_colors)



    # --- States buttons ---

    # create states buttons colors when mouse is outside button
    main_states_1_mouse_out_colors = MousePositionButtonColors(button=(0, 255, 255), font=(0, 0, 255))

    # create states buttons colors when mouse is over button
    main_states_1_mouse_over_colors = MousePositionButtonColors(button=(255, 255, 0), font=(255, 0, 0))

    # create states buttons colors
    main_states_1_colors = ButtonColors(main_states_1_mouse_over_colors, main_states_1_mouse_out_colors)

    # create states buttons fonts
    main_states_1_font = FloatFont("Arial", 50)

    # create states buttons ranges
    main_states_1_range = ["Difficulty: Very Easy", "Difficulty: Easy", "Difficulty: Medium", "Difficulty: Hard", "Difficulty: Very Hard"]

    # create states buttons
    main_states_button_1 = StatesButton(main_states_1_font, main_states_1_range, main_states_1_colors)



    # --- Redirect buttons ---

    # create redirect buttons colors when mouse is outside button
    main_redirect_1_mouse_out_colors = MousePositionButtonColors(button=(0, 255, 255), font=(0, 0, 255))
    main_redirect_2_mouse_out_colors = MousePositionButtonColors(button=(0, 255, 255), font=(0, 0, 255))

    # create redirect buttons colors when mouse is over button
    main_redirect_1_mouse_over_colors = MousePositionButtonColors(button=(255, 255, 0), font=(255, 0, 0))
    main_redirect_2_mouse_over_colors = MousePositionButtonColors(button=(255, 255, 0), font=(255, 0, 0))

    # create redirect buttons colors
    main_redirect_1_colors = ButtonColors(main_redirect_1_mouse_over_colors, main_redirect_1_mouse_out_colors)
    main_redirect_2_colors = ButtonColors(main_redirect_2_mouse_over_colors, main_redirect_2_mouse_out_colors)

    # create redirect buttons fonts
    main_redirect_1_font = FloatFont("Arial", 70)
    main_redirect_2_font = FloatFont("Arial", 70)

    # create redirect buttons text
    main_redirect_1_text = "Exit"
    main_redirect_2_text = "Next"

    # create redirect buttons redirection states
    main_redirect_1_redirection = "STATE_EXIT"
    main_redirect_2_redirection = "STATE_SEC_MENU"

    # create redirect buttons
    main_redirect_1 = RedirectButton(main_redirect_1_font, main_redirect_1_text, main_redirect_1_redirection, main_redirect_1_colors)
    main_redirect_2 = RedirectButton(main_redirect_2_font, main_redirect_2_text, main_redirect_2_redirection, main_redirect_2_colors)



    # --- Buttons block ---

    # create buttons block initial size
    main_block_size = (500, 500)

    # create buttons matrix
    main_block_buttons_matrix = ((main_slide_1, main_slide_2, main_slide_3),
                                 (main_states_button_1,),
                                 (main_redirect_1, main_redirect_2))

    # create block vertical and horizontal margin
    main_block_vertical_margin = 20
    main_block_horizontal_margin = 20

    # create buttons block
    main_block = Block(main_block_size, main_block_buttons_matrix, main_block_vertical_margin, main_block_horizontal_margin)



    # --- Menu ---

    # define margin between title and block
    main_menu_title_block_margin = 30

    # define horizontal and vertical max size ratio
    main_menu_max_size_ratio = (0.80, 0.80)

    # define resize ratio
    main_menu_resize_ratio = 0.80

    # define menu state
    main_menu_state = "STATE_MAIN_MENU"

    # create menu
    main_menu = Menu(screen, main_title, main_block, main_menu_title_block_margin, main_menu_max_size_ratio, main_menu_resize_ratio, main_menu_state)






    # ==================== Second Menu ====================
    # --- Title ---

    # define title color
    sec_title_color = (0, 0, 0)

    # define title font
    sec_title_font = FloatFont("Arial", 150)

    # create title
    sec_title = Title(sec_title_font, sec_title_color, "Second Menu")

    # --- Slide buttons ---

    # create slide buttons colors when mouse is outside button
    sec_slide_1_mouse_out_colors = MousePositionButtonColors(button=(0, 255, 255), font=(0, 0, 255), bar=(200, 200, 255))
    sec_slide_2_mouse_out_colors = MousePositionButtonColors(button=(0, 255, 255), font=(0, 0, 255), bar=(200, 200, 255))
    sec_slide_3_mouse_out_colors = MousePositionButtonColors(button=(0, 255, 255), font=(0, 0, 255), bar=(200, 200, 255))

    # create slide buttons colors when mouse is over button
    sec_slide_1_mouse_over_colors = MousePositionButtonColors(button=(255, 255, 0), font=(255, 0, 0), bar=(255, 165, 0))
    sec_slide_2_mouse_over_colors = MousePositionButtonColors(button=(255, 255, 0), font=(255, 0, 0), bar=(255, 165, 0))
    sec_slide_3_mouse_over_colors = MousePositionButtonColors(button=(255, 255, 0), font=(255, 0, 0), bar=(255, 165, 0))

    # create slide buttons colors
    sec_slide_1_colors = ButtonColors(sec_slide_1_mouse_over_colors, sec_slide_1_mouse_out_colors)
    sec_slide_2_colors = ButtonColors(sec_slide_2_mouse_over_colors, sec_slide_2_mouse_out_colors)
    sec_slide_3_colors = ButtonColors(sec_slide_3_mouse_over_colors, sec_slide_3_mouse_out_colors)

    # create slide buttons fonts
    sec_slide_1_font = FloatFont("Arial", 70)
    sec_slide_2_font = FloatFont("Arial", 50)
    sec_slide_3_font = FloatFont("Arial", 50)

    # create slide buttons ranges
    sec_slide_1_range = ["X: {}".format(i) for i in range(-1000, 1001)]
    sec_slide_2_range = ["Y: {}".format(i) for i in range(-100, 101)]
    sec_slide_3_range = ["Z: {}".format(i) for i in range(101)]

    # define slide buttons bar width
    sec_slide_bar_width = 10

    # create slide buttons
    sec_slide_1 = SlideButton(sec_slide_1_font, sec_slide_bar_width, sec_slide_1_range, sec_slide_1_colors)
    sec_slide_2 = SlideButton(sec_slide_2_font, sec_slide_bar_width, sec_slide_2_range, sec_slide_2_colors)
    sec_slide_3 = SlideButton(sec_slide_3_font, sec_slide_bar_width, sec_slide_3_range, sec_slide_3_colors)

    # --- States buttons ---

    # create states buttons colors when mouse is outside button
    sec_states_1_mouse_out_colors = MousePositionButtonColors(button=(0, 255, 255), font=(0, 0, 255))

    # create states buttons colors when mouse is over button
    sec_states_1_mouse_over_colors = MousePositionButtonColors(button=(255, 255, 0), font=(255, 0, 0))

    # create states buttons colors
    sec_states_1_colors = ButtonColors(sec_states_1_mouse_over_colors, sec_states_1_mouse_out_colors)

    # create states buttons fonts
    sec_states_1_font = FloatFont("Arial", 40)

    # create states buttons ranges
    sec_states_1_range = ["f(x, y, z)", "g(x, y, z)", "h(x, y, z)"]

    # create states buttons
    sec_states_button_1 = StatesButton(sec_states_1_font, sec_states_1_range, sec_states_1_colors)

    # --- Redirect buttons ---

    # create redirect buttons colors when mouse is outside button
    sec_redirect_1_mouse_out_colors = MousePositionButtonColors(button=(0, 255, 255), font=(0, 0, 255))

    # create redirect buttons colors when mouse is over button
    sec_redirect_1_mouse_over_colors = MousePositionButtonColors(button=(255, 255, 0), font=(255, 0, 0))

    # create redirect buttons colors
    sec_redirect_1_colors = ButtonColors(sec_redirect_1_mouse_over_colors, sec_redirect_1_mouse_out_colors)

    # create redirect buttons fonts
    sec_redirect_1_font = FloatFont("Arial", 70)

    # create redirect buttons text
    sec_redirect_1_text = "Back"

    # create redirect buttons redirection states
    sec_redirect_1_redirection = "STATE_MAIN_MENU"

    # create redirect buttons
    sec_redirect_1 = RedirectButton(sec_redirect_1_font, sec_redirect_1_text, sec_redirect_1_redirection, sec_redirect_1_colors)

    # --- Buttons block ---

    # create buttons block initial size
    sec_block_size = (500, 500)

    # create buttons matrix
    sec_block_buttons_matrix = ((sec_slide_1,),
                                (sec_slide_2, None, sec_slide_3),
                                (None, sec_states_button_1, None),
                                (sec_redirect_1, None))

    # create block vertical and horizontal margin
    sec_block_vertical_margin = 20
    sec_block_horizontal_margin = 20

    # create buttons block
    sec_block = Block(sec_block_size, sec_block_buttons_matrix, sec_block_vertical_margin, sec_block_horizontal_margin)

    # --- Menu ---

    # define margin between title and block
    sec_menu_title_block_margin = 30

    # define horizontal and vertical max size ratio
    sec_menu_max_size_ratio = (0.80, 0.80)

    # define resize ratio
    sec_menu_resize_ratio = 0.80

    # define menu state
    sec_menu_state = "STATE_SEC_MENU"

    # create menu
    sec_menu = Menu(screen, sec_title, sec_block, sec_menu_title_block_margin, sec_menu_max_size_ratio, sec_menu_resize_ratio, sec_menu_state)





    # ==================== Menus States Loop ===================

    exit_loop = False
    current_state = "STATE_MAIN_MENU"
    current_screen_display = screen

    while not exit_loop:

        if current_state == "STATE_MAIN_MENU":

            main_menu.set_screen_display(current_screen_display)
            main_menu.loop()
            if main_menu.get_pressed_exit():
                exit_loop = True

            else:
                current_state = main_menu.get_next_state()
                current_screen_display = main_menu.get_screen_display()

            screen.fill((255, 255, 255))
            pygame.display.update()

        elif current_state == "STATE_SEC_MENU":

            sec_menu.set_screen_display(current_screen_display)
            sec_menu.loop()
            if sec_menu.get_pressed_exit():
                exit_loop = True

            else:
                current_state = sec_menu.get_next_state()
                current_screen_display = sec_menu.get_screen_display()

            screen.fill((255, 255, 255))
            pygame.display.update()

        elif current_state == "STATE_EXIT":
            exit_loop = True

        else:
            print("Invalid state!")

    pygame.quit()


example_1()
