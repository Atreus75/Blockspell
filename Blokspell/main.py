from blocklib import Menu, Utils, Game
from PPlay.mouse import *
from PPlay.sound import Sound
from time import time
from random import randint

# Structural variables
player_mouse = Mouse()
#play_sound = Sound('src/play_press.mp3')
in_menu = True
in_game = False
play_delay = 0

# Menu Definitions
menu = Menu(1280, 720)
janela = menu.main_window
janela.set_title('Blockspell')
menu.preset_blocks()
menu.preset_play_btn()
menu.preset_mage()

play_btn_anim_interval = 0.7
blocks_anim_interval = 0.05
mage_anim_interval = 0.05
janela.set_resolution(10, 10)

play_pressed = False
wait_blocks = 0


# Game definitions
game = Game(janela)

# Loop
while True:
    if in_menu:
        # Verifications
        now = time()
        if play_pressed and now - wait_blocks >= 5:
            in_menu = False

        if player_mouse.is_over_object(menu.play_btn):
            play_btn_anim_interval = -1
            mage_anim_interval = 0.005
            
            if player_mouse.is_button_pressed(1):
                menu.mage_hand1.y = menu.origin_mage_hand1_y
                menu.mage_hand2.y = menu.origin_mage_hand2_y
                #play_sound.play()
                wait_blocks = time()
                play_pressed = True
                in_game = True
        else:
            if not player_mouse.is_button_pressed(1):
                play_btn_anim_interval = 0.7
                mage_anim_interval = 0.05

        # Animations
        menu.animate_falling_blocks(blocks_anim_interval, in_game)
        if not in_game:
            menu.animate_mage_hands(mage_anim_interval)

        # Draws in visual layer order (back to front)
        menu.background.draw()
        
        # Draws all blocks
        for block in menu.blocks:
            block.draw()

        Utils.draw_all([menu.play_btn, menu.mage_head, menu.mage_hand1, menu.mage_hand2])
        janela.update()

    if in_game and not in_menu:
        janela.set_background_color('black')

        game.animate_clouds()

        # Draws
        game.ceu.draw()
        if len(game.current_clouds) >= 1:
            for cloud in game.current_clouds:
                cloud.draw()
        game.chao.draw()
        game.castelo.draw()
        game.mago.draw()
        janela.update()
