from dataclasses import dataclass


@dataclass
class Feature:
    text: str
    x: int
    y: int

    def __str__(self):
        return f"({self.text}, ({self.x}, {self.y}))"


def sort_features_A(features: list[Feature], tol=100) -> list[Feature]:
    """
    Sorts a list of Feature objects in reading order.
    Assumes higher y means higher on the page (top).
    Groups features into rows if their y coordinates are within a tolerance,
    then sorts each row by x coordinate (left-to-right).
    """
    # Sort features by y descending (top to bottom)
    features_sorted = sorted(features, key=lambda f: f.y, reverse=True)
    rows = []
    current_row = []
    current_y = None

    for f in features_sorted:
        if current_y is None:
            current_y = f.y
            current_row.append(f)
        elif abs(f.y - current_y) <= tol:
            current_row.append(f)
        else:
            current_row = sorted(current_row, key=lambda f: f.x)

            rows.append(current_row)
            current_row = [f]
            current_y = f.y

    if current_row:
        current_row = sorted(current_row, key=lambda f: f.x)
        rows.append(current_row)

    # Flatten the list of rows into a single list
    sorted_features = [f for row in rows for f in row]
    return sorted_features


def sort_features_B(
    features: list[Feature],
    expected_rows: int = 3,
    expected_cols: int = 4,
    tol_y: int = 100,
    tol_x: int = 20,
) -> list[Feature]:
    """
    Organizes a list of Feature objects into a grid (row-major order) with expected_rows and expected_cols.
    Features are grouped into rows by comparing their y coordinates (within tol_y) and then each row is sorted
    by x coordinate. For each row, if a cell is missing (i.e. no Feature is found close to the expected x position),
    a None is inserted.
    """
    # 1. Sort features by y descending (higher y means top of the page)
    features_sorted = sorted(features, key=lambda f: f.y, reverse=True)

    # 2. Group features into rows
    rows = []
    current_row = []
    current_y = None
    for f in features_sorted:
        if current_y is None or abs(f.y - current_y) <= tol_y:
            current_row.append(f)
            if current_y is None:
                current_y = f.y
        else:
            rows.append(current_row)
            current_row = [f]
            current_y = f.y
    if current_row:
        rows.append(current_row)

    # 3. Ensure we have exactly expected_rows: trim or add empty rows.
    if len(rows) > expected_rows:
        rows = rows[:expected_rows]
    elif len(rows) < expected_rows:
        for _ in range(expected_rows - len(rows)):
            rows.append([])

    # 4. Process each row to align features into expected_cols.
    grid = []
    for row in rows:
        # Sort the row by x ascending (left-to-right)
        row_sorted = sorted(row, key=lambda f: f.x)
        if row_sorted:
            min_x = row_sorted[0].x
            max_x = row_sorted[-1].x
            # If there's only one feature, assume expected positions all equal min_x.
            if len(row_sorted) == 1:
                expected_positions = [min_x] * expected_cols
            else:
                step = (max_x - min_x) / (expected_cols - 1)
                expected_positions = [min_x + i * step for i in range(expected_cols)]
        else:
            expected_positions = [None] * expected_cols

        # For each expected column position, try to find a feature in row_sorted within tol_x.
        new_row = []
        used = set()  # we'll store the id of each Feature to avoid duplicates
        for exp_x in expected_positions:
            found = None
            if exp_x is not None:
                for f in row_sorted:
                    if id(f) in used:
                        continue
                    if abs(f.x - exp_x) <= tol_x:
                        found = f
                        used.add(id(f))
                        break
            new_row.append(found)
        # If the row has fewer than expected_cols, pad with None.
        while len(new_row) < expected_cols:
            new_row.append(None)
        grid.append(new_row)

    # 5. Flatten the grid into a single list (row-major order)
    flat_list = [cell for row in grid for cell in row]
    return flat_list


#############################
# REAL EXAMPLE INPUTS
#############################

# From image_01.json where numbers_1 text="4" is missing in row=1 col=4
times_1 = [
    Feature(text="10:47 PM", x=331, y=3808),
    Feature(text="10:13 PM", x=306, y=2788),
    Feature(text="10:29 PM", x=1734, y=3816),
    Feature(text="10:08 PM", x=1718, y=2780),
    Feature(text="9:51 PM", x=290, y=1759),
    Feature(text="9:48 PM", x=1710, y=1743),
    Feature(text="10:26 PM", x=3171, y=3818),
    Feature(text="10:02 PM", x=3163, y=2772),
    Feature(text="9:46 PM", x=3154, y=1733),
    Feature(text="10:23 PM", x=4599, y=3793),
    Feature(text="10:01 PM", x=4615, y=2762),
    Feature(text="9:43 PM", x=4607, y=1725),
]
numbers_1 = [
    Feature(text="1", x=132, y=3736),
    Feature(text="5", x=107, y=2723),
    Feature(text="2", x=1519, y=3744),
    Feature(text="6", x=1511, y=2714),
    Feature(text="9", x=83, y=1685),
    Feature(text="10", x=1494, y=1668),
    Feature(text="3", x=2963, y=3752),
    Feature(text="7", x=2947, y=2698),
    Feature(text="11", x=2939, y=1668),
    Feature(text="8", x=4400, y=2698),
    Feature(text="12", x=4400, y=1643),
]
registers_1 = [
    Feature(text="Drive Through", x=1129, y=3711),
    Feature(text="Drive Through", x=1104, y=2681),
    Feature(text="Drive Through", x=2548, y=3719),
    Feature(text="Drive Through", x=2548, y=2673),
    Feature(text="Drive Through", x=1095, y=1643),
    Feature(text="Drive Through", x=2540, y=1643),
    Feature(text="Drive Through", x=3993, y=3702),
    Feature(text="Drive Through", x=3993, y=2665),
    Feature(text="Drive Through", x=3985, y=1627),
    Feature(text="Drive Through", x=5413, y=3677),
    Feature(text="Drive Through", x=5421, y=2656),
    Feature(text="In-Store", x=5421, y=1618),
]
totals_1 = [
    Feature(text=11.8, x=1021, y=2971),
    Feature(text=6.12, x=2507, y=2954),
    Feature(text=6.98, x=1054, y=1933),
    Feature(text=12.12, x=2455, y=1913),
    Feature(text=6.77, x=1045, y=894),
    Feature(text=21.0, x=2449, y=863),
    Feature(text=10.83, x=3843, y=2939),
    Feature(text=5.36, x=3943, y=1909),
    Feature(text=0.0, x=3943, y=855),
    Feature(text=12.56, x=5338, y=2930),
    Feature(text=12.12, x=5338, y=1901),
    Feature(text=0.0, x=5371, y=863),
]

