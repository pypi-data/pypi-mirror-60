# PygameMenus
Make menus for pygame with PygameMenus

This packages helps you to not waste time creating menus for games or others pygame projects.

## Commands

### Install

```
py -m pip install PygameMenus
```

### Upload to PyPI

Go to project root folder
```
py setup.py sdist
py -m twine upload dist/*
```

### Release new version to PyPI

Update version number in setup.py
```
py setup.py sdist
py -m twine upload --skip-existing dist/*
```

## Examples

### Setup button colors

```
mouse_out_colors = MousePositionButtonColors(button=(0, 255, 255), font=(0, 0, 255), bar=(200, 200, 255))

mouse_over_colors = MousePositionButtonColors(button=(255, 255, 0), font=(255, 0, 0), bar=(255, 165, 0))

button_colors = ButtonColors(mouse_over_colors, mouse_out_colors)
```
#### Objects
mouse_out_colors - Colors of the button when the mouse cursor is outside the button area.

mouse_over_colors - Colors of the button when the mouse cursor in inside the button area.

button_colors - Colors of the button to be passed to the button object.

#### Parameters
button - Background color of the button.

font - Color of the font inside button.

bar - Color of the bar inside button (only applied in buttons of type SlideButtons).

### Create button

```
button_font = FloatFont("Arial", 70)

button_range = range(101)

slide_button = SlideButton(button_font, 10, button_range, button_colors)
```
#### Objects
button_font - font inside button (Object of PygameFloatObjects package).

button_range - list of all values that can be displayed on the button (In this case, when the bar is leaning to left the value is 0 and when the bar is leaning to the right the value is 100).

slide_button - type of button which has a slide bar (object of PygameMenus package).

10 - bar width.

### Create buttons block

```
buttons_matrix = ((slide_button, slide_button_1, slide_button_2),
                  (states_button_1,),
                  (redirect_button_1, redirect_button_1))
                                 
block = Block((500, 500), buttons_matrix, 20, 30)
```
#### Objects
buttons_matrix - Matrix of buttons that defines where the buttons are displayed in the menu.

block - Object located under the menu title which contains all the menu buttons and their location.

(500, 500) - Size of the block (x, y).

20 - Horizontal margin between buttons.

30 - Vertical margin between buttons.

### Create title

```
title_font = FloatFont("Arial", 150)

title = Title(title_font, (0, 0, 0), "Main Menu")
```
#### Objects
title_font - Font of the title (object of PygameFloatObjects).

(0, 0, 0) - Color of the title font.

"Main Menu" - Text of the title font.

### Create menu

```
main_menu = Menu(screen, title, block, 30, (0.80, 0.80), 0.80, "STATE_MAIN_MENU")
```
#### Objects
screen - Pygame screen display object.

title - Menu title (PygameMenus object).

block - Buttons block (PygameMenus object).

30 - Margin between title and block.

(0.80, 0.80) - Horizontal and vertical menu maximum size ratio (used to know the instance of resizing).

0.80 - Resize ratio (How much the menu should resize).

"STATE_MAIN_MENU" - String corresponding to the menu state name (used in the loop of the program).

### Create loop

```
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
```

