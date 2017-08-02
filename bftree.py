def make_tree(tree, branch_factor, filler=' ', cage=True,
              return_as_list=False, print_out=True):
    '''
    Given an array, tree, this function will display it as a breadth-first
    tree.

    Parameters:
    tree - The array to create the tree from
    branch_factor - The number of branches each node will have
    filler - (default ' ') Is the character that will be placed in the filler
             areas on either side of the numbers
    cage - (default True) If true, will add some ascii art surronding the tree
           with hyphens, pips and plus signs like a cage
    return_as_list - (default False) If true, will return the rows as strings
                     as elements of a list if True
    print_out - (default True) If true, will print out each row as it's found
    '''
    rows, num_nodes = [], 0

    # Find number of max digits in the list. If it's an even number, pump it
    # up by one to conserve symmetry
    num_digits = len(str(max(tree)))
    if not num_digits % 2:
        num_digits += 1

    # Find how many levels (i.e. rows) there are to the tree
    i = 0
    levels = 0
    while i < len(tree):
        i += branch_factor**levels
        levels += 1

    # How many characters the last row will take up
    max_spaces = branch_factor**(levels - 1) * (num_digits + 1)

    # Printing of cage (i.e. the hyphens, pips and plus signs)
    if cage:
        row = '+' + (max_spaces - 1) * '-' + '+'
        if print_out:
            print(row)
        if return_as_list:
            rows.append(row)

    # Run through each row
    for row_num in range(levels):
        row_len = branch_factor**row_num
        num_nodes += row_len

        # Check if row will be partially or completely filled
        if len(tree) < num_nodes:
            column_iter = len(tree) + row_len - num_nodes
        else:
            column_iter = row_len

        # Find number of buffer spaces for each node box
        num_spaces = row_len * (num_digits + 1)
        num_extra_spaces = max_spaces - num_spaces
        num_spaces_per_node = num_extra_spaces // (2 * row_len)
        spaces_per_node = num_spaces_per_node * filler

        # Throw that stuff together
        row = ''
        for num in range(column_iter):
            shift = num + sum([branch_factor**r for r in range(row_num)])
            row += '|' + spaces_per_node + \
                str(tree[shift]).rjust(num_digits) + spaces_per_node

        row += '|'
        if print_out:
            print(row)
        if return_as_list:
            rows.append(row)

        # More cage printing
        if cage:
            row = '+' + (len(row) - 2) * '-' + '+'
            if print_out:
                print(row)
            if return_as_list:
                rows.append(row)

    if return_as_list:
        return rows


if __name__ == "__main__":
    import random
    arr = [random.randint(0, 100) for _ in range(35)]

    make_tree(arr, 3)
