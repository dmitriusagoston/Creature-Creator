import random
import numpy as np
from metrics import metrics

class creature:
    def __init__(self, name="TEST", weight=80, temp=[69, 79], features={}, fitness=None):
        self.name = name
        self.weight = weight
        self.temp = temp
        self.features = features
        self.fitness = fitness

    def __str__(self):
        return f"Name: {self.name}, Weight: {self.weight}, Temp: {self.temp}, Features: {self.features}, Fitness: {self.fitness}"

    def calculate_fitness(self, env, tree, pred_objs, prey_objs):
        measurements = metrics(creature=self, env=env, tree=tree, pred_objs=pred_objs, prey_objs=prey_objs)

        coefficients = dict(
            complexity=1.0,
            weight=1.0,
            temp=1.0,
            terrain=1.0,
            flora=1.0,
            predator=1.0,
            max_prey=1.0,
            avg_prey=1.0,
            std_prey=1.0,
            defense=1.0,
            offense=1.0,
            adaptation=1.0,
        )

        self.fitness = sum(map(lambda m: coefficients[m] * measurements[m], coefficients))

    def get_fitness(self, env, tree, pred_objs, prey_objs):
        if self.fitness is None:
            return self.calculate_fitness(env, tree, pred_objs, prey_objs)
        return self.fitness
    

    # add random probability weighted based on creature fitnesses (maybe add weights to creatures)

    def mutate(self, env, root, rate=0.1):
        mutation_rate = rate

        r = random.random()

        node = root
        if r <= mutation_rate:
            while node.children:
                node = random.choice(node.children) # weight first iteration here
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
                    else:
                        self.mutate(env, root, rate=1)
    

        