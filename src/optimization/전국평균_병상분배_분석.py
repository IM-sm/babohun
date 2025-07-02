import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import os

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

print("=== 전국 평균 병상 분배 분석 ===")
print("📊 병원별 최적화 결과를 전국 평균 관점에서 분석")
print()

# --------------------------------------------------
# 1) 데이터 로드
# --------------------------------------------------
print("1/4: 데이터 로드 중...")

# 병원별 최적화 결과 로드
results_df = pd.read_csv('optimization_results_병상_분배_최적화_병원기준/병상_분배_최적화_결과.csv')

print(f"✅ 데이터 로드 완료: {len(results_df)}개 병원")
print()

# --------------------------------------------------
# 2) 전국 평균 분석
# --------------------------------------------------
print("2/4: 전국 평균 분석 중...")

# 전국 평균 계산
전국_총병상수 = results_df['현재병상수'].sum()
전국_총예측환자수 = results_df['예측환자수'].sum()
전국_평균병상가동률 = (전국_총예측환자수 / 365 / 전국_총병상수) * 100

# 최적화 후 전국 평균
전국_최적총병상수 = results_df['최적병상수'].sum()
전국_최적평균병상가동률 = (전국_총예측환자수 / 365 / 전국_최적총병상수) * 100

# 병상 변화량 분석
총변화량 = results_df['변화량'].sum()
증가병원수 = len(results_df[results_df['변화량'] > 0])
감소병원수 = len(results_df[results_df['변화량'] < 0])
변화없음병원수 = len(results_df[results_df['변화량'] == 0])

# 가동률 개선 분석
가동률_개선_병원수 = len(results_df[results_df['최적_병상가동률'] > results_df['현재_병상가동률']])
가동률_악화_병원수 = len(results_df[results_df['최적_병상가동률'] < results_df['현재_병상가동률']])
가동률_동일_병원수 = len(results_df[results_df['최적_병상가동률'] == results_df['현재_병상가동률']])

print(f"✅ 전국 평균 분석 완료")
print(f"  - 전국 총 병상 수: {전국_총병상수:,.0f}개")
print(f"  - 전국 총 예측 환자 수: {전국_총예측환자수:,.0f}명")
print(f"  - 전국 평균 병상가동률: {전국_평균병상가동률:.2f}%")
print(f"  - 최적화 후 평균 병상가동률: {전국_최적평균병상가동률:.2f}%")
print(f"  - 총 병상 변화량: {총변화량:,.0f}개")
print()

# --------------------------------------------------
# 3) 상세 분석
# --------------------------------------------------
print("3/4: 상세 분석 중...")

# 병상 규모별 분석
results_df['병상규모'] = pd.cut(results_df['현재병상수'], 
                              bins=[0, 100, 300, 500, 1000, float('inf')],
                              labels=['소형(100↓)', '중소형(100-300)', '중형(300-500)', '대형(500-1000)', '초대형(1000↑)'])

규모별_분석 = results_df.groupby('병상규모').agg({
    '현재병상수': ['count', 'sum', 'mean'],
    '최적병상수': ['sum', 'mean'],
    '변화량': ['sum', 'mean'],
    '현재_병상가동률': 'mean',
    '최적_병상가동률': 'mean'
}).round(2)

# 지역별 분석 (병원명에서 지역 추출)
results_df['지역'] = results_df['병원명'].str.extract(r'^([가-힣]+)')[0]

지역별_분석 = results_df.groupby('지역').agg({
    '현재병상수': ['count', 'sum', 'mean'],
    '최적병상수': ['sum', 'mean'],
    '변화량': ['sum', 'mean'],
    '현재_병상가동률': 'mean',
    '최적_병상가동률': 'mean'
}).round(2)

print(f"✅ 상세 분석 완료")
print()

# --------------------------------------------------
# 4) 결과 저장 및 시각화
# --------------------------------------------------
print("4/4: 결과 저장 및 시각화 중...")

# 결과 저장 디렉토리 생성
results_dir = "optimization_results_전국평균_분석"
os.makedirs(results_dir, exist_ok=True)

# 1) 전국 평균 요약 저장
summary_stats = {
    "timestamp": datetime.now().isoformat(),
    "전국_총병상수": int(전국_총병상수),
    "전국_총예측환자수": int(전국_총예측환자수),
    "전국_평균병상가동률": float(전국_평균병상가동률),
    "전국_최적평균병상가동률": float(전국_최적평균병상가동률),
    "총변화량": int(총변화량),
    "증가병원수": int(증가병원수),
    "감소병원수": int(감소병원수),
    "변화없음병원수": int(변화없음병원수),
    "가동률_개선_병원수": int(가동률_개선_병원수),
    "가동률_악화_병원수": int(가동률_악화_병원수),
    "가동률_동일_병원수": int(가동률_동일_병원수),
    "총병원수": int(len(results_df))
}

with open(f"{results_dir}/전국평균_요약.json", 'w', encoding='utf-8') as f:
    json.dump(summary_stats, f, ensure_ascii=False, indent=2)

# 2) 규모별 분석 저장
규모별_분석.to_csv(f"{results_dir}/규모별_분석.csv", encoding='utf-8-sig')

