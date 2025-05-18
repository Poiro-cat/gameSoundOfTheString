'''
class Element():
    def __init__(self, mode, pos, element=None):
        assert type(mode) == str and len(mode) == 4
        self.mode = mode
        self.element = element
        self.pos = [[None]*4, [None]*4]
        for i in range(4):
            j = 'lrxwtbyh'.index(mode[i])
            self.pos[j//4][j%4] = pos[i]
        self.complete_pos()
        self.update_pos()
        
    def complete_pos(self):
        for pos in self.pos:
            i,j = 0,3
            while i < 4 and pos[i] is not None: i += 1
            if i >= 4: continue
            while j >= i and pos[j] is not None: j -= 1
            if (i,j) == (0,1):
                for k in [0,1]: pos[k] = pos[2] + (k-1/2)*pos[3]
            elif i < 2:
                if j < 3: pos[i] = pos[1-i] + (2*i-1)*pos[3]
                else: pos[i] = 2*pos[2] - pos[1-i]
            if pos[2] is None: pos[2] = (pos[0]+pos[1])/2
            if pos[3] is None: pos[3] = pos[1] - pos[0]
    
    def update_pos(self):
        self.left, self.right, self.cx, self.width = self.pos[0]
        self.top, self.bottom, self.cy, self.height = self.pos[1]
    
    def take(self, mode, pos, change, compare):
        i = 'lrxwtbyh'.index(mode)
        j = 'lrxwtbyh'.index(change)
        assert i<4 and j<4 or i>=4 and j>=4
        s = 'lrxwtbyh'[i&4 : (i&4)+4]
        u,v = 0,3
        while s[u] not in self.mode: u += 1
        while s[v] not in self.mode: v -= 1
        if v != j%4: u,v = v,u
        assert v == j%4
        origin_pos = self.pos[i//4].copy()
        self.pos[i//4] = [None]*4
        self.pos[i//4][i%4] = pos
        self.pos[i//4][u] = origin_pos[u]
        self.complete_pos()
        z = compare(self.pos[i//4][j%4], origin_pos[j%4])
        if z != self.pos[i//4][j%4]:
            self.pos[i//4] = origin_pos
        self.update_pos()
'''


class GameElement:
    def __init__(self, shape, *pos):
        self.shape = shape
        self.pos = self.flatten(pos)
        if self.shape == 'rect':
            left, right, top, bottom = self.pos
            self.center = (left+right)/2, (top+bottom)/2
        if self.shape == 'rect_':
            left, top, width, height = self.pos
            self.center = left+width/2, top+height/2
        if self.shape in ['circle','ellip']: self.center = self.pos[:2]
        if self.shape == 'circle_':
            left, top, r = self.pos
            self.center = left+r, top+r
        if self.shape == 'tri': self.center = None
        if self.shape == 'poly': self.center = None
    
    def flatten(self, pos):
        if type(pos) not in [list,tuple]: return pos
        pos_ = list(pos)
        i = 0
        while i < len(pos_):
            if type(pos_[i]) in [list,tuple]:
                pi = self.flatten(pos_[i])
                pos_ = pos_[:i] + pi + pos_[i+1:]
            else: i += 1
        if i == len(pos_): return pos_
    
    def collidepoint(self, x, y):
        if self.shape == 'rect':
            left, right, top, bottom = self.pos
            return left < x < right and top < y < bottom
        if self.shape == 'rect_':
            left, top, width, height = self.pos
            return 0 < x-left < width and 0 < y-top < height
        if self.shape == 'circle':
            x0, y0, r = self.pos
            return (x-x0)**2 + (y-y0)**2 < r**2
        if self.shape == 'circle_':
            left, top, r = self.pos
            return (x-left-r)**2 + (y-top-r)**2 < r**2
        if self.shape == 'ellip':
            x0, y0, a, b, phi = self.pos
            x, y = x-x0, y-y0
            import numpy as np
            c, s = np.cos(phi), np.sin(phi)
            x, y = c*x + s*y, c*y - s*x
            return (x/a)**2 + (y/b)**2 < 1
        if self.shape == 'tri':
            x1, y1, x2, y2, x3, y3 = self.pos
            p1 = (((x-x2)*(y2-y3)+(y-y2)*(x3-x2))*((x1-x2)*(y2-y3)+(y1-y2)*(x3-x2)) > 0)
            p2 = (((x-x1)*(y1-y3)+(y-y1)*(x3-x1))*((x2-x1)*(y1-y3)+(y2-y1)*(x3-x1)) > 0)
            p3 = (((x-x1)*(y1-y2)+(y-y1)*(x2-x1))*((x3-x1)*(y1-y2)+(y3-y1)*(x2-x1)) > 0)
            return p1 and p2 and p3
        if self.shape == 'poly':
            return

if __name__ == '__main__':
    '''
    ele = Element('yblw', (20, 36, 19, 46), True)
    print(ele.left, ele.right, ele.cx, ele.width)
    print(ele.top, ele.bottom, ele.cy, ele.height)

    ele.take('h', 18, 'b', min)
    print(ele.left, ele.right, ele.cx, ele.width)
    print(ele.top, ele.bottom, ele.cy, ele.height)
    '''
    
    a = GameElement('a', 3, 5, (7,9,(11,12),(0,1,(4,(5,6),7,2)), 4), [2,4], -8, [9,(11,4),[69,(14,[125,26])]])
    print(a.pos)
    
    
    a = input()