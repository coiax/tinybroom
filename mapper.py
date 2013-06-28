from PIL import Image
from flufl.enum import Enum

import anvil

class Blocks(Enum):
    air = 0
    stone = 1
    grass_block = 2
    dirt = 3
    cobblestone = 4
    wood_planks = 5
    saplings = 6
    bedrock = 7
    water = 8
    stationary_water = 9
    lava = 10
    stationary_lava = 11
    sand = 12
    gravel = 13
    gold_ore = 14
    iron_ore = 15
    coal_ore = 16
    wood = 17
    leaves = 18
    sponge = 19
    glass = 20
    lapis_lazuli_ore = 21
    lapis_lazuil_block = 22
    dispenser = 23
    sandstone = 24
    note_block = 25
    bed = 26
    powered_rail = 27
    detector_rail = 28
    sticky_piston = 29
    cobweb = 30
    grass = 31
    dead_bush = 32
    piston = 33
    piston_extension = 34
    wool = 35
    block_moved_by_piston = 36
    dandelion = 37
    rose = 38
    brown_mushroom = 39
    red_mushroom = 40
    block_of_gold = 41
    block_of_iron = 42
    double_slabs = 43
    slabs = 44
    bricks = 45
    tnt = 46
    bookshelf = 47
    moss_stone = 48
    obsidian = 49
    torch = 50
    fire = 51
    monster_spawner = 52
    oak_wood_stairs = 53
    chest = 54
    redstone_wire = 55
    diamond_ore = 56
    block_of_diamond = 57
    crafting_table = 58
    wheat = 59
    farmland = 60
    furnace = 61
    burning_furnace = 62
    sign_post = 63
    wooden_door = 64
    ladders = 65
    rail = 66
    cobblestone_stairs = 67
    wall_sign = 68
    lever = 69
    stone_pressure_plate = 70
    iron_door = 71
    wooden_pressure_plate = 72
    redstone_ore = 73
    glowing_redstone_ore = 74
    redstone_torch_inactive = 75
    redstone_torch_active = 76
    stone_button = 77
    snow = 78
    ice = 79
    snow_block = 80
    cactus = 81
    clay = 82
    sugar_cane = 83
    jukebox = 84
    fence = 85
    pumpkin = 86
    netherrack = 87
    soul_sand = 88
    glowstone = 89
    nether_portal = 90
    jack_o_lantern = 91
    cake_block = 92
    redstone_repeater_inactive = 93
    redstone_repeater_active = 94
    locked_chest = 95
    trapdoor = 96
    monster_egg = 97
    stone_bricks = 98
    huge_brown_mushroom = 99
    huge_red_mushroom = 100
    iron_bars = 101
    glass_pane = 102
    melon = 103
    pumpkin_stem = 104
    melon_stem = 105
    vines = 106
    fence_gate = 107
    brick_stairs = 108
    stone_brick_stairs = 109
    mycelium = 110
    lily_pad = 111
    nether_brick = 112
    nether_brick_fence = 113
    nether_brick_stairs = 114
    nether_wart = 115
    enchantment_table = 116
    brewing_stand = 117
    cauldron = 118
    end_portal = 119
    end_portal_block = 120
    end_stone = 121
    dragon_egg = 122
    redstone_lamp_inactive = 123
    redstone_lamp_active = 124
    wooden_double_slab = 125
    wooden_slab = 126
    cocoa = 127
    sandstone_stairs = 128
    emerald_ore = 129
    ender_chest = 130
    tripwire_hook = 131
    tripwire = 132
    block_of_emerald = 133
    spruce_wood_stairs = 134
    birch_wood_stairs = 135
    jungle_wood_stairs = 136
    command_block = 137
    beacon = 138
    cobblestone_wall = 139
    flower_pot = 140
    carrots = 141
    potatoes = 142
    wodden_button = 143
    mob_head = 144
    anvil = 145
    trapped_chest = 146
    weighted_pressure_plate_light = 147
    weighted_pressure_plate_heavy = 148
    redstone_comparator_inactive = 149
    redstone_comparator_active = 150
    daylight_sensor = 151
    block_of_redstone = 152
    nether_quartz_ore = 153
    hopper = 154
    block_of_quartz = 155
    quartz_stairs = 156
    activator_rail = 157
    dropper = 158
    stained_clay = 159

    hay_block = 170
    carpet = 171
    hardened_clay = 172
    block_of_coal = 173

NOT_SOLID = {Blocks.air, Blocks.glass, Blocks.tripwire}

