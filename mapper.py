import os.path
import pickle
import datetime
import json
import re
import argparse
import multiprocessing

from PIL import Image
from flufl.enum import Enum

import anvil

class Blocks(Enum):
    unknown = None

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
    lapis_lazuli_block = 22
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

class WoolBlocks(Enum):
    white = 0x0
    orange = 0x1
    magenta = 0x2
    light_blue = 0x3
    yellow = 0x4
    lime = 0x5
    pink = 0x6
    grey = 0x7
    light_grey = 0x8
    cyan = 0x9
    purple = 0xa
    blue = 0xb
    brown = 0xc
    green = 0xd
    red = 0xe
    black = 0xf

class WoodPlanksBlocks(Enum):
    oak = 0
    spruce = 1
    birch = 2
    jungle = 3

def twofivefive_to_one(colour):
    return (colour[0]/255.0, colour[1]/255.0, colour[2]/255.0, colour[3]/255.0)

def one_to_twofivefive(colour):
    return (int(colour[0]*255), int(colour[1]*255), int(colour[2]*255),
            int(colour[3]*255))

def add_colours(bg, fg):
    bg = twofivefive_to_one(bg)
    fg = twofivefive_to_one(fg)

    a = 1 - (1 - fg[3]) * (1 - bg[3])
    r = fg[0] * fg[3] / a + bg[0] * bg[3] * (1 - fg[3]) / a
    g = fg[1] * fg[3] / a + bg[1] * bg[3] * (1 - fg[3]) / a
    b = fg[2] * fg[3] / a + bg[2] * bg[3] * (1 - fg[3]) / a

    return one_to_twofivefive((r,g,b,a))

