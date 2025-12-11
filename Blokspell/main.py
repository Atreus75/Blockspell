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
menu.menu_loop() 

# Game definitions
game = Game(main_window)
game.game_loop()

# Main Loop
while True:
    # --- MENU PRINCIPAL ---
    menu = Menu(player_mouse, main_window)
    menu.main_window.set_resolution(10, 10)
    menu.menu_loop()

    # --- INICIA UMA NOVA PARTIDA ---
    game = Game(main_window)
    game.game_loop()
    if game.soundtrack.is_playing:
        game.soundtrack.stop()


