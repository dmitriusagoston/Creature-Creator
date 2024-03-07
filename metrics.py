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


def metrics(creature, env, tree):
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

    # Weather
    weather = env.weather

    # Terrain
    terrain = env.terrain

    # Flora
    flora = env.flora

    # Predator
    predator = env.predator

    # Prey
    prey = env.prey

    # Defense
    defense += len([feature for feature in creature.features if feature in defensive_features])

    # Offense
    offense += len([feature for feature in creature.features if feature in offensive_features])

    # Adaptation
    adaptation += len([feature for feature in creature.features if feature in adaptation_features])

    # Caloric
    caloric += len([feature for feature in creature.features if feature in caloric_features])


    return {"complexity": complexity, }