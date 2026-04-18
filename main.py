import cloudscraper
import re
import time
import zipfile
import os

# --- CONFIGURATION ---
ANIME_ID = "2fe62367-d524-455b-4ce9-3399942c2a9b" # JJK Season 2
BASE_URL = "https://animepahe.ru"
ZIP_NAME = "JJK_S2_Full_Collection.zip"

scraper = cloudscraper.create_scraper()

def fetch_all_episode_links(anime_id):
    episode_pages = []
    # Fetching pages 1 and 2 to cover all 23+ episodes
    for page in [1, 2]: 
        api_url = f"{BASE_URL}/api?m=release&id={anime_id}&sort=episode_asc&page={page}"
        try:
            response = scraper.get(api_url).json()
            for item in response.get('data', []):
                session = item['session']
                episode_num = item['episode']
                episode_pages.append((episode_num, f"{BASE_URL}/play/{anime_id}/{session}"))
        except:
            break
    return episode_pages

def get_direct_video(play_url):
    try:
        res = scraper.get(play_url)
        kwik_link = re.search(r'https://kwik\.cx/f/\w+', res.text).group(0)
        res_kwik = scraper.get(kwik_url, headers={'Referer': 'https://animepahe.com/'})
        return re.search(r"source='(.*?)'", res_kwik.text).group(1)
    except:
        return None

# --- EXECUTION ---
episodes = fetch_all_episode_links(ANIME_ID)
print(f"✅ Found {len(episodes)} episodes.")

with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as master_zip:
    for ep_num, play_url in episodes:
        print(f"Processing Episode {ep_num}...")
        direct_link = get_direct_video(play_url)
        
        if direct_link:
            # We use .content to get the data and write it to the ZIP
            video_stream = scraper.get(direct_link, stream=True, headers={'Referer': 'https://kwik.cx/'})
            master_zip.writestr(f"JJK_S2_Episode_{ep_num}.mp4", video_stream.content)
            time.sleep(1) 
        else:
            print(f"❌ Skipped Episode {ep_num}")

print(f"✨ ZIP Created: {ZIP_NAME}")
