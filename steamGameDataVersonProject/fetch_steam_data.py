import requests
import pandas as pd
import json

def fetch_steam_bubble_data():
    print("Connecting to SteamSpy API...")
    # 获取过去两周热门前 100
    api_url = "https://steamspy.com/api.php?request=top100in2weeks"
    
    try:
        response = requests.get(api_url, timeout=20)
        data = response.json()
        
        game_list = []
        count = 0
        
        # 遍历数据
        for appid, info in data.items():
            if count >= 100: break
            
            # 计算好评率
            pos = info.get('positive', 0)
            neg = info.get('negative', 0)
            rating = round((pos / (pos + neg)) * 100, 2) if (pos + neg) > 0 else 0
            
            # 价格转换 (美分 -> 美元)
            price = info.get('price', 0) / 100
            
            # 标签提取
            genres = info.get('genre', 'Other')
            primary_tag = genres.split(',')[0] if genres else "N/A"
            
            game_list.append({
                "Rank": count + 1,
                "Name": info.get('name', 'N/A'),
                "CCU_Current_Players": info.get('ccu', 0),
                "Positive_Rating_Pct": rating,
                "Price_USD": price,
                "Primary_Tag": primary_tag,
                "Publisher": info.get('publisher', 'N/A')
            })
            count += 1

        df = pd.DataFrame(game_list)
        # 按在线人数降序排列
        df = df.sort_values(by="CCU_Current_Players", ascending=False)
        
        # 真实保存到工作目录
        output_file = r"e:\GitHubCode\tEMP\steam_top100_final.csv"
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"Successfully saved to {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_steam_bubble_data()
