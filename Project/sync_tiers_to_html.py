import csv
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / 'steamspy\u4e0atop100\u6e38\u620f\u6570\u636e.csv'
HTML_PATH = BASE_DIR / '\u56fe.html'

CLASSIC = '\u7ecf\u5178\u795e\u4f5c'
AAA = 'AAA\u5927\u4f5c'
FREE = '\u514d\u8d39\u7ade\u6280'
INDIE = '\u72ec\u7acb\u7cbe\u54c1'
MID = '\u4e2d\u578b\u7206\u6b3e'

CLASSIC_NAMES = {
    'Counter-Strike: Global Offensive', 'Team Fortress 2', 'Left 4 Dead 2', 'Terraria',
    'Portal', 'Half-Life', 'Half-Life 2', 'Counter-Strike', 'Counter-Strike: Source',
    'Counter-Strike: Condition Zero', 'Grand Theft Auto IV: Complete Edition',
    'Grand Theft Auto V Legacy', 'The Witcher 3: Wild Hunt', 'Sid Meier\u2019s Civilization VI',
    "Sid Meier's Civilization V",
}

AAA_NAMES = {
    "Baldur's Gate 3", 'ELDEN RING', 'Cyberpunk 2077', 'Black Myth: Wukong',
    'Red Dead Redemption 2', 'HELLDIVERS 2', 'Call of Duty: Modern Warfare II',
    'Monster Hunter Wilds', 'Monster Hunter: World', 'Hogwarts Legacy',
    'Sekiro: Shadows Die Twice - GOTY Edition', 'The Sims 4', 'Fallout 4',
    'Battlefield V', 'Battlefield 2042', 'EA SPORTS FIFA 23',
}

FREE_COMPETITIVE_NAMES = {
    'PUBG: BATTLEGROUNDS', 'Apex Legends', 'War Thunder', 'NARAKA: BLADEPOINT',
    'Rocket League', 'Destiny 2', 'Lost Ark', 'Brawlhalla', 'eFootball', 'SMITE',
    'Paladins', 'Z1 Battle Royale', 'Warface: Clutch', 'Black Squad',
    'War Robots: Frontiers', 'Heroes & Generals', 'Halo Infinite',
    'World of Tanks Blitz', 'World of Warships', 'Ring of Elysium',
}

INDIE_NAMES = {
    'Wallpaper Engine', 'Stardew Valley', 'R.E.P.O.', "Don't Starve Together",
    'Project Zomboid', 'Schedule I', "Garry's Mod", 'Euro Truck Simulator 2',
    'Satisfactory', 'Valheim', 'Phasmophobia', 'Lethal Company', 'Human Fall Flat',
    'Among Us', 'Raft', 'The Forest', 'Risk of Rain 2', 'Last Epoch', 'Grim Dawn',
    'Life is Strange 2', '\u4e09\u56fd\u6740', 'CyberCorp', 'Street Warriors Online',
}

FREE_COMPETITIVE_TAGS = {
    'fps', 'battle royale', 'hero shooter', 'tactical shooter', 'moba', 'sports',
    'vehicular combat', 'arena shooter', 'mech shooter', 'extraction shooter'
}

INDIE_TAGS = {
    'farming sim', 'utility', 'co-op horror', 'sandbox', 'factory sim', 'party',
    'puzzle', 'physics puzzle', 'narrative adventure', 'card game', 'roguelike',
    'city builder', 'driving sim', 'social deduction'
}

AAA_TAGS = {
    'action rpg', 'open world', 'open world rpg', 'crpg', 'action adventure',
    '4x strategy', 'strategy rpg'
}

AAA_PUBLISHERS = {
    'rockstar games', 'activision', 'electronic arts', 'ubisoft', 'playstation publishing llc',
    'bandai namco entertainment', 'warner bros. games', '2k',
    'fromsoftware, inc., bandai namco entertainment'
}


def choose_tier(name: str, price: float, rating: float, ccu: int, primary_tag: str, publisher: str) -> str:
    tag = (primary_tag or '').strip().lower()
    publisher_key = (publisher or '').strip().lower()

    if name in CLASSIC_NAMES:
        return CLASSIC
    if name in AAA_NAMES:
        return AAA
    if name in FREE_COMPETITIVE_NAMES:
        return FREE
    if name in INDIE_NAMES:
        return INDIE

    if price == 0 and tag in FREE_COMPETITIVE_TAGS:
        return FREE
    if (tag in INDIE_TAGS and price <= 25) or (rating >= 92 and price <= 25 and ccu <= 40000):
        return INDIE
    if (tag in AAA_TAGS and (price >= 35 or publisher_key in AAA_PUBLISHERS)) or (price >= 45 and ccu >= 12000):
        return AAA
    if ccu >= 20000 and rating >= 85 and price > 0:
        return CLASSIC
    return MID


def load_rows():
    with CSV_PATH.open('r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def build_chart_data(rows):
    chart_rows = []
    for row in rows:
        name = row['Name']
        ccu = int(float(row['CCU_Current_Players']))
        rating = round(float(row['Positive_Rating_Pct']), 2)
        price = round(float(row['Price_USD']), 2)
        primary_tag = row.get('Primary_Tag', '')
        publisher = row.get('Publisher', '')
        tier = choose_tier(name, price, rating, ccu, primary_tag, publisher)
        chart_rows.append({
            'Name': name,
            'CCU': ccu,
            'Rating': rating,
            'Price': price,
            'Tier': tier,
        })
    return chart_rows


def replace_data_block(html_text: str, chart_rows):
    replacement = 'const data = ' + json.dumps(chart_rows, ensure_ascii=False, indent=8) + ';'
    pattern = re.compile(r'const data = \[(?:.|\r|\n)*?\];', re.MULTILINE)
    new_text, count = pattern.subn(replacement, html_text, count=1)
    if count != 1:
        raise RuntimeError('Unable to find const data block in HTML.')
    return new_text


def main():
    rows = load_rows()
    chart_rows = build_chart_data(rows)
    html_text = HTML_PATH.read_text(encoding='utf-8')
    HTML_PATH.write_text(replace_data_block(html_text, chart_rows), encoding='utf-8')

    counts = {}
    for row in chart_rows:
        counts[row['Tier']] = counts.get(row['Tier'], 0) + 1

    print('Synced:', HTML_PATH.name)
    for key in [AAA, INDIE, FREE, MID, CLASSIC]:
        print(f'{key}: {counts.get(key, 0)}')


if __name__ == '__main__':
    main()
