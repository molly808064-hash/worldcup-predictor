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

    # overall_avg：原有算法，全部比赛（含中立场）
    hs = df_wc.groupby("home_team")["home_score"].sum()
    as_ = df_wc.groupby("away_team")["away_score"].sum()
    hg = df_wc.groupby("home_team").size()
    ag = df_wc.groupby("away_team").size()
    overall_avg = hs.add(as_, fill_value=0) / hg.add(ag, fill_value=0)

    # home_avg / away_avg：只用非中立场比赛
    # reindex 到全部队伍：没有非中立主（客）场记录的队（如 Ghana、Haiti）场次记 0，
    # 落入下面的兜底分支，同时避免 KeyError
    MIN_GAMES = 5  # 样本低于此场次时回退用 overall_avg
    teams = overall_avg.index
    non_neutral = df_wc[~df_wc["neutral"]]
    home_goals = non_neutral.groupby("home_team")["home_score"].sum().reindex(teams, fill_value=0)
    home_games = non_neutral.groupby("home_team").size().reindex(teams, fill_value=0)
    away_goals = non_neutral.groupby("away_team")["away_score"].sum().reindex(teams, fill_value=0)
    away_games = non_neutral.groupby("away_team").size().reindex(teams, fill_value=0)

    # 0 场时除法产生 NaN，但场次 < MIN_GAMES 必被 where 换成 overall_avg
    home_avg = (home_goals / home_games).where(home_games >= MIN_GAMES, overall_avg)
    away_avg = (away_goals / away_games).where(away_games >= MIN_GAMES, overall_avg)

    result = pd.DataFrame({
        "home_avg": home_avg,
        "away_avg": away_avg,
        "overall_avg": overall_avg,
    })
    result.index.name = "team"  # 索引是队名，沿用 groupby 残留的 home_team 名会误导
    return result


# ---- 模型函数：纯函数，只负责由两个进球期望算出比分概率矩阵 ----
# 用哪个均值（主/客/中立的场地逻辑）由调用处决定，队名仅用于行列标签
def score_matrix(team_a, team_b, lam_a, lam_b, max_goals=6):
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
venue = st.selectbox("场地", ["中立场", f"{team_a} 主场", f"{team_b} 主场"])

# 场地逻辑：home_avg / away_avg 在 load_avg_scores 里已做过样本量回退
if venue == f"{team_a} 主场":
    lam_a = avg_scores.loc[team_a, "home_avg"]
    lam_b = avg_scores.loc[team_b, "away_avg"]
elif venue == f"{team_b} 主场":
    lam_a = avg_scores.loc[team_a, "away_avg"]
    lam_b = avg_scores.loc[team_b, "home_avg"]
else:  # 中立场
    lam_a = (avg_scores.loc[team_a, "home_avg"] + avg_scores.loc[team_a, "away_avg"]) / 2
    lam_b = (avg_scores.loc[team_b, "home_avg"] + avg_scores.loc[team_b, "away_avg"]) / 2

table = score_matrix(team_a, team_b, lam_a, lam_b)
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