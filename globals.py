# speed
SECTOR_SIZE = 16
SECTOR_SIDE = 4  # square root of SECTOR_SIZE

# model
FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]

# perlin
OCTAVES = 1
PERSISTENCE = 0.2
LACUNARITY = 100
