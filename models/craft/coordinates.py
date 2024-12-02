def parse_coordinates(data):
    lines = data.strip().split("\n") 
    coordinates = []

    for line in lines:
        if not line.strip(): 
            continue
        values = list(map(int, line.split(",")))
        points = [(values[i], values[i + 1]) for i in range(0, len(values), 2)]
        coordinates.append(points)

    return coordinates


def group_by_y_coordinates(coords, y_threshold):
    coords_sorted = sorted(coords, key=lambda c: c[0][1]) 
    grouped = []
    current_group = []

    for coord in coords_sorted:
        if not current_group:
            current_group.append(coord)
        else:
            if len(grouped) == 4: 
                current_group.append(coord)
            else:
                prev_y = current_group[-1][0][1]
                curr_y = coord[0][1]
                if abs(curr_y - prev_y) <= y_threshold:
                    current_group.append(coord)
                else:
                    grouped.append(current_group)
                    current_group = [coord]

    if current_group:
        grouped.append(current_group)

    if len(grouped) > 5:
        extra_data = []
        for extra_group in grouped[5:]:
            extra_data.extend(extra_group)
        grouped = grouped[:5] 
        grouped[4].extend(extra_data) 

    return grouped



def assign_regions(grouped_coords):
    regions = ["주민등록증", "이름", "주민번호", "주소", "발급정보"]
    region_dict = {region: [] for region in regions}

    for i, group in enumerate(grouped_coords):
        if i < len(regions):
            region_dict[regions[i]] = group

    return region_dict

coordinate_data = """
38,14,169,14,169,40,38,40
34,58,166,58,166,79,34,79
22,89,182,89,182,108,22,108
13,118,118,117,118,135,13,137
120,117,197,117,197,136,120,136
13,133,64,133,64,148,13,148
69,133,121,133,121,149,69,149
124,134,177,134,177,148,124,148
13,148,65,148,65,166,13,166
66,149,175,149,175,166,66,166
146,176,180,176,180,189,146,189
188,176,206,176,206,189,188,189
212,177,232,177,232,189,212,189
76,194,247,194,247,214,76,214
"""

coordinates = parse_coordinates(coordinate_data) 
grouped_coords = group_by_y_coordinates(coordinates, y_threshold=15)
regions = assign_regions(grouped_coords) 

for region, coords in regions.items():
    print(f"{region}: {coords} : {len(coords)}")
