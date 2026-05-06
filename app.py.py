import streamlit as st
import pandas as pd
import sqlite3
import os
import matplotlib.pyplot as plt

# 한글 폰트 설정 (Windows/Mac 공용 처리 시 유의)
# 기본적으로 Streamlit Cloud에서는 폰트 설정이 까다로울 수 있으나, 
# 로컬 테스트를 위해 간단히 설정합니다.
plt.rcParams['font.family'] = 'Malgun Gothic' # Windows 기준
plt.rcParams['axes.unicode_minus'] = False

# 1. DB 연결 및 데이터 로드 함수
def get_connection():
    db_path = '자전거분석.db'
    if not os.path.exists(db_path):
        return None
    return sqlite3.connect(db_path)

# 페이지 설정
st.set_page_config(page_title="따릉이 이용현황 대시보드", layout="wide")
st.title("🚲 서울시 공공자전거 이용 데이터 분석")
st.markdown("---")

conn = get_connection()

# DB 파일 존재 여부 체크
if conn is None:
    st.error("⚠️ '자전거분석.db' 파일을 찾을 수 없습니다. 파일이 같은 폴더에 있는지 확인해주세요!")
    st.stop()

# --- 차트 1: 자치구별 총 이용건수 ---
st.subheader("1. 자치구별 총 이용건수 (라인 차트)")
query1 = """
SELECT t2.자치구, SUM(t1.이용건수) as 총이용건수
FROM 이용정보 t1
INNER JOIN 대여소 t2 ON t1.대여소번호 = t2.대여소번호
GROUP BY t2.자치구
ORDER BY 총이용건수 DESC
"""
df1 = pd.read_sql(query1, conn)

col1, col2 = st.columns([2, 1])
with col1:
    st.line_chart(df1.set_index('자치구'))
with col2:
    st.info("**SQL 쿼리**")
    st.code(query1, language='sql')
    st.success("**인사이트**\n- 이용정보와 대여소 테이블을 결합하여 지역별 수요를 파악했습니다.\n- 특정 자치구의 이용량이 압도적으로 높은지 시각적으로 한눈에 알 수 있습니다.")


# --- 차트 2: 나이대별 평균 이용건수 ---
st.subheader("2. 연령대별 평균 이용건수 (막대 차트)")
query2 = """
SELECT 연령대코드, AVG(이용건수) as 평균이용건수
FROM 이용정보
GROUP BY 연령대코드
ORDER BY 연령대코드
"""
df2 = pd.read_sql(query2, conn)

col3, col4 = st.columns([2, 1])
with col3:
    st.bar_chart(df2.set_index('연령대코드'))
with col4:
    st.info("**SQL 쿼리**")
    st.code(query2, language='sql')
    st.success("**인사이트**\n- 어떤 연령층이 따릉이를 가장 활발하게 이용하는지 보여줍니다.\n- 평균 이용건수가 높은 연령대를 타겟으로 맞춤형 정책을 세울 수 있습니다.")


# --- 차트 3: 날씨와 이용량의 관계 ---
st.subheader("3. 기온 구간별 평균 이용건수 (가로 막대 차트)")
query3 = """
SELECT 
    CASE 
        WHEN 평균기온 < 5 THEN '1. 5도 미만 (추움)'
        WHEN 평균기온 >= 5 AND 평균기온 < 15 THEN '2. 5~15도 (선선)'
        WHEN 평균기온 >= 15 AND 평균기온 < 25 THEN '3. 15~25도 (쾌적)'
        ELSE '4. 25도 이상 (더움)'
    END as 기온구간,
    AVG(이용건수) as 평균이용건수
FROM 이용정보 i
JOIN 기온 t ON i.대여일자 = t.년월
GROUP BY 기온구간
ORDER BY 기온구간
"""
df3 = pd.read_sql(query3, conn)

col5, col6 = st.columns([2, 1])
with col5:
    # 가로 막대 차트를 위해 matplotlib 사용
    fig, ax = plt.subplots()
    ax.barh(df3['기온구간'], df3['평균이용건수'], color='skyblue')
    ax.set_xlabel('평균 이용건수')
    st.pyplot(fig)
with col6:
    st.info("**SQL 쿼리**")
    st.code(query3, language='sql')
    st.success("**인사이트**\n- 기온에 따른 이용 행태 변화를 분석했습니다.\n- 주로 쾌적한 온도(15~25도)에서 이용량이 급증하는 경향을 확인할 수 있습니다.")

conn.close()