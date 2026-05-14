import pandas as pd
import numpy as np
import boto3
import os
from understatapi import UnderstatClient

# S3 클라이언트
s3 = boto3.client('s3')
BUCKET = 'pl-datahub-data'

def collect_season(season_param, season_label):
    print(f"📥 {season_label} 수집 중...")
    understat = UnderstatClient()
    data = understat.league(league="EPL").get_team_data(season=season_param)
    
    rows = []
    for _, row in data.iterrows():
        team_name = row.name
        history = row.get("history", [])
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
            "team":     team_name,
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
    
    # 득실차 기준 순위 계산
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
    match_data = understat.league(league="EPL").get_match_data(season="2025")
    
    rows = []
    for _, match in match_data.iterrows():
        if not match.get("isResult", False):
            rows.append({
                "날짜":       match.get("datetime", ""),
                "홈팀":       match.get("h", {}).get("title", "") if isinstance(match.get("h"), dict) else "",
                "원정팀":     match.get("a", {}).get("title", "") if isinstance(match.get("a"), dict) else "",
                "홈승확률":   match.get("forecast", {}).get("w", "") if isinstance(match.get("forecast"), dict) else "",
                "무승부확률": match.get("forecast", {}).get("d", "") if isinstance(match.get("forecast"), dict) else "",
                "원정승확률": match.get("forecast", {}).get("l", "") if isinstance(match.get("forecast"), dict) else "",
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
    # 25-26 현재 시즌 수집
    df_2526 = collect_season("2025", "25-26")
    save_to_s3(df_2526, "pl_stats_2526.csv")
    save_to_github(df_2526, "data/pl_stats_2526.csv")
    
    # 경기 일정 수집
    df_fix = collect_fixtures()
    save_to_s3(df_fix, "pl_fixtures_2526.csv")
    save_to_github(df_fix, "data/pl_fixtures_2526.csv")
    
    print("\n🎉 전체 수집 완료!")
