import os
import gzip
import re
import requests
import time
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
output_filename = "DrewLive.xml.gz"

def fetch_tvg_ids_from_playlist(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        ids = set(re.findall(r'tvg-id="([^"]+)"', r.text))
        print(f"✅ Loaded {len(ids)} tvg-ids from playlist")
        return ids
    except Exception as e:
        print(f"❌ Failed to fetch tvg-ids from playlist: {e}")
        return set()

def fetch_with_retry(url, retries=3, delay=10, timeout=30):
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            return r
        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed for {url}: {e}")
            if attempt < retries:
                time.sleep(delay)
    return None

def stream_parse_epg(file_obj, valid_tvg_ids, root):
    kept_channels = 0
    total_items = 0
    try:
        tree = ET.parse(file_obj)
        for child in tree.getroot():
            if child.tag == 'channel' or child.tag == 'programme':
                total_items += 1
                tvg_id = child.get('id') or child.get('channel')
                if tvg_id in valid_tvg_ids:
                    root.append(child)
                    kept_channels += 1
    except ET.ParseError:
        print("❌ XML Parse Error")
    return total_items, kept_channels

def merge_and_filter_epg(epg_sources, playlist_url, output_file):
    valid_tvg_ids = fetch_tvg_ids_from_playlist(playlist_url)
    root = ET.Element("tv")
    cumulative_kept = 0
    cumulative_total = 0

    for url in epg_sources:
        print(f"\n🌐 Processing: {url}")
        resp = fetch_with_retry(url, retries=3, delay=10, timeout=60)
        if not resp:
            print(f"❌ Failed to fetch {url}")
            continue
        content = resp.content
        if url.endswith(".gz"):
            content = gzip.decompress(content)
        total, kept = stream_parse_epg(BytesIO(content), valid_tvg_ids, root)
        cumulative_total += total
        cumulative_kept += kept
        print(f"📊 Total items found: {total}, Kept: {kept}")

    with gzip.open(output_file, "wt", encoding="utf-8") as f:
        ET.ElementTree(root).write(f, encoding="unicode", xml_declaration=True)

    print(f"\n✅ Filtered EPG saved to: {output_file}")
    print(f"📈 Cumulative items processed: {cumulative_total}")
    print(f"📈 Total items kept: {cumulative_kept}")

if __name__ == "__main__":
    merge_and_filter_epg(epg_sources, playlist_url, output_filename)
