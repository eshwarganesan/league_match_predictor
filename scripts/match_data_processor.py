MATCH_DATA = {
  'Date': '',
  'MatchID': '',
  'Team A': {
    'Result': '',
    'Top': {
      'SummonerName': '',
      'Champion': '',
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
    'Jungle': {
      'SummonerName': '',
      'Champion': '',
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
    'Mid': {
      'SummonerName': '',
      'Champion': '',
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
    'Bot': {
      'SummonerName': '',
      'Champion': '',
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
    'Support': {
      'SummonerName': '',
      'Champion': '',
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
    'Result': '',
    'Top': {
      'SummonerName': '',
      'Champion': '',
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
    'Jungle': {
      'SummonerName': '',
      'Champion': '',
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
    'Mid': {
      'SummonerName': '',
      'Champion': '',
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
    'Bot': {
      'SummonerName': '',
      'Champion': '',
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
    'Support': {
      'SummonerName': '',
      'Champion': '',
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

def map_roles(team_participants):
    role_map = {}
    for player in team_participants:
        role = player.get('teamPosition', 'NONE')
        role_map[role] = player
    return role_map


def parse_match_data(game_data):
    pass