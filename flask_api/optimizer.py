from pulp import LpProblem, LpVariable, lpSum, LpMinimize, LpInteger, LpStatus, value
import math

def solve_adjustment(base_price, role_names, role_counts, popularity,
                     integer_only=True, max_adj=None, min_adj=None,
                     popularity_levels=None):
    max_adj = max_adj if max_adj is not None else base_price * 0.3
    min_adj = min_adj if min_adj is not None else -base_price * 0.3
    epsilon = 1 if integer_only else 1e-2

    # 人气度映射表（按比例）
    level_bounds = {
        '+++': (0.15, 0.30),
        '++': (0.05, 0.20),
        '+': (-0.05, 0.10),
        '-': (-0.10, 0.05),
        '--': (-0.5, -0.20),
        '---': (-0.15, -0.30)
    }

    prob = LpProblem("AnimeGoodsPriceAdjustment_OptimalOnly", LpMinimize)

    adj_vars = {}
    abs_vars = {}

    for name in role_names:
        if popularity_levels and name in popularity_levels:
            level = popularity_levels[name]
            min_b, max_b = level_bounds[level]
            lb = base_price * min_b
            ub = base_price * max_b
        else:
            lb = min_adj
            ub = max_adj

        adj_vars[name] = LpVariable(
            f"adj_{name}",
            lowBound=math.ceil(lb) if integer_only else lb,
            upBound=math.floor(ub) if integer_only else ub,
            cat=LpInteger if integer_only else "Continuous"
        )
        abs_vars[name] = LpVariable(
            f"abs_{name}",
            lowBound=0,
            cat=LpInteger if integer_only else "Continuous"
        )

    # 绝对值关联
    for name in role_names:
        prob += abs_vars[name] >= adj_vars[name]
        prob += abs_vars[name] >= -adj_vars[name]

    # 至少一个调价非零
    prob += lpSum([abs_vars[name] for name in role_names]) >= epsilon

    # 人气排序约束（仍需满足顺序递减）
    for i in range(len(popularity) - 1):
        higher = popularity[i]
        lower = popularity[i + 1]
        delta = LpVariable(f"delta_{higher}_{lower}",
                           lowBound=epsilon,
                           cat=LpInteger if integer_only else "Continuous")
        prob += adj_vars[higher] >= adj_vars[lower] + delta

    # 总价差值变量（目标函数变量）
    total_original = base_price * sum(role_counts[r] for r in role_names)
    total_adjusted = lpSum((base_price + adj_vars[r]) * role_counts[r] for r in role_names)

    surplus = LpVariable("surplus_diff", lowBound=0,
                         cat=LpInteger if integer_only else "Continuous")

    prob += total_adjusted == total_original + surplus
    prob += surplus  # Objective: minimize surplus

    # 求解
    status = prob.solve()

    if LpStatus[status] != "Optimal":
        return []

    return [{
        "adjustments": {r: round(value(adj_vars[r])) if integer_only else value(adj_vars[r]) for r in role_names},
        "final_total": sum((base_price + value(adj_vars[r])) * role_counts[r] for r in role_names),
        "diff": value(surplus)
    }]
