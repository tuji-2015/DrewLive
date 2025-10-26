import gzip
import re
import requests
from xml.etree import ElementTree as ET
from io import BytesIO

epg_sources = [
    "https://raw.githubusercontent.com/matthuisman/i.mjh.nz/refs/heads/master/Plex/all.xml",
    "https://raw.githubusercontent.com/matthuisman/i.mjh.nz/refs/heads/master/PlutoTV/all.xml",
    "https://raw.githubusercontent.com/matthuisman/i.mjh.nz/refs/heads/master/SamsungTVPlus/all.xml",
    "https://epgshare01.online/epgshare01/epg_ripper_PLEX1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_AU1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_CA2.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_DUMMY_CHANNELS.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_FANDUEL1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_NZ1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz",
    "https://raw.githubusercontent.com/BuddyChewChew/localnow-playlist-generator/refs/heads/main/epg.xml",
    "https://raw.githubusercontent.com/BuddyChewChew/tubi-scraper/refs/heads/main/tubi_epg.xml",
    "https://github.com/matthuisman/i.mjh.nz/raw/master/Roku/all.xml.gz",
    "https://tvpass.org/epg.xml",
    "https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS1.xml.gz",
    "http://drewlive24.duckdns.org:8081/JapanTV.xml.gz",
    "https://raw.githubusercontent.com/BuddyChewChew/xumo-playlist-generator/main/playlists/xumo_epg.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_AL1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_IE1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_NL1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_IN1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_MY1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_SG1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_PL1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_HK1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_FANDUEL1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_GR1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_PT1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_BG1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_KE1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_NG1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_JM1.xml.gz"
]

playlist_url = "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/MergedPlaylist.m3u8"
output_file = "DrewLive.xml.gz"

def fetch_tvg_ids(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        ids = set(re.findall(r'tvg-id="([^"]+)"', r.text))
        print(f"✅ Loaded {len(ids)} tvg-ids from playlist")
        return ids
    except Exception as e:
        print(f"❌ Failed to fetch tvg-ids: {e}")
        return set()

def fetch_epg(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        content = r.content
        if url.endswith(".gz"):
            content = gzip.decompress(content)
        return BytesIO(content)
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None

def merge_and_filter_epg(epg_sources, playlist_url, output_file):
    valid_ids = fetch_tvg_ids(playlist_url)
    root = ET.Element("tv")
    total_items = 0
    kept_items = 0

    for url in epg_sources:
        print(f"\n🌐 Processing: {url}")
        file_obj = fetch_epg(url)
        if not file_obj:
            continue
        try:
            for event, elem in ET.iterparse(file_obj, events=('end',)):
                tag = elem.tag.split('}')[-1]  
                if tag not in ('channel', 'programme'):
                    elem.clear()
                    continue

                tvg_id = elem.get('id') if tag == 'channel' else elem.get('channel')
                if not valid_ids or (tvg_id and tvg_id in valid_ids):
                    root.append(elem)
                    kept_items += 1

                total_items += 1
                elem.clear()
        except ET.ParseError as e:
            print(f"❌ Parse error for {url}: {e}")

    print(f"\n📊 Total items processed: {total_items}, Kept: {kept_items}")

    try:
        with gzip.open(output_file, "wb") as f:
            ET.ElementTree(root).write(f, encoding="utf-8", xml_declaration=True)
        print(f"✅ Filtered EPG saved to: {output_file}")
    except Exception as e:
        print(f"❌ Failed to write output file: {e}")

if __name__ == "__main__":
    merge_and_filter_epg(epg_sources, playlist_url, output_file)
