import asyncio
import aiohttp
from match_data_processor import map_roles, MATCH_DATA
from datetime import datetime
from json import dump, dumps
import os
import sqlite3
from tqdm import tqdm

API_KEY = "RGAPI-9692dc56-853d-4be6-a128-eb0bc798e0fa"
QUEUE_TYPE = input("Enter queue type (e.g., RANKED_SOLO_5x5, RANKED_FLEX_SR): ").strip()
TIER = input("Enter tier (e.g., DIAMOND): ").strip().upper()
DIVISION = input("Enter division (e.g., I, II, III, IV): ").strip().upper()
HEADERS = {"X-Riot-Token": API_KEY}
QUEUE_ID = {
    'RANKED_SOLO_5x5': 420,
    'RANKED_FLEX_SR': 440
}


def append_ndjson(file_path, obj):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    line = dumps(obj, default=str)
    
    # create fresh array file if missing/empty
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('[\n')
            f.write(line)
            f.write('\n]\n')
        return

    # read whole file, insert before last ']'
    with open(file_path, 'r+', encoding='utf-8') as f:
        content = f.read()
        idx = content.rfind(']')
        if idx == -1:
            # corrupt file: back it up and recreate
            backup = file_path + '.corrupt'
            os.rename(file_path, backup)
            with open(file_path, 'w', encoding='utf-8') as g:
                g.write('[\n' + line + '\n]\n')
            print(f'Backed up corrupt file to {backup} and created new array file.')
            return

        # check if array currently empty (i.e. '...[' immediately before ']')
        prefix = content[:idx]
        if prefix.rstrip().endswith('['):
            new_content = prefix + line + content[idx:]
        else:
            new_content = prefix + ',\n' + line + content[idx:]

        f.seek(0)
        f.truncate()
        f.write(new_content)


def init_index(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10, isolation_level=None)
    # use WAL for better concurrent append behavior
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS match_index (
        match_id TEXT PRIMARY KEY,
        created_at REAL,
        pending INTEGER DEFAULT 1
    )
    """)
    return conn


def reserve_match(conn, match_id):
    try:
        now = datetime.now().timestamp()
        with conn:
            conn.execute(
                "INSERT INTO match_index(match_id, created_at, pending) VALUES (?, ?, 1)",
                (match_id, now)
            )
        return True
    except sqlite3.IntegrityError:
        # already present
        return False


def finalize_match(conn, match_id):
    with conn:
        conn.execute("UPDATE match_index SET pending=0 WHERE match_id = ?", (match_id,))


def get_all_match_ids(conn):
    cur = conn.execute("SELECT match_id FROM match_index WHERE pending = 0")
    return {row[0] for row in cur.fetchall()}


def get_pending_matches(conn):
    cur = conn.execute("SELECT match_id FROM match_index WHERE pending = 1")
    return [row[0] for row in cur.fetchall()]


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
            player['ChampionID'] = player_data['championId']

            # champion mastery and summoner name
            puuid = player_data['puuid']
            champId = player_data['championId']

            mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{champId}"
            mastery = await get_json(session, mastery_url)
            player['Mastery'] = mastery['championPoints']

            """
            summoner_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
            summoner = await get_json(session, summoner_url)
            player['SummonerName'] = f'{summoner['gameName']}#{summoner['tagLine']}'
            """

            player['PUUID'] = puuid
            
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


async def get_match_ids(session, puuid, queue, startDate, endDate):
    matches_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={startDate}&endTime={endDate}&count=100&queue={queue}"
    matches = await get_json(session, matches_url)
    return matches


async def get_json(session, url):
    async with session.get(url, headers=HEADERS) as resp:
        if resp.status == 429:
            print("Rate limit hit, waiting...")
            await asyncio.sleep(120)  # simple backoff
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
    file_path = f'data/{QUEUE_TYPE}/{TIER}/dataset.json'
    db_path = f'data/{QUEUE_TYPE}/{TIER}/dataset_index.db'
    conn = init_index(db_path)
    puuids = set()
    unique_matches = set()

    async with aiohttp.ClientSession() as session:
        # Get league entries
        league_url = f"https://na1.api.riotgames.com/lol/league/v4/entries/{QUEUE_TYPE}/{TIER}/{DIVISION}?page=1"
        league_entries = await get_json(session, league_url)
        print(f"Found {len(league_entries)} summoners in {QUEUE_TYPE} {TIER} {DIVISION}")
        current_time = int(datetime.now().timestamp())

        # Convert summonerId -> PUUID
        for entry in league_entries:
            print(f'PUUID: {entry["puuid"]}')
            puuids.add(entry['puuid'])
        
        # Get match IDs for each PUUID
        for puuid in puuids:
            print(f'Getting match IDs for PUUID: {puuid}')
            matches = await get_match_ids(session, puuid, QUEUE_ID[QUEUE_TYPE], 1767953321, 1770718121)
            print(f'Matches found: {matches}')
            unique_matches.update(matches)

        # Get match details and outcome (show progress bar; keep status updates on same line)
        matches_list = list(unique_matches)
        total = len(matches_list)
        print(f'{total} matches found')
        with tqdm(matches_list, desc="Fetching matches", unit="match") as pbar:
            for match in pbar:
                # update an inline status instead of printing new lines
                remaining = total - pbar.n - 1
                pbar.set_postfix({"left": remaining})
                pbar.set_description(f"Getting")

                # Reserve in index; if already present, emit a single-line message
                if not reserve_match(conn, match):
                    pbar.write(f'Match {match} already exists, skipping.')
                    continue

                try:
                    game_data = await get_match_data(session, match)
                    append_ndjson(file_path, game_data)
                    finalize_match(conn, match)
                except Exception as err:
                    # use pbar.write so the error shows above the progress bar without corrupting it
                    pbar.write(f'Failed to get data for {match} due to {err}')
                    continue
            


asyncio.run(main())
