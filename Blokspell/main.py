from os import access

from PPlay.window import *
from PPlay.sprite import *
from PPlay.gameimage import *

# Variáveis GLobais
resolution = {'x' : 1280, 'y' : 720}


def initialize_menu():
    global resolution

    # Inicialização da Janela Principal
    main_window = Window(resolution['x'], resolution['y'])
    main_window.set_title('Blockspell')

    # Inicialização do Menu
    menu_background = GameImage('src/fundo_menu.jpg')
    menu_background.image = pygame.transform.scale(menu_background.image, (resolution['x'], resolution['y']))
    menu_background.width = main_window.width
    menu_background.height = main_window.height

    return [main_window, menu_background]

main_window, menu_background = initialize_menu()

# Game Loop
while True:
    menu_background.draw()
    main_window.update()
