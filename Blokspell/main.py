from blocklib import Menu, Game
from PPlay.mouse import *
from PPlay.sound import Sound
from PPlay.window import Window
from time import time

# General variables
player_mouse = Mouse()
main_window = Window(1280, 720)
main_window.set_title('Blockspell')
#play_sound = Sound('src/play_press.mp3')


# Menu Definitions
menu = Menu(player_mouse, main_window)
menu.main_window.set_resolution(10, 10)

# Game definitions
game = Game(main_window)
entered_game = False

# Main Loop
while True:
    if entered_game and time() - game.esc_pressed >= 1:
        menu = Menu(player_mouse, main_window)
        menu.main_window.set_resolution(10, 10)
        entered_game = False
    elif not entered_game:
        menu.menu_loop()
        game.game_loop()
        entered_game = True

