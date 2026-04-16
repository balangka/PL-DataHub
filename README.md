# ⚽ PL-DataHub
**프리미어리그 팀 전술 스타일 분석 (2023-24 시즌)**

## 📌 프로젝트 개요
프리미어리그 팀들의 전술 지표(점유율, xG, 슈팅, 압박 등)를 분석하여
전술 스타일과 최종 순위 사이의 관계를 통계적으로 검증합니다.

## 🔍 연구 질문
> PL 팀들의 전술 지표(점유율, xG, 압박 횟수)는 최종 순위와
> 통계적으로 유의미한 상관관계가 있는가? (2023-24 시즌 기준)

## 📊 분석 내용
- **피어슨 상관분석** — 전술 지표와 순위의 관계 검증
- **K-means 군집분석** — Elbow/Silhouette으로 최적 k=3 결정 후 팀 유형 분류
- **Granger Causality** — 전술 지표 변화가 순위에 선행하는지 검증 (예정)

## 🔑 핵심 발견
- xG와 순위의 상관계수: **-0.89** (가장 강한 관계)
- 점유율과 순위의 상관계수: **-0.85**
- 슈팅수와 순위의 상관계수: **-0.81**
- 상위권 팀일수록 점유율과 xG가 높음

## 📈 군집 분석 결과
| 군집 | 팀 | 특징 |
|---|---|---|
| 엘리트 | 맨시티, 아스날, 리버풀, 아스톤빌라 | 높은 점유율 + 높은 xG |
| 중상위권 | 토트넘, 첼시, 뉴캐슬 등 | 중간 전술 지표 |
| 하위권 | 웨스트햄, 울버햄튼 등 | 낮은 점유율 + 낮은 xG |

## 🗂️ 파일 구조
```
PL-DataHub/
  📁 data/
    └── pl_merged_2324.csv
  📁 notebooks/
    └── 14_장진원.ipynb
  📄 correlation_heatmap.png
  📄 kmeans_cluster.png
  📄 elbow_silhouette.png
  📄 README.md
```

## 🛠️ 기술 스택
Python | pandas | scikit-learn | matplotlib | seaborn | Google Colab | GitHub

## 📅 데이터 출처
- Kaggle: 2023-2024 Premier League Stats (FBref 기반)

## 📅 향후 계획
- 나머지 4시즌 데이터 추가 (2019-20 ~ 2022-23)
- Granger Causality 분석 추가
- Streamlit 대시보드 구축
