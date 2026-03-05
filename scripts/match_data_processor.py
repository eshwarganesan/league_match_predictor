MATCH_DATA = {
  'Date': '',
  'MatchID': '',
  'Winner': '',
  'Team A': {
    'TOP': {
      'SummonerName': '',
      'Champion': '',
      'ChampionID': '',
      'Runes': {
        'Primary': '',
        'Secondary': '',
      },
      'Mastery': 0,
      'SummonerSpells': [],
      'Rank': {
          'Division': '',
          'Tier': '',
      }
    },
    'JUNGLE': {
      'SummonerName': '',
      'Champion': '',
      'ChampionID': '',
      'Runes': {
        'Primary': '',
        'Secondary': '',
      },
      'Mastery': 0,
      'SummonerSpells': [],
      'Rank': {
          'Division': '',
          'Tier': '',
      }
    },
    'MIDDLE': {
      'SummonerName': '',
      'Champion': '',
      'ChampionID': '',
      'Runes': {
        'Primary': '',
        'Secondary': '',
      },
      'Mastery': 0,
      'SummonerSpells': [],
      'Rank': {
          'Division': '',
          'Tier': '',
      }
    },
    'BOTTOM': {
      'SummonerName': '',
      'Champion': '',
      'ChampionID': '',
      'Runes': {
        'Primary': '',
        'Secondary': '',
      },
      'Mastery': 0,
      'SummonerSpells': [],
      'Rank': {
          'Division': '',
          'Tier': '',
      }
    },
    'SUPPORT': {
      'SummonerName': '',
      'Champion': '',
      'ChampionID': '',
      'Runes': {
        'Primary': '',
        'Secondary': '',
      },
      'Mastery': 0,
      'SummonerSpells': [],
      'Rank': {
          'Division': '',
          'Tier': '',
      }
    }
  },
  'Team B': {
    'TOP': {
      'SummonerName': '',
      'Champion': '',
      'ChampionID': '',
      'Runes': {
        'Primary': '',
        'Secondary': '',
      },
      'Mastery': 0,
      'SummonerSpells': [],
      'Rank': {
          'Division': '',
          'Tier': '',
      }
    },
    'JUNGLE': {
      'SummonerName': '',
      'Champion': '',
      'ChampionID': '',
      'Runes': {
        'Primary': '',
        'Secondary': '',
      },
      'Mastery': 0,
      'SummonerSpells': [],
      'Rank': {
          'Division': '',
          'Tier': '',
      }
    },
    'MIDDLE': {
      'SummonerName': '',
      'Champion': '',
      'ChampionID': '',
      'Runes': {
        'Primary': '',
        'Secondary': '',
      },
      'Mastery': 0,
      'SummonerSpells': [],
      'Rank': {
          'Division': '',
          'Tier': '',
      }
    },
    'BOTTOM': {
      'SummonerName': '',
      'Champion': '',
      'ChampionID': '',
      'Runes': {
        'Primary': '',
        'Secondary': '',
      },
      'Mastery': 0,
      'SummonerSpells': [],
      'Rank': {
          'Division': '',
          'Tier': '',
      }
    },
    'SUPPORT': {
      'SummonerName': '',
      'Champion': '',
      'ChampionID': '',
      'Runes': {
        'Primary': '',
        'Secondary': '',
      },
      'Mastery': 0,
      'SummonerSpells': [],
      'Rank': {
          'Division': '',
          'Tier': '',
      }
    }
  }
}

SUMMONERS_SPELLS = {
    21: 'Barrier',
    1: 'Cleanse',
    2202: 'Flash',
    14: 'Ignite',
    3: 'Exhaust',
    4: 'Flash',
    6: 'Ghost',
    7: 'Heal',
    11: 'Smite',
    12: 'Teleport',
}

RUNE = {
    8100: 'Domination',
    8112: 'Electrocute',
    8128: 'Dark Harvest',
    8300: 'Inspiration',
    9923: 'Hail of Blades',
    8351: 'Glacial Augment',
    8360: 'Unsealed Spellbook',
    8369: 'First Strike',
    8000: 'Precision',
    8005: 'Press the Attack',
    8008: 'Lethal Tempo',
    8021: 'Fleet of Footwork',
    8010: 'Conqueror',
    8400: 'Resolve',
    8437: 'Grasp of the Undying',
    8439: 'Aftershock',
    8465: 'Guardian',
    8200: 'Sorcery',
    8214: 'Summon Aery',
    8229: 'Arcane Comet',
    8230: 'Phase Rush',
}  

def map_roles(team_participants):
    role_map = {}
    for player in team_participants:
        role = player.get('teamPosition', 'NONE')
        role_map[role] = player
    return role_map


def save_match_data(game_data):
    teamA = game_data['Team A']
    teamB = game_data['Team B']


def parse_match_data(game_data):
    pass