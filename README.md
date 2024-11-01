# CMRankingSimulator - 国标麻将比赛排名计算模拟器

A Chinese Mahjong Match Ranking Simulator.
国标麻将比赛排名计算模拟。

## Usage

`clone` 下来然后 `python` 运行即可

```git
git clone https://github.com/Choimoe/CMRankingSimulator.git
cd CMRankingSimulator
pip install -r requirements.txt
python main.py
```

## Input

输入在 `data.json` 中：

```json
{
    "initial_scores": [
        {"name": "A", "标准分": 9, "比赛分": 588},
        {"name": "B", "标准分": 5, "比赛分": -71},
        {"name": "C", "标准分": 5, "比赛分": -153},
        {"name": "D", "标准分": 4, "比赛分": 95},
        {"name": "E", "标准分": 4, "比赛分": -17},
        {"name": "F", "标准分": 4, "比赛分": -102},
        {"name": "G", "标准分": 3, "比赛分": -23},
        {"name": "H", "标准分": 1, "比赛分": -357}
    ],
    "waiting_list": [
        ["D", "E", "G", "H"]
    ],
    "top_k": 4
}
```

其中：
- `initial_scores` 表示目前选手名字、标准分、比赛分；
- `waiting_list` 表示目前等待进行的桌；
- `top_k` 表示晋级取前多少名次。

## Output

会输出模拟的次数、必定晋级的最低标准分、能够晋级的最低标准分、每个玩家进入前 `top_k` 名的概率、以及具体的顺位概率信息。

```
模拟次数：100000

=====================
必定晋级的最低标准分：5
能够晋级的最低标准分：5

=====================
每个玩家进入前4名的概率：
A:  100.00%
B:  86.99%
D:  74.94%
E:  71.45%
G:  49.91%
C:  14.93%
H:  1.78%

=====================
玩家名称：模拟顺位        (1)   (2)   (3)   (4)   (5)   (6)   (7)   (8) 
A       :  1.00  (    100.00%    0.00%    0.00%    0.00%    0.00%    0.00%    0.00%    0.00%   )
D       :  3.49  (    0.00%    36.45%    33.43%    5.05%    2.81%    15.08%    6.39%    0.79%   )
E       :  3.91  (    0.00%    33.60%    25.85%    12.00%    3.98%    1.22%    15.77%    7.59%   )
B       :  3.89  (    0.00%    0.00%    24.08%    62.92%    13.01%    0.00%    0.00%    0.00%   )
C       :  5.05  (    0.00%    0.00%    0.00%    14.93%    65.15%    19.92%    0.00%    0.00%   )
F       :  6.70  (    0.00%    0.00%    0.00%    0.00%    0.76%    35.94%    56.01%    7.28%   )
G       :  4.59  (    0.00%    29.95%    16.56%    3.41%    4.64%    14.42%    21.83%    9.20%   )
H       :  7.37  (    0.00%    0.00%    0.08%    1.70%    9.65%    13.42%    0.00%    75.14%   )
```

## Advanced

在 `settings.json` 中 `num_simulations` 记录模拟的次数。防止执行时间过长，模拟过程超过 `max_time` 秒后会截断。

```json
{
    "num_simulations": 1000,
    "max_time": 60
}
```

在 `table.json` 中记录模拟比赛分的数据，使用了雀渣的[统计数据](https://www.tziakcha.xyz/statistic/)，以正态分布 `normalvariate` 来拟合，下文中 `rewards_mean` 与 `rewards_sigma` 表示正态分布的均值与标准差。

```json
{
    "rewards_mean": {
        "0": [4, 160.8561],
        "1": [2, 35.7374],
        "2": [1, -51.1230],
        "3": [0, -145.4544]
    },
    "rewards_sigma": {
        "0": 50,
        "1": 20,
        "2": 30,
        "3": 40
    }
}
```

