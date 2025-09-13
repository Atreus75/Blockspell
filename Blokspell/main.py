from blocklib import Menu, Utils
from PPlay.mouse import *
from time import sleep

# Structural variables
resolution = {'x' : 1280, 'y' : 720}
player_mouse = Mouse()
in_menu = True

# Menu Definitions
menu = Menu(1200, 720)
menu.main_window.set_title('Blockspell')
menu.preset_blocks()
menu.preset_play_btn()
menu.preset_mage()

play_btn_anim_interval = 0.7
blocks_anim_interval = 0.05
mage_anim_interval = 0.05


# Menu Loop
while True:
    if in_menu:
        # Verifications
        if player_mouse.is_over_object(menu.play_btn):
            play_btn_anim_interval = -1
            mage_anim_interval = 0.005
            
            if player_mouse.is_button_pressed(1):
                menu.mage_hand1.y = menu.origin_mage_hand1_y
                menu.mage_hand2.y = menu.origin_mage_hand2_y
                

        else:
            play_btn_anim_interval = 0.7
            mage_anim_interval = 0.05

        # Animations
        menu.animate_falling_blocks(blocks_anim_interval)
#        menu.animate_play_btn(play_btn_anim_interval)
        menu.animate_mage_hands(mage_anim_interval)

        # Draws in visual layer order (back to front)
        menu.background.draw()
        
        # Draws all blocks
        for block in menu.blocks:
            block.draw()

        Utils.draw_all([menu.play_btn, menu.mage_head, menu.mage_hand1, menu.mage_hand2])
        menu.main_window.update()