def _generate_colours():
    COLOURS = {
        Blocks.air: (255,255,255,0),
        Blocks.stone: (128,128,128,255),
        Blocks.grass_block: (120,172,70,255),
        Blocks.dirt: (134,96,67,255),
        Blocks.cobblestone: (100,100,100,255),
        Blocks.wood_planks: (157,128,79,255),
        Blocks.saplings: (120,120,120,0),
        Blocks.bedrock: (84,84,84,255),
        Blocks.water: (56,68,127,64),
        Blocks.stationary_water: (56,68,127,64),
        Blocks.lava: (255,90,0,255),
        Blocks.stationary_lava: (255,90,0,255),
        Blocks.sand: (218,210,158,255),
        Blocks.gravel: (136,126,126,255),
        Blocks.gold_ore: (143,140,125,255),
        Blocks.iron_ore: (136,130,127,255),
        Blocks.coal_ore: (115,115,115,255),
        Blocks.wood: (102,81,51,255),
        Blocks.leaves: (0x4a,0x83,0x42,0x80),
        Blocks.sponge: (0xc3,0xc3,0x32,0xff),
        Blocks.glass: (255,255,255,48),
        Blocks.lapis_lazuli_ore: (102,112,134,255),
        Blocks.lapis_lazuli_block: (29,71,165,255),
        Blocks.dispenser: (107,107,107,255),
        Blocks.sandstone: Blocks.sand,
        Blocks.note_block: (100,67,50,255),
        Blocks.bed: (150,0,0,255),
        Blocks.powered_rail: (120, 120, 120, 128),
        Blocks.detector_rail: Blocks.powered_rail,
        Blocks.sticky_piston: (157,192,79,255),
        Blocks.grass: (0x90, 0xbc, 0x27, 0xff),
        Blocks.dead_bush: Blocks.wood,
        Blocks.piston: Blocks.wood,
        Blocks.piston_extension: Blocks.air,
        Blocks.dandelion: (255,255,0,255),
        Blocks.rose: (255,0,0,255),
        Blocks.brown_mushroom: (0x00, 0x00, 0x00, 0x00),
        Blocks.red_mushroom: (0x00, 0x00, 0x00, 0x00),
        Blocks.block_of_gold: (0xff, 0xed, 0x8c, 0xff),
        Blocks.block_of_iron: (0xd9, 0xd9, 0xd9, 0xff),
        Blocks.double_slabs: (200,200,200,255),
        Blocks.slabs: (200,200,200,255),
        Blocks.bricks: (0x56, 0x23, 0x17, 0xff),
        Blocks.tnt: (0xff, 0x0, 0x0, 0xff),
        Blocks.bookshelf: (0xbf, 0xa9, 0x74, 0xff),
        Blocks.moss_stone: (0x7f, 0xae, 0x7d, 0xff),
        Blocks.obsidian: (0x11, 0x0d, 0x1a, 0xff),
        Blocks.torch: (0xff, 0xe1, 0x60,0xd0),
        Blocks.fire: (0xe0, 0xae, 0x15, 0xff),
        Blocks.monster_spawner: (0xff, 0xff, 0xff, 0x00),
        Blocks.cactus: (85,107,47,255),
        Blocks.sugar_cane: (193,234,150,255),
        Blocks.crafting_table: (0xa9, 0x6b, 0x00, 0xff),
        Blocks.sign_post: (0,0,0,0),
        Blocks.wall_sign: Blocks.sign_post,
        Blocks.clay: (0x90, 0x98, 0xa8, 0xff),
        Blocks.ice: (120, 120, 255, 120),
        Blocks.snow: (255,255,255,255),
        Blocks.snow_block: Blocks.snow,
        Blocks.ladders: (0xff, 0xc8, 0x8c, 0),
        Blocks.fence: (0x58, 0x36, 0x16, 200),
        Blocks.fence_gate: Blocks.fence,
        Blocks.pumpkin: (0xe3, 0x90, 0x1d, 0xff),
        Blocks.jack_o_lantern: Blocks.pumpkin,
        Blocks.pumpkin_stem: (0, 0, 0, 0),
        Blocks.farmland: Blocks.dirt,
        Blocks.stone_brick_stairs: Blocks.stone,
        Blocks.redstone_repeater_inactive: Blocks.redstone_wire,
        Blocks.redstone_repeater_active: Blocks.redstone_wire,
        Blocks.vines: (50,89,45,128),
        Blocks.stone_bricks: Blocks.stone,
        Blocks.stone_brick_stairs: Blocks.stone,
        Blocks.wooden_door: Blocks.wood_planks,
        Blocks.mycelium: (110,93,113,255),
        Blocks.glass_pane: Blocks.glass,
        Blocks.redstone_wire: (0x6f, 0x01, 0x01, 0xff),
        Blocks.cobblestone_stairs: (120, 120, 120, 128),
        Blocks.nether_wart: (149, 21, 8, 255),
        Blocks.melon: (50,200,45,192),
        Blocks.wheat: (0x90, 0xbc, 0x27, 0xff),
        Blocks.iron_bars: Blocks.block_of_iron,
        Blocks.trapdoor: Blocks.wood_planks,
        Blocks.wooden_pressure_plate: Blocks.wood_planks,
        Blocks.rail: (120, 120, 120, 128),
        Blocks.powered_rail: (255,220,0, 128),
        Blocks.soul_sand: (0x79, 0x61, 0x52, 0xff),
        Blocks.oak_wood_stairs: Blocks.wood_planks, #FIXME not accurate
        Blocks.furnace: (0xbc, 0xbc, 0xbc, 0xff),
        Blocks.burning_furnace: (0xdd, 0xdd, 0xdd, 0xff),
        Blocks.wool: (223, 223, 223, 255), #FIXME special.
        Blocks.brick_stairs: Blocks.bricks,
        Blocks.redstone_torch_active: (255,0,0,0xb0),
        Blocks.redstone_torch_inactive: (181,140,64,32),
        Blocks.redstone_lamp_active: Blocks.glowstone,
        Blocks.redstone_lamp_inactive: Blocks.glowstone,
        Blocks.glowstone: (0xff,0xbc,0x53,0xff),
        Blocks.huge_red_mushroom: (183, 31, 29, 0xff),
        Blocks.stone_button: (0,0,0,0),
        Blocks.wooden_double_slab: Blocks.wood_planks, #FIXME not accurate
        Blocks.melon_stem: Blocks.wheat,
        Blocks.lily_pad: (50,89,45,128),
        Blocks.chest: (0xbf, 0x87, 0x02, 0xff),
        Blocks.wooden_slab: Blocks.wood_planks, #FIXME still not accurate?
        Blocks.stone_pressure_plate: Blocks.stone,
        Blocks.lever: Blocks.stone,
        Blocks.block_of_diamond: (45,166,152,255),
        Blocks.brewing_stand: Blocks.stone,

        WoolBlocks.black: (27,23,23,255),
        WoolBlocks.white: (223,223,223,255),
        WoolBlocks.orange: (234,128,55,255),
        WoolBlocks.magenta: (191,76,201,255),
        WoolBlocks.light_blue: (105,139,212,255),
        WoolBlocks.yellow: (195,181,28,255),
        WoolBlocks.lime: (59,189,48,255),
        WoolBlocks.pink: (218,132,155,255),
        WoolBlocks.grey: (67,67,67,255),
        WoolBlocks.light_grey: (159,166,166,255),
        WoolBlocks.cyan: (39,117,150,255),
        WoolBlocks.purple: (130,54,196,255),
        WoolBlocks.blue: (39,51,154,255),
        WoolBlocks.brown: (86,51,28,255),
        WoolBlocks.green: (56,77,24,255),
        WoolBlocks.red: (164,45,41,255),

        WoodPlanksBlocks.oak: Blocks.wood_planks,
        WoodPlanksBlocks.spruce: (0x80,0x5e,0x36,255),
        WoodPlanksBlocks.birch: (0xd7,0xcb,0x8d,255),
        WoodPlanksBlocks.jungle: (0xb1,0x80,0x5c,255),

        Blocks.unknown: (200,200,200,255),
    }

    colours = COLOURS


    for key in list(colours.keys()):
        value = colours[key]
        if value in Blocks:
            colours[key] = colours[value]

    for key, value in colours.items():
        assert value not in Blocks

    return colours

