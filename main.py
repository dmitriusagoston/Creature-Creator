import json
import random
import numpy as np
import sys
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
        cur_flora = {}
        for i in range(1,4):
            for f in cur_e['flora']['tier'+str(i)]:
                cur_flora[f] = i
        cur_prey = {}
        for i in range(1,4):
            for p in cur_e['fauna']['prey']['tier'+str(i)]:
                cur_prey[p] = i
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

    [individual.get_fitness(env, root, pred_objs, prey_objs, heavyness, complexness, realness) for individual in creatures]

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
        selection = random.choices(creatures, [max(0.01, ind.fitness) for ind in creatures], k=2)
        results.append(generate_children(selection[0], selection[1]))

    return results
        
def generate_children(parent1, parent2):
    crossover_i = random.randint(0, min(len(parent1.features), len(parent2.features)))
    keys_parent1 = set(parent1.features.keys())
    keys_parent2 = set(parent2.features.keys())
    
    # Select a subset of keys common to both parents
    common_keys = keys_parent1.intersection(keys_parent2)
    crossover_keys = random.sample(list(common_keys), k=min(len(common_keys), min(len(keys_parent1), len(keys_parent2))//2))

    child_f = {}
    
    # Combine genetic material from both parents
    for key in keys_parent1.union(keys_parent2):
        if key in crossover_keys:
            if key in parent2.features:
                val = parent2.features[key]
            else:
                val = parent1.features[key]
            child_f[key] = parent2.features.get(key, val)
        else:
            if key in parent1.features:
                val = parent1.features[key]
            else:
                val = parent2.features[key]
            child_f[key] = parent1.features.get(key, val)
    
    # child = creature(name=parent1.name, weight=np.mean([parent1.weight, parent2.weight]), features=parent1.features[:crossover_i] + parent2.features[crossover_i:], fitness=None)
    child = creature(name=parent1.name, weight=np.mean([parent1.weight, parent2.weight]), features=child_f)
    child.mutate(env, root, pred_objs, prey_objs, heavyness, complexness, realness, rate=0.9)
    return child

if __name__ == "__main__":
    print("Welcome to Creature Creator!\n")
    print("This program uses a genetic algorithm to evolve creatures that are well adapted to their environment.\n")
    print("Please choose an environment from the following list:")

    global prey_objs, pred_objs, env, root, heavyness, complexness, realness
    static_predators, static_prey = load_creatures('creatures.JSON')
    envs = load_environments('environments.JSON')

    for e in envs:
        print(f"{e} ")
    enviro = input("Please enter the name of the environment you would like to use: ")
    while enviro not in envs:
        print("Invalid environment\n")
        enviro = input("Please enter the name of the environment you would like to use: ")
    env = envs[enviro]

    root = tree_build()
    pred_objs = static_predators
    prey_objs = static_prey

    print("Keep in mind the larger scores will affect the extremity of the creature's other factors\n")
    heavyness = input("How heavy should the creature be? (1-10): ")
    while not heavyness.isdigit() or int(heavyness) < 1 or int(heavyness) > 10:
        print("Invalid input\n")
        heavyness = input("How heavy should the creature be? (1-10): ")
    heavyness = int(heavyness)

    complexness = input("How complex should the creature be? (1-10): ")
    while not complexness.isdigit() or int(complexness) < 1 or int(complexness) > 10:
        print("Invalid input\n")
        complexness = input("How complex should the creature be? (1-10): ")
    complexness = int(complexness)

    realness = input("How much should the creature resemble known animals? (1-10): ")
    while not realness.isdigit() or int(realness) < 1 or int(realness) > 10:
        print("Invalid input\n")
        realness = input("How much should the creature resemble known animals? (1-10): ")
    realness = int(realness)

    print("Generating initial population...\n")

    population = [creature() for _ in range(100)]
    generation = 0
    try:
        while generation < 300:
            generation += 1
            next_population = generate_successors(population)
            population = next_population
            if generation % 50 == 0 and generation != 0 and generation < 300:
                [individual.get_fitness(env, root, pred_objs, prey_objs, heavyness, complexness, realness) for individual in population]
                best = sorted(population, key=lambda creature: creature.fitness, reverse=True)[0]
                best.name = "Gen" + str(generation)
                sys.stdout.write('\r' + ' ' * 50)
                sys.stdout.write("\rBest Creature:\n")
                sys.stdout.write("Generation: " + str(generation) + "\n")
                sys.stdout.write("Weight: " + str(best.weight) + "\n")
                sys.stdout.write("Features: " + str(best.features) + "\n")
                # sys.stdout.flush()
                print("\n")
            sys.stdout.write('\rCurrent Generation: {}'.format(generation))
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass

    [individual.get_fitness(env, root, pred_objs, prey_objs, heavyness, complexness, realness) for individual in population]
    best = sorted(population, key=lambda creature: creature.fitness, reverse=True)[0]
    sys.stdout.write('\r' + ' ' * 50)
    sys.stdout.write("\rFINAL Best Creature:\n")
    sys.stdout.write("Weight: " + str(best.weight) + "\n")
    sys.stdout.write("Features: " + str(best.features) + "\n")
    sys.stdout.write("Fitness: " + str(best.scores) + "\n")


    