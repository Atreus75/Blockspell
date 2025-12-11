from PPlay.gameimage import *
from PPlay.mouse import *
from PPlay.sprite import *
from PPlay.window import *
from PPlay.animation import *
from PPlay.sound import Sound
from random import randint, choice
from time import time
from tetris import Tetris
from math import sin

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
        self.state = "walking"
        self.dash_speed = 500        # ataque violento
        self.return_speed = 350       # retorno rápido
        self.taking_hit = False
        self.hit_back_offset = 0
        self.hit_back_timer = 0
        self.origin_x = self.x
        self.image_file = image_file

    def move(self):
        self.x -= self.vel_x
    
    def take_damage(self, dmg):
        self.life -= dmg
        if self.life <= 0:
            self.alive = False

        # knockback simples
        self.taking_hit = True
        self.hit_back_offset = 10   # empurra um pouco pra direita
        self.hit_back_timer = 0.12
        self.origin_x = self.x

    def update_hit(self, dt):
        if not self.taking_hit:
            return

        self.hit_back_timer -= dt
        if self.hit_back_timer > 0:
            self.x = self.origin_x + self.hit_back_offset
        else:
            self.x = self.origin_x
            self.taking_hit = False


class Cachorro(Enemie):
    def __init__(self):
        image_file = 'src/inimigos/cachorro_spritesheet.png'
        super().__init__(image_file, frames=12, move_timeout=3, damage=10, life=100, vel_x=25, attack_cooldown=5)

class Gorila(Enemie):
    def __init__(self):
        image_file = 'src/inimigos/gorila_spritesheet.png'
        super().__init__(image_file, frames=6, move_timeout=5, damage=25, life=200, vel_x=15, attack_cooldown=8)

class Rato(Enemie):
    def __init__(self):
        image_file = 'src/inimigos/rato_spritesheet.png'
        super().__init__(image_file, frames=3, move_timeout=1, damage=2, life=50, vel_x=45, attack_cooldown=2)

class Mago(Sprite):
    def __init__(self, image_file, frames=1):
        super().__init__(image_file, frames)
        self.life = 100
        self.mana = 100
        self.life_limit = 100
        self.mana_limit = 100
        self.anim_state = False
        self.last_animation = 0.0
        self.imune = False
        self.imune_time = 1
        self.damage_multiplier = 1.0

        self.taking_hit = False
        self.hit_back_offset = 0
        self.hit_back_timer = 0
        self.origin_x = self.x

    def take_damage(self, dmg):
        self.life -= dmg
        if self.life < 0:
            self.life = 0

        # início da sacudida simples
        self.taking_hit = True
        self.hit_back_offset = -8     # leve empurrão para trás
        self.hit_back_timer = 0.15    # dura 0.15s
        self.origin_x = self.x
    
    def update_hit(self, dt):
        if not self.taking_hit:
            return

        self.hit_back_timer -= dt
        if self.hit_back_timer > 0:
            self.x = self.origin_x + self.hit_back_offset
        else:
            self.x = self.origin_x
            self.taking_hit = False
    
    def regenerate_life(self, points=0):
        total_regen = 10 * points
        self.life = self.life + total_regen if self.life + total_regen <= self.life_limit else self.life_limit
        
    def regenerate_mana(self, points=0):
        total_regen = 10 * points
        if self.mana < 50 and self.mana + points >= 50:
            Sound('src/sounds/thunder_disp.mp3').play()
        if self.mana < 100 and self.mana + points >= 100:
            Sound('src/sounds/shield_disp.mp3').play()
        self.mana = self.mana + total_regen if self.mana + total_regen <= self.mana_limit else self.mana_limit
    
class Spell(Sprite):
    def __init__(self, x=0, y=0):
        self.current_frame = 0
        self.current_collision_frame = 0
        self.image_path = 'src/bola_fodona/Bola_0.png'
        super().__init__(self.image_path)
        self.damage = 10
        self.last_animation = time()
        self.last_collision_animation = 0
        self.animation_timeout = 0.2
        self.state = "moving"  # "moving", "colliding", "finished"
        self.collided_with = None

        # Posição inicial (evita nascer fora da tela)
        self.x = x
        self.y = y
        self.scale = 1.0

