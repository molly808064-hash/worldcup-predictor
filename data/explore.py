import pandas as pd

df = pd.read_csv("data/results.csv")

# print(df.shape)    # (行数, 列数)
# print(df.head())   # 前 5 行长啥样
# print(df.info())   # 每列叫什么、是什么类型、有没有空值



# 看 home_score 和 away_score 这两行，非空数量是 49257，可总共有 49329 行。差了 72 行也就是说有 72 场比赛没有比分。
# pandas 的整数列装不下"空"(NaN),只要一列里有缺失值,它就自动把整列升级成小数类型来容纳。所以这个 float 不是数据错了,
# 是缺失值的副作用

# 只保留主客队都有比分的行
df = df.dropna(subset=["home_score", "away_score"])   
# df.dropna删除
# subset=[...] 的意思是:只看这两列,哪行在这两列里有空就删该行;其他列(比如 city)有没有空我们不管
# print(df.shape)   # 应该变成 (49257, 9)

# home_scores = df.groupby("home_team")["home_score"].sum()
# away_scores = df.groupby("away_team")["away_score"].sum()
#total_scores = home_scores + away_scores
# 在 pandas 眼里,"某个数 + 没有 = NaN"。NaN 还会传染:NaN ÷ 场次 还是 NaN
# 像 Niue 这种冷门队,历史上只当过客队、从没当过主队，于是它只出现在 away_scores 里,home_scores 里根本没有它。
# total_scores = home_scores.add(away_scores, fill_value=0)  # 缺的那边不当NaN当0算

# home_games = df.groupby("home_team").size()
# away_games = df.groupby("away_team").size()
# total_games  = home_games.add(away_games,  fill_value=0)

# avg_scores = total_scores / total_games
# print(avg_scores)
# print(avg_scores.isna().sum())   # 应该是 0

# 排个序,看谁进球最多 / 最少(最实用,用来检验逻辑对不对)
# print(avg_scores.sort_values(ascending=False).head(10))   # 场均进球最多的 10 队
# print(avg_scores.sort_values().head(10))                   # 最少的 10 队

# print(avg_scores.to_string())   # 强制把全部行都打出来，不省略，一般没必要

# 2026 世界杯 48 强（用数据里的叫法：Cape Verde / Ivory Coast / Turkey / Czech Republic）
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

# 三个筛选条件 会先生成一列 True/False,再用它把 True 的行挑出来。
recent  = df["date"] >= "2022-01-01"           # 近期
home_in = df["home_team"].isin(teams_2026)     # 主队在 48 强里
away_in = df["away_team"].isin(teams_2026)     # 客队也在 48 强里
# .isin(列表) 就是逐行问:"这个队名在我这份 48 强名单里吗?"在就 True,不在就 False

# 三个条件同时成立的行才留下
df_wc = df[recent & home_in & away_in]  #& 是"逐行取与"只有三个标签同时是 True,合并结果才是 True
# 两个必须记住的坑:
# 第一,用 &,不能用 Python 平时的 and。and 一次只能判断一个真假,而我们要对一整列几万个值逐行判断,得用 &。
# 写成 and 会直接报错。(同理"或"是 |,不是 or。)
# 第二,多个条件每个最好用括号包起来,比如 (df["date"] >= "2022-01-01") & (...)。我上面拆成了 recent、home_in 三个变量,
# 所以没写括号也清楚;但要是挤在一行里,& 的运算优先级会坑你,加括号最稳。
print(df_wc.shape)   # 应该是 (533, 9)

home_scores = df_wc.groupby("home_team")["home_score"].sum()
away_scores = df_wc.groupby("away_team")["away_score"].sum()
total_scores = home_scores.add(away_scores, fill_value=0)  # 缺的那边不当NaN当0算

home_games = df_wc.groupby("home_team").size()
away_games = df_wc.groupby("away_team").size()
total_games  = home_games.add(away_games,  fill_value=0)

avg_scores = total_scores / total_games
# print(avg_scores)
print(avg_scores.sort_values(ascending=False).round(2))   # 从高到低，保留两位小数

from scipy.stats import poisson
# lam_brazil = avg_scores["Brazil"]       # 取巴西的真实场均进球
# print(f"巴西的 λ = {lam_brazil:.2f}")

# for goals in range(7):
#     p = poisson.pmf(goals, lam_brazil)
#     print(f"巴西进 {goals} 球: {p:.1%}")

def score_matrix(team_a, team_b, avg_scores, max_goals=6):
    lam_a = avg_scores[team_a]      # A 队场均进球
    lam_b = avg_scores[team_b]      # B 队场均进球

    rows = []
    for i in range(max_goals + 1):          # A 队进 i 球
        row = []
        for j in range(max_goals + 1):      # B 队进 j 球
            p = poisson.pmf(i, lam_a) * poisson.pmf(j, lam_b)   # 相乘
            row.append(p)
        rows.append(row)

    return pd.DataFrame(
        rows,
        index=[f"{team_a} {i}" for i in range(max_goals + 1)],
        columns=[f"{team_b} {j}" for j in range(max_goals + 1)],
    )


# 用一下
table = score_matrix("Brazil", "England", avg_scores)
print((table * 100).round(1))

flat = table.stack()                                  # 把表摊平成一长列
# top = flat.sort_values(ascending=False).head(5)       # 概率从高到低取前 5
top = flat.sort_values(ascending=False).head(5)  # type: ignore # 这行我心里有数,你的类型检查跳过它
print(top.round(2))


# .stack() 把二维的表压成一列(每个格子变成一行),这样才能用你早就熟悉的 sort_values 排序,又是老朋友了。