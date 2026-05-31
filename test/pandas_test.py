import pandas as pd

df = pd.read_csv("matches.csv")

print(df)
# print(df["home_goals"])
# print(df["home_goals"].sum()/len(df))         #是pandas的写法，但是Python的库，适配度高，相像
# print(df.groupby("home_team")["home_goals"].mean())   #按主队分堆,每堆的主场进球,各算个平均给我（mean（）是主队）
print(df.groupby("home_team")["home_goals"].sum())
home_goals = df.groupby("home_team")["home_goals"].sum()
away_goals = df.groupby("away_team")["away_goals"].sum()
total_goals = home_goals + away_goals  #pandas自动设计，按队名自动对齐

home_games = df.groupby("home_team").size()    #数每组有几行，当了几次主队
away_games = df.groupby("away_team").size()    ##当了几次客队
total_games = home_games + away_games          #总共踢了几场

avg_goals = total_goals / total_games
print(avg_goals)