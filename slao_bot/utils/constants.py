from enum import Enum


class Role(str, Enum):
    TANK = 'tank'
    DPS = 'dps'
    HEALER = 'healer'


SPECS = {
    'DeathKnight_Blood': '<:DeathKnight_Blood:1015254887040303143>',
    'DeathKnight_Frost': '<:DeathKnight_Frost:1015254314547167252>',
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
    0: 'https://cdn.discordapp.com/attachments/762790105026920468/843540093422796810/RH-TBC-DarkPortal1-1200x300.png',
    # Molten Core
    1000: 'https://cdn.discordapp.com/attachments/762790105026920468/762790308844273714/image0.jpg',
    # Onyxia
    1001: 'https://cdn.discordapp.com/attachments/762790105026920468/762790309100388382/image1.jpg',
    # BWL
    1002: 'https://cdn.discordapp.com/attachments/762790105026920468/762790309376688128/image2.jpg',
    # ZG
    1003: 'https://cdn.discordapp.com/attachments/762790105026920468/763170902271197204/RH-ZG2.png',
    # AQ20
    1004: 'https://cdn.discordapp.com/attachments/762790105026920468/763170907035533362/RH-AQ20-1.png',
    # AQ40
    1005: 'https://cdn.discordapp.com/attachments/762790105026920468/763170914220900392/RH-AQ40-1.png',
    # Naxx
    1006: 'https://media.discordapp.net/attachments/762790105026920468/773622157456572486/RH-Naxx-2.png',
    # Karazhan
    1007: 'https://cdn.discordapp.com/attachments/762790105026920468/843540146379948042/RH-TBC-Karazhan1-1200x300.png',
    # Gruul + Magtheridon
    1008: 'https://cdn.discordapp.com/attachments/762790105026920468/'
          '876774093943349258/RH-TBC-GruulMaggie_1200x300.png',
    # Heroics
    1009: 'https://cdn.discordapp.com/attachments/762790105026920468/841635106954149898/dungeons.png',
    # SSK + TK
    1010: 'https://cdn.discordapp.com/attachments/762790105026920468/887556750134374420/EyeAndSSCpng.png',
    # BT
    1011: 'https://cdn.discordapp.com/attachments/762790105026920468/935942801642905600/RH-TBC-MTBT2_1200x300.png',
    # ZA
    1012: 'https://cdn.discordapp.com/attachments/762790105026920468/951451058985652264/RH-TBC-ZA1_1200x300.png',
    # SWP
    1013: 'https://cdn.discordapp.com/attachments/762790105026920468/773981418052386866/8._TBC_SWP.png',
    # WotLK Heorics
    1014: 'https://cdn.discordapp.com/attachments/762790105026920468/841635106954149898/dungeons.png',
    # Naxx, Sart, Maly
    1015: 'https://media.discordapp.net/attachments/762790105026920468/1023622172117311528/'
          'RH-Wrath-P1Raids_1200x300.png',
    # Archavon
    1016: 'https://cdn.discordapp.com/attachments/762790105026920468/843540093422796810/'
          'RH-TBC-DarkPortal1-1200x300.png',
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


}
EXEC_VALUES = {
    0: 'Слабо',
    1: 'На троечку',
    2: 'Крутим гайки',
    3: 'МоЩЩно',
}

# Combat consumables with short cooldown
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


COMBAT_POTS = {
    'Mana Pot': [17531, 28499, 41617, 41618],
    'Healing Pot': [17534, 28495],
    'Heal and Mana Pot': [45051],
    'Mana Gem': [10052, 10058, 27103],
    'Healthstone': [27235, 27236, 27237],
    'Mana Runes': [16666, 27869],
    'Drums': [35476, 35478, 351355, 351360, 351358],
    'Herbs': [28527, 28714, 28726],
    'School Prot': [28513],
    'Combat Pot': [28507, 28508, 28515],
}

POT_IMAGES = {
    'mana': '<:inv_potion_137:906160204960395284>',
    'hp': '<:inv_potion_131:906160204868100127>',
    'hpmana': '<:inv_potion_134:906161254316507187>',
    'manarunes': '<:spell_shadow_sealofkings:906160351064760332> или <:inv_misc_rune_04:906160171238195200>',
    'drums': '<:inv_misc_drum_021:906160171489853470> <:inv_misc_drum_03:906160171217190912>'
             ' <:inv_misc_drum_07:906160171204616232>',
    'herbs': '<:inv_misc_herb_flamecap:906160171007492097> <:inv_misc_herb_nightmareseed:906160171246567454>',
    'combatpots': '<:inv_potion_108:906160205094584380> <:inv_potion_107:906160171246551050>'
                  '<:inv_potion_133:906160204985544744>',
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
}
