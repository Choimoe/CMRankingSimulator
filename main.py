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
avg_std_score = 0
sim_records = []

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

    # 记录本次模拟每名玩家的标准分与是否进入前K
    top_four_names = set(p['name'] for p in top_four)
    sim_record = {}
    for p in result:
        sim_record[p['name']] = {'标准分': p['标准分'], 'in_topk': (p['name'] in top_four_names)}
    sim_records.append(sim_record)

    # noinspection PyTypeChecker
    must_std_score = max(top_four[top_k - 1]['标准分'], must_std_score)
    avg_std_score += top_four[top_k - 1]['标准分']
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

result = []

result.append(f"模拟次数：{num_simulations}")

result.append("\n=====================")
result.append(f"必定晋级的最低标准分：{must_std_score}")
result.append(f"能够晋级的最低标准分：{min_std_score}")
avg_std_score /= num_simulations
result.append(f"平均晋级的最低标准分：{avg_std_score: .2f}")

# # 打印最终结果
# result.append("\n=====================")
# result.append("模拟结果：")
# for result, count in sorted_result:
#     res = sorted(result, key=lambda x: (x[1]), reverse=True)
#     result.append(f"Result: {res} - Count: {count}")

# 计算并打印每个玩家进入前四名的概率

result.append("\n=====================")
sorted_top_four = sorted(top_four_counts.items(), key=lambda x: x[1], reverse=True)
result.append(f"每个玩家进入前{top_k}名的概率：")
for name, count in sorted_top_four:
    probability = count / num_simulations * PERCENT
    result.append(f"{name}: {probability: .3f}%")

result.append("\n=====================")
result.append("\n每名玩家的晋级门限（基于剩余对局需获得的标准分增量）：")
player_must_gain = {}
player_possible_gain = {}
player_names = [p['name'] for p in initial_scores]
initial_std_map = {p['name']: p['标准分'] for p in initial_scores}
actual_simulations = len(sim_records)

if actual_simulations == 0:
    for name in player_names:
        player_must_gain[name] = None
        player_possible_gain[name] = None
        result.append(f"{name}：必定需得分：无，能够得分：无（无模拟）")
else:
    total_players = len(player_names)
    for name in player_names:
        initial = initial_std_map[name]
        # 能够晋级时，在那些模拟中本玩家需要获得的增量（最终-初始）
        gains_in_top = [rec[name]['标准分'] - initial for rec in sim_records if rec[name]['in_topk']]
        if gains_in_top:
            possible_gain = max(0, min(gains_in_top))
        else:
            possible_gain = None

        # 如果 top_k >= 总玩家数，则任何人都直接晋级
        if top_k >= total_players:
            must_gain = 0
        else:
            required_gains = []
            for rec in sim_records:
                # 其他玩家在该模拟下的最终标准分
                others = [rec[player_name]['标准分'] for player_name in rec.keys() if player_name != name]
                # 如果其他玩家不足 top_k，则不需要额外分
                if len(others) < top_k:
                    required_gains.append(0)
                    continue
                # 找到其他玩家中第 top_k 高的标准分（0-based index top_k-1）
                others_sorted = sorted(others, reverse=True)
                threshold_std = others_sorted[top_k - 1]
                # 要超过该阈值才能保证进入前K（严格大于），因此需要的增量为 threshold_std - initial + 1
                req_gain = max(0, threshold_std - initial + 1)
                required_gains.append(req_gain)
            must_gain = max(required_gains) if required_gains else None

        player_must_gain[name] = must_gain
        player_possible_gain[name] = possible_gain
        result.append(f"{name}：必定需得分：{must_gain if must_gain is not None else '无'}，能够得分：{possible_gain if possible_gain is not None else '无'}")


print(" ".join(result))

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

with open('result.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(result) + "\n")
    f.write(" ".join(header) + "\n")
    for row in output_matrix:
        f.write(" ".join(row) + "\n")
