import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
import plotly.graph_objects as go

# CSV 파일 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv('processed_data.csv')
    return df

df = load_data()

# 시작일시가 2024-04, 2024-05인 데이터만 선택
df_april = df[df["시작일시"].str.contains("2024-04")]
df_may = df[df["시작일시"].str.contains("2024-05")]

# 점포별 종합만족도 계산 (4월)
average_scores_april = df_april.groupby("점포")[["직원 서비스", "정보 제공", "상품 준비", "신속 결제", "매장 환경"]].mean()
average_scores_april_100 = average_scores_april * 100 / 7
average_scores_april_100["종합만족도"] = average_scores_april_100.mean(axis=1)
average_scores_april_100 = average_scores_april_100.round(0).astype(int)

# 점포별 종합만족도 계산 (5월)
average_scores_may = df_may.groupby("점포")[["직원 서비스", "정보 제공", "상품 준비", "신속 결제", "매장 환경"]].mean()
average_scores_may_100 = average_scores_may * 100 / 7
average_scores_may_100["종합만족도"] = average_scores_may_100.mean(axis=1)
average_scores_may_100 = average_scores_may_100.round(0).astype(int)

# 점포별 NCSI 계산 (4월)
ncsi_scores_april = df_april.groupby("점포")[["고객기대수준", "고객인지품질", "고객인지가치"]].mean()
ncsi_scores_april_100 = ncsi_scores_april * 100 / 7
ncsi_scores_april_100["NCSI"] = ncsi_scores_april_100.mean(axis=1)
ncsi_scores_april_100 = ncsi_scores_april_100.round(0).astype(int)

# 점포별 NCSI 계산 (5월)
ncsi_scores_may = df_may.groupby("점포")[["고객기대수준", "고객인지품질", "고객인지가치"]].mean()
ncsi_scores_may_100 = ncsi_scores_may * 100 / 7
ncsi_scores_may_100["NCSI"] = ncsi_scores_may_100.mean(axis=1)
ncsi_scores_may_100 = ncsi_scores_may_100.round(0).astype(int)

# Helper function to calculate reusage rate
def calculate_reusage_rate(df, month):
    reusage_rates = df["재이용의향률"].value_counts(normalize=True) * 100
    reusage_rate_df = pd.DataFrame(reusage_rates).reset_index()
    reusage_rate_df.columns = ["재이용의향률", f"{month} 재이용의향률"]
    return reusage_rate_df

