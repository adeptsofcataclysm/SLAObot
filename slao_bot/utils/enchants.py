ENCHANTABLE_SLOT = {
    0,  # Head
    2,  # Shoulders
    4,  # Chest
    6,  # Leggings
    7,  # Boots
    8,  # Bracers
    9,  # Hands
    15,  # Main hand
}

BAD_ENCHANTS = {
    0: [
        2841,  # Heavy Knothide Kit
        2591,  # Head/Legs - ZG
        2586,  # Head/Legs - ZG
        2588,  # Head/Legs - ZG
        2584,  # Head/Legs - ZG
        2590,  # Head/Legs - ZG
        2585,  # Head/Legs - ZG
        2587,  # Head/Legs - ZG
        2589,  # Head/Legs - ZG
    ],
    2: [
        2606,  # Shoulder - ZG
        2605,  # Shoulder - ZG
        2604,  # Shoulder - ZG
        2996,  # Shoulder - Scryer Hon
        2990,  # Shoulder - Scryer Hon
        2992,  # Shoulder - Scryer Hon
        2994,  # Shoulder - Scryer Hon
        2981,  # Shoulder - Aldor Hon
        2979,  # Shoulder - Aldor Hon
        2983,  # Shoulder - Aldor Hon
        2977,  # Shoulder - Aldor Hon
        2841,  # Heavy Knothide Kit
    ],
    4: [
        908,  # Chest - 50 HP
        850,  # Chest - 35 HP
        254,  # Chest - 25 HP
        242,  # Chest - 15 HP
        41,   # Chest - 5 HP
        913,  # Chest - 65 Mana
        857,  # Chest - 50 Mana
        843,  # Chest - 30 Mana
        246,  # Chest - 20 Mana
        24,   # Chest - 5 Mana
        928,  # Chest - 3 Stats
        866,  # Chest - 2 Stats
        847,  # Chest - 1 Stats
        63,   # Chest - 25 Absorb
        44,   # Chest - 10 Absorb
        1891,  # Chest - 4 Stats
        1893,  # Chest - 100 Mana
        2841,  # Heavy Knothide Kit
        2792,  # Knothide Kit
        2503,  # 3 Def
        1843,  # 40 Armor
        18,   # 32 Armor
        17,   # 24 Armor
        16,   # 16 Armor
        15,   # 8 Armor
    ],
    6: [
        2591,  # Head/Legs - ZG
        2586,  # Head/Legs - ZG
        2588,  # Head/Legs - ZG
        2584,  # Head/Legs - ZG
        2590,  # Head/Legs - ZG
        2585,  # Head/Legs - ZG
        2587,  # Head/Legs - ZG
        2589,  # Head/Legs - ZG
        2583,  # Warrior Legs - ZG
        2841,  # Heavy Knothide Kit
        2792,  # Knothide Kit
        2503,  # 3 Def
        1843,  # 40 Armor
        18,    # 32 Armor
        17,    # 24 Armor
        16,    # 16 Armor
        15,    # 8 Armor
        2745,  # Legs - Silver Thread
        2747,  # Legs - Mystic Thread
        3010,  # Legs - 40AP/10Crit
    ],
    7: [
        255,  # Boots - 3 Spi
        904,  # Boots - 5 Agi
        849,  # Boots - 3 Agi
        247,  # Boots - 1 Agi
        852,  # Boots - 5 Sta
        724,  # Boots - 3 Sta
        66,   # Boots - 1 Sta
        1887,  # Boots - 7 Agi
        929,  # Boots - 7 Sta
        911,  # Boots - Minor Speed
        464,  # Boots - Mount Speed
        2841,  # Heavy Knothide Kit
        2792,  # Knothide Kit
        2503,  # 3 Def
        1843,  # 40 Armor
        18,   # 32 Armor
        17,   # 24 Armor
        16,   # 16 Armor
        15,   # 8 Armor
    ],
    8: [
        927,  # Bracers - 7 Str
        856,  # Bracers - 5 Str
        823,  # Bracers - 3 Str
        248,  # Bracers - 1 Str
        929,  # Bracers - 7 Sta
        852,  # Bracers - 5 Sta
        724,  # Bracers - 3 Sta
        66,   # Bracers - 1 Sta
        41,   # Bracers - 5 HP
        907,  # Bracers - 7 Spi
        851,  # Bracers - 5 Spi
        255,  # Bracers - 3 Spi
        905,  # Bracers - 5 Int
        723,  # Bracers - 3 Int
        923,  # Bracers - 3 Def
        925,  # Bracers - 2 Def
        924,  # Bracers - 1 Def
        1886,  # Bracers - 9 Sta
        1885,  # Bracers - 9 Str
    ],
    9: [
        1887,  # Gloves - 7 Agi
        904,   # Gloves - 5 Agi
        856,   # Gloves - 5 Str
        909,   # Gloves - 5 Herb
        845,   # Gloves - 3 Herb
        906,   # Gloves - 5 Mining
        844,   # Gloves - 3 Mining
        865,   # Gloves - 5 Skinn
        846,   # Gloves - 2 Fishing
        2934,  # Gloves - Blasting
        927,   # Gloves - 7 Str
        930,   # Gloves - Mount Speed
        2503,  # 3 Def
        1843,  # 40 Armor
        18,    # 32 Armor
        17,    # 24 Armor
        16,    # 16 Armor
        15,    # 8 Armor
        2792,  # Knothide Kit
    ],
    15: [
        1903,  # Weapon - 9 Spi
        255,  # Weapon - 3 Spi
        1904,  # Weapon - 9 Int
        723,  # Weapon - 3 Int
        1896,  # Weapon - 9 Dmg
        963,  # Weapon - 7 Dmg
        943,  # Weapon - 3 Dmg
        241,  # Weapon - 2 Dmg
        2443,  # Weapon - 7 Frost
        1899,  # Weapon - Unholy
        1898,  # Weapon - Lifesteal
        803,  # Weapon - Fiery
        854,  # Weapon - Elemental
        805,  # Weapon - 4 Dmg
        943,  # Weapon - 3 Dmg
        2646,  # Weapon - 25 Agi
        2568,  # Weapon - 22 Int
        1900,  # Weapon - Crusader
    ],
}
