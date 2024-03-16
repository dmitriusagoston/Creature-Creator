import random
import numpy as np
from metrics import metrics

class creature:
    def __init__(self, name="TEST", weight=80, temp=[69, 79], features={}, fitness=None, scores=None):
        self.name = name
        self.weight = weight
        self.temp = temp
        self.features = features
        self.fitness = fitness
        self.scores = scores

    def __str__(self):
        return f"Name: {self.name}, Weight: {self.weight}, Temp: {self.temp}, Features: {self.features}, Fitness: {self.fitness}"

    def calculate_fitness(self, env, tree, pred_objs, prey_objs, heavyness, complexness, realness):
        measurements = metrics(creature=self, env=env, tree=tree, pred_objs=pred_objs, prey_objs=prey_objs)
        heavy, light = 0, 0
        if heavyness > 5:
            heavy = float(heavyness)
            light = float(10 - heavyness)
        else:
            light = float(10 - heavyness)
            heavy = float(heavyness)

        simple, complex = 0, 0
        if complexness > 5:
            complex = float(complexness)
            simple = float(10 - complexness)
        else:
            simple = float(10 - complexness)
            complex = float(complexness)

        coefficients = dict(
            complexity=complex,
            simplicity=simple,
            less=7.0,
            heavy=heavy + 2,
            light=light + 2,
            temp=2.0,
            terrain=2.0,
            flora=1.0,
            predator=1.0,
            prey=1.0,
            max_prey=1.0,
            avg_prey=1.0,
            std_prey=1.0,
            defense=1.0,
            offense=1.0,
            adaptation=0.5,
            realistic=float(realness)
        )
        self.scores = measurements

        # Calculate the median
        median_val = np.median(list(measurements.values()))

        # Calculate the mean absolute deviation
        mad = np.mean(np.abs(np.array(list(measurements.values())) - median_val))

        # Normalize the data using the MAD
        normalized_data = {key: (value - median_val) / mad for key, value in measurements.items()}

        norm = self.min_max_normalize(measurements)
        # self.scores = norm
        # self.fitness = sum(map(lambda m: coefficients[m] * norm[m], coefficients))
        self.fitness = sum(map(lambda m: coefficients[m] * measurements[m], coefficients))

    def min_max_normalize(self, weights):
        min_val = min(weights.values())
        max_val = max(weights.values())
        range_val = max_val - min_val
        normalized_weights = {key: (value - min_val) / range_val for key, value in weights.items()}
        return normalized_weights

    def get_fitness(self, env, tree, pred_objs, prey_objs, heavyness, complexness, realness):
        if self.fitness is None:
            return self.calculate_fitness(env, tree, pred_objs, prey_objs, heavyness, complexness, realness)
        return self.fitness
    

    # add random probability weighted based on creature fitnesses (maybe add weights to creatures)

    def mutate(self, env, root, pred_objs, prey_objs, heavyness, complexness, realness, rate=0.9):
        mutation_rate = rate

        r = random.random()
        node = root
        if r <= mutation_rate:
            if random.random() < 0.1:
                self.weight += self.weight * random.uniform(-0.5, 0.12)
                return
            self.get_fitness(env, root, pred_objs, prey_objs, heavyness, complexness, realness)
            weights = [self.scores["defense"], self.scores["offense"], self.scores["adaptation"]]
            total = sum(weights)
            if total == 0:
                weights = [1, 1, 1]
            else:
                weights = [total - weights[0], total - weights[1], total - weights[2]]
            node = random.choices(node.children, weights)[0]
            while node.children:
                node = random.choice(node.children)
                if node.name == "remove" and len(self.features) != 0:
                    to_remove = random.choice(list(self.features.keys()))
                    self.features[to_remove] -= 1
                    if self.features[to_remove] == 0:
                        del self.features[to_remove]
                elif not node.children and node.name != "remove":
                    if node in self.features.keys() and node.conditions["multiple"] == True:
                        self.features[node] += 1
                    elif node not in self.features:
                        self.features[node] = 1
                    # else:
                        # self.mutate(env, root, rate=1)
            self.fitness = None
    

        