COLOURS = _generate_colours()

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


class Renderer:
    def render_region(self, region):
        self.unknown_blocks = set()
        self.colourless_blocks = set()

        im = Image.new("RGBA", (512, 512))
        pix = im.load()
        for chunk_x,chunk_z in region:
            chunk = region[chunk_x, chunk_z]
            offset_x = chunk_x * 16
            offset_z = chunk_z * 16
            if chunk['empty'] == True:
                # An empty chunk is transparent.
                # The default filling is transparency, so we don't need to put
                # anything in.
                #for y in range(16):
                #    for x in range(16):
                #        pix[x + offset_x, y + offset_z] = (200,20,20,255)
                pass
            else:
                #print("Doing chunk ({},{})".format(chunk_x,chunk_z))
                self.render_chunk(chunk, pix, offset_x, offset_z)
        print("Unrecognised block IDs:")
        for block in self.unknown_blocks:
            print(block)

        print("Blocks do not have colours:")
        for block in self.colourless_blocks:
            print(block)
        return im

    def render_chunk(self, chunk, pix, offset_x, offset_z):
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
        # have the "top soil".
        done = False
        series_of_blocks = {}
        top_soiled = []
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
                if len(top_soiled) == 256:
                    # We don't need to go any deeper.
                    done = True
                    break
                actual_y = section['Y']*16 + y
                for x in range(16):
                    for z in range(16):
                        if (x,z) in top_soiled:
                            continue
                        # Dear lord, what a monster of a for loop.
                        block_pos = BLOCK_INDEXES[x,y,z]

                        block_id_a = blocks[block_pos]
                        block_id_b = _nibble4(add, block_pos)
                        block_id = block_id_a + (block_id_b << 8)
                        block_data = _nibble4(data, block_pos)
                        block_light = _nibble4(block_lights, block_pos)
                        block_sky_light = _nibble4(sky_lights, block_pos)

                        try:
                            block_type = Blocks[block_id]
                        except ValueError:
                            self.unknown_blocks.add(block_id)
                            block_type = Blocks.unknown

                        # Then we get the colour, using a combination
                        # of the block_type, and no doubt some data
                        # and maybe the light values, AND DEAR LORD HELP MEEE
                        if block_type == Blocks.wool:
                            # Special case for various things. Like wool.
                            wool_type = WoolBlocks[block_data]
                            colour = COLOURS[wool_type]
                        elif block_type == Blocks.wood_planks:
                            wood_planks_type = WoodPlanksBlocks[block_data]
                            colour = COLOURS[wood_planks_type]
                        elif block_type in COLOURS:
                            colour = COLOURS[block_type]

                        else:
                            colour = COLOURS[Blocks.unknown]
                            self.colourless_blocks.add(block_type)
                        # Take the first block, don't know how to add
                        # values.
                        is_air = block_type == Blocks.air

                        if (x,z) not in series_of_blocks and not is_air:
                            series_of_blocks[x,z] = []
                        if (x,z) in series_of_blocks:
                            series_of_blocks[x,z].append((actual_y, colour))

                        if colour[3] == 255:
                            top_soiled.append((x,z))

        # END THE INCREDIBLY GIANT FOR LOOP

        # now we have a series of (height,colours) for each x,z coordinate
        # but since we can't work out the appropriate pixel value
        # just take the first.
        for x_z, blocks in series_of_blocks.items():
            x,z = x_z
            height, colour = blocks.pop()
            while blocks:
                other_height, other_colour = blocks.pop()
                colour = add_colours(colour, other_colour)

            pix[x + offset_x, z + offset_z] = colour

_renderer = Renderer()
render_region = _renderer.render_region

