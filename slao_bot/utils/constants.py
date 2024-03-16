from enum import Enum


class Role(str, Enum):
    TANK = 'tank'
    DPS = 'dps'
    HEALER = 'healer'


SPECS = {
    'DeathKnight_Blood': '<:DeathKnight_Blood:1015254887040303143>',
    'DeathKnight_BloodDPS': '<:DeathKnight_BloodDPS:1129197573882794064>',
    'DeathKnight_Frost': '<:DeathKnight_Frost:1015254314547167252>',
    'DeathKnight_Lichborne': '<:DeathKnight_Lichborne:1032213432382005268>',
    'DeathKnight_Runeblade': '<:DeathKnight_Runeblade:1030424355508863027>',
    'DeathKnight_Unholy': '<:DeathKnight_Unholy:1015252279668002826>',
    'Druid_Balance': '<:Druid_Balance:880098174985961542>',
    'Druid_Dreamstate': '<:Druid_Dreamstate:990644826657681418>',
    'Druid_Feral': '<:Druid_Feral:880098483636408392>',
    'Druid_Guardian': '<:druid_guardian:880068396803297311>',
    'Druid_Restoration': '<:Druid_Restoration:880089474753785897>',
    'Druid_Warden': '<:Druid_Warden:880081285501046854>',
    'Hunter_BeastMastery': '<:Hunter_BeastMastery:880083922120233030>',
    'Hunter_Marksmanship': '<:Hunter_Marksmanship:881622924564516934>',
    'Hunter_Survival': '<:Hunter_Survival:887527410004803624>',
    'Mage_Arcane': '<:Mage_Arcane:880098759936196669>',
    'Mage_Fire': '<:Mage_Fire:880083302306947113>',
    'Mage_Frost': '<:Mage_Frost:881623228177596437>',
    'Paladin_Holy': '<:Paladin_Holy:880089741847060550>',
    'Paladin_Justicar': '<:Paladin_Justicar:967337482020585553>',
    'Paladin_Protection': '<:Paladin_Protection:880076303615787009>',
    'Paladin_Retribution': '<:Paladin_Retribution:880099271645470750>',
    'Priest_Discipline': '<:Priest_Discipline:880089778551414824>',
    'Priest_Holy': '<:Priest_Holy:880089805990535169>',
    'Priest_Shadow': '<:Priest_Shadow:880099152548208731>',
    'Priest_Smiter': '<:Priest_Smiter:880085315149258848>',
    'Rogue_Assassination': '<:Rogue_Assassination:881623680025780245>',
    'Rogue_Combat': '<:Rogue_Combat:880082256373370891>',
    'Rogue_Subtlety': '<:Rogue_Subtlety:1129198294648770681>',
    'Shaman_Elemental': '<:Shaman_Elemental:880084253700923412>',
    'Shaman_Enhancement': '<:Shaman_Enhancement:880082514683756615>',
    'Shaman_Restoration': '<:Shaman_Restoration:880099191706247208>',
    'Warlock_Affliction': '<:Warlock_Affliction:880099108369612801>',
    'Warlock_Demonology': '<:Warlock_Demonology:880090452949336125>',
    'Warlock_Destruction': '<:Warlock_Destruction:880085124606210109>',
    'Warrior_Arms': '<:Warrior_Arms:880084581901025340>',
    'Warrior_Champion': '<:Warrior_Champion:887526073380790333>',
    'Warrior_Fury': '<:Warrior_Fury:880084813376286762>',
    'Warrior_Gladiator': '<:Warrior_Gladiator:884439137493610616>',
    'Warrior_Protection': '<:Warrior_Protection:880080701930733638>',
}

