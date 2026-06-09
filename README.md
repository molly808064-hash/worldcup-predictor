# 世界杯比分预测 ⚽

基于历史比赛数据和**泊松分布（Poisson distribution）**，预测 2026 世界杯参赛球队之间的比分概率。
通过一个简单的 [Streamlit](https://streamlit.io/) 网页界面，选择对阵双方，即可看到胜平负概率、最可能的比分以及完整的比分概率表。

## 原理

1. 从历史比赛数据中，筛选出 2026 世界杯参赛球队在 **2022 年以后**的所有对阵记录。
2. 计算每支球队的**场均进球数** λ（lambda）。
3. 用泊松分布 `P(进 k 球) = poisson.pmf(k, λ)` 估算双方各进 0~6 球的概率。
4. 把两队的进球概率相乘，得到每种比分的联合概率，进而汇总出胜 / 平 / 负的概率。

## 运行

需要 Python 3.11+。

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run app.py
```

启动后浏览器会自动打开界面：

- 在两个下拉框中分别选择 **A 队**和 **B 队**
- 页面会展示：
  - **胜平负**概率（三个并排的大数字）
  - **最可能的 5 个比分**
  - **完整比分概率表**（A 队 0~6 球 × B 队 0~6 球）

## 项目结构

```
worldcup-predictor/
├── app.py              # 主程序：Streamlit 界面 + 泊松模型
├── data/
│   └── results.csv     # 历史比赛数据（约 49000 场）
└── README.md
```

> 说明：仓库中的 `data/model.py`、`data/explore.py`、`test/` 目录及若干 `test*.txt`
> 是学习与测试过程中的草稿/无效数据，与正式功能无关。

## 数据来源

历史比赛数据来自 Kaggle / GitHub 上的公开数据集
[**International football results from 1872 to present**](https://github.com/martj42/international_results)（作者 martj42），
收录了 1872 年至今的国际足球赛事记录。

`data/results.csv` 的字段：

| 字段 | 含义 |
| --- | --- |
| `date` | 比赛日期 |
| `home_team` / `away_team` | 主队 / 客队 |
| `home_score` / `away_score` | 主队 / 客队进球数 |
| `tournament` | 赛事名称 |
| `city` / `country` | 比赛城市 / 国家 |
| `neutral` | 是否中立场地 |

## 局限性

- 模型只用**场均进球数**这一个指标，未考虑主客场、防守强度、近期状态、伤病等因素。
- 数据样本为 2022 年后的对阵，部分球队样本量较小，结果仅供娱乐参考。
