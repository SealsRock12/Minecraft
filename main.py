from pyglet.gl import *
from pyglet.window import key
import math
import terrain
from collections import defaultdict, deque

xrange = range

def normalize(position):
    """ Accepts `position` of arbitrary precision and returns the block
    containing that position.
    Parameters
    ----------
    position : tuple of len 3
    Returns
    -------
    block_position : tuple of ints of len 3
    """
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return (x, y, z)





class Block(object):
    tex = []
    files = []

    def get_tex(self,file):
        tex = pyglet.image.load(file).get_texture()
        glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
        return pyglet.graphics.TextureGroup(tex)

    def __init__(self):
        for nme in self.files:
            self.tex.append(self.get_tex(nme))

class GrassBlock(Block):
    files = ['grass_block_side.png','grass_block_top.png','dirt.png']

class Model:
    queue = deque()
    def __init__(self, player):
        self.batch = pyglet.graphics.Batch()
        self.world = defaultdict(lambda: None)
        self.shown = {}
        self._shown = {}
        self.player = player
        self.gen_terrain()

    def inqueue(self, func, *args):
        self.queue.append([func, args])

    def outqueue(self):
        return self.queue.popleft()

    def gen_terrain(self):
        for x in range(1000):
            for z in range(1000):
                self.gen_block(x, z)


    def _hide_all(self):
        '''
        Debug function to hide all
        '''
        for pos in self._shown.keys():
            self.hide_block(pos)

    def _gen_block(self, x, z):
        y = terrain.perlin(abs(x), abs(z))
        self.add_block((x, y, z), GrassBlock())

    def gen_block(self,x, z, immediate=False):
        if immediate:
            self._gen_block(x, z)
        else:
            self.inqueue(self._gen_block, x, z)


    def add_block(self,position, block, immediate=True):
        self.world[position] = block
        if immediate:
            self.show_block(position)
        else:
            self.inqueue(self.show_block, position)

    def _hide_block(self,position):
        del self.shown[position]   # delete block reference
        for vlist in self._shown[position]:
            vlist.delete()
        del self._shown[position]  # delete vertex list

    def hide_block(self, position, immediate=False):
        if immediate:
            self._hide_block(position)
        else:
            self.inqueue(self._hide_block, position)

    def show_block(self,position):
        self.shown[position] = self.world[position]
        self.cuboid(*position, self.world[position])

    def cuboid(self, x, y, z, block):
        '''
        Draws a cuboid from x1,y1,z1 to x2,y2,z2 and covers each side with tex
        tex format:
            (side, top, bottom)
        Facing in the -z direction
        '''
        tex = block.tex
        front = tex[0]
        back = tex[0]
        left = tex[0]
        right = tex[0]
        top = tex[1]
        bottom = tex[2]

        tex_coords = ("t2f", (0, 0, 1, 0, 1, 1, 0, 1))
        x1, y1, z1 = x, y, z
        x2, y2, z2 = x + 1, y + 1, z + 1

        cube = (self.batch.add(4, GL_QUADS, right, ('v3f', (x1, y1, z1, x1, y1, z2, x1, y2, z2, x1, y2, z1)), tex_coords),
        self.batch.add(4, GL_QUADS, left, ('v3f', (x2, y1, z2, x2, y1, z1, x2, y2, z1, x2, y2, z2)), tex_coords),
        self.batch.add(4, GL_QUADS, bottom, ('v3f', (x1, y1, z1, x2, y1, z1, x2, y1, z2, x1, y1, z2)), tex_coords),
        self.batch.add(4, GL_QUADS, top, ('v3f', (x1, y2, z2, x2, y2, z2, x2, y2, z1, x1, y2, z1)), tex_coords),
        self.batch.add(4, GL_QUADS, back, ('v3f', (x2, y1, z1, x1, y1, z1, x1, y2, z1, x2, y2, z1)), tex_coords),
        self.batch.add(4, GL_QUADS, front, ('v3f', (x1, y1, z2, x2, y1, z2, x2, y2, z2, x1, y2, z2)), tex_coords))
        self._shown[(x, y, z)] = cube

    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the player is looking.
        """
        x, y = self.player.rot
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)

    def hit_test(self, position, vector, max_distance=8):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.
        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in xrange(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def update(self):
        for i in range(5):
            if len(self.queue) != 0:
                func, args = self.outqueue()
                func(*args)

    def draw(self):
        self.batch.draw()



class Player:
    def __init__(self,pos=(0,0,0),rot=(0,0)):
        self.pos = list(pos)
        self.rot = list(rot)

    def mouse_motion(self,dx,dy):
        dx/=8; dy/=8; self.rot[0]+=dy; self.rot[1]-=dx
        if self.rot[0]>90: self.rot[0] = 90
        elif self.rot[0]<-90: self.rot[0] = -90

    def update(self,dt,keys):
        s = dt*10
        rotY = -self.rot[1]/180*math.pi
        dx,dz = s*math.sin(rotY),s*math.cos(rotY)
        if keys[key.W]: self.pos[0]+=dx; self.pos[2]-=dz
        if keys[key.S]: self.pos[0]-=dx; self.pos[2]+=dz
        if keys[key.A]: self.pos[0]-=dz; self.pos[2]-=dx
        if keys[key.D]: self.pos[0]+=dz; self.pos[2]+=dx

        if keys[key.SPACE]: self.pos[1]+=s
        if keys[key.LSHIFT]: self.pos[1]-=s

class Window(pyglet.window.Window):
    def push(self,pos,rot): glPushMatrix(); glRotatef(-rot[0],1,0,0); glRotatef(-rot[1],0,1,0); glTranslatef(-pos[0],-pos[1],-pos[2],)
    def Projection(self): glMatrixMode(GL_PROJECTION); glLoadIdentity()
    def Model(self): glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    def set2d(self): self.Projection(); gluOrtho2D(0,self.width,0,self.height); self.Model()
    def set3d(self): self.Projection(); gluPerspective(70,self.width/self.height,0.05,1000); self.Model()

    def setLock(self,state): self.lock = state; self.set_exclusive_mouse(state)
    lock = False
    mouse_lock = property(lambda self: self.lock, setLock)

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(300, 200)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule(self.update)

        self.player = Player((0.5, 1.5, 1.5), (-30, 0))
        self.model = Model(self.player)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.mouse_lock:
            self.player.mouse_motion(dx, dy)

    def on_key_press(self, KEY, MOD):
        if KEY == key.Q: self.mouse_lock = not self.mouse_lock
        if KEY == key.M: self.model.hide_block((0, 0, 0))

    def update(self, dt):
        self.player.update(dt,self.keys)
        self.model.update()


    def on_draw(self):
        self.clear()
        self.set3d()
        self.push(self.player.pos,self.player.rot)
        self.model.draw()
        glPopMatrix()


if __name__ == '__main__':
    window = Window(width=854,height=480,caption='Minecraft',resizable=True)
    glClearColor(0.5,0.7,1,1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    pyglet.app.run()