ZONE_IMAGES = {
    0: 'https://raid-helper.dev/uploads/banners/gw2/raids.png',
    # Molten Core
    1000: 'https://raid-helper.dev/uploads/banners/classic/image0.jpg',
    # Onyxia
    1001: 'https://raid-helper.dev/uploads/banners/classic/image1.jpg',
    # BWL
    1002: 'https://raid-helper.dev/uploads/banners/classic/image2.jpg',
    # ZG
    1003: 'https://raid-helper.dev/uploads/banners/classic/RH-ZG2.png',
    # AQ20
    1004: 'https://raid-helper.dev/uploads/banners/classic/RH-AQ20.png',
    # AQ40
    1005: 'https://raid-helper.dev/uploads/banners/classic/RH-AQ40-1.png',
    # Naxramas
    1006: 'https://raid-helper.dev/uploads/banners/classic/RH-Naxx-3.png',
    # Karazhan
    1007: 'https://raid-helper.dev/uploads/banners/tbc/RH-TBC-Karazhan1-1200x300.png',
    # Gruul + Magtheridon
    1008: 'https://raid-helper.dev/uploads/banners/tbc/RH-TBC-GruulMaggie_1200x300.png',
    # Heroics
    1009: 'https://raid-helper.dev/uploads/banners/retail/RH-MYTHICS-1.png',
    # SSK + TK
    1010: 'https://raid-helper.dev/uploads/banners/tbc/RH-TBC-SSCTK_1200x300.png',
    # BT
    1011: 'https://raid-helper.dev/uploads/banners/tbc/RH-TBC-MTBT2_1200x300.png',
    # ZA
    1012: 'https://raid-helper.dev/uploads/banners/tbc/RH-TBC-ZA1_1200x300.png',
    # SWP
    1013: 'https://raid-helper.dev/uploads/banners/tbc/RH-TBC-SWP1_1200x300.png',
    # WotLK Heroics
    1014: 'https://raid-helper.dev/uploads/banners/retail/RH-MYTHICS-1.png',
    # Naxx, Sart, Maly
    1015: 'https://raid-helper.dev/uploads/banners/wotlk/RH-Wrath-P1Raids_1200x300.png',
    # Archavon
    1016: 'https://raid-helper.dev/uploads/banners/wotlk/RH-Wrath-VoA1_1200x300.png',
    # Ulduar
    1017: 'https://raid-helper.dev/uploads/banners/wotlk/ulduar_3.png',
    # ToC
    1018: 'https://cdn.discordapp.com/attachments/762790105026920468/1121486358117109912/ToC_Banner.png',
    # Ony-80
    1019: 'https://cdn.discordapp.com/attachments/762790105026920468/762790309100388382/image1.jpg',
    # ICC
    1020: 'https://cdn.discordapp.com/attachments/762790105026920468/1151338038736195684/icc_draft1.jpg',
    # RS
    1021: 'https://cdn.discordapp.com/attachments/873895928480817253/1198959475525173339/RubySanctum.png',

}

ZONE_NAMES = {
    0: ':regional_indicator_r: :regional_indicator_a: :id:',
    1000: ':regional_indicator_m: :regional_indicator_c:',
    1001: ':regional_indicator_o: :regional_indicator_n: :regional_indicator_y:',
    1002: ':regional_indicator_b: :regional_indicator_w: :regional_indicator_l:',
    1003: ':regional_indicator_z: :regional_indicator_g:',
    1004: ':regional_indicator_a: :regional_indicator_q: :two: :zero:',
    1005: ':regional_indicator_a: :regional_indicator_q: :four: :zero:',
    1006: ':regional_indicator_n: :regional_indicator_a: :regional_indicator_x: :regional_indicator_x:'
          ':regional_indicator_r: :regional_indicator_a: :regional_indicator_m: :regional_indicator_a:'
          ':regional_indicator_s:',
    1007: ':regional_indicator_k: :regional_indicator_a: :regional_indicator_r: :regional_indicator_a: '
          ':regional_indicator_z: :regional_indicator_h: :regional_indicator_a: :regional_indicator_n:',
    1008: ':regional_indicator_g: :regional_indicator_r: :regional_indicator_u: :regional_indicator_u: '
          ':regional_indicator_l: :left_right_arrow: :regional_indicator_m: :regional_indicator_a: '
          ':regional_indicator_g: :regional_indicator_a:',
    1009: ':regional_indicator_p: :regional_indicator_a: :regional_indicator_r: :regional_indicator_t:'
          ':regional_indicator_y:',
    1010: ':regional_indicator_s: :regional_indicator_s: :regional_indicator_k: :left_right_arrow:'
          ':regional_indicator_t: :regional_indicator_k:',
    1011: ':regional_indicator_b: :regional_indicator_t: :left_right_arrow: :regional_indicator_h:'
          ':regional_indicator_y: :regional_indicator_j: :regional_indicator_a::regional_indicator_l:',
    1012: ':regional_indicator_z: :regional_indicator_u: :regional_indicator_l: :regional_indicator_a: '
          ':regional_indicator_m: :regional_indicator_a: :regional_indicator_n:',
    1013: ':regional_indicator_s: :regional_indicator_u: :regional_indicator_n: :regional_indicator_w: '
          ':regional_indicator_e: :regional_indicator_l: :regional_indicator_l:',
    1014: ':regional_indicator_h: :regional_indicator_e: :regional_indicator_r: :regional_indicator_o: '
          ':regional_indicator_i: :regional_indicator_k: :regional_indicator_s:',
    1015: ':regional_indicator_t: :regional_indicator_i: :regional_indicator_e: :regional_indicator_r: '
          ':seven:',
    1016: ':regional_indicator_a: :regional_indicator_r: :regional_indicator_c: :regional_indicator_h: '
          ':regional_indicator_a: :regional_indicator_v: :regional_indicator_o: :regional_indicator_n:',
    1017: ':regional_indicator_u: :regional_indicator_l: :regional_indicator_d: :regional_indicator_u: '
          ':regional_indicator_a: :regional_indicator_r:',
    1018: ':regional_indicator_t: :regional_indicator_o: :regional_indicator_c:',
    1019: ':regional_indicator_o: :regional_indicator_n: :regional_indicator_y:',
    1020: ':regional_indicator_i: :regional_indicator_c: :regional_indicator_c:',
    1021: ':regional_indicator_r: :regional_indicator_s:',



}
EXEC_VALUES = {
    0: 'Слабо',
    1: 'На троечку',
    2: 'Крутим гайки',
    3: 'МоЩЩно',
}

