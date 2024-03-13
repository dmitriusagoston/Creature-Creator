import random
import numpy as np
from metrics import metrics

class creature:
    def __init__(self, name="TEST", weight=80, temp=[69, 79], features=[], fitness=None):
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
            weather=1.0,
            terrain=1.0,
            flora=1.0,
            predator=1.0,
            max_prey=1.0,
            avg_prey=1.0,
            std_prey=1.0,
            defense=1.0,
            offense=1.0,
            adaptation=1.0,
            caloric=1.0
        )

        self.fitness = sum(map(lambda m: coefficients[m] * measurements[m], coefficients))

    def get_fitness(self, env, tree, pred_objs, prey_objs):
        if self.fitness is None:
            return self.calculate_fitness(env, tree, pred_objs, prey_objs)
        return self.fitness
    
    def mutate(self, env, root):
        mutation_rate = 0.9

        r = random.random()

        node = root
        if r <= mutation_rate:
            while node.children:
                node = random.choice(node.children)
                if node.name == "remove" and len(self.features) != 0:
                    self.features.remove(random.choice(self.features))
                elif not node.children:
                    self.features.append(node)
    

        