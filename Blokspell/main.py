from blocklib import Utils, Menu

# Variáveis GLobais
resolution = {'x' : 1280, 'y' : 720}



menu = Menu(1200, 720)
menu.main_window.set_title('Blockspell')

# Menu Loop
while True:
    menu.background.draw()
    
    # Animations
    menu.falling_blocks_anim(1)
    for block in menu.blocks:
        block.draw()

#    menu.enemies_anim(2)
 #   for enemie in menu.enemies:
  #      enemie.draw()
    
    menu.play_btn_anim(0.7)
    menu.play_btn.draw()
    menu.mage_head.draw()
    menu.mage_hand1.draw()
    menu.mage_hand2.draw()
    menu.main_window.update()