class Rain(Sprite):
    def __init__(self, x=0, y=0, frames=None):
        super().__init__('src/açoes/raio/frame1.png')
        self.x = x
        self.y = y
        self.frames = frames or []
        self.current_frame = 0
        self.damage = 100.0
        self.last_animation = time()
        self.animation_timeout = 0.1
        self.finished = False
        self.wait = False
        self.has_hit = False  # garante que só dá dano uma vez
        self.enemy_hitbox_radius = 60  # tolerância do impacto

    def update(self, window, enemies):
        """Atualiza animação e aplica dano no frame do impacto."""
        now = time()
        if now - self.last_animation >= self.animation_timeout and self.current_frame != 4 or self.current_frame == 4 and now - self.last_animation >= 0.5:
            self.last_animation = now
            self.current_frame += 1

            # se acabou os frames, remove
            if self.current_frame >= len(self.frames):
                self.finished = True
                return

            # atualiza imagem
            self.image = self.frames[self.current_frame]

            # aplica dano no frame do impacto (ajuste fino)
            if self.current_frame == 4 and not self.has_hit:
                for enemy in enemies:
                    if enemy and abs(enemy.x - self.x) < self.enemy_hitbox_radius:
                        enemy.take_damage(self.damage)
                        Sound('src/sounds/spell_collision.wav').play()
                        if enemy.life <= 0:
                            enemy.alive = False
                        self.has_hit = True

        # desenha o raio em tela
        self.draw()

class BlockOption(Sprite):
    def __init__(self, image_path, color, shape, selection_box):
        super().__init__(image_path)
        self.color = color
        self.shape = shape
        self.image = pygame.transform.scale(self.image, (int(selection_box.width) - 20, int(selection_box.height/4 - 20)))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

class Shield(Sprite):
    def __init__(self, x=0, y=0, launch_time=0.0):
        super().__init__('src/açoes/escudo.png')
        self.x = x
        self.launch_time = launch_time
        self.duration = 5

class Upgrade(Sprite):
    def __init__(self, x=0, y=0, type='dmg'):
        super().__init__(f'src/hud/upgrade_{type}.png')
        self.x = x
        self.y = y
        self.type = type



