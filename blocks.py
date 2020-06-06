from pyglet.gl import *


def get_tex(file):
    tex = pyglet.image.load(file).get_texture()
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    return pyglet.graphics.TextureGroup(tex)


class Block(object):
    tex = []
    files = []

    def __init__(self):
        for nme in self.files:
            self.tex.append(get_tex(nme))


class GrassBlock(Block):
    files = ['grass_block_side.png', 'grass_block_top.png', 'dirt.png']
