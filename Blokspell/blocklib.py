from PPlay.gameimage import *
from PPlay.mouse import *
from PPlay.sprite import *
from PPlay.window import *
from PPlay.animation import *
from random import randint, choice
from time import time
from tetris import Tetris


class Utils:
    def __init__(self):
        pass

    # Centralizes an object over another object
    def centralize_over_object(top_obj, back_obj):
        top_obj.x = back_obj.width/2 - top_obj.width/2
        top_obj.y = back_obj.height/2 - top_obj.height/2
        return top_obj

    def draw_all(objects=[]):
        for obj in objects:
            obj.draw()

class Enemie(Animation):
    def __init__(self, image_file, frames=1, move_timeout=0, damage=0, life=0, vel_x=0, attack_cooldown=0):
        super().__init__(image_file, frames)
        self.set_total_duration(1000)
        self.move_timeout = move_timeout
        self.damage = damage
        self.life = life
        self.vel_x = vel_x
        self.last_move = time()
        self.last_attack = 0
        self.attack_cooldown = attack_cooldown
        self.alive = True

    def move(self):
        self.x -= self.vel_x


class Cachorro(Enemie):
    def __init__(self):
        image_file = 'src/inimigos/cachorro_spritesheet.png'
        super().__init__(image_file, frames=12, move_timeout=3, damage=20, life=100, vel_x=25, attack_cooldown=5)

class Gorila(Enemie):
    def __init__(self):
        image_file = 'src/inimigos/gorila_spritesheet.png'
        super().__init__(image_file, frames=6, move_timeout=5, damage=50, life=200, vel_x=10, attack_cooldown=8)

class Rato(Enemie):
    def __init__(self):
        image_file = 'src/inimigos/rato_spritesheet.png'
        super().__init__(image_file, frames=3, move_timeout=1, damage=5, life=50, vel_x=40, attack_cooldown=2)

class Mago(Sprite):
    def __init__(self, image_file, frames=1):
        super().__init__(image_file, frames)
        self.life = 100
        self.mana = 100
        self.anim_state = False
        self.last_animation = 0.0
    
    def regenerate_life(self, points=0):
        total_regen = 10 * points
        self.life = self.life + total_regen if self.life + total_regen <= 100 else 100
        
    def regenerate_mana(self, points=0):
        self.mana += 10 * points
    
class Spell(Sprite):
    def __init__(self, x=0, y=0):
        self.current_frame = 0
        self.current_collision_frame = 0
        self.image_path = 'src/bola_fodona/Bola_0.png'
        super().__init__(self.image_path)
        self.damage = 25
        self.last_animation = time()
        self.last_collision_animation = 0
        self.animation_timeout = 0.2
        self.state = "moving"  # "moving", "colliding", "finished"
        self.collided_with = None

        # Posição inicial (evita nascer fora da tela)
        self.x = x
        self.y = y




class Regeneration(Sprite):
    def __init__(self):
        super().__init__('/src/açoes/rec_vida.png')
        self.life_points = 5
        self.animation_duration = 1

