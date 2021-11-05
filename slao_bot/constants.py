from enum import Enum


class Role(str, Enum):
    TANK = 'tank'
    DPS = 'dps'
    HEALER = 'healer'


SPECS = {
    'Druid_Balance': '<:Druid_Balance:880098174985961542>',
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
#   45051: "Mad Alchemist's Potion"


COMBAT_POTS = {
    "Mana Pot": [17531, 28499, 41617],
    "Healing Pot": [17534, 28495],
    "Heal and Mana Pot": [45051],
    "Mana Gem": [10052, 10058, 27103],
    "Healthstone": [27235, 27236, 27237],
    "Mana Runes": [16666, 27869],
    "Drums": [35476, 35478],
    "Herbs": [28527, 28714, 28726],
    "School Prot": [28513],
    "Combat Pot": [28507, 28508, 28515],
}
