from blocklib import Utils, Menu

# Variáveis GLobais
resolution = {'x' : 1280, 'y' : 720}



menu = Menu(1200, 720)
menu.main_window.set_title('Blockspell')

# Menu Loop
while True:
    menu.background.draw()
    menu.play_btn.draw()
    for block in menu.blocks:
        block.draw()
    menu.falling_blocks_anim()
    menu.main_window.update()
