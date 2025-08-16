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
    unique_matches=set()

    async with aiohttp.ClientSession() as session:
        #Get league entries
        league_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/{QUEUE_TYPE}/{TIER}/{DIVISION}?page=1"
        league_entries = await get_json(session, league_url)
        print(f"Found {len(league_entries)} summoners in {QUEUE_TYPE} {TIER} {DIVISION}")

        #Convert summonerId -> PUUID
        print("Raw API response:", league_entries)
        '''
        for entry in league_entries:
            summoner_url = f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/{entry['summonerId']}"
            summoner_data = await get_json(session, summoner_url)
            puuids.add(summoner_data['puuid'])
        
        # 3. Get match IDs for each PUUID
        for puuid in puuids:
            matches_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=20&queue=420"
            matches = await get_json(session, matches_url)
            unique_matches.update(matches)
        '''
        

asyncio.run(main())
