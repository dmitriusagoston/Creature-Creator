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
    weight = 0
    # Temp - creature temperature viability
    temp = 0
    # Weather - creature weather viability
    weather = 0
    # Terrain - creature terrain viability
    terrain = 0
    # Flora - creature ability to consume flora
    flora = 0
    # Predator - creature ability to survive predetors
    predator = 0
    # Prey - creature ability to hunt prey  
    prey = 0
    # Defense - creature amount of defense features
    defense = 0
    # Offense - creature amount of offense features
    offense = 0
    # Adaptation - creature amount of adaptation features
    adaptation = 0
    # Caloric - creature caloric features
    caloric = 0

    # Get features from tree
    defensive_features = get_features_from_root(tree, "defensive")
    offensive_features = get_features_from_root(tree, "offensive")
    adaptation_features = get_features_from_root(tree, "adaptation")
    caloric_features = get_features_from_root(tree, "caloric")

    defensive_feature_names = [f.name for f in defensive_features]
    offensive_feature_names = [f.name for f in offensive_features]
    adaptation_feature_names = [f.name for f in adaptation_features]
    caloric_feature_names = [f.name for f in caloric_features]

    # Complexity
    complexity = len(creature.features)

    # Weight
    weight = creature.weight

    # Temp
    min_temp = creature.temp[0]
    max_temp = creature.temp[1]
    '''
    add this later to mutate function, make it more complex to edit both max and min temp depending on the feature

    min_temp_mod = sum([temp for temp in creature.features["temp"] if creature.features["temp"] < 0])
    max_temp_mod = sum([temp for temp in creature.features["temp"] if creature.features["temp"] > 0])
    min_temp += min_temp_mod
    max_temp += max_temp_mod
    '''
    underheat = max(0, creature.temp[0] - env.temp[0])**2
    overheat = max(0, env.temp[1] - creature.temp[1])**2
    temp -= underheat #/ creature.cold_resistance - ask gillian about this (bio major)
    temp -= overheat #/ creature.heat_resitance

    # Weather - potentially remove later
    cur_weather = None
    # snow case
    if env.weather[1] > 5 and env.temp[1] <= 32:
        cur_weather = "snow"
    elif env.weather[1] > 5 and env.temp[0] > 32:
        cur_weather = "rain"
    else:
        cur_weather = "clear"
    weather = 0 

    # Terrain
    for feature in creature.features:
        cur_f = tree.get_node_by_name(feature.name)
        if 'terrain' in cur_f.conditions:
            terrain += sum(terrain in cur_f.conditions['terrain'] for terrain in env.terrain)

    # Flora
            
    # Need to fix!!!!!!

    for feature in creature.features:
        cur_f = tree.get_node_by_name(feature.name)
        for i in range(1,4):
            if 'flora' in cur_f.conditions:
                flora += i*sum(flora in cur_f.conditions['flora'] for flora in env.flora)
            # flora += i*sum(flora in feature["flora"]["tier"+str(i)] for flora in env.flora)
        
        # flora += sum(flora in feature["flora"]["tier1"] for flora in env.flora)
        # flora += 2*sum(flora in feature["flora"]["tier2"] for flora in env.flora)
        # flora += 3*sum(flora in feature["flora"]["tier3"] for flora in env.flora)

    # Predator
    survivability = []
    countered_features = []
    for f in creature.features:
        cur_f = tree.get_node_by_name(f.name)
        if 'predator' in cur_f.conditions:
            countered_features.extend(cur_f.conditions['predator'])
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
    success = []
    countered_features = []
    for f in creature.features:
        cur_f = tree.get_node_by_name(f.name)
        if 'prey' in cur_f.conditions:
            countered_features.extend(cur_f.conditions['prey'])
    for prey in env.prey:
        cur_p = prey_objs[prey]
        cur_win = 0.0
        cur_lose = 0.0
        for feature in [f for f in cur_p.features if f in defensive_feature_names]:
            if feature in countered_features:
                cur_win += 1.0
            else:
                cur_lose += 1.0
        success.append(cur_win / (cur_win + cur_lose))
    
    max_prey = max(success)
    avg_prey = np.mean(success)
    std_prey = np.std(success)
    
    # Defense
    defense += len([feature for feature in creature.features if feature in defensive_feature_names])

    # Offense
    offense += len([feature for feature in creature.features if feature in offensive_feature_names])

    # Adaptation
    adaptation += len([feature for feature in creature.features if feature in adaptation_feature_names])

    # Caloric
    caloric += len([feature for feature in creature.features if feature in caloric_feature_names])


    return {"complexity": complexity,
            "weight": weight,
            "temp": temp,
            "weather": weather,
            "terrain": terrain,
            "flora": flora,
            "predator": predator,
            "max_prey": max_prey,
            "avg_prey": avg_prey,
            "std_prey": std_prey,
            "defense": defense,
            "offense": offense,
            "adaptation": adaptation,
            "caloric": caloric
            }