# 3) 지역별 분석 저장
지역별_분석.to_csv(f"{results_dir}/지역별_분석.csv", encoding='utf-8-sig')

# 4) 시각화
plt.figure(figsize=(20, 12))

# 서브플롯 1: 전국 평균 병상가동률 비교
plt.subplot(2, 3, 1)
labels = ['현재', '최적화 후']
values = [전국_평균병상가동률, 전국_최적평균병상가동률]
colors = ['lightcoral', 'lightblue']
bars = plt.bar(labels, values, color=colors, alpha=0.7)
plt.ylabel('병상가동률 (%)')
plt.title('전국 평균 병상가동률 비교')
plt.grid(True, alpha=0.3)
for bar, value in zip(bars, values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
             f'{value:.1f}%', ha='center', va='bottom')

# 서브플롯 2: 병상 변화량 분포
plt.subplot(2, 3, 2)
plt.hist(results_df['변화량'], bins=15, alpha=0.7, color='skyblue', edgecolor='black')
plt.xlabel('병상 수 변화량')
plt.ylabel('병원 수')
plt.title('병상 수 변화량 분포')
plt.axvline(x=0, color='red', linestyle='--', alpha=0.7)
plt.grid(True, alpha=0.3)

# 서브플롯 3: 병상 규모별 평균 변화량
plt.subplot(2, 3, 3)
규모별_변화량 = results_df.groupby('병상규모')['변화량'].mean().sort_values(ascending=True)
plt.barh(규모별_변화량.index.astype(str), 규모별_변화량.values, alpha=0.7, color='lightgreen')
plt.xlabel('평균 변화량')
plt.title('병상 규모별 평균 변화량')
plt.axvline(x=0, color='red', linestyle='--', alpha=0.7)
plt.grid(True, alpha=0.3)

# 서브플롯 4: 지역별 평균 가동률 개선
plt.subplot(2, 3, 4)
지역별_개선 = results_df.groupby('지역').apply(
    lambda x: (x['최적_병상가동률'] - x['현재_병상가동률']).mean()
).sort_values(ascending=True)
plt.barh(지역별_개선.index.astype(str), 지역별_개선.values, alpha=0.7, color='orange')
plt.xlabel('가동률 개선도 (%)')
plt.title('지역별 평균 가동률 개선')
plt.axvline(x=0, color='red', linestyle='--', alpha=0.7)
plt.grid(True, alpha=0.3)

# 서브플롯 5: 현재 vs 최적 가동률 산점도
plt.subplot(2, 3, 5)
plt.scatter(results_df['현재_병상가동률'], results_df['최적_병상가동률'], 
           alpha=0.6, c=results_df['변화량'], cmap='RdYlBu')
plt.colorbar(label='변화량')
max_util = max(results_df['현재_병상가동률'].max(), results_df['최적_병상가동률'].max())
plt.plot([0, max_util], [0, max_util], 'r--', alpha=0.5)
plt.xlabel('현재 병상가동률 (%)')
plt.ylabel('최적 병상가동률 (%)')
plt.title('현재 vs 최적 가동률 비교')
plt.grid(True, alpha=0.3)

# 서브플롯 6: 병상 규모별 병원 수 분포
plt.subplot(2, 3, 6)
규모별_병원수 = results_df['병상규모'].value_counts().sort_index()
plt.pie(규모별_병원수.values, labels=규모별_병원수.index.astype(str), autopct='%1.1f%%', 
        startangle=90, colors=plt.cm.tab10(np.linspace(0, 1, len(규모별_병원수))))
plt.title('병상 규모별 병원 수 분포')

plt.tight_layout()
plt.savefig(f"{results_dir}/전국평균_분석_시각화.png", dpi=300, bbox_inches='tight')
plt.show()

# 5) 상세 리포트 출력
print("\n" + "="*60)
print("📊 전국 평균 병상 분배 분석 결과")
print("="*60)

print(f"\n🎯 전국 전체 현황:")
print(f"  - 총 병원 수: {len(results_df):,}개")
print(f"  - 총 병상 수: {전국_총병상수:,.0f}개")
print(f"  - 총 예측 환자 수: {전국_총예측환자수:,.0f}명")
print(f"  - 평균 병상가동률: {전국_평균병상가동률:.2f}% → {전국_최적평균병상가동률:.2f}%")

print(f"\n📈 병상 변화 현황:")
print(f"  - 총 변화량: {총변화량:,.0f}개")
print(f"  - 증가 병원: {증가병원수}개")
print(f"  - 감소 병원: {감소병원수}개")
print(f"  - 변화 없음: {변화없음병원수}개")

print(f"\n🏥 가동률 개선 현황:")
print(f"  - 개선 병원: {가동률_개선_병원수}개")
print(f"  - 악화 병원: {가동률_악화_병원수}개")
print(f"  - 동일 병원: {가동률_동일_병원수}개")

print(f"\n📋 규모별 분석:")
print(규모별_분석[['현재병상수', '변화량', '현재_병상가동률', '최적_병상가동률']].round(2))

print(f"\n🌍 지역별 분석:")
print(지역별_분석[['현재병상수', '변화량', '현재_병상가동률', '최적_병상가동률']].round(2))

print(f"\n✅ 모든 결과가 {results_dir}/ 디렉토리에 저장되었습니다!")
print("="*60) 