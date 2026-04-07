import requests
import pandas as pd


def safe_int(value):
    try:
        return int(value)
    except:
        return 0


def safe_float(value):
    try:
        return float(value)
    except:
        return 0.0


def fetch_steam_bubble_data():
    print("Connecting to SteamSpy API...")

    api_url = "https://steamspy.com/api.php?request=top100in2weeks"

    try:
        # ✅ 加 headers 防止被拒绝连接（关键）
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()

        game_list = []
        count = 0

        for appid, info in data.items():
            if count >= 100:
                break

            # ✅ 安全转换
            pos = safe_int(info.get('positive', 0))
            neg = safe_int(info.get('negative', 0))
            ccu = safe_int(info.get('ccu', 0))

            rating = round((pos / (pos + neg)) * 100, 2) if (pos + neg) > 0 else 0

            price_raw = info.get('price', 0)
            price = safe_float(price_raw) / 100

            genres = info.get('genre', 'Other')
            primary_tag = genres.split(',')[0] if genres else "N/A"

            game_list.append({
                "Rank": count + 1,
                "Name": info.get('name', 'N/A'),
                "CCU_Current_Players": ccu,
                "Positive_Rating_Pct": rating,
                "Price_USD": price,
                "Primary_Tag": primary_tag,
                "Publisher": info.get('publisher', 'N/A')
            })

            count += 1

        # ✅ 单独加入“三国杀”
        san_guo_sha_data = {
            "Rank": 101,
            "Name": "三国杀",
            "CCU_Current_Players": 5000,   # 可自行修改真实值
            "Positive_Rating_Pct": 85.0,
            "Price_USD": 0.0,
            "Primary_Tag": "Card Game",
            "Publisher": "Shengqu Games"
        }

        game_list.append(san_guo_sha_data)

        # 转 DataFrame
        df = pd.DataFrame(game_list)

        # 按在线人数排序
        df = df.sort_values(by="CCU_Current_Players", ascending=False)

        # 保存
        output_file = r"steamspy上top100游戏数据.csv"
        df.to_csv(output_file, index=False, encoding="utf-8-sig")

        print(f"Successfully saved to {output_file}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    fetch_steam_bubble_data()