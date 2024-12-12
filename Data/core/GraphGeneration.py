import pandas as pd

from ..core.Saving import get_logs

def organise_data(path):
    data = get_logs(path)
    df = pd.DataFrame(data)

    return df

def organise_sankey_data(path):
    data = get_logs(path)

    from_list = []
    to_list = []
    locations = []
    counts = {}

    for log in data:
        from_location = log["from"]
        to_location = log["to"]

        if from_location is not None and to_location is not None:
            from_list.append(from_location)
            to_list.append(to_location)

            if from_location not in locations:
                locations.append(from_location)
            if to_location not in locations:
                locations.append(to_location)

            pair = (from_location, to_location)
            if pair not in counts:
                counts[pair] = 0
            counts[pair] += 1

    location_indices = {location: index for index, location in enumerate(locations)}

    source = [location_indices[from_location] for from_location in from_list]
    target = [location_indices[to_location] for to_location in to_list]
    values = [counts[(from_location, to_location)] for from_location, to_location in zip(from_list, to_list)]

    return locations, source, target, values
