import numpy as np
import pandas as pd
import pulp

def haversine_km(lat1, lon1, lat2, lon2):
    """Straight-line distance (km) given in degrees."""
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = (np.sin((lat2 - lat1) / 2) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2)
    return 6371 * 2 * np.arcsin(np.sqrt(a))

class RebalancingProblem:
    def __init__(self, flow, min_imbalance=2):
        flow = flow.dropna(subset=["lat", "lon"]).copy()
        flow["bikes"] = flow["net"].round().astype(int)

        self.supply = flow[flow["bikes"] >= min_imbalance].set_index("station_id")
        self.demand = flow[flow["bikes"] <= -min_imbalance].set_index("station_id")
        self.demand["bikes"] = -self.demand["bikes"]

        self.dist = pd.DataFrame(
            haversine_km(self.supply["lat"].values[:, None],
                         self.supply["lon"].values[:, None],
                         self.demand["lat"].values[None, :],
                         self.demand["lon"].values[None, :]),
            index=self.supply.index,
            columns=self.demand.index,
        )
        self.total = int(min(self.supply["bikes"].sum(), self.demand["bikes"].sum()))

    def solve_optimal(self):
        prob = pulp.LpProblem("bike_rebalancing", pulp.LpMinimize)

        x = {}
        for i in self.supply.index:
            for j in self.demand.index:
                x[i, j] = pulp.LpVariable(f"x_{i}_{j}", lowBound=0)

        prob += pulp.lpSum(self.dist.at[i, j] * x[i, j] for (i, j) in x)

        for i in self.supply.index:
            prob += pulp.lpSum(x[i, j] for j in self.demand.index) <= self.supply.at[i, "bikes"]

        for j in self.demand.index:
            prob += pulp.lpSum(x[i, j] for i in self.supply.index) <= self.demand.at[j, "bikes"]

        prob += pulp.lpSum(x.values()) == self.total

        prob.solve(pulp.PULP_CBC_CMD(msg=False))
        print("Solver status:", pulp.LpStatus[prob.status])

        moves = [(i, j, var.value()) for (i, j), var in x.items() if var.value() > 0.5]
        return self._to_frame(moves)

    def solve_greedy(self):
        still_needed = self.demand["bikes"].to_dict()
        moves = []
        for i in self.supply.index:
            spare = int(self.supply.at[i, "bikes"])
            for j in self.dist.loc[i].sort_values().index:
                if spare == 0:
                    break
                k = min(spare, still_needed[j])
                if k > 0:
                    moves.append((i, j, k))
                    still_needed[j] -= k
                    spare -= k
        return self._to_frame(moves)

    def _to_frame(self, moves):
        df = pd.DataFrame(moves, columns=["from_id", "to_id", "bikes"])
        df["bikes"] = df["bikes"].round().astype(int)
        df["from_name"] = df["from_id"].map(self.supply["station_name"])
        df["to_name"] = df["to_id"].map(self.demand["station_name"])
        df["km"] = [self.dist.at[i, j] for i, j in zip(df["from_id"], df["to_id"])]
        df["bike_km"] = df["bikes"] * df["km"]
        return df