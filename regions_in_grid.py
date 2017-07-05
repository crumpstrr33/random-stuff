def find_connected(n, m, n_max, m_max):
    '''
    Finds the (at most 8) nodes surrounding a given node in a 2D array.

    Params:
    n - The x coordinate of the node
    m - The y coordinate of the node
    '''
    coords = []
    for i in range(3):
        for j in range(3):
            x = n - 1 + i
            y = m - 1 + j
            if 0 <= x <= n_max and 0 <= y <= n_max:
                coords.append((x, y))

    return coords


def find_regions(grid):
    '''
    Given a 2D array, of 1's and 0's, a dict will be created whose values
    contains each region of the array where a region is a section of the array
    of ones that are connected vertically, horizontally or diagonally.

    Parameters:
    grid - The 2D array to find the regions for
    '''
    rows = len(grid)
    regions = {}
    ones = []

    # Get coords of every 1
    for n in range(len(grid)):
        for m in range(len(grid[n])):
            if grid[n][m] == 1:
                ones.append((n, m))

    # For each one found, find every one that is connected to it
    for one in ones:
        connected = find_connected(*one, rows, len(grid[one[0]]))
        connected_in_ones = list(filter(lambda x: x in ones, connected))

        regions[one] = connected_in_ones + [one]

    # Consolidate dict
    while True:
        tmp_regions = {}
        change = 0
        # Travel through the dictionary
        for init_coord, coords in regions.items():
            decreasing_dict = False
            # If init_coord is in a value of the new dict, add init_coord and
            # init_coord's values to this value in the new dict
            for other_init_coord, other_coords in tmp_regions.items():
                if init_coord in other_coords or len(list(filter(lambda x: x in other_coords, coords))):
                    for coord in coords:
                        if coord not in tmp_regions[other_init_coord]:
                            tmp_regions[other_init_coord].append(coord)
                    change += 1
                    decreasing_dict = True
                    break
            # If not, just add this init_coord and it's values to the new dict
            if not decreasing_dict:
                tmp_regions[init_coord] = coords
        # End the loop if we don't decrease the new dict size
        if not change:
            return [list(set(coords)) for coords in regions.values()]
        else:
            regions = tmp_regions