class Menu:
    def __init__(self, mouse=Mouse(), window=Window(0, 0)):
        self.main_window = window

        self.player_mouse = mouse
        self.background = GameImage('src/menu/fundo_menu.jpg')
        self.background.image = pygame.transform.scale(self.background.image, (self.main_window.width, self.main_window.height))
        self.background.width = self.main_window.width
        self.background.height = self.main_window.height
        self.last_window_animation = 0
        
        self.start_sound = Sound('src/sounds/game_start.mp3')
        self.music = Sound('src/sounds/8bitheaven.mp3')
        self.music.loop = True
        self.music.play()


    def preset_blocks(self):
        # Pre-configures the little blocks for their background animation
        self.block_vely = 100
        self.blocks = [
            Sprite('src/peças/I_azul.png'),
            Sprite('src/peças/I_verde.png'),
            Sprite('src/peças/I_vermelho.png'),
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
            block.width = block.image.get_width()
            block.height = block.image.get_height()
            block.rect = block.image.get_rect()
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
                block.y = randint(-1000, -5) - block.height
                self.block_ocupied_positions.append(pos_x)
        for block in self.blocks:
            if self.main_window.mouse.is_over_object(block):
                block.y += self.block_vely * 3 * self.main_window.delta_time()
            else:
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
        init = time()

        self.preset_blocks()
        self.preset_play_btn()
        self.preset_mage()
        
        # Loop
        while True:
            # Verifications
            if not self.music.is_playing:
                self.music.play()

            if self.main_window.get_keyboard().key_pressed('ESC'):
                self.main_window.close()
                exit() # End window and the entire program
            
            now = time()
            if play_pressed and now - wait_blocks >= 5:
                break # End menu loop and goes to game loop

            if self.player_mouse.is_over_object(self.play_btn) and time() - init >= 0.5 and not play_pressed:
                mage_anim_interval = 0.005
                
                if self.player_mouse.is_button_pressed(1):
                    self.mage_hand1.y = self.origin_mage_hand1_y
                    self.mage_hand2.y = self.origin_mage_hand2_y
                    self.music.stop()
                    self.start_sound.play()
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
        self.score = 0

        self.ceu = Sprite('src/cenario/ceu.png')
        self.chao = Sprite('src/cenario/chao3.png')
        self.chao.y = self.main_window.height - (self.chao.height) + 30
        self.castelo = Sprite('src/cenario/castelo2.png')
        self.castelo.x = 0
        self.castelo.y = self.chao.y - self.castelo.height + 5
        self.mago = Mago('src/magos/mago_p.png')
        self.mago.x = (self.castelo.x + self.castelo.width - 20)
        self.mago.y = self.chao.y - self.mago.height + 5
        self.tetris = Tetris(self.main_window, 10, 15, 28, (self.main_window.width//2 - 190, self.main_window.height//2 - 350))
        self.selection_box = Sprite('src/cenario/select_back.png')
        self.selection_box.x = self.tetris.x - self.selection_box.width - 20
        self.selection_box.y = self.tetris.y + 70

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

        self.block_sprites = [
            'src/peças/I_azul.png',
            'src/peças/I_verde.png',
            'src/peças/I_vermelha.png',
            'src/peças/L_azul.png',
            'src/peças/L_verde.png',
            'src/peças/L_vermelho.png',
            'src/peças/O_azul.png',
            'src/peças/O_verde.png',
            'src/peças/O_vermelho.png',
            'src/peças/S_azul.png',
            'src/peças/S_verde.png',
            'src/peças/S_vermelho.png',
            'src/peças/T_azul.png',
            'src/peças/T_verde.png',
            'src/peças/T_vermelho.png'
        ]
        self.block_colors = [
            'vermelho',
            'azul',
            'verde'
        ]
        self.block_shapes = [
            'I',
            'O',
            'L',
            'S',
            'T'
        ]
        
        self.current_block_options = []
        self.last_piece_choice = 0

        self.enemy_slots = [None, None, None]  # 3 posições fixas
        self.slot_positions = [
            self.mago.x + 300,  # Posição mais próxima
            self.mago.x + 450,  # Posição intermediária
            self.mago.x + 600  # Posição mais distante
        ]
        self.slot_damage_multiplier = [1.0, 0.7, 0.4]  # Dano reduzido conforme distância
        self.last_enemy_gen = time()
        self.current_spells = []
        self.spell_velx = 200
        self._load_spell_assets()
        self.current_rain_clouds = []
        
        self.rain_frames = [
            pygame.image.load(f'src/açoes/raio/frame{i}.png').convert_alpha()
            for i in range(1, 9)
        ]
        self.current_rains = []
        self.last_rain_gen = 0

        # Life regen stuff
        self.last_life_regen_frame_change = 0
        self.regen_life_frames = [
            pygame.transform.scale(pygame.image.load(f'src/açoes/rec_vida/rec_vida{i}.png'), (self.mago.width+20, self.mago.height+20))
            for i in range(1, 8)
        ]
        self.life_regenerations = []
        self.life_regen_frame = 0

        # Mana regen stuff
        self.last_mana_regen_frame_change = 0
        self.regen_mana_frames = [
            pygame.transform.scale(pygame.image.load(f'src/açoes/rec_mana/rec_mana{i}.png'), (self.mago.width+20, self.mago.height+20))
            for i in range(1, 7)
        ]
        self.mana_regenerations = []
        self.mana_regen_frame = 0

        self.now = time()

        # Difficulty stuff
        self.next_threshold = 500
        self.difficulty_stage = 0
        # multiplicadores cumulativos aplicados a inimigos
        self.dmg_multiplier = 1.0
        self.speed_multiplier = 1.0
        self.recoil_multiplier = 1.0
        self.cooldown_multiplier = 1.0
        self.life_multiplier = 1.0
        
        self.hud_book = Sprite('src/hud/spell_book.png')
        self.hud_book.x = self.mago.x - 100
        self.hud_book.y = self.chao.y + 20
        self.hud_shield = Sprite('src/hud/escudo.png')
        self.hud_shield.x = self.hud_book.x + 5
        self.hud_shield.y = self.hud_book.y + self.hud_book.height/2 - self.hud_shield.height/2
        self.hud_rain = Sprite('src/hud/raio.png')
        self.hud_rain.x = self.hud_shield.x + self.hud_shield.width + 5
        self.hud_rain.y = self.hud_shield.y
        
        self.current_shields = []

        self.player_life_mult = 1.0
        self.player_mana_mult = 1.0
        self.player_damage_mult = 1.0
        self.shield_duration_mult = 1.0

        self.shield_unlocked = False
        self.thunder_unlocked = False

    def upgrade_loop(self):

        back_screen = Sprite('src/hud/upgrade-background.png')
        back_screen.y = self.main_window.height/2 - back_screen.height/2
        back_screen.x = self.main_window.width/2 - back_screen.width/2
        options = ['dmg', 'life', 'mana']
        if not self.shield_unlocked:
            options.append('shield')
        if not self.thunder_unlocked:
            options.append('thunder')
        op1 = choice(options)
        options.remove(op1)
        op2 = choice(options)

        op1 = Upgrade(type=op1)
        op1.x = int(back_screen.x + back_screen.width/2 - op1.width - 50)
        op2 = Upgrade(type=op2)
        op2.x = int(back_screen.x + back_screen.width/2 + 50)
        final = op1
        op1.y = int(back_screen.y + back_screen.height/2 - op1.height/2)
        op2.y = op1.y

        mouse = self.main_window.get_mouse()
        while True:
            if mouse.is_over_object(op1):
                if mouse.is_button_pressed(1):
                    final = op1
                    break
            elif mouse.is_over_object(op2):
                if mouse.is_button_pressed(1):
                    final = op2
                    break
            self.ceu.draw()
            self.castelo.draw()
            self.chao.draw()
            back_screen.draw()
            self.main_window.draw_text('OS DEUSES DAS FORMAS LHE DÃO FORÇAS', int(back_screen.x+back_screen.width/2 - 150), back_screen.y + 50, 20, (255, 0, 0), 'freemono', True, False)
            op1.draw()
            op2.draw()
            self.main_window.update()

        if final.type == 'damage':
            self.mago.damage_multiplier *= 1.25
        elif final.type == 'life':
            self.mago.life_limit = int(self.mago.life_limit * 1.25)
        elif final.type == 'mana':
            self.mago.mana_limit = int(self.mago.mana_limit * 1.25)
        elif final.type == 'thunder':
            self.thunder_unlocked = True
            Sound('src/sounds/thunder_disp.mp3')
        elif final.type == 'shield':
            self.shield_unlocked = True
            Sound('src/sounds/shield_disp.mp3')
 
    def regen_life(self):
        if len(self.life_regenerations) > 0:
            if self.life_regen_frame >= 6:
                self.life_regen_frame = 0
                self.life_regenerations = []
            elif self.now - self.last_life_regen_frame_change >= 0.5:
                self.life_regen_frame += 1
                for lr in self.life_regenerations:
                    lr.x = self.mago.x - 5
                    lr.y = self.mago.y + self.mago.height/2 - 25
                    nf = self.life_regen_frame
                    lr.image = self.regen_life_frames[self.life_regen_frame]
                    lr.draw()
                self.last_mana_regen_frame_change = self.now

    def regen_mana(self):
        if len(self.mana_regenerations) > 0:
            if self.mana_regen_frame >= 5:
                self.mana_regen_frame = 0
                self.mana_regenerations = []
            elif self.now - self.last_mana_regen_frame_change >= 0.5:
                self.mana_regen_frame += 1
                for mr in self.mana_regenerations:
                    mr.x = self.mago.x - 5
                    mr.y = self.mago.y + self.mago.height/2 - 25
                    nf = self.mana_regen_frame
                    mr.image = self.regen_mana_frames[self.mana_regen_frame]
                    mr.draw()
                self.last_regen_frame_change = self.now


    def _maybe_increase_difficulty(self):
        """
        Verifica se passou o próximo threshold de score.
        Ao passar, dobra a próxima marca e aumenta os multiplicadores.
        Aplica o efeito aos inimigos já existentes.
        """
        if self.score < self.next_threshold:
            return

        # parâmetros de subida (ajuste se quiser mais/menos agressivo)
        dmg_mul = 1.5        # +15% dano
        speed_mul = 1.5      # +10% velocidade de movimento
        recoil_mul = 1.10     # +10% intensidade de recuo (visível)
        cooldown_mul = 0.95   # -5% no cooldown entre ataques (mais agressivo)
        life_mul = 1.5

        # atualiza estágio / próxima meta
        self.difficulty_stage += 1
        self.next_threshold *= 3

        # acumula nos multiplicadores gerais
        self.dmg_multiplier *= dmg_mul
        self.speed_multiplier *= speed_mul
        self.recoil_multiplier *= recoil_mul
        self.cooldown_multiplier *= cooldown_mul
        self.life_multiplier *= life_mul

        # aplica imediatamente aos inimigos já existentes nos slots
        for e in self.enemy_slots:
            if not e:
                continue
            # ajuste seguro (int para dano)
            try:
                e.damage = int(e.damage * dmg_mul)
            except Exception:
                pass
            try:
                e.vel_x = e.vel_x * speed_mul
            except Exception:
                pass
            try:
                # se a propriedade existir
                if hasattr(e, 'attack_recoil'):
                    e.attack_recoil = e.attack_recoil * recoil_mul
            except Exception:
                pass
            try:
                # reduz o cooldown (mais agressivo). limite mínimo
                if hasattr(e, 'attack_cooldown'):
                    e.attack_cooldown = max(0.1, e.attack_cooldown * cooldown_mul)
            except Exception:
                pass

        self.upgrade_loop()

    def placar(self):
        self.main_window.draw_text(f"Score: {self.score}", 10, 40, size=25, color=(255, 255, 255))

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
        """Garante até 3 inimigos em fila da esquerda pra direita."""
        # Remove mortos
        for i in range(3):
            e = self.enemy_slots[i]
            if e and not e.alive:
                self.enemy_slots[i] = None

        # Avança os de trás para frente se houver espaço
        for i in range(2):
            if self.enemy_slots[i] is None and self.enemy_slots[i + 1]:
                self.enemy_slots[i] = self.enemy_slots[i + 1]
                self.enemy_slots[i + 1] = None
                self.enemy_slots[i].target_slot = i

        # Gera novos inimigos sempre na posição mais à direita disponível
        for i in range(2, -1, -1):
            if self.enemy_slots[i] is None:
                choose = randint(0, 19)
                if 0 <= choose <= 9:
                    e = Cachorro()
                elif 10 <= choose <= 13:
                    e = Gorila()
                else:
                    e = Rato()
                
                # nasce fora da tela, anda até o slot
                e.x = self.main_window.width + randint(50, 100)
                e.y = self.chao.y - e.height + 5
                e.target_slot = i
                e.state = "walking"
                e.alive = True
                e.last_attack = self.now
                self.enemy_slots[i] = e
                
                # aplica multiplicadores atuais (faz novos inimigos já nascerem mais fortes)
                try:
                    e.damage = int(e.damage * self.dmg_multiplier)
                except Exception:
                    pass
                try:
                    e.vel_x = e.vel_x * self.speed_multiplier
                except Exception:
                    pass
                try:
                    if hasattr(e, 'attack_recoil'):
                        e.attack_recoil = e.attack_recoil * self.recoil_multiplier
                except Exception:
                    pass
                try:
                    if hasattr(e, 'attack_cooldown'):
                        e.attack_cooldown = max(0.1, e.attack_cooldown * self.cooldown_multiplier)
                except Exception:
                    pass
                e.life *= self.life_multiplier

                self.enemy_slots[i] = e

    def launch_shield(self):
        self.mago.mana -= 100
        if not self.mago.imune:
            self.mago.imune = True
        shield = Shield(launch_time=self.now)
        x = int(self.mago.x + self.mago.width/2 - shield.width/2) + randint(-5, 5)
        y = self.chao.y - shield.height + 10
        shield.x = x
        shield.y = y
        self.current_shields.append(shield)
    
    def update_shield(self):
        for shield in self.current_shields:
            if isinstance(shield, Shield):
                if self.now - shield.launch_time >= shield.duration:
                    self.current_shields.remove(shield)
                else:
                    shield.draw()
        if len(self.current_shields) <= 0:
            self.mago.imune = False

    def launch_rain(self):
        """Lança um raio sobre cada inimigo visível, respeitando cooldown individual.
        agora: cria nuvem+raio só quando for realmente spawnar o raio, e alinha o raio à superfície do chão.
        """
        # custo de mana (mantive teu comportamento)
        self.mago.mana -= 50
        any_spawned = False

        for enemy in self.enemy_slots:
            if not enemy:
                continue

            # cooldown individual de cada inimigo
            if not hasattr(enemy, "last_rain_time"):
                enemy.last_rain_time = 0

            if self.now - enemy.last_rain_time >= 1.5:
                enemy.last_rain_time = self.now

                # cria nuvem posicionada sobre o inimigo (apenas agora, quando vamos realmente spawnar)
                nuvem = Sprite('src/cenario/nuvem_raio.png')
                nuvem.width = nuvem.image.get_width()
                nuvem.height = nuvem.image.get_height()
                nuvem.x = int(enemy.x + enemy.width / 2 - nuvem.width / 2)
                nuvem.y = -5

                # cria o raio e alinha X ao centro do inimigo
                raio = Rain(0, 0, self.rain_frames)
                # garante que width/height estejam atualizados
                raio.width = raio.image.get_width()
                raio.height = raio.image.get_height()
                raio.x = int(enemy.x + enemy.width / 2 - raio.width / 2)

                # coloca o raio de forma que sua base coincida com o topo do chão:
                # => raio.y + raio.height == self.chao.y
                raio.y = int(self.chao.y - raio.height) + 5
                raio.damage *= self.mago.damage_multiplier
                # agora sim adiciona ambos às listas (permite manter sincronização por índice)
                self.current_rain_clouds.append(nuvem)
                self.current_rains.append(raio)
                any_spawned = True

        print(f"[DEBUG] Raios ativos: {len(self.current_rains)} (spawned={any_spawned})")


    def update_rain(self):
        """Atualiza todos os raios ativos. mantém listas sincronizadas."""
        for idx in range(len(self.current_rains) - 1, -1, -1):
            rain = self.current_rains[idx]
            cloud = self.current_rain_clouds[idx]

            # atualiza o raio (a própria função desenha também)
            rain.update(self.main_window, self.enemy_slots)
            cloud.draw()

            # quando terminar, remove nuvem+raio mantendo os índices alinhados
            if rain.finished:
                try:
                    self.current_rains.pop(idx)
                    self.current_rain_clouds.pop(idx)
                except Exception:
                    # segurança caso algo estranho aconteça
                    pass
                
    def launch_spell(self, power=1):
        """Cria e adiciona um novo feitiço ofensivo escalonado visualmente pelo dano."""
        x = self.mago.x + self.mago.width - 20
        y = self.mago.y + self.mago.height // 3

        spell = Spell(x, y)
        spell.state = "moving"
        spell.current_frame = 0
        spell.current_collision_frame = 0
        spell.last_animation = self.now
        spell.last_collision_animation = 0
        spell.animation_timeout = 0.08
        spell.damage *= power  # dano proporcional à força

        # --- Escala visual conforme dano ---
        scale = 1.0 + (spell.damage / 100)/2
        if scale > 4:
            scale = 4
        elif scale < 1.0:
            scale = 1.0

        w = int(spell.width * scale)
        h = int(spell.height * scale)
        spell.image = pygame.transform.scale(spell.image, (w, h))
        spell.width = w
        spell.height = h
        spell.rect = spell.image.get_rect(topleft=(spell.x, spell.y))
        spell.scale = scale

        print(f'Spell lançado com dano {spell.damage} (escala {scale:.2f}x)')
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
                if self.now - spell.last_animation >= spell.animation_timeout:
                    spell.last_animation = self.now
                    spell.current_frame = (spell.current_frame + 1) % 5
                    spell.image = self.spell_frames[spell.current_frame]
                    spell.image = pygame.transform.scale(spell.image, (spell.image.get_width()*spell.scale, spell.image.get_height()*spell.scale))
                    spell.width = spell.image.get_width()
                    spell.height = spell.image.get_height()
                    spell.rect = spell.image.get_rect(topleft=(spell.x, spell.y))
                    spell.y = self.mago.y + self.mago.height//2 - spell.height//2 + 25

                # colisão com inimigos
                for enemy in self.enemy_slots:
                    if not enemy:
                        continue  # slot vazio
                    if spell.collided_perfect(enemy):
                        damage = spell.damage
                        spell.damage -= enemy.life
                        if spell.damage <= 0:
                            spell.state = "colliding"
                            spell.collided_with = enemy
                            spell.last_collision_animation = self.now
                        enemy.take_damage(damage)
                        Sound('src/sounds/spell_collision.wav').play()
                        spell.scale -= 0.5

                        # inimigo morre?
                        if enemy.life <= 0:
                            enemy.alive = False
                            self.score += 100 if isinstance(enemy, Rato) else 200 if isinstance(enemy, Cachorro) else 300

                        break 

                # saiu da tela
                if spell.x > self.main_window.width:
                    spell.state = "finished"

            # COLISÃO / EXPLOSÃO
            elif spell.state == "colliding":
                if self.now - spell.last_collision_animation >= spell.animation_timeout:
                    spell.last_collision_animation = self.now
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

    def draw_bars(self):
        x = self.mago.x + 60
        life_y = self.chao.y + 30
        life_bar_w = self.mago.life
        life_bar_h = 10
        life_back_bar_w = self.mago.life_limit
        life_back_bar_h = 10
        life_color = (153,163,163) if self.mago.imune else (0, 245, 0) if self.mago.life >= self.mago.life_limit/100*70 else (231, 245, 0) if self.mago.life_limit/100*50 <= self.mago.life < self.mago.life_limit/100*70 else (255, 0, 0)
        # Life back 
        pygame.draw.rect(self.main_window.get_screen(), (153,163,163), (x, life_y, life_back_bar_w, life_back_bar_h))
        # Life bar
        pygame.draw.rect(self.main_window.get_screen(), life_color, (x, life_y, life_bar_w, life_bar_h))

        mana_y = self.chao.y + 60
        mana_bar_w = self.mago.mana
        mana_bar_h = 10
        mana_back_bar_w = self.mago.mana_limit
        mana_back_bar_h = 10
        # Mana back
        pygame.draw.rect(self.main_window.get_screen(), (153,163,163), (x, mana_y, mana_back_bar_w, mana_back_bar_h))
        pygame.draw.rect(self.main_window.get_screen(), (0, 0, 255), (x, mana_y, mana_bar_w, mana_bar_h))


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
        """Atualiza movimento, ataques e animações dos inimigos por slot."""
        for i, e in enumerate(self.enemy_slots):
            if not e:
                continue

            target_x = self.slot_positions[e.target_slot]

            # --- 1️⃣ Movimento até o slot ---
            if e.state == "walking":
                e.x -= e.vel_x * self.main_window.delta_time()
                e.update()
                e.update_hit(self.main_window.delta_time())

                # chegou no slot (com margem de 2px)
                if e.x <= target_x + 2:
                    e.x = target_x
                    e.state = "attacking"
                    e.image = pygame.image.load(e.image_file).convert_alpha()  # garante frame neutro

            # --- 2️⃣ Ataque à distância (corporal) ---
            elif e.state == "attacking":
                if self.now - e.last_attack >= e.attack_cooldown:
                    e.last_attack = self.now
                    e.state = "dashing"
                    e.origin_x = e.x

            # --- DASH até o mago ---
            elif e.state == "dashing":
                e.x -= e.dash_speed * self.main_window.delta_time()

                # quando alcança o mago → causa dano e começa voltar
                if e.x <= self.mago.x + 30:
                    if not self.mago.imune:
                        self.mago.take_damage(e.damage)
                        Sound('src/sounds/player_hit.wav').play()
                    e.state = "returning"

            # --- Voltando ao slot ---
            elif e.state == "returning":
                e.x += e.return_speed * self.main_window.delta_time()

                if e.x >= target_x:
                    e.x = target_x
                    e.state = "attacking"

            e.draw()


    def animate_mage(self):
        if self.mago.anim_state == True and self.mago.last_animation == 0:
            self.mago.image = pygame.image.load(f"src/magos/mago_atk.png").convert_alpha()
            self.mago.last_animation = self.now
        elif self.now - self.mago.last_animation >= 0.5:
            self.mago.image = pygame.image.load(f"src/magos/mago_p.png").convert_alpha()
            self.mago.anim_state = False 
            self.mago.last_animation = 0

    def update_select_box(self):
        # Generate new block options and visually aligns it
        if len(self.current_block_options) < 4:
            if randint(0, 10) == randint(0, 10):
                color = 'amarelo'
                shape = 'O'
                complete_block_name = 'peça_dourada.png'
            else:
                random_value = randint(0, 10)
                if random_value <= 7:
                    color = choice(['vermelho', 'verde'])
                else:
                    color = choice(['vermelho', 'azul'])
                shape = choice(self.block_shapes)
                complete_block_name = f'{shape}_{color}.png'
            
            block = BlockOption(f'src/peças/{complete_block_name}', color, shape, self.selection_box)
            block.x = self.selection_box.x + self.selection_box.width/2 - block.width/2
            block.y = self.selection_box.y + self.selection_box.height - block.height if len(self.current_block_options) == 0 else self.current_block_options[-1].y - block.height - 25
            self.current_block_options.append(block)

        # Draws current options and aligns it
        self.selection_box.draw()
        controls = ['R', 'E', 'W', 'Q']
        for c in range(0, len(self.current_block_options)):
            option = self.current_block_options[c]
            self.main_window.draw_text(f'{controls[c]}', self.selection_box.x - 50, option.y, 20, (0, 0, 0), 'freemono', True, False)
            option.y = self.selection_box.y + self.selection_box.height - option.height if c == 0 else self.current_block_options[c-1].y - option.height - 25
            option.draw()

    def create_piece(self):
        controls = ['R', 'E', 'W', 'Q']
        for c in range(4):
            if self.main_window.keyboard.key_pressed(controls[c]) and not self.tetris.falling_piece and self.now - self.last_piece_choice >= 0.5 or self.now - self.tetris.last_locked_piece >= 3 and not self.tetris.falling_piece:
                self.last_piece_choice = self.now
                option = self.current_block_options[c]
                shape = option.shape
                color = option.color
                self.current_block_options.remove(option)
                self.tetris.spawn_piece_manual(shape, color)
                return

    def game_loop(self):
        soundtrack = Sound('src/sounds/game_soundtrack.wav')
        soundtrack.loop = True
        soundtrack.play()
        soundtrack.decrease_volume(20)

        last_limit_increse = 0
        kb = self.main_window.get_keyboard()
        last_key_state = {"1": False, "2": False, "ESC": False}
        while True:
            self.now = time()
            current_1 = kb.key_pressed("1") and self.thunder_unlocked
            current_2 = kb.key_pressed("2") and self.shield_unlocked
            current_ESC = kb.key_pressed("ESC")

            # Aumenta o limite de inimigos a cada 60 segundos usando o total time
            if self.now - last_limit_increse >=60:
                last_limit_increse = self.now
                self.enemie_limit += 1
            
            self.main_window.set_background_color('black')

            # Verificação de pressionamento das teclas
            if current_1 and not last_key_state["1"]:
                if self.mago.mana >= 50:
                    self.launch_rain()
                    print(f'{len(self.current_rains)} rains in game.')
            elif current_2 and not last_key_state["2"]:
                if self.mago.mana >= 100:
                    self.launch_shield()
            elif current_ESC and not last_key_state["ESC"]:
                pygame.time.wait(150)
                resultado = self.pause_menu()
                if resultado == "menu":
                    break

            if self.mago.life <= 0: # game over
                soundtrack.stop()
                break
            
            if self.tetris.game_over:
                self.tetris.reset()
            self.animate_clouds()
            self._maybe_increase_difficulty()
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

                    if amarelos > 0:
                        verdes *= 2
                        azuis *= 2
                        vermelhos *= 2
                    
                    # Verde → lança feitiço ofensivo
                    if verdes > 0:
                        self.mago.regenerate_life(verdes)
                        for c in range(0, verdes):
                            lr  = Sprite('src/açoes/rec_vida/rec_vida1.png')
                            lr.width = lr.image.get_width()
                            lr.height = lr.image.get_height()
                            lr.x = self.mago.x - 5
                            lr.y = self.mago.y + self.mago.height/2 - 10
                            self.life_regenerations.append(lr)
                        self.last_life_regen_frame_change = self.now

                    # Azul → cura vida
                    if azuis > 0:
                        self.mago.regenerate_mana(azuis)
                        for c in range(azuis):
                            mr = Sprite('src/açoes/rec_mana/rec_mana1.png')
                            mr.width = mr.image.get_width()
                            mr.height = mr.image.get_height()
                            mr.x = self.mago.x - 5
                            mr.y = self.mago.y + self.mago.height/2 - 10
                            self.mana_regenerations.append(mr)
                        self.last_mana_regen_frame_change = self.now


                    # Vermelho → regenera mana
                    if vermelhos > 0:
                        self.mago.anim_state = True
                        self.launch_spell(vermelhos)
                        # posiciona certinho
                        spell = self.current_spells[-1]
                        spell.x = self.mago.x + self.mago.width - 20
                        spell.y = self.mago.y + self.mago.height//2 - spell.height//2


                # limpa após processar tudo
                self.tetris.last_cleared_color_counts.clear()
            
            # Draws
            self.ceu.draw()
            if len(self.current_clouds) >= 1:
                for cloud in self.current_clouds:
                    cloud.draw()
            self.chao.draw()
            self.castelo.draw()
            self.mago.update_hit(self.main_window.delta_time())
            self.mago.draw()
            self.placar()
            self.tetris.draw()
            self.animate_enemies()
            self.regen_life()
            self.regen_mana()
            self.update_spells()
            self.update_shield()
            self.update_rain()
            self.update_select_box()
            self.create_piece()

            self.main_window.draw_text(f'LIFE: ', self.mago.x, self.chao.y+25, 20, (0, 255, 0), 'freemono', True, False)
            self.main_window.draw_text(f'MANA: ', self.mago.x, self.chao.y+50, 20, (0, 0, 255), 'freemono', True, False)
            self.draw_bars()

            if self.mago.mana >= 50 and self.thunder_unlocked:
                self.hud_rain.unhide()
            else:
                self.hud_rain.hide()
            
            if self.mago.mana >= 100 and self.shield_unlocked:
                self.hud_shield.unhide()
            else:
                self.hud_shield.hide()
            self.hud_book.draw()
            self.hud_rain.draw()
            self.hud_shield.draw()
            self.main_window.update()
            self.tetris.update()
            last_key_state["1"] = current_1
            last_key_state["2"] = current_2
            last_key_state["ESC"] = current_ESC