# Helper function to add metrics
def add_metrics(store_name, df_april, df_may, average_scores_april_100, average_scores_may_100, ncsi_scores_april_100, ncsi_scores_may_100):
    # Store data for April and May
    store_april = df_april[df_april["점포"] == store_name]
    store_may = df_may[df_may["점포"] == store_name]

    # 종합만족도 계산
    satisfaction_april = average_scores_april_100.loc[store_name]["종합만족도"]
    satisfaction_may = average_scores_may_100.loc[store_name]["종합만족도"]
    satisfaction_delta = satisfaction_may - satisfaction_april

    # NCSI 계산
    ncsi_april = ncsi_scores_april_100.loc[store_name]["NCSI"]
    ncsi_may = ncsi_scores_may_100.loc[store_name]["NCSI"]
    ncsi_delta = ncsi_may - ncsi_april

    # 재이용의향률 계산
    reusage_rate_april = calculate_reusage_rate(store_april, "4월")
    reusage_rate_may = calculate_reusage_rate(store_may, "5월")

    reusage_rate_merged = pd.merge(reusage_rate_april, reusage_rate_may, on="재이용의향률", how="outer").fillna(0)
    reusage_rate_merged["Delta"] = reusage_rate_merged["5월 재이용의향률"] - reusage_rate_merged["4월 재이용의향률"]

    # 5월 재이용의향률 값 추가
    reusage_rate_may_value = reusage_rate_merged[reusage_rate_merged["재이용의향률"] == "예."].iloc[0]["5월 재이용의향률"]
    reusage_rate_delta = reusage_rate_merged[reusage_rate_merged["재이용의향률"] == "예."].iloc[0]["Delta"]

    # Display metrics with increased font size and bold labels
    cols = st.columns(3)
    style = """
    <style>
    .big-font {
        font-size:20px !important;
        font-weight:bold !important;
    }
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)

    with cols[0]:
        st.write(f"<span class='big-font'>종합만족도</span>", unsafe_allow_html=True)
        st.metric(label="종합만족도", value=f"{satisfaction_may}점", delta=f"{satisfaction_delta}점", label_visibility='collapsed')

    with cols[1]:
        st.write(f"<span class='big-font'>NCSI</span>", unsafe_allow_html=True)
        st.metric(label="NCSI", value=f"{ncsi_may}점", delta=f"{ncsi_delta}점", label_visibility='collapsed')

    with cols[2]:
        st.write(f"<span class='big-font'>재이용의향률</span>", unsafe_allow_html=True)
        st.metric(label="재이용의향률", value=f"{int(reusage_rate_may_value)}%", delta=f"{int(reusage_rate_delta)}%", label_visibility='collapsed')

# 종합만족도 항목별 점수 가로형 바 차트
def plot_satisfaction_scores(store_name, average_scores_april_100, average_scores_may_100):
    st.write(f"**{store_name} 종합만족도 항목별 점수**")
    categories = ["직원 서비스", "정보 제공", "상품 준비", "신속 결제", "매장 환경"]
    satisfaction_april_scores = average_scores_april_100.loc[store_name, categories]
    satisfaction_may_scores = average_scores_may_100.loc[store_name, categories]

    fig_satisfaction = go.Figure()
    fig_satisfaction.add_trace(go.Bar(
        y=categories,
        x=satisfaction_april_scores.values,
        name='4월 점수',
        orientation='h',
        marker=dict(color='#E5ECF6')
    ))
    fig_satisfaction.add_trace(go.Bar(
        y=categories,
        x=satisfaction_may_scores.values,
        name='5월 점수',
        orientation='h',
        marker=dict(color='#636EFA')
    ))
    fig_satisfaction.update_layout(barmode='group', xaxis_title="점수", yaxis_title="항목", title=f"항목별 종합만족도 비교 (4월 vs 5월) - {store_name}")
    st.plotly_chart(fig_satisfaction)

# Function to filter comments by store and add search functionality
def add_comments_section(store_name, df):
    st.write(f"**추가 의견**")
    store_comments = df[(df["점포"] == store_name) & (df["추가 의견"].notna()) & (df["추가 의견"] != '')][["점포", "추가 의견"]]
    
    search_term = st.text_input(f"{store_name} 관련 궁금한 키워드를 검색해보세요.", "")
    if search_term:
        store_comments = store_comments[store_comments["추가 의견"].str.contains(search_term, case=False, na=False)]
    
    # Display dataframe
    st.dataframe(store_comments)

# 각 점포별로 추가 의견 란에 가장 길게 입력해준 사람의 의견을 찾기
longest_comments = df.groupby('점포')['추가 의견'].apply(lambda x: x.loc[x.str.len().idxmax()])

# 결과를 데이터프레임으로 변환
longest_comments_df = longest_comments.reset_index()
longest_comments_df.columns = ['점포', '가장 긴 추가 의견']

# 점포별 증감률 계산
ncsi_delta_scores = ncsi_scores_may_100["NCSI"] - ncsi_scores_april_100["NCSI"]

# 점포 리스트
store_labels = average_scores_may_100.index

# 점포별 증감률 계산
delta_scores = average_scores_may_100["종합만족도"] - average_scores_april_100["종합만족도"]

# Function to get the response counts for May
def get_response_counts(store_name, df_may):
    response_count = df_may[df_may["점포"] == store_name].shape[0]
    return f"응답수: {response_count}건"

def plot_expectation_pie_chart(store_name, df):
    st.write(f"**{store_name} 고객 기대 수준 분포**")
    store_data = df[(df["점포"] == store_name) & (df["시작일시"].str.contains("2024-05"))]
    
    low_expectation = store_data[(store_data["고객기대수준"] >= 1) & (store_data["고객기대수준"] <= 4)].shape[0]
    mid_expectation = store_data[store_data["고객기대수준"] == 5].shape[0]
    high_expectation = store_data[(store_data["고객기대수준"] == 6) | (store_data["고객기대수준"] == 7)].shape[0]

    labels = ['낮은 기대 수준', '중간 기대 수준', '높은 기대 수준']
    values = [low_expectation, mid_expectation, high_expectation]
    colors = ['#636EFA', '#AEB4FC', '#E5ECF6']

    fig = px.pie(names=labels, values=values, color=labels, color_discrete_map={'낮은 기대 수준':'#636EFA', '중간 기대 수준':'#AEB4FC', '높은 기대 수준':'#E5ECF6'})
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False)  # Hide the legend
    st.plotly_chart(fig, use_container_width=True)

# Function to filter low expectation reasons
def low_expectation_reasons(store_name, df):
    st.write(f"**{store_name} 낮은 기대 수준 이유**")
    reasons_df = df[(df["점포"] == store_name) & (df["고객기대수준"].between(1, 4))][["고객기대수준", "낮은 기대수준 이유"]]
    reasons_df = reasons_df[reasons_df["낮은 기대수준 이유"].notna() & (reasons_df["낮은 기대수준 이유"] != '')]
    
    # Count occurrences of each reason
    reasons_counts = reasons_df["낮은 기대수준 이유"].value_counts().reset_index()
    reasons_counts.columns = ["낮은 기대수준 이유", "개수"]

    st.dataframe(reasons_counts)

# 응답수 데이터프레임 생성
response_counts = pd.DataFrame({
    '점포': store_labels,
    '4월 응답수': [df_april[df_april["점포"] == label].shape[0] for label in store_labels],
    '5월 응답수': [df_may[df_may["점포"] == label].shape[0] for label in store_labels],
    '4월 종합만족도': average_scores_april_100.loc[store_labels]["종합만족도"].values,
    '5월 종합만족도': average_scores_may_100["종합만족도"].values,
    '증감률': delta_scores.values
})

# 오각형 그래프 (레이다 차트) 생성
def create_radar_chart():
    categories = ["직원 서비스", "정보 제공", "상품 준비", "신속 결제", "매장 환경"]
    fig = go.Figure()

    for store in store_labels:
        fig.add_trace(go.Scatterpolar(
            r=average_scores_may_100.loc[store, categories].values,
            theta=categories,
            fill='toself',
            name=store
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[60, 100]
            )),
        showlegend=True,
        title="항목별 종합만족도"
    )
    
    return fig

# 삼각형 그래프 (레이다 차트) 생성
def create_triangle_chart():
    categories = ["고객기대수준", "고객인지품질", "고객인지가치"]
    fig = go.Figure()

    for store in store_labels:
        fig.add_trace(go.Scatterpolar(
            r=ncsi_scores_may_100.loc[store, categories].values,
            theta=categories,
            fill='toself',
            name=store
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[75, 88]
            )),
        showlegend=True,
        title="항목별 NCSI"
    )
    
    return fig

# Streamlit 앱
st.title("5월 고객만족도📊")

# 탭 생성
tab1, tab2, tab3, tab4 = st.tabs(['요약', '명동점', '인천공항점', '부산점'])

with tab1:
    st.subheader("종합만족도")
    st.markdown("""