class Menu:
    def __init__(self, mouse=Mouse(), window=Window(0, 0)):
        self.main_window = window

        self.player_mouse = mouse
        self.background = GameImage('src/menu/fundo_menu.jpg')
        self.background.image = pygame.transform.scale(self.background.image, (self.main_window.width, self.main_window.height))
        self.background.width = self.main_window.width
        self.background.height = self.main_window.height
        self.last_window_animation = 0

    def preset_blocks(self):
        # Pre-configures the little blocks for their background animation
        self.block_vely = 100
        self.blocks = [
            Sprite('src/peças/I_azul.png'),
            Sprite('src/peças/I_verde.png'),
            Sprite('src/peças/I_vermelha.png'),
            Sprite('src/peças/L_azul.png'),
            Sprite('src/peças/L_verde.png'),
            Sprite('src/peças/L_vermelho.png'),
            Sprite('src/peças/O_azul.png'),
            Sprite('src/peças/O_verde.png'),
            Sprite('src/peças/O_vermelho.png'),
            Sprite('src/peças/peça_dourada.png'),
            Sprite('src/peças/S_azul.png'),
            Sprite('src/peças/S_verde.png'),
            Sprite('src/peças/S_vermelho.png'),
            Sprite('src/peças/T_azul.png'),
            Sprite('src/peças/T_verde.png'),
            Sprite('src/peças/T_vermelho.png')
                ]

        self.block_ocupied_positions = []
        for block in self.blocks:
            block.image = pygame.transform.scale(block.image, (self.main_window.width/100*6, self.main_window.height/100*6))
            block.y = self.main_window.height
        self.last_block_renderization = time()

    def preset_play_btn(self):
        # Play button configuration
        self.play_btn = GameImage('src/menu/play_button1.png')
        self.play_btn = Utils.centralize_over_object(self.play_btn, self.main_window)
        self.play_btn.y = self.play_btn.y + 80
        self.last_play_btn_animation = time()
        self.play_btn.height -= self.play_btn.height/2.7

    def preset_mage(self):
        # Menu Mage
        self.mage_head = GameImage('src/menu/cabeça_mago.png')
        self.mage_head.image = pygame.transform.scale(self.mage_head.image, (self.main_window.width/100*60, self.main_window.height/100*80))
        self.mage_head.x = self.main_window.width/2 - int(self.mage_head.image.get_width()/2)
        self.mage_head.y = 0

        self.mage_hand1 = GameImage('src/menu/mao1.png')
        self.mage_hand1.x = self.play_btn.x - int(self.play_btn.width)/2 + 75
        self.mage_hand1.y = self.play_btn.y - (int(self.play_btn.height) - 30)

        self.mage_hand2 = GameImage('src/menu/mao2.png')
        self.mage_hand2.x = self.mage_hand1.x - 55
        self.mage_hand2.y = self.mage_hand1.y - 15
        
        self.origin_mage_hand1_y = self.mage_hand1.y
        self.origin_mage_hand2_y = self.mage_hand2.y
        self.last_mage_animation = time()
        self.hand_vely = 1

    def animate_falling_blocks(self, interval_secs, play_pressed=False):
        block = choice(self.blocks)
        if time()-self.last_block_renderization >= interval_secs and play_pressed == False:
            self.last_block_renderization = time()

            if block.y >= self.main_window.height:    
                if block.x in self.block_ocupied_positions:
                    self.block_ocupied_positions.remove(block.x)
                
                first_space = range(0, int(self.mage_head.x)-50)
                second_space = range(int(self.mage_head.x+self.mage_head.width+50), int(self.main_window.width)-int(block.width))
                pos_x = choice(list(first_space)+list(second_space))
                while pos_x in self.block_ocupied_positions:
                    pos_x = choice(list(first_space)+list(second_space))
                block.x = pos_x
                block.y = randint(-30, -5) - block.height
                self.block_ocupied_positions.append(pos_x)
        for block in self.blocks:
            block.y += self.block_vely * self.main_window.delta_time()

    def animate_mage_hands(self, interval_secs):
        reached_top = self.mage_hand1.y >= self.origin_mage_hand1_y
        reached_bottom = self.mage_hand1.y+10 <= self.origin_mage_hand1_y - 20

        if time()-self.last_mage_animation >= interval_secs:
            self.last_mage_animation = time()
            if reached_top or reached_bottom:
                self.hand_vely *= -1
            self.mage_hand1.y += self.hand_vely
            self.mage_hand2.y += self.hand_vely * -1

    def animate_play_btn(self, interval_secs):
        if time() - self.last_play_btn_animation >= interval_secs and interval_secs != -1:
            self.play_btn.x = self.play_btn.x * -1
            self.last_play_btn_animation = time()
        elif interval_secs == -1:
            self.play_btn.x = self.play_btn.x if self.play_btn.x > 0 else self.play_btn.x * -1

    def menu_loop(self):
        # Menu Definitions
        play_pressed = False
        wait_blocks = 0
        mage_anim_interval = 0.05
        blocks_anim_interval = 0.05

        self.preset_blocks()
        self.preset_play_btn()
        self.preset_mage()
        
        # Loop
        while True:
            # Verifications
            if self.main_window.get_keyboard().key_pressed('ESC'):
                self.main_window.close()
                exit() # End window and the entire program
            
            now = time()
            if play_pressed and now - wait_blocks >= 5:
                break # End menu loop and goes to game loop

            if self.player_mouse.is_over_object(self.play_btn):
                mage_anim_interval = 0.005
                
                if self.player_mouse.is_button_pressed(1):
                    self.mage_hand1.y = self.origin_mage_hand1_y
                    self.mage_hand2.y = self.origin_mage_hand2_y
                    #play_sound.play()
                    wait_blocks = time()
                    play_pressed = True
            else:
                if not self.player_mouse.is_button_pressed(1):
                    mage_anim_interval = 0.05

            # Animations
            self.animate_falling_blocks(blocks_anim_interval)
            if not play_pressed:
                self.animate_mage_hands(mage_anim_interval)

            # Draws in visual layer order (back to front)
            self.background.draw()
            
            # Draws all blocks
            for block in self.blocks:
                block.draw()

            Utils.draw_all([self.play_btn, self.mage_head, self.mage_hand1, self.mage_hand2])
            self.main_window.update()


