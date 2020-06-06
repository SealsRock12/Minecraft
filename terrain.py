from noise import snoise2
import math
import globals as G


def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)


def perlin(x, y):
    return normal_round(snoise2(x, y, G.OCTAVES, G.PERSISTENCE, G.LACUNARITY))

# debug
# if __name__ == "__main__":
#     for x in range(10):
#         for y in range(10):
#             print(abs(perlin(x, y)) * 100)
