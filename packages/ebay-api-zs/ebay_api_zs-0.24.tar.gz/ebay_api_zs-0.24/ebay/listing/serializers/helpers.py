def aspects_to_representation(aspects: list) -> dict:
    representation = dict()
    for aspect in aspects:
        name = aspect["name"]
        if name in representation:
            representation[name].append(aspect["value"])
        else:
            representation[name] = [aspect["value"]]
    return representation
