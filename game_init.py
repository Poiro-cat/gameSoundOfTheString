import sys
import pygame
from configs import PATH


################ 游戏初始化 ################

class GameCore:
    
    #======== 创建游戏对象 ========#
    def __init__(self, window_width, window_height):
        # 初始化pygame
        pygame.init()
        # 确保中文正常显示
        pygame.font.init()
        # 创建屏幕
        self.window_size = window_width, window_height
        self.window = pygame.display.set_mode(self.window_size, flags=pygame.RESIZABLE)
        pygame.display.set_caption("弦内之音")
        self.full_screen_size = pygame.display.list_modes()[0]
        self.full_screen = False
        # 尺寸比例常数
        self.KSC = 1.5 # main scene
        self.KAR = 1.7 # left/right button
        self.KD = 0.88 # scene and column
        # 时间常数/s
        self.fade_time = 0.3
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
                      'item' : ['music_book', 'key', 'knife', 'tape', 'instrument_pics', 'my_photo', 'plectrum', 'string', 'guitar', 'letter'],
                      'icon' : ['button', 'menu', 'go_left', 'go_right', 'go_back', 'go_back_white'] + [f'note_{i}' for i in range(4)]
                      }
        # 初始化游戏状态
        self.load_images()
        self.game_started = False
        self.initialize_state()
    
    #======== 初始化游戏参数 ========#
    def initialize_state(self):
        self.scene_changing = 0
        self.time_marker = None
        self.current_scene = 'menu'
        self.saved_scene = None
        self.next_scene = None
        self.items_column_num = 8
        self.items_column = [None] * self.items_column_num
        self.chosen_item = None
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
    
    #======== 加载图片资源 ========#
    def load_images(self):
        self.images = {}
        for kind in self.names:
            for name in self.names[kind]:
                if kind in ['item','icon']: name = kind + '_' + name
                try:
                    image = pygame.image.load(PATH+f'figs/{name}.png').convert_alpha()
                    self.images[name] = image
                except Exception as e:
                    print('Imgae loading error:', e)


##########################################################

if __name__ == "__main__":
    print('\nThis is STAGE[0] (init) of the game.')
    a = input()