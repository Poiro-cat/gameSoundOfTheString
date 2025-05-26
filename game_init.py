import sys
import pygame
from configs import PATH, VISION_RATIO, SCENE_RATIO, COLUMN_RATIO, ARROW_RATIO, COLUMN_NUM, FADE_TIME


################ 游戏初始化 ################

class GameCore:
    
    #======== 创建游戏对象 ========#
    def __init__(self, window_width, window_height):
        # 初始化pygame
        pygame.init()
        pygame.mixer.init()
        # 确保中文正常显示
        pygame.font.init()
        # 尺寸比例常数
        self.ratio_vision = VISION_RATIO
        self.ratio_scene = SCENE_RATIO
        self.ratio_column = COLUMN_RATIO
        self.ratio_arrow = ARROW_RATIO
        print(f'\n[Init]  VISION_RATIO = {int(self.ratio_vision*720)}:720')
        print(f'[Init]  SCENE_RATIO = {int(self.ratio_scene*720)}:720')
        print(f'[Init]  COLUMN_RATIO = {int(self.ratio_column*720)}:720')
        print(f'[Init]  ARROW_RATIO = {self.ratio_arrow}')
        # 淡入/淡出时间（秒）
        self.fade_time = FADE_TIME
        print(f'\n[Init]  FADE_TIME = {self.fade_time}')
        # 道具栏个数
        self.item_column_num = COLUMN_NUM
        print(f'\n[Init]  COLUMN_NUM = {self.item_column_num}')
        # 创建屏幕
        self.window_size = window_width, window_height
        self.window = pygame.display.set_mode(self.window_size, flags=pygame.RESIZABLE)
        pygame.display.set_caption("弦内之音")
        self.full_screen_size = pygame.display.list_modes()[0]
        self.full_screen = False
        print(f'\n[Init]  initial window size = {self.window_size}\n[Init]  full screen size = {self.full_screen_size}')
        # 游戏元素名称
        self.names = {'scene': ['black', 'title_pic', 'band_photo', 'frame',
                                'wall_door', 'zoom_photo', 'zoom_peephole',
                                'wall_window', 'zoom_cupboard', 'zoom_pillow',
                                'wall_guitar', 'zoom_chest_big', 'zoom_guitar',
                                'wall_desk', 'zoom_radio', 'zoom_drawer', 'zoom_book', 'zoom_chest'],
                      'furnish': ['door', 'band_photo_complete', 'band_photo_incomplete',
                                  'curtain_up', 'curtain_down', 'cupboard_close', 'cupboard_open', 'pillow_good', 'pillow_scratched',
                                  'chest_big_close', 'chest_big_open', 'paper_down', 'paper_up',
                                  'radio_empty', 'radio_with_tape', 'drawer_open', 'shelf_with_book', 'shelf_no_book', 'chest_close', 'chest_open',
                                  'music_book', 'key', 'knife', 'tape', 'instrument_pics', 'my_photo', 'plectrum', 'string', 'letter'] + \
                                 [f'guitar_{i}' for i in range(2,7)],
                      'item' : ['music_book', 'music_book_open', 'key', 'knife', 'tape', 'instrument_pics', 'my_photo', 'plectrum', 'string', 'guitar', 'letter'],
                      'icon' : ['button', 'menu', 'go_left', 'go_right', 'go_back', 'go_back_white'] + [f'note_{i}' for i in range(4)]
                      }
        print('\n[Init]  Generating all names of elements success.')
        # 初始化游戏状态
        self.load_images()
        self.initialize_state()
        self.game_started = False
    
    #======== 初始化游戏参数 ========#
    def initialize_state(self):
        self.scene_changing = 0
        self.time_marker = None
        self.current_scene = 'menu'
        self.saved_scene = None
        self.next_scene = None
        self.item_column = [None] * self.item_column_num
        self.chosen_column = None
        self.showing_detail = None
        self.got_items = {}
        for name in self.names['item']:
            if name == 'string': self.got_items[name] = [False]*4
            elif name == 'plectrum': self.got_items[name] = [False]*3
            else: self.got_items[name] = False
        # 书架上拿书-钥匙开抽屉-拿到小刀和磁带
        self.drawer_unlocked = False
        self.drawer_pulled_out = False
        # 小刀-枕头-图片-颜色数字-吉他弦1+拨片1
        self.pillow_scratched = False
        self.chest_code = [0]*4
        self.chest_unlocked = False
        self.chest_open = False
        # 磁带-音符-床头柜-吉他弦2+拨片2
        self.tape_in_radio = False
        self.radio_playing = False
        self.cupboard_code = [0]*4
        self.cupboard_unlocked = False
        self.cupboard_open = False
        # 乐谱-照片-吉他弦3
        self.music_paper_lifted = False
        self.band_photo_complete = False
        # 窗帘-拨片3
        self.curtain_open = False
        # 拨片123-吉他弦4
        self.plectrum_on_chest = [False]*3
        self.chest_big_unlocked = False
        self.chest_big_open = False
        # 吉他弦1234-吉他
        self.num_string_on_guitar = 2
        # 信中密码-开门
        self.door_unlocked = False
        ###
        print('\n[Init]  Initializing all game parameters success.')
    
    #======== 加载图片资源 ========#
    def load_images(self):
        print('\n[Init]  Loading images ...')
        self.images = {}
        for kind in self.names:
            for name in self.names[kind]:
                if kind in ['item','icon']: name = kind + '_' + name
                try:
                    image = pygame.image.load(PATH+f'figs/{name}.png').convert_alpha()
                    self.images[name] = image
                except Exception as e:
                    print(f'[Imgae loading error]  {e}')
        print('[Init]  Loading images success.')
    
    #======== 加载音乐资源 ========#
    def load_musics(self):
        print('\n[Init]  Loading musics ...')
        self.sounds = {}
        for name in ['bgm_rock', 'bgm_beethoven']:
            try:
                sound = pygame.mixer.Sound(PATH+'musics/'+name+'.mp3')
                self.sounds[name] = sound
            except Exception as e:
                print(f'[Music loading error]  {e}')
        print('[Init]  Loading musics success.')


##########################################################

if __name__ == "__main__":
    print('\nThis is STAGE[0] (init) of the game.')
    a = input()
