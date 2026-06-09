import streamlit as st
import pandas as pd
from scipy.stats import poisson

# ---- 准备数据：靠 @st.cache_data，只在第一次算，之后记住结果 ----
@st.cache_data
def load_avg_scores():
    df = pd.read_csv("data/results.csv")
    df = df.dropna(subset=["home_score", "away_score"])

    teams_2026 = [
        "Australia", "Iran", "Japan", "Jordan", "South Korea", "Qatar", "Saudi Arabia", "Uzbekistan", "Iraq",
        "Algeria", "Cape Verde", "Ivory Coast", "Egypt", "Ghana", "Morocco", "Senegal", "South Africa", "Tunisia", "DR Congo",
        "United States", "Canada", "Mexico", "Curaçao", "Haiti", "Panama",
        "Argentina", "Brazil", "Colombia", "Ecuador", "Paraguay", "Uruguay",
        "New Zealand",
        "England", "France", "Croatia", "Norway", "Portugal", "Germany", "Netherlands",
        "Austria", "Belgium", "Scotland", "Spain", "Switzerland", "Sweden", "Turkey",
        "Bosnia and Herzegovina", "Czech Republic",
    ]
    df_wc = df[(df["date"] >= "2022-01-01")
               & df["home_team"].isin(teams_2026)
               & df["away_team"].isin(teams_2026)]

    hs = df_wc.groupby("home_team")["home_score"].sum()
    as_ = df_wc.groupby("away_team")["away_score"].sum()
    hg = df_wc.groupby("home_team").size()
    ag = df_wc.groupby("away_team").size()
    return hs.add(as_, fill_value=0) / hg.add(ag, fill_value=0)


# ---- 你已经写好的模型函数，原封不动 ----
def score_matrix(team_a, team_b, avg_scores, max_goals=6):
    lam_a = avg_scores[team_a]
    lam_b = avg_scores[team_b]
    rows = []
    for i in range(max_goals + 1):
        row = []
        for j in range(max_goals + 1):
            row.append(poisson.pmf(i, lam_a) * poisson.pmf(j, lam_b))
        rows.append(row)
    return pd.DataFrame(
        rows,
        index=[f"{team_a} {i}" for i in range(max_goals + 1)],
        columns=[f"{team_b} {j}" for j in range(max_goals + 1)],
    )


# ---- 网页界面 ----
avg_scores = load_avg_scores()
teams = sorted(avg_scores.index)          # 队名排序，下拉框里好找

st.title("2026 世界杯比分预测")

team_a = st.selectbox("A 队", teams, index=teams.index("Brazil"))
team_b = st.selectbox("B 队", teams, index=teams.index("England"))

table = score_matrix(team_a, team_b, avg_scores)
top = table.stack().sort_values(ascending=False).head(5)  # type: ignore
# ---- 算胜平负 ----
p_a_win = 0.0
p_draw  = 0.0
p_b_win = 0.0
for i in range(len(table)):          # A 队进 i 球
    for j in range(len(table)):      # B 队进 j 球
        p = table.iloc[i, j]
        if i > j:
            p_a_win += p             # A 进得多 → A 赢
        elif i == j:
            p_draw += p              # 一样多 → 平
        else:
            p_b_win += p             # B 进得多 → B 赢

# ---- 显示成三个大数字，并排 ----
st.subheader("胜平负")
c1, c2, c3 = st.columns(3)
c1.metric(f"{team_a} 赢", f"{p_a_win:.1%}")
c2.metric("平局",          f"{p_draw:.1%}")
c3.metric(f"{team_b} 赢",  f"{p_b_win:.1%}")

st.subheader("最可能的比分")
for (a, b), p in top.items():
    st.write(f"{a}  :  {b}  —  {p:.1%}")

st.subheader("完整比分概率表")

disp = table.copy()                       # 复制一份专门用来显示，不动原表
disp.index = range(len(disp))             # 行标签换成 0,1,2…
disp.columns = range(len(disp.columns))   # 列标签换成 0,1,2…
disp.index.name = team_a                  # 队名提到左上角当轴标题
disp.columns.name = team_b
st.dataframe((disp * 100).round(1))       # 显示成百分数，保留一位