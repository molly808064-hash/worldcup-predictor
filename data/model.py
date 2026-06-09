# from scipy.stats import poisson

# poisson.pmf(goals, lam) 是主角。pmf 全称 probability mass function,概率质量函数,
# 你就理解成一句话:"在平均 lam 的前提下,正好发生 goals 次的概率"


# 一支场均 1.8 球的队（先用图里那个数字，验证我们没写错）
# lam = 1.8

# 算它单场进 0~6 球的概率
# for goals in range(7):              # range(7) 生成 0,1,2,3,4,5,6（不含 7）
#     p = poisson.pmf(goals, lam)
#     print(f"进 {goals} 球: {p:.1%}")
# {p:.1%} 是格式化:把小数(0.298)显示成百分比、保留一位小数(29.8%),看着清爽。
# lam 这个名字是惯例,希腊字母 λ(lambda)在泊松里专指那个平均值

# lam_brazil = avg_scores["Brazil"]       # 取巴西的真实场均进球
# print(f"巴西的 λ = {lam_brazil:.2f}")

# for goals in range(7):
#     p = poisson.pmf(goals, lam_brazil)
#     print(f"巴西进 {goals} 球: {p:.1%}")

# import pandas as pd
# from scipy.stats import poisson

# # ---- 数据层：读、清、筛、算平均 ----
# df = pd.read_csv("data/results.csv")
# df = df.dropna(subset=["home_score", "away_score"])
# # ...（你之前的筛选 + 算 avg_scores 的代码）...

# # ---- 模型层：泊松 ----
# lam_brazil = avg_scores["Brazil"]        # 这里能用，因为上面刚算出来，还在内存里
# for goals in range(7):
#     print(f"巴西进 {goals} 球: {poisson.pmf(goals, lam_brazil):.1%}")