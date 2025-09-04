import asyncio
import aiohttp

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
    game_data = []
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

        # Get each champion names
        top_champ_A = match['info']['participants'][0]['championName']
        jungle_champ_A = match['info']['participants'][1]['championName']
        mid_champ_A = match['info']['participants'][2]['championName']
        bot_champ_A = match['info']['participants'][3]['championName']
        supp_champ_A = match['info']['participants'][4]['championName']
        top_champ_B = match['info']['participants'][5]['championName']
        jungle_champ_B = match['info']['participants'][6]['championName']
        mid_champ_B = match['info']['participants'][7]['championName']
        bot_champ_B = match['info']['participants'][8]['championName']
        supp_champ_B = match['info']['participants'][9]['championName']
      
        # Get champion mastery
        top_puuid_A = match['info']['participants'][0]['puuid']
        top_champId_A = match['info']['participants'][0]['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{top_puuid_A}/by-champion/{top_champId_A}"
        top_mastery_A = await get_json(session, mastery_url)
        
        jungle_puuid_A = match['info']['participants'][1]['puuid']
        jungle_champId_A = match['info']['participants'][1]['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{jungle_puuid_A}/by-champion/{jungle_champId_A}"
        jungle_mastery_A = await get_json(session, mastery_url)

        mid_puuid_A = match['info']['participants'][2]['puuid']
        mid_champId_A = match['info']['participants'][2]['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{mid_puuid_A}/by-champion/{mid_champId_A}"
        mid_mastery_A = await get_json(session, mastery_url)

        bot_puuid_A = match['info']['participants'][3]['puuid']
        bot_champ_A = match['info']['participants'][3]['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{bot_puuid_A}/by-champion/{bot_champ_A}"
        bot_mastery_A = await get_json(session, mastery_url)

        supp_puuid_A = match['info']['participants'][4]['puuid']
        supp_champ_A = match['info']['participants'][4]['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{supp_puuid_A}/by-champion/{supp_champ_A}"
        supp_mastery_A = await get_json(session, mastery_url)
        
        top_puuid_B = match['info']['participants'][5]['puuid']
        top_champId_B = match['info']['participants'][5]['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{top_puuid_B}/by-champion/{top_champId_B}"
        top_mastery_B = await get_json(session, mastery_url)
        
        jungle_puuid_B = match['info']['participants'][6]['puuid']
        jungle_champId_B = match['info']['participants'][6]['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{jungle_puuid_B}/by-champion/{jungle_champId_B}"
        jungle_mastery_B = await get_json(session, mastery_url)

        mid_puuid_B = match['info']['participants'][7]['puuid']
        mid_champId_B = match['info']['participants'][7]['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{mid_puuid_B}/by-champion/{mid_champId_B}"
        mid_mastery_B = await get_json(session, mastery_url)

        bot_puuid_B = match['info']['participants'][8]['puuid']
        bot_champ_B = match['info']['participants'][8]['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{bot_puuid_B}/by-champion/{bot_champ_B}"
        bot_mastery_B = await get_json(session, mastery_url)

        supp_puuid_B = match['info']['participants'][9]['puuid']
        supp_champ_B = match['info']['participants'][9]['championId']
        mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{supp_puuid_B}/by-champion/{supp_champ_B}"
        supp_mastery_B = await get_json(session, mastery_url)

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
        top_spells_A = [match['info']['participants'][0]['summoner1Id'], match['info']['participants'][0]['summoner2Id']]
        jungle_spells_A = [match['info']['participants'][1]['summoner1Id'], match['info']['participants'][1]['summoner2Id']]
        mid_spells_A = [match['info']['participants'][2]['summoner1Id'], match['info']['participants'][2]['summoner2Id']]
        bot_spells_A = [match['info']['participants'][3]['summoner1Id'], match['info']['participants'][3]['summoner2Id']]
        supp_spells_A = [match['info']['participants'][4]['summoner1Id'], match['info']['participants'][4]['summoner2Id']]
        top_spells_B = [match['info']['participants'][5]['summoner1Id'], match['info']['participants'][5]['summoner2Id']]
        jungle_spells_B = [match['info']['participants'][6]['summoner1Id'], match['info']['participants'][6]['summoner2Id']]
        mid_spells_B = [match['info']['participants'][7]['summoner1Id'], match['info']['participants'][7]['summoner2Id']]
        bot_spells_B = [match['info']['participants'][8]['summoner1Id'], match['info']['participants'][8]['summoner2Id']]
        supp_spells_B = [match['info']['participants'][9]['summoner1Id'], match['info']['participants'][9]['summoner2Id']]

        # Get primary runes       
        top_runes_A = [match['info']['participants'][0]['perks']['styles'][0]['selections'][0]['perk'], match['info']['participants'][0]['perks']['styles'][1]['style']]
        jungle_runes_A = [match['info']['participants'][1]['perks']['styles'][0]['selections'][0]['perk'], match['info']['participants'][1]['perks']['styles'][1]['style']]
        mid_runes_A = [match['info']['participants'][2]['perks']['styles'][0]['selections'][0]['perk'], match['info']['participants'][2]['perks']['styles'][1]['style']]
        bot_runes_A = [match['info']['participants'][3]['perks']['styles'][0]['selections'][0]['perk'], match['info']['participants'][3]['perks']['styles'][1]['style']]
        supp_runes_A = [match['info']['participants'][4]['perks']['styles'][0]['selections'][0]['perk'], match['info']['participants'][4]['perks']['styles'][1]['style']]
        top_runes_B = [match['info']['participants'][5]['perks']['styles'][0]['selections'][0]['perk'], match['info']['participants'][5]['perks']['styles'][1]['style']]
        jungle_runes_B = [match['info']['participants'][6]['perks']['styles'][0]['selections'][0]['perk'], match['info']['participants'][6]['perks']['styles'][1]['style']]
        mid_runes_B = [match['info']['participants'][7]['perks']['styles'][0]['selections'][0]['perk'], match['info']['participants'][7]['perks']['styles'][1]['style']]
        bot_runes_B = [match['info']['participants'][8]['perks']['styles'][0]['selections'][0]['perk'], match['info']['participants'][8]['perks']['styles'][1]['style']]
        supp_runes_B = [match['info']['participants'][9]['perks']['styles'][0]['selections'][0]['perk'], match['info']['participants'][9]['perks']['styles'][1]['style']]

        

asyncio.run(main())