# Combat consumables with short cooldown
# TBC consumables
#   10052: "Mana Jade"
#   10058: "Mana Ruby"
#   16666: "Demonic Rune"
#   17531: "Major Mana Pot"
#   17534: "Major Healing Pot"
#   27103: "Mana Emerald"
#   27235: "Master Healthstone"
#   27236: "Master Healthstone"
#   27237: "Master Healthstone"
#   27869: "Dark Rune"
#   28495: "Super Healing Pot"
#   28499: "Super Mana Pot"
#   28507: "Haste Pot"
#   28508: "Destruction Pot"
#   28513: "Nature Protection"
#   28515: "2.5k armor"
#   28527: "Fel Blossom"
#   28714: "Flame Cap"
#   28726: "Nightmare Seed"
#   35476: "Drums of Battle"
#   35478: "Drums of Restoration"
#   41617: "Cenarion Mana"
#   41618: "Bottled Nethergon Energy"
#   45051: "Mad Alchemist's Potion"
#   351355: "Greater Drums of Battle"
#   351360: "Greater Drums of War"
#   351358: "Greater Drums of Restoration"

# WotLK consumables
HP_MANA_POTS = {
    '43186',  # Runic mana pot
    '67490',  # Runic mana injector
    '43185',  # Runic healing pot
    '67489',  # Runic healing injector
    '53750',  # Crazy Alchemist's pot
    '53761',  # Powerful Rejuvenation pot
}

HP_MANA_STONES = {
    '42987',  # Mana Sapphire
    '47872',  # Master Healthstone
    '47873',  # Master Healthstone
    '47874',  # Master Healthstone
    '47875',  # Master Healthstone
    '47876',  # Master Healthstone
    '47877',  # Master Healthstone
}

COMBAT_POTS = {
    '53762',  # 3.5k armor
    '53908',  # Potion of Speed
    '53909',  # Wild Magic pot
}

POT_IMAGES = {
    'hp_mana_pots': '<:hp_mana_pot:906161254316507187>',
    'hp_mana_stones': '<:mana_gem:1129159265274306633>',
    'combat_pots': '<:combat_pot:1129159544258441377>',
}

SLOT_NAMES = {
    0: 'Голова',
    1: 'Шея',
    2: 'Плечи',
    3: 'Рубашка',
    4: 'Нагрудник',
    5: 'Пояс',
    6: 'Ноги',
    7: 'Ступни',
    8: 'Запястья',
    9: 'Кисти рук',
    10: 'Кольцо',
    11: 'Кольцо',
    12: 'Аксессуар',
    13: 'Аксессуар',
    14: 'Спина',
    15: 'Оружие',
    16: 'Левая рука',
    17: 'Дальний бой',
}

CLASS_COEFF = {
    'Mage': {
        'Arcane': 1.22,
        'Fire': 1.03,
        'Frost': 1.55,
    },
    'Rogue': {
        'Combat': 1.12,
        'Assassination': 1.14,
        'Subtlety': 1.38,
    },
    'Shaman': {
        'Elemental': 1.14,
        'Enhancement': 1.14,
    },
    'Warrior': {
        'Fury': 1.13,
        'Arms': 1.31,
        'Gladiator': 4.55,
    },
    'Paladin': {
        'Retribution': 1.12,
    },
    'Warlock': {
        'Demonology': 1.2,
        'Destruction': 1.21,
        'Affliction': 1.04,
    },
    'DeathKnight': {
        'Unholy': 1,
        'Frost': 1.12,
        'BloodDPS': 1.53,
    },
    'Hunter': {
        'Survival': 1.17,
        'Beast Mastery': 1.43,
        'Marksmanship': 1.3,
    },
    'Druid': {
        'Balance': 1.16,
        'Feral': 1.1,
    },
    'Priest': {
        'Shadow': 1.23,
    },

}