def _get_autoversion():
    try:
        with open('autoversion') as f:
            return int(f.read().strip("\n"))
    except (IOError, ValueError):
        return None

def render_world(world_folder,options):
    if options.ignore_autoversion:
        current_autoversion = None
    else:
        current_autoversion = _get_autoversion()


    print("Current autoversion is {}".format(current_autoversion))
    region_path = os.path.abspath(os.path.join(world_folder, 'region'))
    # We want the second part, the TAIL part
    world_name = os.path.split(os.path.abspath(world_folder))[1]
    print("Rendering the world '{}'".format(world_name))
    print("Region files at: {}".format(region_path))
    cache_folder = os.path.join("/tmp/tinybroom", world_name)
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)

    region_regex = re.compile(r'r\.(-?\d+)\.(-?\d+)\.mca')

    region_files = []
    for region_file in os.listdir(region_path):
        if region_file.endswith('.mca'):
            region_files.append(region_file)

    def key(filename):
        mo = region_regex.match(filename)
        assert mo is not None
        return int(mo.group(1)), int(mo.group(2))

    region_files.sort(key=key)
    assert region_files

    if options.processes == 1:
        pool = None
    else:
        pool = multiprocessing.Pool(options.processes)


    if not options.stitch_only:
        for region_file in region_files:
            region_file_path = os.path.join(region_path, region_file)

            x,z = key(region_file)

            region_file_path = os.path.join(region_path, region_file)
            last_modified = os.path.getmtime(region_file_path)
            cache_file = os.path.join(cache_folder, "{}.{}.cache".format(x,z))
            image_file = os.path.join(cache_folder, "{}.{}.png".format(x,z))
            reuse = False
            # The check to ignore the cache or not, is here.
            if os.path.exists(cache_file) and not options.ignore_cache:
                with open(cache_file, 'r') as f:
                    cache_details = json.load(f)
                    cache_last_modified = cache_details['last_modified']
                    cache_version = cache_details['version']

                    if (cache_last_modified == last_modified and
                        (current_autoversion is None or
                         cache_version == current_autoversion)):
                        #
                        print("Reusing image {}.".format(region_file))
                        reuse = True

            if not reuse:
                func = _render_region_from_filename_also_cache
                args = (current_autoversion, region_file_path,
                        cache_file, image_file)

                if pool is None:
                    func(*args)
                else:
                    pool.apply_async(func, args)

    if pool is not None:
        # Now wait for everyone to finish.
        pool.close()
        pool.join()

    coords = [key(region_file) for region_file in region_files]
    x_coords = [coord[0] for coord in coords]
    z_coords = [coord[1] for coord in coords]

    max_x = max(x_coords)
    min_x = min(x_coords)

    max_z = max(z_coords)
    min_z = min(z_coords)

    x_size = abs(max_x) + abs(min_x) + 1
    z_size = abs(max_z) + abs(min_z) + 1

    im = Image.new("RGBA", (512*x_size, 512*z_size))

    for region_file in region_files:
        x,z = key(region_file)
        image_path = os.path.join(cache_folder, "{}.{}.png".format(x,z))

        tiny_im = Image.open(image_path)

        coord_x = x - min_x
        coord_z = z - min_z

        im.paste(tiny_im, (512*coord_x, 512*coord_z))

    if options.rotate % 360 != 0:
        angle = options.rotate % 360
        im.rotate(angle, Image.NEAREST, expand=True)

    # TODO there is a transparent border, generally, you might want
    # to get rid of it
    im.save(options.output)

def _render_region_from_filename_also_cache(current_autoversion,
                                            region_file,cache_file,image_file):

    last_modified = os.path.getmtime(region_file)
    head, tail = os.path.split(region_file)

    print("Reading file {}".format(tail))
    region = anvil.read_region_from_file(region_file)
    print("Rendering region {}".format(tail))
    im = render_region(region)

    im.save(image_file)

    cache_details = {'last_modified': last_modified,
                     'version': current_autoversion}

    with open(cache_file, 'w') as f:
        json.dump(cache_details, f, indent=1)

def _main():
    p = argparse.ArgumentParser()
    p.add_argument("world")
    p.add_argument('-o','--output',default='out.png')
    p.add_argument('--ignore-autoversion',action='store_true')
    p.add_argument('--ignore-cache',action='store_true')
    p.add_argument('--stitch-only',action='store_true')
    p.add_argument('-r','--rotate',type=int,default=0)
    p.add_argument('-p','--processes',type=int,default=None)

    ns = p.parse_args()
    assert (ns.rotate % 90) == 0
    render_world(ns.world, ns)

if __name__=='__main__':
    _main()