class Game:
    def __init__(self, main_window=Window(0, 0)):
        self.main_window = main_window
        self.esc_pressed = 0
        self.enemie_generation_rate = 20
        self.enemie_limit = 4

        self.ceu = Sprite('src/cenario/ceu.png')
        self.chao = Sprite('src/cenario/chao2.png')
        self.chao.y = self.main_window.height - (self.chao.height)
        self.castelo = Sprite('src/cenario/castelo.png')
        self.castelo.x = 0
        self.castelo.y = self.main_window.height - (self.castelo.height + (self.chao.height))
        self.mago = Mago('src/magos/mago_p.png')
        self.mago.x = (self.castelo.x + self.castelo.width - 20)
        self.mago.y = self.main_window.height - (self.mago.height + (self.chao.height))
        self.tetris = Tetris(self.main_window, 10, 15, 28, (self.main_window.width//2 - 190, self.main_window.height//2 - 300))

        # Preset das clouds
        self.clouds = [
            'src/nuvens/nuvem_0.png',
            'src/nuvens/nuvem_1.png',
            'src/nuvens/nuvem_2.png',
            'src/nuvens/nuvem_3.png',
            'src/nuvens/nuvem_casa.png'
        ]
        
        self.current_clouds = []
        self.cloud_vel = -100
        self.last_cloud_animation = time()
        
        self.current_enemies = []
        self.last_enemie_generation = time()

        self.current_spells = []
        self.spell_velx = 200
        self._load_spell_assets()

    def _load_spell_assets(self):
        """Carrega todas as imagens do feitiço na memória para evitar lag."""
        self.spell_frames = [
            pygame.image.load(f"src/bola_fodona/Bola_{i}.png").convert_alpha() 
            for i in range(8)
        ]


    def animate_clouds(self):
        if len(self.current_clouds) >= 1:
            if randint(0, 1500) == randint(0, 1500):
                self.current_clouds.append(Sprite(choice(self.clouds[0:4])))
                self.current_clouds[-1].x = randint(self.main_window.width + int(self.current_clouds[-1].width), self.main_window.width + int(self.current_clouds[-1].width) + 100)
                self.current_clouds[-1].y = randint(0, int(self.main_window.height / 2) - int(self.current_clouds[-1].height))

            for cloud in self.current_clouds:
                if cloud.x < (0-cloud.width):
                    self.current_clouds.remove(cloud)
                else:
                    cloud.x += self.cloud_vel * self.main_window.delta_time()
        else:
            self.current_clouds.append(Sprite(choice(self.clouds[0:4])))
            self.current_clouds[-1].x = self.main_window.width + self.current_clouds[-1].width
            self.current_clouds[-1].y = randint(0, int(self.main_window.height/2))
    # tetris_pplay.py

    def generate_enemies(self):
        if (time() - self.last_enemie_generation >= self.enemie_generation_rate or len(self.current_enemies) == 0) and len(self.current_enemies) <= self.enemie_limit:
            self.last_enemie_generation = time()
            
            choose = randint(1, 20)
            if 0 <= choose <= 9:
                self.current_enemies.append(Cachorro())
            elif 10 <= choose <= 13:
                self.current_enemies.append(Gorila())
            elif 14 <= choose <= 19:
                self.current_enemies.append(Rato())
            else:
                self.current_enemies.append(Cachorro())
            
            self.current_enemies[-1].x = self.main_window.width
            self.current_enemies[-1].y = self.chao.y - self.current_enemies[-1].height
    
    def launch_spell(self, power=1):
        """Cria e adiciona um novo feitiço ofensivo na lista atual."""
        x = self.mago.x + self.mago.width - 20
        y = self.mago.y + self.mago.height // 3

        spell = Spell(x, y)
        spell.state = "moving"
        spell.current_frame = 0
        spell.current_collision_frame = 0
        spell.last_animation = time()
        spell.last_collision_animation = 0
        spell.animation_timeout = 0.08
        spell.damage = 10 * power  # dano baseado na força

        print(f'Spell launched with {power} points of power.')
        self.current_spells.append(spell)


    
    def update_spells(self):
        """Atualiza movimento, colisões e animações de todos os feitiços ativos."""
        spells_to_remove = []

        for spell in self.current_spells:
            # MOVIMENTO
            if spell.state == "moving":
                
            # Cria um pequeno brilho atrás do feitiço
                if not hasattr(spell, "trail"):
                    spell.trail = []

                # Guarda a posição atual
                spell.trail.append((spell.x, spell.y+int(spell.height/2)))
                if len(spell.trail) > 8:  # limita o tamanho da trilha
                    spell.trail.pop(0)

                # Desenha a trilha com transparência
                for i, (tx, ty) in enumerate(spell.trail):
                    alpha = 255 - i * 30
                    if alpha < 50:
                        alpha = 50
                    surface = pygame.Surface((8, 8), pygame.SRCALPHA)
                    pygame.draw.circle(surface, (255, 255, 180, alpha), (4, 4), 4)
                    self.main_window.screen.blit(surface, (tx, ty))
                
                spell.x += self.spell_velx * self.main_window.delta_time()

                # animação cíclica de voo
                if time() - spell.last_animation >= spell.animation_timeout:
                    spell.last_animation = time()
                    spell.current_frame = (spell.current_frame + 1) % 5
                    spell.image = self.spell_frames[spell.current_frame]
                    spell.width = spell.image.get_width()
                    spell.height = spell.image.get_height()
                    spell.rect = spell.image.get_rect(topleft=(spell.x, spell.y))

                # colisão com inimigos
                for enemy in self.current_enemies:
                    if spell.collided(enemy):
                        if enemy.life - spell.damage >= 0: # Só inicia animação de colisão se dano for exatamente ou não-suficiente para matar inimigo
                            spell.state = "colliding"
                        spell.collided_with = enemy
                        spell.last_collision_animation = time()
                        enemy.life -= spell.damage
                        spell.damage -= enemy.life
                        break

                # saiu da tela
                if spell.x > self.main_window.width:
                    spell.state = "finished"

            # COLISÃO / EXPLOSÃO
            elif spell.state == "colliding":
                if time() - spell.last_collision_animation >= spell.animation_timeout:
                    spell.last_collision_animation = time()
                    spell.current_collision_frame += 1

                    if spell.current_collision_frame < 3:
                        idx = 5 + spell.current_collision_frame
                        spell.image = self.spell_frames[idx]
                        spell.width = spell.image.get_width()
                        spell.height = spell.image.get_height()
                        spell.rect = spell.image.get_rect(topleft=(spell.x, spell.y))
                    else:
                        spell.state = "finished"
            

            # DESENHA (apenas se não acabou)
            if spell.state != "finished":
                spell.draw()
            else:
                spells_to_remove.append(spell)

        # LIMPA feitiços terminados
        for spell in spells_to_remove:
            self.current_spells.remove(spell)


    def pause_menu(self):
        mouse = self.main_window.get_mouse()
        # --- Carrega imagens ---
        fundo = GameImage("src/menu/fundo_menu.jpg")
        fundo.image = pygame.transform.scale(
            fundo.image, (self.main_window.width, self.main_window.height)
        )

        btn_continuar = GameImage("src/menu/play.png")
        btn_menu = GameImage("src/menu/sair.png")

        # Centraliza os botões
        btn_continuar.x = self.main_window.width / 2 - btn_continuar.width / 2
        btn_menu.x = self.main_window.width / 2 - btn_menu.width / 2
        btn_continuar.y = self.main_window.height / 2 - 80
        btn_menu.y = self.main_window.height / 2 + 20

        while True:
            fundo.draw()
            btn_continuar.draw()
            btn_menu.draw()

            self.main_window.draw_text("PAUSADO", self.main_window.width / 2 - 100, 100, 50, (255, 255, 255))

            if mouse.is_over_object(btn_continuar):
                if mouse.is_button_pressed(1):
                    pygame.time.wait(150)
                    return "continuar"

            if mouse.is_over_object(btn_menu):
                if mouse.is_button_pressed(1):
                    pygame.time.wait(150)
                    return "menu"

            self.main_window.update()

    def animate_enemies(self):
        for enemie in self.current_enemies:
            if enemie.life <= 0:
                enemie.alive = False
                self.current_enemies.remove(enemie)
            
            if time() - enemie.last_move >= enemie.move_timeout and enemie.alive:
                enemie.last_move = time()
                if enemie.x >= self.mago.x + self.mago.width:
                    enemie.update()
                    enemie.move()
                else:
                    if time() - enemie.last_attack >= enemie.attack_cooldown:
                        self.mago.life -= enemie.damage

            enemie.draw()

    def animate_mage(self):
        now = time()
        if self.mago.anim_state == True and self.mago.last_animation == 0:
            self.mago.image = pygame.image.load(f"src/magos/mago_atk.png").convert_alpha()
            self.mago.last_animation = now
        elif now - self.mago.last_animation >= 0.5:
            self.mago.image = pygame.image.load(f"src/magos/mago_p.png").convert_alpha()
            self.mago.anim_state = False 
            self.mago.last_animation = 0


    def game_loop(self):
        last_limit_increse = 0
        while True:
            # Aumenta o limite de inimigos a cada 60 segundos usando o total time
            if time() - last_limit_increse >=60:
                last_limit_increse = time()
                self.enemie_limit += 1
            
            self.main_window.set_background_color('black')
            kb = self.main_window.get_keyboard()

            # --- pausa ---
            if kb.key_pressed('ESC'):
                pygame.time.wait(150)
                resultado = self.pause_menu()
                if resultado == "menu":
                    self.esc_pressed = time()
                    break
            if self.mago.life <= 0: # game over
                break
            
            if self.tetris.game_over:
                self.tetris.reset()
            self.animate_clouds()
            self.generate_enemies()
            
            # Mage actions
            self.animate_mage()
            if self.tetris.last_cleared_color_counts:
                # DEBUG opcional: print(self.tetris.last_cleared_color_counts)

                for counts in self.tetris.last_cleared_color_counts:
                    # counts agora é um dicionário com keys 'red','green','blue','yellow'
                    red = counts.get("red", 0)
                    green = counts.get("green", 0)
                    blue = counts.get("blue", 0)
                    yellow = counts.get("yellow", 0)

                    # sua ordem original queria verdes, azuis, vermelhos, amarelos
                    verdes = green
                    azuis = blue
                    vermelhos = red
                    amarelos = yellow

                    # Verde → lança feitiço ofensivo
                    if verdes > 0:
                        self.mago.regenerate_life(verdes)
                

                    # Azul → cura vida
                    if azuis > 0:
                        self.mago.regenerate_mana(azuis)

                    # Vermelho → regenera mana
                    if vermelhos > 0:
                        self.mago.anim_state = True
                        self.launch_spell(vermelhos)
                        # posiciona certinho
                        spell = self.current_spells[-1]
                        spell.x = self.mago.x + self.mago.width - 20
                        spell.y = self.mago.y + (self.mago.height // 3)

                    # Amarelo → opcional
                    # if amarelos > 0:
                    #     self.mago.apply_buff("ataque", amarelos)

                # limpa após processar tudo
                self.tetris.last_cleared_color_counts.clear()

            # Enemies animations
            
            # Draws
            self.ceu.draw()
            if len(self.current_clouds) >= 1:
                for cloud in self.current_clouds:
                    cloud.draw()
            self.chao.draw()
            life_color = (0, 245, 0) if self.mago.life >= 70 else (231, 245, 0) if 50 <= self.mago.life < 70 else (255, 0, 0)
            self.castelo.draw()
            self.mago.draw()
            self.tetris.draw()
            self.animate_enemies()
            self.update_spells()
            self.main_window.draw_text(f'LIFE: {self.mago.life}', self.mago.x, self.chao.y+25, 20, life_color, 'Arial', True, False)
            self.main_window.draw_text(f'MANA: {self.mago.mana}', self.mago.x + 100, self.chao.y+25, 20, (0, 0, 255), 'Arial', True, False)
            self.main_window.update()
            self.tetris.update()
