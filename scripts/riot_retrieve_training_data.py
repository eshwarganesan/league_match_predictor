import asyncio
import aiohttp
from match_data_processor import map_roles, MATCH_DATA
from datetime import datetime

API_KEY = "RGAPI-9692dc56-853d-4be6-a128-eb0bc798e0fa"
QUEUE_TYPE = input("Enter queue type (e.g., RANKED_SOLO_5x5): ").strip()
TIER = input("Enter tier (e.g., DIAMOND): ").strip().upper()
DIVISION = input("Enter division (e.g., I, II, III, IV): ").strip().upper()
HEADERS = {"X-Riot-Token": API_KEY}


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
    game_data = MATCH_DATA
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
        match_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{unique_matches_list[0]}"
        match = await get_json(session, match_url)
        print(match)
        team_A_result = 'win' if match['info']['teams'][0]['win'] == True else 'loss'
        team_B_result = 'win' if match['info']['teams'][1]['win'] == True else 'loss' 

        # Get each position's respective participant
        team_A = map_roles(match['info']['participants'][:5])
        team_B = map_roles(match['info']['participants'][5:])

        topA = team_A.get('TOP')
        jungleA = team_A.get('JUNGLE')
        midA = team_A.get('MIDDLE')
        botA = team_A.get('BOTTOM')
        suppA = team_A.get('UTILITY')

        topB = team_B.get('TOP')
        jungleB = team_B.get('JUNGLE')
        midB = team_B.get('MIDDLE')
        botB = team_B.get('BOTTOM')
        suppB = team_B.get('UTILITY')

        # Get each champion names
        top_champ_A = topA['championName']
        jungle_champ_A = jungleA['championName']
        mid_champ_A = midA['championName']
        bot_champ_A = botA['championName']
        supp_champ_A = suppA['championName']
        top_champ_B = topB['championName']
        jungle_champ_B = jungleB['championName']
        mid_champ_B = midB['championName']
        bot_champ_B = botB['championName']
        supp_champ_B = suppB['championName']
      
        # Get champion mastery and summoner name
        top_puuid_A = topA['puuid']
        top_champId_A = topA['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{top_puuid_A}/by-champion/{top_champId_A}"
        top_mastery_A = await get_json(session, mastery_url)
        summoner_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{top_puuid_A}"
        top_summoner_A = await get_json(session, summoner_url)
        
        jungle_puuid_A = jungleA['puuid']
        jungle_champId_A = jungleA['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{jungle_puuid_A}/by-champion/{jungle_champId_A}"
        jungle_mastery_A = await get_json(session, mastery_url)
        summoner_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{jungle_puuid_A}"
        jungle_summoner_A = await get_json(session, summoner_url)

        mid_puuid_A = midA['puuid']
        mid_champId_A = midA['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{mid_puuid_A}/by-champion/{mid_champId_A}"
        mid_mastery_A = await get_json(session, mastery_url)
        summoner_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{mid_puuid_A}"
        mid_summoner_A = await get_json(session, summoner_url)

        bot_puuid_A = botA['puuid']
        bot_champId_A = botA['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{bot_puuid_A}/by-champion/{bot_champId_A}"
        bot_mastery_A = await get_json(session, mastery_url)
        summoner_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{bot_puuid_A}"
        bot_summoner_A = await get_json(session, summoner_url)

        supp_puuid_A = suppA['puuid']
        supp_champId_A = suppA['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{supp_puuid_A}/by-champion/{supp_champId_A}"
        supp_mastery_A = await get_json(session, mastery_url)
        summoner_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{supp_puuid_A}"
        supp_summoner_A = await get_json(session, summoner_url)
        
        top_puuid_B = topB['puuid']
        top_champId_B = topB['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{top_puuid_B}/by-champion/{top_champId_B}"
        top_mastery_B = await get_json(session, mastery_url)
        summoner_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{top_puuid_B}"
        top_summoner_b = await get_json(session, summoner_url)
        
        jungle_puuid_B = jungleB['puuid']
        jungle_champId_B = jungleB['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{jungle_puuid_B}/by-champion/{jungle_champId_B}"
        jungle_mastery_B = await get_json(session, mastery_url)
        summoner_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{jungle_puuid_B}"
        jungle_summoner_B = await get_json(session, summoner_url)

        mid_puuid_B = midB['puuid']
        mid_champId_B = midB['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{mid_puuid_B}/by-champion/{mid_champId_B}"
        mid_mastery_B = await get_json(session, mastery_url)
        summoner_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{mid_puuid_B}"
        mid_summoner_B = await get_json(session, summoner_url)

        bot_puuid_B = botB['puuid']
        bot_champId_B = botB['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{bot_puuid_B}/by-champion/{bot_champId_B}"
        bot_mastery_B = await get_json(session, mastery_url)
        summoner_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{bot_puuid_B}"
        bot_summoner_B = await get_json(session, summoner_url)

        supp_puuid_B = suppB['puuid']
        supp_champId_B = suppB['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{supp_puuid_B}/by-champion/{supp_champId_B}"
        supp_mastery_B = await get_json(session, mastery_url)
        summoner_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{supp_puuid_B}"
        supp_summoner_B = await get_json(session, summoner_url)

        # Get player's rank
        rank_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/{top_puuid_A}"
        top_rank_A = await get_json(session, rank_url)
        top_tier_A = None
        top_division_A = None
        for queue in top_rank_A:
            if queue['queueType'] == QUEUE_TYPE:
                top_tier_A = queue['tier']
                top_division_A = queue['rank']

        rank_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/{jungle_puuid_A}"
        jungle_rank_A = await get_json(session, rank_url)
        jungle_tier_A = None
        jungle_division_A = None
        for queue in jungle_rank_A:
            if queue['queueType'] == QUEUE_TYPE:
                jungle_tier_A = queue['tier']
                jungle_division_A = queue['rank']

        rank_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/{mid_puuid_A}"
        mid_rank_A = await get_json(session, rank_url)
        mid_tier_A = None
        mid_division_A = None
        for queue in mid_rank_A:
            if queue['queueType'] == QUEUE_TYPE:
                mid_tier_A = queue['tier']
                mid_division_A = queue['rank']

        rank_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/{bot_puuid_A}"
        bot_rank_A = await get_json(session, rank_url)
        bot_tier_A = None
        bot_division_A = None
        for queue in bot_rank_A:
            if queue['queueType'] == QUEUE_TYPE:
                bot_tier_A = queue['tier']
                bot_division_A = queue['rank']

        rank_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/{supp_puuid_A}"
        supp_rank_A = await get_json(session, rank_url)
        supp_tier_A = None
        supp_division_A = None
        for queue in supp_rank_A:
            if queue['queueType'] == QUEUE_TYPE:
                supp_tier_A = queue['tier']
                supp_division_A = queue['rank']
                
        rank_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/{top_puuid_B}"
        top_rank_B = await get_json(session, rank_url)
        top_tier_B = None
        top_division_B = None
        for queue in top_rank_B:
            if queue['queueType'] == QUEUE_TYPE:
                top_tier_B = queue['tier']
                top_division_B = queue['rank']

        rank_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/{jungle_puuid_B}"
        jungle_rank_B = await get_json(session, rank_url)
        jungle_tier_B = None
        jungle_division_B = None
        for queue in jungle_rank_B:
            if queue['queueType'] == QUEUE_TYPE:
                jungle_tier_B = queue['tier']
                jungle_division_B = queue['rank']

        rank_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/{mid_puuid_B}"
        mid_rank_B = await get_json(session, rank_url)
        mid_tier_B = None
        mid_division_B = None
        for queue in mid_rank_B:
            if queue['queueType'] == QUEUE_TYPE:
                mid_tier_B = queue['tier']
                mid_division_B = queue['rank']

        rank_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/{bot_puuid_B}"
        bot_rank_B = await get_json(session, rank_url)
        bot_tier_B = None
        bot_division_B = None
        for queue in bot_rank_B:
            if queue['queueType'] == QUEUE_TYPE:
                bot_tier_B = queue['tier']
                bot_division_B = queue['rank']

        rank_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/{supp_puuid_B}"
        supp_rank_B = await get_json(session, rank_url)
        supp_tier_B = None
        supp_division_B = None
        for queue in supp_rank_B:
            if queue['queueType'] == QUEUE_TYPE:
                supp_tier_B = queue['tier']
                supp_division_B = queue['rank']

        # Get summoner's spells
        top_spells_A = [topA['summoner1Id'], topA['summoner2Id']]
        jungle_spells_A = [jungleA['summoner1Id'], jungleA['summoner2Id']]
        mid_spells_A = [midA['summoner1Id'], midA['summoner2Id']]
        bot_spells_A = [botA['summoner1Id'], botA['summoner2Id']]
        supp_spells_A = [suppA['summoner1Id'], suppA['summoner2Id']]
        top_spells_B = [topB['summoner1Id'], topB['summoner2Id']]
        jungle_spells_B = [jungleB['summoner1Id'], jungleB['summoner2Id']]
        mid_spells_B = [midB['summoner1Id'], midB['summoner2Id']]
        bot_spells_B = [botB['summoner1Id'], botB['summoner2Id']]
        supp_spells_B = [suppB['summoner1Id'], suppB['summoner2Id']]

        # Get primary runes       
        top_runes_A = [topA['perks']['styles'][0]['selections'][0]['perk'], topA['perks']['styles'][1]['style']]
        jungle_runes_A = [jungleA['perks']['styles'][0]['selections'][0]['perk'], jungleA['perks']['styles'][1]['style']]
        mid_runes_A = [midA['perks']['styles'][0]['selections'][0]['perk'], midA['perks']['styles'][1]['style']]
        bot_runes_A = [botA['perks']['styles'][0]['selections'][0]['perk'], botA['perks']['styles'][1]['style']]
        supp_runes_A = [suppA['perks']['styles'][0]['selections'][0]['perk'], suppA['perks']['styles'][1]['style']]
        top_runes_B = [topB['perks']['styles'][0]['selections'][0]['perk'], topB['perks']['styles'][1]['style']]
        jungle_runes_B = [jungleB['perks']['styles'][0]['selections'][0]['perk'], jungleB['perks']['styles'][1]['style']]
        mid_runes_B = [midB['perks']['styles'][0]['selections'][0]['perk'], midB['perks']['styles'][1]['style']]
        bot_runes_B = [botB['perks']['styles'][0]['selections'][0]['perk'], botB['perks']['styles'][1]['style']]
        supp_runes_B = [suppB['perks']['styles'][0]['selections'][0]['perk'], suppB['perks']['styles'][1]['style']]

        # Assign all variables to game data
        game_data['Team A']['Top']['SummonerName'] = f"{top_summoner_A['gameName']}#{top_summoner_A['tagLine']}"
        game_data['Team A']['Top']['Champion'] = top_champ_A
        game_data['Team A']['Top']['Runes']['Primary'] = top_runes_A[0]
        game_data['Team A']['Top']['Runes']['Secondary'] = top_runes_A[1]
        game_data['Team A']['Top']['Mastery'] = top_mastery_A['championPoints']
        game_data['Team A']['Top']['SummonerSpells'] = top_spells_A
        game_data['Team A']['Top']['Rank']['Division'] = top_division_A
        game_data['Team A']['Top']['Rank']['Tier'] = top_tier_A

        game_data['Team A']['Jungle']['SummonerName'] = f"{jungle_summoner_A['gameName']}#{jungle_summoner_A['tagLine']}"
        game_data['Team A']['Jungle']['Champion'] = jungle_champ_A
        game_data['Team A']['Jungle']['Runes']['Primary'] = jungle_runes_A[0]
        game_data['Team A']['Jungle']['Runes']['Secondary'] = jungle_runes_A[1]
        game_data['Team A']['Jungle']['Mastery'] = jungle_mastery_A['championPoints']
        game_data['Team A']['Jungle']['SummonerSpells'] = jungle_spells_A
        game_data['Team A']['Jungle']['Rank']['Division'] = jungle_division_A
        game_data['Team A']['Jungle']['Rank']['Tier'] = jungle_tier_A

        game_data['Team A']['Mid']['SummonerName'] = f"{mid_summoner_A['gameName']}#{mid_summoner_A['tagLine']}"
        game_data['Team A']['Mid']['Champion'] = mid_champ_A
        game_data['Team A']['Mid']['Runes']['Primary'] = mid_runes_A[0]
        game_data['Team A']['Mid']['Runes']['Secondary'] = mid_runes_A[1]
        game_data['Team A']['Mid']['Mastery'] = mid_mastery_A['championPoints']
        game_data['Team A']['Mid']['SummonerSpells'] = mid_spells_A
        game_data['Team A']['Mid']['Rank']['Division'] = mid_division_A
        game_data['Team A']['Mid']['Rank']['Tier'] = mid_tier_A

        game_data['Team A']['Bot']['SummonerName'] = f"{bot_summoner_A['gameName']}#{bot_summoner_A['tagLine']}"
        game_data['Team A']['Bot']['Champion'] = bot_champ_A
        game_data['Team A']['Bot']['Runes']['Primary'] = bot_runes_A[0]
        game_data['Team A']['Bot']['Runes']['Secondary'] = bot_runes_A[1]
        game_data['Team A']['Bot']['Mastery'] = bot_mastery_A['championPoints']
        game_data['Team A']['Bot']['SummonerSpells'] = bot_spells_A
        game_data['Team A']['Bot']['Rank']['Division'] = bot_division_A
        game_data['Team A']['Bot']['Rank']['Tier'] = bot_tier_A

        game_data['Team A']['Support']['SummonerName'] = f"{supp_summoner_A['gameName']}#{supp_summoner_A['tagLine']}"
        game_data['Team A']['Support']['Champion'] = supp_champ_A
        game_data['Team A']['Support']['Runes']['Primary'] = supp_runes_A[0]
        game_data['Team A']['Support']['Runes']['Secondary'] = supp_runes_A[1]
        game_data['Team A']['Support']['Mastery'] = supp_mastery_A['championPoints']
        game_data['Team A']['Support']['SummonerSpells'] = supp_spells_A
        game_data['Team A']['Support']['Rank']['Division'] = supp_division_A
        game_data['Team A']['Support']['Rank']['Tier'] = supp_tier_A

        game_data['Team B']['Top']['SummonerName'] = f"{top_summoner_b['gameName']}#{top_summoner_b['tagLine']}"
        game_data['Team B']['Top']['Champion'] = top_champ_B
        game_data['Team B']['Top']['Runes']['Primary'] = top_runes_B[0]
        game_data['Team B']['Top']['Runes']['Secondary'] = top_runes_B[1]
        game_data['Team B']['Top']['Mastery'] = top_mastery_B['championPoints']
        game_data['Team B']['Top']['SummonerSpells'] = top_spells_B
        game_data['Team B']['Top']['Rank']['Division'] = top_division_B
        game_data['Team B']['Top']['Rank']['Tier'] = top_tier_B

        game_data['Team B']['Jungle']['SummonerName'] = f"{jungle_summoner_B['gameName']}#{jungle_summoner_B['tagLine']}"
        game_data['Team B']['Jungle']['Champion'] = jungle_champ_B
        game_data['Team B']['Jungle']['Runes']['Primary'] = jungle_runes_B[0]
        game_data['Team B']['Jungle']['Runes']['Secondary'] = jungle_runes_B[1]
        game_data['Team B']['Jungle']['Mastery'] = jungle_mastery_B['championPoints']
        game_data['Team B']['Jungle']['SummonerSpells'] = jungle_spells_B
        game_data['Team B']['Jungle']['Rank']['Division'] = jungle_division_B
        game_data['Team B']['Jungle']['Rank']['Tier'] = jungle_tier_B

        game_data['Team B']['Mid']['SummonerName'] = f"{mid_summoner_B['gameName']}#{mid_summoner_B['tagLine']}"
        game_data['Team B']['Mid']['Champion'] = mid_champ_B
        game_data['Team B']['Mid']['Runes']['Primary'] = mid_runes_B[0]
        game_data['Team B']['Mid']['Runes']['Secondary'] = mid_runes_B[1]
        game_data['Team B']['Mid']['Mastery'] = mid_mastery_B['championPoints']
        game_data['Team B']['Mid']['SummonerSpells'] = mid_spells_B
        game_data['Team B']['Mid']['Rank']['Division'] = mid_division_B
        game_data['Team B']['Mid']['Rank']['Tier'] = mid_tier_B

        game_data['Team B']['Bot']['SummonerName'] = f"{bot_summoner_B['gameName']}#{bot_summoner_B['tagLine']}"
        game_data['Team B']['Bot']['Champion'] = bot_champ_B
        game_data['Team B']['Bot']['Runes']['Primary'] = bot_runes_B[0]
        game_data['Team B']['Bot']['Runes']['Secondary'] = bot_runes_B[1]
        game_data['Team B']['Bot']['Mastery'] = bot_mastery_B['championPoints']
        game_data['Team B']['Bot']['SummonerSpells'] = bot_spells_B
        game_data['Team B']['Bot']['Rank']['Division'] = bot_division_B
        game_data['Team B']['Bot']['Rank']['Tier'] = bot_tier_B

        game_data['Team B']['Support']['SummonerName'] = f"{supp_summoner_B['gameName']}#{supp_summoner_B['tagLine']}"
        game_data['Team B']['Support']['Champion'] = supp_champ_B
        game_data['Team B']['Support']['Runes']['Primary'] = supp_runes_B[0]
        game_data['Team B']['Support']['Runes']['Secondary'] = supp_runes_B[1]
        game_data['Team B']['Support']['Mastery'] = supp_mastery_B['championPoints']
        game_data['Team B']['Support']['SummonerSpells'] = supp_spells_B
        game_data['Team B']['Support']['Rank']['Division'] = supp_division_B
        game_data['Team B']['Support']['Rank']['Tier'] = supp_tier_B

        game_data['Team A']['Result'] = team_A_result
        game_data['Team B']['Result'] = team_B_result

        date_unix = (match['info']['gameCreation'])/1000
        date = datetime.fromtimestamp(date_unix).strftime('%Y-%m-%d')
        game_data['Date'] = date

        game_data['MatchID'] = match['metadata']['matchId']

        print(game_data)

asyncio.run(main())
