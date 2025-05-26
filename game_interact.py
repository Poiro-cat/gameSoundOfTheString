import sys
import pygame
from configs import PATH
from game_init import GameCore
from pgu import gui

class AskWindow(gui.Dialog):
    def __init__(this):
        title = gui.Label('test')
        label = gui.Label('hahaha')
        gui.Dialog.__init__(this, title, label)


################ 游戏交互事件 ################

class GameInteract(GameCore):
    
    #======== 键盘操作 ========#
    def handle_keydown(self, key):
        if key == pygame.K_SPACE:
            if self.current_scene != 'menu': self.to_menu()
            else: self.game_continue()
        elif not self.full_screen and key == pygame.K_F11:
            self.full_screen = True
            self.window = pygame.display.set_mode(self.full_screen_size, pygame.FULLSCREEN)
        elif self.full_screen and key in [pygame.K_F11, pygame.K_ESCAPE]:
            self.full_screen = False
            self.window = pygame.display.set_mode(self.window_size, flags=pygame.RESIZABLE)
    
    #======== 鼠标操作 ========#
    def handle_click(self, x, y, button):
        if button != 1: return
        kx = (x-self.vision_pos.x) / self.scene_size.x
        ky = (y-self.vision_pos.y) / self.scene_size.y
        # 主菜单界面按钮：新游戏，继续游戏，退出
        if self.current_scene == 'menu':
            if self.button_new_game.collidepoint(x, y):
                self.new_game_start()
            elif self.game_started and self.button_continue.collidepoint(x, y):
                self.game_continue()
            elif self.button_exit.collidepoint(x, y):
                self.game_quit()
        # 游戏：菜单图标
        elif self.button_menu.collidepoint(x, y): self.to_menu()
        # 游戏：道具栏
        elif 1 < kx < self.vision_size.x/self.scene_size.x and 0 < ky < 1:
            i = 0
            while not self.item_buttons[i].collidepoint(x, y):
                i += 1
                if i == self.item_column_num: return
            if self.chosen_column is None:
                if self.item_column[i] is not None: self.chosen_column = i # 未选中任何道具，则选中该道具
            elif self.chosen_column == i: self.chosen_column = self.showing_detail = None # 已选中该道具，则取消选中
            elif self.item_column[self.chosen_column] is not None and self.item_column[i] is None: # 已选中其他道具，该栏为空，则移动道具
                self.item_column[i] = self.item_column[self.chosen_column]
                self.item_column[self.chosen_column] = None
                self.chosen_column = None
            else: self.chosen_column = i
            if self.chosen_item() in ['music_book', 'instrument_pics', 'letter']:
                self.showing_detail = self.chosen_item()
        # 游戏：下箭头
        elif self.showing_detail is not None:
            if self.button_go_back.collidepoint(x, y): self.showing_detail = self.chosen_column = None
            elif self.showing_detail == 'music_book' and self.button_book.collidepoint(kx, ky): self.showing_detail = 'music_book_open'
        elif 'zoom' in self.current_scene and self.button_go_back.collidepoint(x, y):
            if self.current_scene in ['zoom_photo', 'zoom_peephole']: self.change_to_scene('wall_door')
            elif self.current_scene in ['zoom_pillow', 'zoom_cupboard']: self.change_to_scene('wall_window')
            elif self.current_scene in ['zoom_chest_big', 'zoom_guitar']: self.change_to_scene('wall_guitar')
            elif self.current_scene in ['zoom_radio', 'zoom_drawer', 'zoom_book', 'zoom_chest']: self.change_to_scene('wall_desk')
        # 游戏：左箭头
        elif 'wall' in self.current_scene and self.button_go_left.collidepoint(x, y):
            if self.current_scene == 'wall_door': self.change_to_scene('wall_desk')
            elif self.current_scene == 'wall_window': self.change_to_scene('wall_door')
            elif self.current_scene == 'wall_guitar': self.change_to_scene('wall_window')
            elif self.current_scene == 'wall_desk': self.change_to_scene('wall_guitar')
        # 游戏：右箭头
        elif 'wall' in self.current_scene and self.button_go_right.collidepoint(x, y):
            if self.current_scene == 'wall_door': self.change_to_scene('wall_window')
            elif self.current_scene == 'wall_window': self.change_to_scene('wall_guitar')
            elif self.current_scene == 'wall_guitar': self.change_to_scene('wall_desk')
            elif self.current_scene == 'wall_desk': self.change_to_scene('wall_door')
        # 游戏场景框内
        elif self.button_scene.collidepoint(x, y):
            print('Click inside the scene:', (kx,ky))
            # 场景：第一面墙，门，床侧面，乐队照片
            if self.current_scene == 'wall_door':
                if self.button_photo.collidepoint(x, y) or (self.band_photo_complete and not self.got_items['string'][2] and self.button_string.collidepoint(x, y)): self.change_to_scene('zoom_photo') # 照片近景
                elif self.door_unlocked:
                    pass
                else:
                    if self.button_peephole.collidepoint(kx, ky): self.change_to_scene('zoom_peephole') # 猫眼
                    elif self.button_lock.collidepoint(kx, ky): pass
                    elif self.button_door.collidepoint(x, y): pass
            # 场景：第二面墙，窗户，床正面，床头柜
            elif self.current_scene == 'wall_window':
                if self.curtain_open and not self.got_items['plectrum'][2] and self.button_plectrum.collidepoint(x, y):
                    self.get_item('plectrum', 2) # 获得拨片3
                elif self.button_curtain.collidepoint(kx, ky): self.curtain_open = not self.curtain_open # 拉开/放下窗帘
                elif self.button_pillow.collidepoint(x, y): self.change_to_scene('zoom_pillow') # 枕头近景
                elif self.button_cupboard.collidepoint(x, y): self.change_to_scene('zoom_cupboard') # 床头柜近景
            # 场景：第三面墙，吉他，乐谱，大箱子
            elif self.current_scene == 'wall_guitar':
                if 0: pass
                elif self.button_paper.collidepoint(x, y):
                    if self.music_paper_lifted and not self.got_items['my_photo']: self.get_item('my_photo')
                    else: self.music_paper_lifted = not self.music_paper_lifted
                elif self.button_chest.collidepoint(x, y): self.change_to_scene('zoom_chest_big')
                
                
            # 场景：第四面墙，书桌，收音机，书架
            elif self.current_scene == 'wall_desk':
                if self.button_book.collidepoint(kx, ky): self.change_to_scene('zoom_book')
                elif self.button_chest.collidepoint(x, y): self.change_to_scene('zoom_chest')
            
            
            
            # 场景：拉近，乐队照片
            elif self.current_scene == 'zoom_photo':
                if self.button_photo.collidepoint(kx, ky) and self.chosen('my_photo'):
                    self.use_chosen_item()
                    self.band_photo_complete = True
                elif self.band_photo_complete and not self.got_items['string'][2]  and self.button_string.collidepoint(x, y):
                    self.get_item('string', 2)
            # 场景：拉近，床上枕头
            elif self.current_scene == 'zoom_pillow':
                if not self.pillow_scratched and self.chosen('knife') and self.button_pillow.collidepoint(x, y):
                    self.use_chosen_item()
                    self.pillow_scratched = True
                elif self.pillow_scratched and not self.got_items['instrument_pics'] and self.button_card.collidepoint(kx, ky):
                    self.get_item('instrument_pics')
            # 场景：拉近，床头柜
            elif self.current_scene == 'zoom_cupboard':
                if not self.cupboard_unlocked and any(button.collidepoint(x, y) for button in self.button_music_note):
                    i = 0
                    while not self.button_music_note[i].collidepoint(x, y): i += 1
                    self.cupboard_code[i] += 1
                    self.cupboard_code[i] %= 4
                    if self.cupboard_code == [1, 0, 3, 2]:
                        self.cupboard_unlocked = True
                        print('Cupboard unlocked with correct music notes.')
                elif self.cupboard_unlocked:
                    if self.cupboard_open and not self.got_items['plectrum'][1] and self.button_plectrum.collidepoint(x, y): self.get_item('plectrum',1)
                    elif self.cupboard_open and not self.got_items['string'][1] and self.button_string.collidepoint(x, y): self.get_item('string',1)
                    elif self.button_cupboard.collidepoint(kx, ky): self.cupboard_open = not self.cupboard_open
                    
            # 场景：拉近，大箱子（拨片）
            elif self.current_scene == 'zoom_chest_big':
                if not self.chest_big_unlocked and self.chosen('plectrum') \
                and any(button.collidepoint(kx, ky) for button in self.button_chest_hole):
                    self.use_chosen_item()
                    i = 0
                    while not self.button_chest_hole[i].collidepoint(kx, ky): i += 1
                    self.plectrum_on_chest[i] = True
                    if all(self.plectrum_on_chest):
                        self.chest_big_unlocked = True
                        print('Chest_big unlocked with 3 plectrums.')
                elif self.chest_big_unlocked and self.button_chest.collidepoint(x, y):
                    self.chest_big_open = not self.chest_big_open
                    
            
            
            
            
    #======== 新游戏，菜单，继续游戏，退出 ========#
    def new_game_start(self):
        if self.game_started and 0:
            app = gui.App()
            container = gui.Container(align=-1, valign=-1)
            ask = AskWindow()
            button_ = gui.Button('nei')
            button_.connect(gui.CLICK, ask.open, None)
            container.add(button_, 0, 0)
            app.init(container)
        print('New game start')
        self.initialize_state()
        self.change_to_scene('wall_window')
        self.play_music('beethoven', -1, 0.2)
    def to_menu(self):
        print('Go to menu')
        self.saved_scene = self.current_scene
        self.change_to_scene('menu')
        self.play_music('rock', -1, 0.1)
    def game_continue(self):
        print('Continue game.')
        self.change_to_scene(self.saved_scene)
        self.play_music('beethoven', -1, 0.2)
    def game_quit(self):
        print('Quit game.')
        pygame.mixer.music.stop()
        pygame.quit()
        sys.exit()
    
    #======== 获得道具 ========#
    def get_item(self, item, index=None):
        print('Get item:', (item, index))
        if item in ['plectrum','string']: self.got_items[item][index] = True
        else: self.got_items[item] = True
        for i in range(self.item_column_num):
            if self.item_column[i] is None:
                self.item_column[i] = item
                break
        if item in ['music_book', 'instrument_pics', 'my_photo']:
            self.chosen_column = i
            self.showing_detail = item
        assert self.item_column[i] == item, 'Item column full !'
    
    #======== 消耗道具 ========#
    def use_chosen_item(self):
        assert self.chosen_column is not None and self.item_column[self.chosen_column] is not None
        print('Used item:', self.item_column[self.chosen_column])
        self.item_column[self.chosen_column] = None
        self.chosen_column = None

    #======== 返回当前选中道具 ========#
    def chosen_item(self):
        if self.chosen_column is None: return None
        return self.item_column[self.chosen_column]

    #======== 判断道具是否被选中 ========#
    def chosen(self, item):
        if self.chosen_column is None: return False
        return self.item_column[self.chosen_column] == item
    
    #======== 切换场景 ========#
    def change_to_scene(self, new_scene):
        print('Change to scene:', new_scene)
        self.scene_changing = 1 + int(self.current_scene == 'menu' or new_scene == 'menu')
        self.time_marker = pygame.time.get_ticks()
        self.next_scene = new_scene
    
    #======== 播放/切换音乐 ========#
    def play_music(self, music, loops, volume):
        print('Play music:', music)
        pygame.mixer.music.load(PATH + 'musics/' + music + '.mp3')
        pygame.mixer.music.play(loops=loops)
        pygame.mixer.music.set_volume(volume)


##########################################################

if __name__ == "__main__":
    print('\nThis is STAGE[1] (interact) of the game')
    a = input()
