#dice.py
import random

def rollPool(dice, options=None):
    pool = []
    modifiers = []
    glitches = 0
    hits = 0
    wild = False
    explode = False
    twosGlitch = False
    fivesCancelled = False
    wildResult = []
    modifiers = []
    if options is not None:
        modifiers = list(options)

    if "w" in modifiers:
        wild = True
    if "e" in modifiers:
        explode = True
    if "2" in modifiers:
        twosGlitch = True

    for d in range(dice if wild == False else dice - 1):
        val = random.randint(1, 6)
        if val >= 5:
            hits += 1
        if val == 1:
            glitches += 1
        if twosGlitch & val == 2:
            glitches += 1
        pool.append(val)
        if explode:
            while val == 6:
                val = random.randint(1, 6)
                if val >= 5:
                    hits += 1
                if val == 1:
                    glitches += 1
                pool.append(val)
    if wild:
        val = random.randint(1, 6)
        
        if val >= 5:
            hits += 3
        if val == 1:
            glitches += 1
            fivesCancelled = True
        if twosGlitch & val == 2:
            glitches += 1
        wildResult.append(val)
        if explode:
            while val == 6:
                val = random.randint(1, 6)
                if val >= 5:
                    hits += 1
                if val == 1:
                    glitches += 1
                wildResult.append(val)
    if fivesCancelled:
        for d in range(pool):
            if pool[d] == 5:
                hits -= 1
    print("Pool: " + str(pool) + " Wild: " + str(wildResult) + " Hits: " + str(hits) + " Glitches: " + str(glitches))
    return pool, wildResult, hits, glitches

# rollPool(3, "2ew")

            