COLOURS = {
    Blocks.grass_block: (34, 139, 34, 255),
    Blocks.grass: (113,118,120, 255),
    Blocks.snow: (248, 248, 255, 255),
    Blocks.leaves: (116, 195, 101, 255),
    Blocks.dirt: (68, 56, 56, 255),
    Blocks.stone: (128, 128, 128, 255),
    Blocks.dandelion: (255,255,127,255),
    Blocks.rose: (200, 180, 0, 255),
    Blocks.sand: (255,240, 127, 255),
    Blocks.stationary_water: (0, 0, 255, 255),
    Blocks.ice: (200, 200, 255, 255),
}

def _make_block_indexes():
    indexes = {}
    for x in range(16):
        for y in range(16):
            for z in range(16):
                indexes[x,y,z] = y*16*16 + z*16 + x
    return indexes

BLOCK_INDEXES = _make_block_indexes()

def _nibble4(array, index):
    if index % 2 == 0:
        return array[index // 2] & 0x0F
    else:
        return (array[index // 2] >> 4) & 0X0F

def render_region(region):
    im = Image.new("RGBA", (512, 512))
    pix = im.load()
    for chunk_x,chunk_z in region:
        offset_x = chunk_x * 16
        offset_z = chunk_z * 16
        if region[chunk_x, chunk_z]['empty'] == True:
            # An empty chunk is transparent.
            for y in range(16):
                for x in range(16):
                    pix[x + offset_x, y + offset_z] = (0,0,0,255)
            continue

        render_chunk(region[chunk_x,chunk_z], pix, offset_x, offset_z)
    im.save("out.png")


def render_chunk(chunk, pix, offset_x, offset_z):
    # right, to continue, you need to go from the top section
    # for each chunk, and find a "solid" block.
    sections = chunk['data'][1]['Level']['Sections']

    # okay, the sections appear to be ordered, with 0 at the bottom
    # and 15 at the top
    # not all of them are there though, and it'll remove sections
    # that are completely air.
    sections.sort(key=lambda section: section['Y'], reverse=True)

    # When we encounter a X,Z block that's solid, we add it to this
    # and when we have 256 entries, we stop going down, because we
    # have the top soil.
    done = False
    encountered = []
    for section in sections:
        if done:
            break

        blocks = section['Blocks']
        add = section.get('Add', [0]*16*16*16)
        data = section['Data']
        block_lights = section['BlockLight']
        sky_lights = section['SkyLight']
        # That's 15 14 13 ... 1 0
        for y in range(15,-1,-1):
            if len(encountered) == 256:
                # We don't need to go any deeper.
                done = True
                break
            for x in range(16):
                for z in range(16):
                    if (x,z) in encountered:
                        continue
                    # Dear lord, what a monster of a for loop.
                    block_pos = BLOCK_INDEXES[x,y,z]

                    block_id_a = blocks[block_pos]
                    block_id_b = _nibble4(add, block_pos)
                    block_id = block_id_a + (block_id_b << 8)
                    block_data = _nibble4(data, block_pos)
                    block_light = _nibble4(block_lights, block_pos)
                    block_sky_light = _nibble4(sky_lights, block_pos)

                    block_type = Blocks[block_id]

                    # Then we get the colour, using a combination
                    # of the block_type, and no doubt some data
                    # and maybe the light values, AND DEAR LORD HELP MEEE

                    # No doubt later, with transparent things, we'll
                    # just add them into the pixel or something. But for
                    # now, just set it.
                    if block_type not in NOT_SOLID:
                        # for those confused by double negatives,
                        # this means it's A *SOLID* BLOCK
                        assert (x,z) not in encountered
                        encountered.append((x,z))
                        # right... I think we need to set the colour of
                        # the pixel. Remember that? Way back, many
                        # hundreds of lines ago? I was a wee lad then...
                        if block_type in COLOURS:
                            colour = COLOURS[block_type]
                        else:
                            # random orange for testing.
                            colour = (255,127,127,255)
                            print(block_type)


                        pix[x + offset_x, z + offset_z] = colour


if __name__=='__main__':
    import os.path
    import pickle

    if os.path.exists('_region_cache.pickle'):
        with open('_region_cache.pickle','rb') as f:
            region = pickle.load(f)
    else:
        region = anvil.read_region_from_file('r.-1.0.mca')
    print("""Now doing some "rendering". It'll definitely be quick. -_-""")
    render_region(region)
