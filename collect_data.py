import pandas as pd
import boto3
import os
from understatapi import UnderstatClient
import understatapi
print(f"understatapi 버전: {understatapi.__version__}")
s3 = boto3.client('s3')
BUCKET = 'pl-datahub-data'

def collect_season(season_param, season_label):
    print(f"📥 {season_label} 수집 중...")
    understat = UnderstatClient()
    # 버전에 따라 다른 방식 시도
    try:
        data = understat.league.get_team_data(league="EPL", season=season_param)
    except AttributeError:
        try:
            data = understat.league(league="EPL").get_team_data(season=season_param)
        except TypeError:
            data = understat.league("EPL").get_team_data(season_param)
    
    rows = []
    
    # dict 형태로 처리
    if isinstance(data, dict):
        items = data.items()
    else:
        items = [(row.name, row) for _, row in data.iterrows()]
    
    for team_name, team_info in items:
        if isinstance(team_info, dict):
            history = team_info.get("history", [])
            name = team_info.get("title", team_name)
        else:
            history = team_info.get("history", [])
            name = team_name
        
        if not history:
            continue
        
        xG_total   = sum(float(m.get("xG", 0))   for m in history)
        xGA_total  = sum(float(m.get("xGA", 0))  for m in history)
        xPTS_total = sum(float(m.get("xpts", 0)) for m in history)
        dc_total   = sum(float(m.get("deep", 0)) for m in history)
        
        ppda_list = []
        for m in history:
            ppda = m.get("ppda", {})
            if isinstance(ppda, dict):
                att  = float(ppda.get("att", 0))
                defn = float(ppda.get("def", 1))
                if defn > 0:
                    ppda_list.append(att / defn)
        ppda_avg = sum(ppda_list) / len(ppda_list) if ppda_list else 0
        
        actual_goals    = sum(int(m.get("scored", 0)) for m in history)
        actual_conceded = sum(int(m.get("missed", 0)) for m in history)
        actual_pts      = sum(int(m.get("pts", 0))    for m in history)
        wins   = sum(int(m.get("wins", 0))  for m in history)
        draws  = sum(int(m.get("draws", 0)) for m in history)
        losses = sum(int(m.get("loses", 0)) for m in history)
        
        rows.append({
            "team":     name,
            "season":   season_label,
            "xG":       round(xG_total, 2),
            "xGA":      round(xGA_total, 2),
            "xPTS":     round(xPTS_total, 2),
            "PPDA":     round(ppda_avg, 2),
            "DC":       int(dc_total),
            "실제득점": actual_goals,
            "실제실점": actual_conceded,
            "실제승점": actual_pts,
            "승":       wins,
            "무":       draws,
            "패":       losses,
        })
    
    df = pd.DataFrame(rows)
    df["득실차"] = df["실제득점"] - df["실제실점"]
    df = df.sort_values(
        ["실제승점", "득실차", "실제득점"],
        ascending=[False, False, False]
    ).reset_index(drop=True)
    df["순위"] = range(1, len(df) + 1)
    
    print(f"✅ {season_label} {len(df)}팀 완료!")
    return df

def collect_fixtures():
    print("📅 경기 일정 수집 중...")
    understat = UnderstatClient()
    try:
        match_data = understat.league.get_match_data(league="EPL", season="2025")
    except AttributeError:
        try:
            match_data = understat.league(league="EPL").get_match_data(season="2025")
        except TypeError:
            match_data = understat.league("EPL").get_match_data("2025")
    
    rows = []
    
    if isinstance(match_data, dict):
        matches = match_data.values()
    else:
        matches = [row for _, row in match_data.iterrows()]
    
    for match in matches:
        if isinstance(match, dict):
            is_result = match.get("isResult", False)
        else:
            is_result = match.get("isResult", False)
        
        if not is_result:
            h = match.get("h", {})
            a = match.get("a", {})
            forecast = match.get("forecast", {})
            
            rows.append({
                "날짜":       match.get("datetime", ""),
                "홈팀":       h.get("title", "") if isinstance(h, dict) else "",
                "원정팀":     a.get("title", "") if isinstance(a, dict) else "",
                "홈승확률":   forecast.get("w", "") if isinstance(forecast, dict) else "",
                "무승부확률": forecast.get("d", "") if isinstance(forecast, dict) else "",
                "원정승확률": forecast.get("l", "") if isinstance(forecast, dict) else "",
            })
    
    df = pd.DataFrame(rows)
    print(f"✅ 예정 경기 {len(df)}경기 완료!")
    return df

def save_to_s3(df, filename):
    csv_data = df.to_csv(index=False, encoding="utf-8-sig")
    s3.put_object(
        Bucket=BUCKET,
        Key=filename,
        Body=csv_data.encode("utf-8-sig"),
        ContentType="text/csv"
    )
    print(f"✅ S3 저장: {filename}")

def save_to_github(df, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"✅ GitHub 저장: {filepath}")

if __name__ == "__main__":
    df_2526 = collect_season("2025", "25-26")
    save_to_s3(df_2526, "pl_stats_2526.csv")
    save_to_github(df_2526, "data/pl_stats_2526.csv")
    
    df_fix = collect_fixtures()
    save_to_s3(df_fix, "pl_fixtures_2526.csv")
    save_to_github(df_fix, "data/pl_fixtures_2526.csv")
    
    print("\n🎉 전체 수집 완료!")
