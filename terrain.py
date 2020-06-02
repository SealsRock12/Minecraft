from noise import snoise2

def perlin(x,y):
    #                    octaves  persistence
    return snoise2(x, y, 10    , 1.25        , 10)
if __name__ == "__main__":
    for x in range(10):
        for y in range(10):
            print(abs(perlin(x,y))*100)