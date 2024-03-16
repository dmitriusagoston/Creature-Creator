import numpy as np

def get_features_from_root(root, type):
    '''
    This function takes in a root node and a type and returns a list of features of that type

    Parameters:
    root (Node): A node object
    type (str): A string representing the type of feature to return
    '''
    features = []
    for child in root.children:
        if child.name == type:
            for ffg in child.children:
                features.extend(ffg.children)
    return features

def metrics(creature, env, tree, pred_objs, prey_objs):
    '''
    This function takes in a creature and environment and returns a set of metrics

    Parameters:
    creature (Creature): A creature object
    env (Environment): An environment object
    '''

    # Weights

    # Complexity - number of creature parts
    complexity = 0
    # Weight - creature weight
    heavy = 0
    light = 0
    # Temp - creature temperature viability
    temp = 0
    # Terrain - creature terrain viability
    terrain = 0
    # Flora - creature ability to consume flora
    flora = 0
    # Predator - creature ability to survive predetors
    predator = 0
    # Prey - creature ability to hunt prey  
    prey_v = 0
    # Defense - creature amount of defense features
    defense = 0
    # Offense - creature amount of offense features
    offense = 0
    # Adaptation - creature amount of adaptation features
    adaptation = 0

    # Get features from tree
    defensive_features = get_features_from_root(tree, "defensive")
    offensive_features = get_features_from_root(tree, "offensive")
    adaptation_features = get_features_from_root(tree, "adaptation")

    defensive_feature_names = [f.name for f in defensive_features]
    offensive_feature_names = [f.name for f in offensive_features]
    adaptation_feature_names = [f.name for f in adaptation_features]

    # Complexity
    complexity = sum(creature.features.values())

    simplicity = 40 - len(creature.features) // 2

    less = 40 - complexity // 2

    # Weight
    heavy = creature.weight // 10
    light = 16 - (creature.weight // 10)

    # Temp - rework
    min_temp = creature.temp[0]
    max_temp = creature.temp[1]
    
    # add this later to mutate function, make it more complex to edit both max and min temp depending on the feature

    min_temp_mod = 0
    max_temp_mod = 0
    for feature in creature.features:
        cur_f = tree.get_node_by_name(feature.name)
        if "temperature" in cur_f.conditions:
            min_temp_mod += cur_f.conditions["temperature"][0]
            max_temp_mod += cur_f.conditions["temperature"][1]
    min_temp += min_temp_mod * 15
    max_temp += max_temp_mod * 15
    
    underheat = max(0, min_temp - env.temp[0])
    overheat = max(0, env.temp[1] - max_temp)
    temp -= underheat / 10
    temp -= overheat / 10

    # Terrain
    for feature in creature.features:
        cur_f = tree.get_node_by_name(feature.name)
        if 'terrain' in cur_f.conditions:
            terrain += sum(terrain in cur_f.conditions['terrain'] for terrain in env.terrain)
            terrain -= sum(terrain not in cur_f.conditions['terrain'] for terrain in env.terrain)

    # Flora
    tiers_f = [0, 0, 0]
    total_f = [0, 0, 0]
    for plant, tier in env.flora.items():
        total_f[tier - 1] += 1
    for feature, val in creature.features.items():
        cur_f = tree.get_node_by_name(feature.name)
        if 'flora' in cur_f.conditions:
            tier = cur_f.conditions['flora'][0] - 1
            tiers_f[tier] += val
    for tier in range(3):
        flora += min(total_f[tier], tiers_f[tier]) * (tier + 1)

    # Predator
    survivability = []
    countered_features = []
    for f in creature.features:
        cur_f = tree.get_node_by_name(f.name)
        if 'counters' in cur_f.conditions:
            countered_features.extend(cur_f.conditions['counters'])
    for predator in env.predators:
        cur_p = pred_objs[predator]
        cur_win = 0.0
        cur_lose = 0.0
        for feature in [f for f in cur_p.features if f in offensive_feature_names]:
            if feature in countered_features:
                cur_win += 1.0
            else:
                cur_lose += 1.0
        survivability.append(cur_win / (cur_win + cur_lose))
    predator = sum(survivability) / len(survivability)

    # Prey
    success = {}
    countered_features = []
    for f in creature.features:
        cur_f = tree.get_node_by_name(f.name)
        if 'exploits' in cur_f.conditions:
            countered_features.extend(cur_f.conditions['exploits'])
    for prey in env.prey:
        cur_p = prey_objs[prey]
        cur_win = 0.0
        cur_lose = 0.0
        for feature in [f for f in cur_p.features if f in defensive_feature_names]:
            if feature in countered_features:
                cur_win += 1.0
            else:
                cur_lose += 1.0
        success[prey] = cur_win / (cur_win + cur_lose)
    for prey, val in env.prey.items():
        prey_v += val * success[prey]
        
    max_prey = max(success.values())
    avg_prey = np.mean(list(success.values()))
    std_prey = np.std(list(success.values()))
    
    for feature, val in creature.features.items():
        if feature.name in defensive_feature_names:
            defense += val
        elif feature.name in offensive_feature_names:
            offense += val
        elif feature.name in adaptation_feature_names:
            adaptation += val


    # Realistic
    realistic = 0
    even = ["arm", "leg", "thumb", "antler", "eye", "wings", "ear"]
    single = ["mouth", "horns", "spine", "tail"]
    for feature, val in creature.features.items():
        cur = feature.name
        if cur in even and val % 2 == 0:
            realistic += 5
            # 4 case
            if cur in ["leg", "wings"]:
                # insect case
                if creature.weight < 1:
                    if cur == "wings" and val > 4:
                        realistic -= val - 4
                    else:
                        realistic += 5
                    if cur == "leg":
                        realistic += val
                else:
                    realistic -= max(0, val - 4)
                    if cur == "wings" and val >= 4:
                        realistic -= 5
                    # centaur case
                    arm = tree.get_node_by_name("arm")
                    if arm in creature.features:
                        if cur == "leg" and val == 4 and creature.features[arm] >= 2:
                            realistic -= 5
                        elif cur == "leg" and val == 4 and creature.features[arm] < 2:
                            realistic += 5
                    if cur == "wings" and val == 2:
                        realistic += 5
            # 2 case
            else:
                realistic -= max(0, val - 2)
        elif cur in single:
            if val == 1:
                realistic += 5
            else:
                realistic -= val - 1
    

    return {"complexity": complexity,
            "simplicity": simplicity,
            "less": less,
            "heavy": heavy,
            "light": light,
            "temp": temp,
            "terrain": terrain,
            "flora": flora,
            "predator": predator,
            "prey": prey_v,
            "max_prey": max_prey,
            "avg_prey": avg_prey,
            "std_prey": std_prey,
            "defense": defense,
            "offense": offense,
            "adaptation": adaptation,
            "realistic": realistic
            }