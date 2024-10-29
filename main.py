import random
from collections import defaultdict, Counter
import wcwidth
import time
import json

from gen_score import get_reward

with open('data.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

initial_scores = config["initial_scores"]
waiting_list = config["waiting_list"]
top_k = config["top_k"]

with open('settings.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

num_simulations = config["num_simulations"]
max_time = config["max_time"]
count_per_iter = config["count_per_iter"]
space_len_min = config["space_len_min"]

TABLE_PLAYER = 4
MAX_STD_SCORE = 1000000
MIN_STD_SCORE = 0
PERCENT = 100


def simulate_match(players_list, specified_participants=None):
    if specified_participants:
        participants = [player for player in players_list if player['name'] in specified_participants]
        if len(participants) != TABLE_PLAYER:
            raise ValueError("必须指定恰好四名选手")
    else:
        participants = random.sample(players_list, TABLE_PLAYER)

    # 随机分配名次
    random.shuffle(participants)

    # 更新分数
    for rank, player in enumerate(participants):
        std_points, match_points = get_reward(rank)
        player['标准分'] += std_points
        player['比赛分'] += match_points

    return players_list


# 执行模拟
start_time = time.time()
result_counts = defaultdict(int)
top_four_counts = Counter()
rank_counts = defaultdict(lambda: defaultdict(int))
min_std_score = MAX_STD_SCORE
must_std_score = MIN_STD_SCORE

for _ in range(num_simulations):
    # 模拟前重置分数
    players = [player.copy() for player in initial_scores]
    # 比赛模拟
    result = []
    for matches in waiting_list:
        result = simulate_match(players, matches)

    result_tuple = tuple((player['name'], player['标准分']) for player in result)

    # 统计该结果出现的次数
    result_tuple_sorted = sorted(result_tuple, key=lambda x: x[1], reverse=True)

    result_counts[tuple(result_tuple_sorted)] += 1
    # 统计进入前四名的次数
    top_four = sorted(result, key=lambda x: (x['标准分'], x['比赛分']), reverse=True)[:top_k]
    for player in top_four:
        top_four_counts[player['name']] += 1
        min_std_score = min(min_std_score, player['标准分'])

    # noinspection PyTypeChecker
    must_std_score = max(top_four[top_k - 1]['标准分'], must_std_score)
    # 统计选手的所有排名
    ranks = sorted(result, key=lambda x: (x['标准分'], x['比赛分']), reverse=True)
    rank_count = 0
    for player in ranks:
        rank_count += 1
        rank_counts[player['name']][rank_count] += 1
        rank_counts[player['name']]['total_score'] += rank_count

    # 每 count_per_iter 统计时间，超过 max_time 进行截断
    if (_ + 1) % count_per_iter == 0:
        elapsed_time = time.time() - start_time
        if elapsed_time > max_time:
            print(f"超过截止时间 {max_time} 秒，进行夹断（已进行 {_ + 1} 次模拟）。")
            num_simulations = _ + 1
            break

items = list(result_counts.items())


def sort_key(item):
    return tuple(sorted(item[0], key=lambda x: x[0]))


sorted_items = sorted(items, key=sort_key)

sorted_result = [(tuple(key), value) for key, value in sorted_items]

print(f"模拟次数：{num_simulations}")

print("\n=====================")
print(f"必定晋级的最低标准分：{must_std_score}")
print(f"能够晋级的最低标准分：{min_std_score}")

# # 打印最终结果
# print("\n=====================")
# print("模拟结果：")
# for result, count in sorted_result:
#     res = sorted(result, key=lambda x: (x[1]), reverse=True)
#     print(f"Result: {res} - Count: {count}")

# 计算并打印每个玩家进入前四名的概率

print("\n=====================")
sorted_top_four = sorted(top_four_counts.items(), key=lambda x: x[1], reverse=True)
print(f"每个玩家进入前{top_k}名的概率：")
for name, count in sorted_top_four:
    probability = count / num_simulations * PERCENT
    print(f"{name}: {probability: .2f}%")

print("\n=====================")
output_matrix = []
all_ranks = set()
# 收集所有出现过的排名
for details in rank_counts.values():
    all_ranks.update([rank for rank in details.keys() if isinstance(rank, int)])

# 将所有排名排序
all_ranks = sorted(all_ranks)

max_len = space_len_min
for player in initial_scores:
    max_len = max(max_len, len(player['name']))

# 输出内容
for player, details in rank_counts.items():
    average_rank = details['total_score'] / num_simulations
    current_width = sum(wcwidth.wcswidth(c) for c in player)
    row = [f"{player + ' ' * (max_len + space_len_min - current_width)}: {average_rank: .2f}", ' ( ']
    for rank in all_ranks:
        row.append(f" {(details[rank] / num_simulations * PERCENT): .2f}% ")
    row.append(' )')
    output_matrix.append(row)

header = ["玩家名称：模拟顺位      "] + [f" ({rank}) " for rank in all_ranks]
print(" ".join(header))

for row in output_matrix:
    print(" ".join(row))