종합만족도는 다섯 가지 서비스 요소; <span style="background-color: #ffffe0;">직원 서비스, 정보 제공, 상품 준비, 신속 결제, 매장 환경의 점수를 평균</span> 낸 값으로, 신세계면세점의 전반적인 만족도를 측정할 수 있습니다. 
""", unsafe_allow_html=True)

    cols = st.columns(3)
    for index, row in response_counts.iterrows():
        with cols[index % 3]:
            st.metric(label=row['점포'], value=f"{row['5월 종합만족도']}점", delta=f"{row['증감률']}점")
    
    st.plotly_chart(create_radar_chart())

    st.divider()

    st.subheader("NCSI")
    st.markdown("""
NCSI는 한국생산성본부가 개발한 고객만족 측정 지표로 <span style="background-color: #ffffe0;">고객기대수준, 고객인지품질, 고객인지가치의 점수</span>를 평균 낸 값입니다. 신세계면세점은 고객의 요구사항을 얼마나 충족시켜 줄 것이라 기대했으며, 실제로 얼마나 충족되었는지 비교평가할 수 있습니다. 
""", unsafe_allow_html=True)

    cols_ncsi = st.columns(3)
    for index, row in enumerate(ncsi_scores_may_100.iterrows()):
        with cols_ncsi[index % 3]:
            st.metric(label=row[0], value=f"{row[1]['NCSI']:.0f}점", delta=f"{ncsi_delta_scores.loc[row[0]]:.0f}점" if pd.notna(ncsi_delta_scores.loc[row[0]]) else "0점")
    
    st.plotly_chart(create_triangle_chart())

    st.divider()

    # 점포별 가장 긴 추가 의견
    st.subheader("점포별 주요 의견")
    for index, row in longest_comments_df.iterrows():
        st.write(f"{row['점포']}")
        st.text_area(label='가장 긴 추가 의견', value=row['가장 긴 추가 의견'], height=200, key=index, label_visibility='collapsed')

# 명동점 탭
with tab2:
    response_count_text = get_response_counts("명동점", df_may)
    st.markdown(f"### 명동점 <span style='font-size: 12px;'>({response_count_text})</span>", unsafe_allow_html=True)
    add_metrics("명동점", df_april, df_may, average_scores_april_100, average_scores_may_100, ncsi_scores_april_100, ncsi_scores_may_100)
    st.divider()
    
    col1, col2 = st.columns([2, 3])
    # In the first column, add the pie chart
    with col1:
        plot_expectation_pie_chart("명동점", df)
    
    # In the second column, add the low expectation reasons dataframe
    with col2:
        low_expectation_reasons("명동점", df)
    
    st.divider()
    plot_satisfaction_scores("명동점", average_scores_april_100, average_scores_may_100)
    add_comments_section("명동점", df)

# 인천공항점 탭
with tab3:
    response_count_text = get_response_counts("인천공항점", df_may)
    st.markdown(f"### 인천공항점 <span style='font-size: 12px;'>({response_count_text})</span>", unsafe_allow_html=True)
    add_metrics("인천공항점", df_april, df_may, average_scores_april_100, average_scores_may_100, ncsi_scores_april_100, ncsi_scores_may_100)
    st.divider()
    
    col1, col2 = st.columns([2, 3])
    # In the first column, add the pie chart
    with col1:
        plot_expectation_pie_chart("인천공항점", df)
    
    # In the second column, add the low expectation reasons dataframe
    with col2:
        low_expectation_reasons("인천공항점", df)
    
    st.divider()
    plot_satisfaction_scores("인천공항점", average_scores_april_100, average_scores_may_100)
    add_comments_section("인천공항점", df)

# 부산점 탭
with tab4:
    response_count_text = get_response_counts("부산점", df_may)
    st.markdown(f"### 부산점 <span style='font-size: 12px;'>({response_count_text})</span>", unsafe_allow_html=True)
    add_metrics("부산점", df_april, df_may, average_scores_april_100, average_scores_may_100, ncsi_scores_april_100, ncsi_scores_may_100)
    st.divider()
    
    col1, col2 = st.columns([2, 3])
    # In the first column, add the pie chart
    with col1:
        plot_expectation_pie_chart("부산점", df)
    
    # In the second column, add the low expectation reasons dataframe
    with col2:
        low_expectation_reasons("부산점", df)
    
    st.divider()
    plot_satisfaction_scores("부산점", average_scores_april_100, average_scores_may_100)
    add_comments_section("부산점", df)
