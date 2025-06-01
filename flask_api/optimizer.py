from pulp import LpProblem, LpVariable, lpSum, LpMinimize, LpInteger, LpStatus, value
import math

def solve_multiple_adjustments(base_price, role_names, role_counts, popularity,
                              integer_only=True, max_adj=None, min_adj=None, max_solutions=10):
    max_adj = max_adj if max_adj is not None else base_price * 0.3
    min_adj = min_adj if min_adj is not None else -base_price * 0.3
    epsilon = 1 if integer_only else 1e-2

    solutions = []
    tried_solutions = set()

    for attempt in range(max_solutions):
        prob = LpProblem(f"AnimeGoodsPriceAdjustment_{attempt}", LpMinimize)

        adj_vars = {
            name: LpVariable(
                f"adj_{name}_{attempt}",
                lowBound=math.ceil(min_adj) if integer_only else min_adj,
                upBound=math.floor(max_adj) if integer_only else max_adj,
                cat=LpInteger if integer_only else "Continuous"
            )
            for name in role_names
        }

        abs_vars = {
            name: LpVariable(
                f"abs_{name}_{attempt}",
                lowBound=0,
                cat=LpInteger if integer_only else "Continuous"
            )
            for name in role_names
        }

        # 绝对值关联
        for name in role_names:
            prob += abs_vars[name] >= adj_vars[name]
            prob += abs_vars[name] >= -adj_vars[name]

        # 至少一个调价非零
        prob += lpSum([abs_vars[name] for name in role_names]) >= epsilon

        # 人气排序约束
        for i in range(len(popularity) - 1):
            higher = popularity[i]
            lower = popularity[i + 1]
            delta = LpVariable(f"delta_{higher}_{lower}_{attempt}",
                               lowBound=epsilon,
                               cat=LpInteger if integer_only else "Continuous")
            prob += adj_vars[higher] >= adj_vars[lower] + delta

        # 总价控制
        total_original = base_price * sum(role_counts[r] for r in role_names)
        total_adjusted = lpSum((base_price + adj_vars[r]) * role_counts[r] for r in role_names)

        if integer_only:
            prob += total_adjusted >= total_original
            prob += total_adjusted - total_original
        else:
            prob += total_adjusted == total_original
            prob += lpSum(abs_vars[r] for r in role_names)

        # 加入“与已知解不同”的约束
        for sol in tried_solutions:
            prob += lpSum([adj_vars[r] != val for r, val in zip(role_names, sol)]) >= 1

        status = prob.solve()

        if LpStatus[status] != "Optimal":
            break

        current_solution = tuple(round(value(adj_vars[r])) for r in role_names)
        if current_solution in tried_solutions:
            break
        tried_solutions.add(current_solution)

        solutions.append({
            "adjustments": {r: round(value(adj_vars[r])) if integer_only else value(adj_vars[r]) for r in role_names},
            "final_total": sum((base_price + value(adj_vars[r])) * role_counts[r] for r in role_names),
            "diff": sum((base_price + value(adj_vars[r])) * role_counts[r] for r in role_names) - total_original
        })

    return solutions