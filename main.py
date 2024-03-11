import json
import random
import numpy as np
from metrics import metrics
from creature_tree import tree_build
from creature import creature
from environment import environment

def load_creatures(filename):
    preds = {}
    prey = {}
    with open(filename) as f:
        static_creatures = json.load(f)
    for p in static_creatures['predators']:
        cur_p = static_creatures['predators'][p]
        preds[p] = creature(name=p, weight=cur_p['weight'], features=cur_p['features'])
    for p in static_creatures['prey']:
        cur_p = static_creatures['prey'][p]
        prey[p] = creature(name=p, weight=cur_p['weight'], features=cur_p['features'])
    return preds, prey

def load_environments(filename):
    envs = {}
    with open(filename) as f:
        environments = json.load(f)
    for e in environments['environments']:
        cur_e = environments['environments'][e]
        cur_temp = [cur_e['temperature']['min'], cur_e['temperature']['max']]
        cur_weather = [cur_e['weather']['min'], cur_e['weather']['max']]
        cur_flora = []
        for i in range(1,4):
            cur_flora.extend(cur_e['flora']['tier'+str(i)])
        cur_prey = []
        for i in range(1,4):
            cur_prey.extend(cur_e['fauna']['prey']['tier'+str(i)])
        cur_predators = cur_e['fauna']['predator']
        envs[e] = environment(name=e, 
                              temp=cur_temp, 
                              weather=cur_weather, 
                              terrain=cur_e['terrain'], 
                              flora=cur_flora, 
                              prey=cur_prey, 
                              predators=cur_predators)
    return envs

def generate_successors(creatures):
    results = []

    [individual.fitness(env, root, pred_objs, prey_objs) for individual in creatures]

    # Elitism
    keep = 10
    best = sorted(creatures, key=lambda creature: creature.fitness, reverse=True)
    best = best[:keep]
    results.extend(best)

    # Truncate
    for creature in best[1:]:
        results.append(generate_children(creature, best[0]))
    
    # Roulette Wheel
    spins = 80
    for _ in range(spins):
        selection = random.choices(creatures, [max(0, ind.fitness) for ind in creatures], k=2)
        results.append(generate_children(selection[0], selection[1]))

    return results
        
def generate_children(parent1, parent2):
    crossover_i = random.randint(0, min(len(parent1.features), len(parent2.features)))
    child = creature(name=parent1.name, weight=np.mean([parent1.weight, parent2.weight]), features=parent1.features[:crossover_i] + parent2.features[crossover_i:], fitness=0.0)
    return child.mutate(env, root)

if __name__ == "__main__":
    global prey_objs, pred_objs, env, root
    static_predators, static_prey = load_creatures('creatures.json')
    envs = load_environments('environments.json')
    env = envs['forest']
    root = tree_build()
    pred_objs = static_predators
    prey_objs = static_prey

    test_dude = static_predators['big_dude']
    m = metrics(creature=test_dude, 
                env=env, 
                tree=root, 
                pred_objs=static_predators, 
                prey_objs=static_prey)
    print(m)
    