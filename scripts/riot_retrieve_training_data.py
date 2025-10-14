import asyncio
import aiohttp
from match_data_processor import map_roles, MATCH_DATA
from datetime import datetime

API_KEY = "RGAPI-9692dc56-853d-4be6-a128-eb0bc798e0fa"
QUEUE_TYPE = input("Enter queue type (e.g., RANKED_SOLO_5x5): ").strip()
TIER = input("Enter tier (e.g., DIAMOND): ").strip().upper()
DIVISION = input("Enter division (e.g., I, II, III, IV): ").strip().upper()
HEADERS = {"X-Riot-Token": API_KEY}


async def get_match_data(session, matchId):

    game_data = MATCH_DATA

    match_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{matchId}"
    match = await get_json(session, match_url)

    if match['info']['teams'][0]['win']:
        game_data['Winner'] = 'Team A'
    elif match['info']['teams'][1]['win']:
        game_data['Winner'] = 'Team B'

    # Get each position's respective participant
    team_A = map_roles(match['info']['participants'][:5])
    team_B = map_roles(match['info']['participants'][5:])
    
    for team in [team_A, team_B]:
        teamName = 'Team A' if team == team_A else 'Team B'
        for position, player in game_data[teamName].items():
            if position == 'SUPPORT': position = 'UTILITY'
            player_data = team.get(position)

            # champion name
            player['Champion'] = player_data['championName']

            # champion mastery and summoner name
            puuid = player_data['puuid']
            champId = player_data['championId']

            mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{champId}"
            mastery = await get_json(session, mastery_url)
            player['Mastery'] = mastery['championPoints']

            summoner_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
            summoner = await get_json(session, summoner_url)
            player['SummonerName'] = f'{summoner['gameName']}#{summoner['tagLine']}'

            # get summoner's rank
            rank_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
            rank = await get_json(session, rank_url)
            rank_tier = None
            rank_division = None
            for queue in rank:
                if queue['queueType'] == QUEUE_TYPE:
                    rank_tier = queue['tier']
                    rank_division = queue['rank']
            player['Rank']['Division'] = rank_division
            player['Rank']['Tier'] = rank_tier

            # get spells
            spells = [player_data['summoner1Id'], player_data['summoner2Id']]
            player['SummonerSpells'] = spells

            # get runes
            runes = [player_data['perks']['styles'][0]['selections'][0]['perk'], player_data['perks']['styles'][1]['style']]
            player['Runes']['Primary'] = runes[0]
            player['Runes']['Secondary'] = runes[1]

    date_unix = (match['info']['gameCreation'])/1000
    date = datetime.fromtimestamp(date_unix).strftime('%Y-%m-%d')
    game_data['Date'] = date

    game_data['MatchID'] = match['metadata']['matchId']

    return game_data


async def get_json(session, url):
    async with session.get(url, headers=HEADERS) as resp:
        if resp.status == 429:
            print("Rate limit hit, waiting...")
            await asyncio.sleep(2)  # simple backoff
            return await get_json(session, url)
        if resp.status == 200:
            return await resp.json()
        else:
            try:
                error_json = await resp.json()
                message = error_json.get("status", {}).get("message", str(error_json))
            except Exception:
                message = await resp.text()

            raise ConnectionError(f"API Error Code: {resp.status}, Message: {message}")

async def main():
    puuids = set()
    unique_matches = set()
    async with aiohttp.ClientSession() as session:
        # Get league entries
        league_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/{QUEUE_TYPE}/{TIER}/{DIVISION}?page=1"
        league_entries = await get_json(session, league_url)
        print(f"Found {len(league_entries)} summoners in {QUEUE_TYPE} {TIER} {DIVISION}")

        # Convert summonerId -> PUUID
        for entry in league_entries:
            print(f'PUUID: {entry['puuid']}')
            puuids.add(entry['puuid'])
        
        # Get match IDs for each PUUID
        '''
        for puuid in puuids:
            matches_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=100&queue=420"
            matches = await get_json(session, matches_url)
            unique_matches.update(matches)
        '''
        puuid_list = list(puuids)
        matches_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid_list[0]}/ids?count=100&queue=420"
        matches = await get_json(session, matches_url)
        unique_matches.update(matches)
        unique_matches_list = list(unique_matches)
        print(unique_matches_list[0])

        # Get match details and outcome
        game_data = await get_match_data(session, unique_matches_list[0])
        print(game_data)

asyncio.run(main())
