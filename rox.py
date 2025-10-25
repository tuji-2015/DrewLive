import requests
import re

# Mapping of event URLs to proper names
EVENTS = {
    "https://roxiestreams.cc/ppv-streams-1": "EVLS Prague Pro",
    "https://roxiestreams.cc/soccer": "Premier League",
    "https://roxiestreams.cc/ufc": "UFC 321: Tom Aspinall vs Ciryl Gane",
    "https://roxiestreams.cc/soccer-streams-5": "Ligue 1",
    "https://roxiestreams.cc/nfl": "NCAA (College Football)",
    "https://roxiestreams.cc/f1-streams": "Formula 1",
    "https://roxiestreams.cc/wwe-streams": "WWE NXT: Halloween Havoc",
    "https://roxiestreams.cc/nba": "NBA",
    "https://roxiestreams.cc/mlb-streams-1": "MLB World Series"
}

# TV info for logos and IDs
TV_INFO = {
    "ppv": ("PPV.EVENTS.Dummy.us", "http://drewlive24.duckdns.org:9000/Logos/PPV.png"),
    "soccer": ("Soccer.Dummy.us", "http://drewlive24.duckdns.org:9000/Logos/Soccer.png"),
    "ufc": ("UFC.247.Dummy.us", "http://drewlive24.duckdns.org:9000/Logos/CombatSports2.png"),
    "nfl": ("Football.Dummy.us", "http://drewlive24.duckdns.org:9000/Logos/Maxx.png"),
    "f1": ("Racing.Dummy.us", "http://drewlive24.duckdns.org:9000/Logos/F1.png"),
    "wwe": ("WWE.Dummy.us", "http://drewlive24.duckdns.org:9000/Logos/WWE2.png"),
    "nba": ("NBA.Basketball.Dummy.us", "http://drewlive24.duckdns.org:9000/Logos/Basketball-2.png"),
    "mlb": ("MLB.Baseball.Dummy.us", "http://drewlive24.duckdns.org:9000/Logos/Baseball3.png")
}

def extract_m3u8_links(event_url):
    """Fetch event page and extract all .m3u8 links."""
    try:
        resp = requests.get(event_url, timeout=10)
        if resp.status_code != 200:
            return []
        links = re.findall(r'https?://[^\s"\'<>]+\.m3u8', resp.text)
        return list(dict.fromkeys(links))  # remove duplicates
    except:
        return []

def get_tv_info(url):
    for key, value in TV_INFO.items():
        if key in url.lower():
            return value
    return ("Unknown.Dummy.us", "")

def main():
    playlist_lines = ["#EXTM3U"]

    for url, title in EVENTS.items():
        links = extract_m3u8_links(url)
        if not links:
            continue  # skip events without M3U8 links
        tv_id, logo = get_tv_info(url)
        for link in links:
            playlist_lines.append(f'#EXTINF:-1 tvg-logo="{logo}" tvg-id="{tv_id}" group-title="Roxiestreams",Roxiestreams - {title}')
            playlist_lines.append(link)

    content = "\n".join(playlist_lines)
    with open("Roxiestreams.m3u8", "w") as f:
        f.write(content)
    print("Playlist saved as Roxiestreams.m3u8")

if __name__ == "__main__":
    main()