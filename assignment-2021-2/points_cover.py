import sys
from itertools import groupby, combinations, chain, product


def create_points(filename):
    points = []
    with open(filename) as points_file:
        for line in points_file:
            if line.endswith('\n'):
                x, y = line[:-1].split(' ')
            else:
                x, y = line.split(' ')
            points.append((int(x), int(y)))
    return points


def print_results(lines):
    for line in lines:
        if len(line) == 1:
            x, y = line[0]
            print(line[0], (x+1, y))
            continue

        for point in line:
            print(point, end=" ")
        print()


# Checks if the line of the given points has already been found previously.
def check(lines, point_1, point_2):
    for line in lines:
        if point_1 in line and point_2 in line:
            return True
    return False


def line_equation(point_1, point_2):
    x1, y1 = point_1
    x2, y2 = point_2

    slope = float('inf')
    intercept = x1
    if x2 - x1 != 0:
        slope = (y2 - y1)/(x2 - x1)
        intercept = y1 - x1*slope

    return slope, intercept


def point_belongs(slope, intercept, point):
    x, y = point

    if slope == float('inf'): # perpendicular line
        if intercept == x:
            return True
        else :
            return False

    return y == x*slope + intercept


def powerset(lines):
    return chain.from_iterable(combinations(lines, n) for n in range(1, len(lines) + 1))


def create_groups(points, num):
    sorted_points = sorted(points, key=lambda x: x[num])
    return groupby(sorted_points, lambda x: x[num])


def sort_points_per_line(lines):
    sorted_lines = []
    for line in lines:
        sorted_lines.append(sorted(line, key=lambda x: x[0]))
    return sorted_lines


def find_lines(lines, points, num):
    groups = create_groups(points, num)

    for key, group in groups:
        lines.append(list(group))


def find_minimun_num_of_lines(lines, points):
    line_subsets = list(powerset(lines))

    curr_min_subset = lines
    for subset in line_subsets:
        if len(subset) >= len(curr_min_subset):
            continue

        points_to_cover = points[:]
        for line in subset:
            for point in line:
                if point in points_to_cover:
                    points_to_cover.remove(point)
                    if len(points_to_cover) == 0:
                        if len(subset) < len(curr_min_subset):
                            curr_min_subset = subset
                        break
            if len(points_to_cover) == 0:
                break

    return curr_min_subset


def find_all_lines(lines, points):
    point_pairs = list(combinations(points, 2))

    for point_1, point_2 in point_pairs:
        if check(lines, point_1, point_2):
            continue

        lines.append([])
        lines[len(lines) - 1].append(point_1)
        lines[len(lines) - 1].append(point_2)
        slope, intercept = line_equation(point_1, point_2)
        for point in points:
            if point != point_1 and point != point_2 and point_belongs(slope, intercept, point):
                    lines[len(lines) - 1].append(point)


def expand_line(line, used_points, col=False):
    if len(line) >= 2:
        slope, intercept = line_equation(line[0], line[1])
        for point in used_points:
            if point_belongs(slope, intercept, point):
                line.append(point)
        line_sorted = sorted(line, key=lambda x: x[0])
        return line_sorted

    if not col:
        x, y = line[0]
        for point in used_points:
            x_point, y_point = point
            if y == y_point:
                line.append(point)
        line_sorted = sorted(line, key=lambda x: x[0])
        return line_sorted


# num = 0 => col & num = 1 => row
def find_biggest_line(points, num):
    groups = create_groups(points, num)
    group_lists = []
    for key, group in groups:
        group_lists.append(list(group))
    row_max_group = max([(group, len(group)) for group in group_lists], key=lambda x: x[1])[0]
    return row_max_group


if __name__ == '__main__':
    points = create_points(sys.argv[-1])
    executed = False

    f, g = False, False
    for arg in sys.argv:
        if arg == '-f':
            f = True
        if arg == '-g':
            g = True


    if f == True and g == True:
        lines = []

        find_lines(lines, points, 1) # Horizontal

        find_lines(lines, points, 0) # Perpendicular
        
        min_subset = find_minimun_num_of_lines(lines, points)

        min_subset_sorted = sort_points_per_line(min_subset)

        print_results(min_subset_sorted)

        executed = True
    

    if f == True and not(executed):
        lines = []

        find_all_lines(lines, points)

        min_subset = find_minimun_num_of_lines(lines, points)

        print_results(min_subset)

        executed = True


    if g == True and not(executed):
        lines = []
        used_points = []

        while len(points) != 0:
            row_max_group = find_biggest_line(points, 1)

            col_max_group = find_biggest_line(points, 0)

            if len(row_max_group) >= len(col_max_group):
                expanded_line = expand_line(row_max_group, used_points)
                lines.append(expanded_line)
                for point in expanded_line:
                    if point in points:
                        points.remove(point)
                        used_points.append(point)
            else:
                expanded_line = expand_line(col_max_group, used_points, col=True)
                lines.append(expanded_line)
                for point in col_max_group:
                    if point in points:
                        points.remove(point)
                        used_points.append(point)
        
        print_results(lines)

        executed = True
    

    if not(executed):
        lines = []

        find_all_lines(lines, points)

        chosen_lines = []
        used_points = set()
        while len(points) != 0:   
            lines_to_choose_from = []

            for line in lines:
                unused_points = 0
                for point in line:
                    if point not in used_points:
                        unused_points += 1
                lines_to_choose_from.append((unused_points, line))

            max_line = max(lines_to_choose_from, key=lambda x: x[0])[1]
            chosen_lines.append(max_line)
            lines.remove(max_line)
            for point in max_line:
                if point in points:
                    points.remove(point)
                    used_points.add(point)
        
        print_results(chosen_lines)