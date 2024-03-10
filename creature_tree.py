import json

class Node:
    def __init__(self, parent=None, name=None, is_feature=False):
        self.parent = parent
        self.name = name
        self.children = []
        self.conditions = []
        self.is_feature = is_feature

    def is_feature(self):
        return self.is_feature

    def __repr__(self) -> str:
        return f'{self.name}'

    def tree_to_string(self, horizon=1, indent=0):
        # return structure of tree
        string = ''.join(['| ' for i in range(indent)]) + str(self) + '\n'
        if horizon > 0:
            for child in self.children:
                string += child.tree_to_string(horizon, indent + 1)
        return string

    # def add_children(self, childs):
    #     self.children.extend(childs)


def tree_build():
    # json file data location
    features_filename = 'features.json'
    biomes_filename = 'environments.json'

    # grab json data
    with open(features_filename) as f:
        features = json.load(f)

    with open(biomes_filename) as f:
        biomes = json.load(f)

    # start of tree
    root = Node(name="root")
    # sub categories for root node
    feature_groupings = ["defensive", "offensive", "adaptation", "caloric"]
    # feature function groupings
    ffg = ["remove", "limbs", "torso", "head", "skin", "misc"]
    # adding categories to root
    for grouping in feature_groupings:
        new_group = Node(parent=root, name=grouping)
        root.children.append(new_group)

    # adding feature locations/function groupings
    for child in root.children:
        # add feature function grouping to categories
        for grouping in ffg:
            new_group = Node(parent=child, name=grouping)
            child.children.append(new_group)
            parts = features[child.name][grouping]
            for key, val in parts.items():
                feature_node = Node(parent=new_group, name=key)
                feature_node.conditions = val
                new_group.children.append(feature_node)


    return root

if __name__ == '__main__':
    tree = tree_build()
    print(tree.tree_to_string())
    

    