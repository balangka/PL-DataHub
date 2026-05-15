# ⚽ PL DataHub
> 프리미어리그 팀 전술 스타일 분석 및 경기 결과 예측 대시보드

**성균관대학교 정보통신대학원 빅데이터학과 · 2025720344 · 장진원**

[![Streamlit](https://img.shields.io/badge/Streamlit-Live-brightgreen)](http://3.39.23.159:8501)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/balangka/PL-DataHub)

---

## 📋 프로젝트 개요

### 연구 질문
> PL 팀들의 전술 지표(xG, xGA, xPTS, PPDA, DC)는 최종 순위와 통계적으로 유의미한 상관관계가 있는가?

### 목표
- 전술 지표와 순위 간 상관관계 검증
- 팀 유형 분류 (K-means 군집 분석)
- 5시즌 데이터 기반 예측 모델 구축
- 실시간 대시보드 구현

---

## 📊 분석 지표 설명

| 지표 | 설명 | 높을수록 |
|------|------|---------|
| **xG** (Expected Goals) | 슈팅 질 기반 예상 득점 | 공격력 강함 |
| **xGA** (Expected Goals Against) | 실점 기댓값 | 수비력 약함 |
| **xPTS** (Expected Points) | 경기 내용 기반 기대 승점 | 실력 강함 |
| **PPDA** (Passes Per Defensive Action) | 압박 강도 지표 | 압박 약함 |
| **DC** (Deep Completions) | 상대 진영 침투 횟수 | 공격 침투 강함 |

---

## 🔬 분석 방법론

### 1. Pearson vs Spearman 상관분석
**왜 두 가지를 비교했나?**
- 순위(1~20위)는 **순서형(ordinal) 변수**
- Pearson은 연속형 변수에 적합
- Spearman은 순서형 변수에 더 적절
- 두 결과를 비교해 **분석의 견고성** 확인

**p-value를 함께 보고한 이유**
- 상관계수만으로는 우연인지 진짜인지 알 수 없음
- p < 0.05: 통계적으로 유의미한 관계
- 결과의 신뢰성 검증

### 2. VIF 다중공선성 분석
**왜 했나?**
- xG, xPTS, DC가 서로 높은 상관관계 보임
- xPTS는 xG 기반으로 산출된 지표
- 변수 간 겹침이 크면 분석 결과 왜곡 가능
- VIF > 10: 심각한 다중공선성

**결과 및 해석**
- xPTS VIF = 100~180 → 심각한 다중공선성
- PCA로 5개 지표를 1개 축으로 압축 → PC1이 79% 설명

### 3. K-means 군집 분석
**왜 K-means를 선택했나?**
- K-means, 계층적(Ward), GMM, DBSCAN 비교
- K-means Silhouette Score 0.326으로 가장 높음
- 도메인 지식(상/중/하위권) 반영해 k=3 선택

### 4. Granger Causality 분석
**왜 했나?**
- 상관관계 ≠ 인과관계
- "xG가 높으면 순위도 높다" vs "좋은 팀이 xG를 만든다"
- 전술 지표가 순위를 **선행(예측)** 하는지 검증

**결과**
- 모든 지표 p > 0.05 → 다음 시즌 예측 불가
- 해석: 매 시즌 실시간 모니터링이 필요 → **PL DataHub의 존재 이유**

### 5. 수비의 역설 재검증
**교수님 지적 사항**
- "수비 지표 양의 상관이 단순히 수비 시간 누적 효과 아닌가?"

**검증 방법**
- PPDA(압박 강도)로 per-game 보정 후 재분석
- 4시즌 모두 양의 상관 유지 → 단순 누적 효과 아님
- 압박 약한 팀(PPDA 높음)이 하위권인 패턴 확인

---

## 🗂️ 데이터 수집

### 수집 방법
- **Understat API** (`understatapi` 패키지)
- 자동 수집: GitHub Actions (매일 자정 KST)
- 저장: AWS S3 (`pl-datahub-data`)

### 수집 시즌
| 시즌 | 용도 |
|------|------|
| 21-22 | 분석/학습용 |
| 22-23 | 분석/학습용 |
| 23-24 | 분석/학습용 (중간고사) |
| 24-25 | 분석/학습용 |
| 25-26 | 현재 시즌 (예측용) |

---

## 🏗️ 시스템 아키텍처
GitHub Actions (매일 자정 KST)
↓ Understat 데이터 자동 수집
↓ AWS S3 저장
AWS EC2 (Streamlit 호스팅)
↓ S3에서 실시간 데이터 로드 (1시간 캐싱)
↓ 대시보드 표시
---

## 📱 대시보드 구성

| 탭 | 내용 |
|----|------|
| 📊 시즌 분석 | 상관분석, VIF, PCA, 군집 비교 |
| 🔴 현재 시즌 | 25-26 실시간 순위표 |
| 📅 예측 모델 | Random Forest 순위 예측 |
| ⚽ 경기 일정 & 예측 | 예정 경기 + 승패 확률 |

---

## 🔑 주요 발견

1. **xPTS가 핵심 지표** — 예측 모델 중요도 61.5%
2. **4시즌 일관성** — Pearson/Spearman 모두 동일한 패턴
3. **다중공선성 존재** — PCA로 5개 → 1개 축 압축 가능
4. **수비의 역설** — 압박 약한 팀이 하위권 (4시즌 일관)
5. **Granger 비유의** — 매 시즌 실시간 모니터링 필요

---

## 🛠️ 기술 스택
Python 3.11
├── Streamlit (대시보드)
├── Pandas / NumPy (데이터 처리)
├── Scikit-learn (머신러닝)
├── Scipy / Statsmodels (통계 분석)
├── Matplotlib (시각화)
└── Understatapi (데이터 수집)
AWS
├── EC2 (서버 호스팅)
└── S3 (데이터 저장)
GitHub Actions (자동화)
---

## 📁 파일 구조
PL-DataHub/
├── app.py                    # Streamlit 대시보드
├── collect_data.py           # 데이터 수집 스크립트
├── data/
│   ├── pl_stats_2526.csv    # 현재 시즌 (자동 업데이트)
│   └── pl_fixtures_2526.csv # 경기 일정 (자동 업데이트)
├── notebooks/
│   └── 14_장진원.ipynb      # 분석 노트북
└── .github/
└── workflows/
└── update_data.yml  # GitHub Actions
