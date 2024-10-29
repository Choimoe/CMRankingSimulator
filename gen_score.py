import random
import json

with open('table.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

rewards_mean = config["rewards_mean"]
rewards_sigma = config["rewards_sigma"]


def get_reward(rank):
    """
    根据排名返回奖励的标准分和比赛分。
    比赛分按照正态分布随机生成。
    """
    std_points, match_points_mean = rewards_mean[str(rank)]
    match_points_sigma = rewards_sigma[str(rank)]
    match_points = random.normalvariate(match_points_mean, match_points_sigma)
    return std_points, match_points