# From image_15.json where time text="3:02 PM" in row = 2 col = 2
time_15 = [
    Feature(text="3:08 PM", x=323, y=3817),
    Feature(text="3:07 PM", x=1726, y=3835),
    Feature(text="3:02 PM", x=307, y=2797),
    Feature(text="2:52 PM", x=290, y=1768),
    Feature(text="2:51 PM", x=1718, y=1758),
    Feature(text="3:06 PM", x=3171, y=3834),
    Feature(text="2:55 PM", x=3162, y=2779),
    Feature(text="2:50 PM", x=3154, y=1740),
    Feature(text="3:05 PM", x=4607, y=3809),
    Feature(text="2:52 PM", x=4616, y=2780),
    Feature(text="2:48 PM", x=4615, y=1732),
]

numbers_15 = [
    Feature(text="169", x=116, y=3744),
    Feature(text="170", x=1519, y=3760),
    Feature(text="174", x=1502, y=2723),
    Feature(text="173", x=99, y=2723),
    Feature(text="177", x=91, y=1693),
    Feature(text="178", x=1494, y=1685),
    Feature(text="171", x=2955, y=3760),
    Feature(text="175", x=2947, y=2706),
    Feature(text="179", x=2939, y=1677),
    Feature(text="172", x=4400, y=3736),
    Feature(text="176", x=4408, y=2706),
    Feature(text="180", x=4400, y=1660),
]
registers_15 = [
    Feature(text="In-Store", x=1129, y=3727),
    Feature(text="Drive Through", x=1104, y=2698),
    Feature(text="Drive Through", x=2548, y=3727),
    Feature(text="Delivery", x=2532, y=2681),
    Feature(text="Drive Through", x=1095, y=1660),
    Feature(text="Delivery", x=2523, y=1652),
    Feature(text="Delivery", x=3985, y=3719),
    Feature(text="Drive Through", x=3993, y=2681),
    Feature(text="Drive Through", x=3993, y=1635),
    Feature(text="Drive Through", x=5421, y=3694),
    Feature(text="Delivery", x=5404, y=2665),
    Feature(text="Delivery", x=5404, y=1627),
]
totals_15 = [
    Feature(text=0.0, x=1062, y=2979),
    Feature(text=11.37, x=2465, y=2971),
    Feature(text=7.98, x=1053, y=1932),
    Feature(text=14.18, x=2456, y=1931),
    Feature(text=13.64, x=1004, y=904),
    Feature(text=6.77, x=2490, y=879),
    Feature(text=0.0, x=3960, y=2972),
    Feature(text=0.0, x=3943, y=1925),
    Feature(text=6.98, x=3943, y=863),
    Feature(text=19.32, x=5338, y=2947),
    Feature(text=7.47, x=5388, y=1917),
    Feature(text=4.06, x=5371, y=870),
]


def print_outputs(
    times: list[Feature],
    numbers: list[Feature],
    registers: list[Feature],
    totals: list[Feature],
):
    print("Time Features (should be decreasing):")
    for f in times:
        print(f)
    print("\nTransaction Number Features (should be increasing):")
    for f in numbers:
        print(f)
    print("\nRegister Features:")
    for f in registers:
        print(f)
    print("\nTotal Features:")
    for f in totals:
        print(f)


if __name__ == "__main__":
    """
    Most images of the computer screen (taken with my iphone) look like this:
    ____________________
    [txt][txt][txt][txt]
    [txt][txt][txt][txt]
    [txt][txt][txt][txt]
    ____________________
    where the "[txt]" is a graphical box on the screen that holds all the info (features) for each transaction
    
    But look like this:
    ____________________
    [txt][txt][txt][txt]
    [txt][txt]
    
    ____________________
    where we have less graphical boxes bc were at the butt end of the transaction-logs for the day.
    
    So, in each [txt] graphical-area, features like total and transaction number are right next to each other.
    The image-to-text tool we used seemingly grabed the text from the whole image at random.
    My current method is to conceptually impose rows and columns into the image and use the proximitt of the 
    coordinates to associate them with eachother. But I cant get it to work.
    - Ryan
    """
    times_1 = sort_features_A(times_1)
    numbers_1 = sort_features_A(numbers_1)
    registers_1 = sort_features_A(registers_1)
    totals_1 = sort_features_A(totals_1)
    print_outputs(times_1, numbers_1, registers_1, totals_1)
