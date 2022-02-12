import sys
from collections import deque
from itertools import permutations


def gc_dfs(recursion_depth, node, max_coord, number_of_bits, visited, gc, all_codes):
    if recursion_depth == 2**number_of_bits:
        all_codes.append(gc[:])
        return
    
    for i in range(min(number_of_bits, max_coord + 1)):
        node_binary = convert_to_binary(node, number_of_bits)
        coord = number_of_bits - i - 1
        x = int(flip(node_binary, coord), 2)
        if not visited[x]:
            visited[x] = True
            gc.append(x)
            gc_dfs(recursion_depth + 1, x, max(i+1, max_coord), number_of_bits, visited, gc, all_codes)
            visited[x] = False
            gc.pop()


def bgc_dfs(recursion_depth, node, max_coord, number_of_bits, visited, gc, queue, all_codes):
    if recursion_depth == 2**number_of_bits:
        all_codes.append(gc[:])
        return
    
    for i in range(min(number_of_bits, max_coord + 1)):
        node_binary = convert_to_binary(node, number_of_bits)
        coord = number_of_bits - i - 1
        if node_binary[coord] == '1' and queue[-1] == coord:
            x = int(flip(node_binary, coord), 2)
            queue.pop()
        elif node_binary[coord] == '0':
            x = int(flip(node_binary, coord), 2)
            queue.appendleft(coord)
        else: # node_binary[coord] == '1' but isn't the one thats the longer in the queue
            continue

        if not visited[x]:
            visited[x] = True
            gc.append(x)
            bgc_dfs(recursion_depth + 1, x, max(i+1, max_coord), number_of_bits, visited, gc, queue, all_codes)
            visited[x] = False
            gc.pop()
        
        if node_binary[coord] == '1':
            queue.append(coord) # revert queue.pop()
        elif node_binary[coord] == '0':
            queue.popleft() # revert queue.appendleft(coord)


def convert_to_binary(node, number_of_bits):
    binary = format(node, "b")
    if len(binary) != number_of_bits:
        padding_length = number_of_bits - len(binary)
        padding = ''
        for _ in range(padding_length):
            padding += '0'
        binary = padding + binary
    return binary


def flip(x, coord):
  if x[coord] == '0':
    x = x[:coord] + '1' + x[(coord + 1):]
  else:
    x = x[:coord] + '0' + x[(coord + 1):]
  return x


def convert_to_delta(gc, number_of_bits):
  delta = ''
  for node, next_node in zip(gc, gc[1:]):
    node_binary = convert_to_binary(node, number_of_bits)
    next_node_binary = convert_to_binary(next_node, number_of_bits)
    for j in range(number_of_bits):
      if not (node_binary[j] == next_node_binary[j]):
        coord = number_of_bits - j - 1
        delta += str(coord)

  first_node = convert_to_binary(gc[0], number_of_bits)
  last_node = convert_to_binary(gc[-1], number_of_bits)
  bits_differ = 0
  coord = 0
  for j in range(number_of_bits):
    if not (first_node[j] == last_node[j]):
      bits_differ += 1
      coord = number_of_bits - j - 1
  
  if bits_differ == 1:
    delta = delta + str(coord)

  return delta


def find_reverse_isomorphisms(bgc_delta, number_of_bits):
    reverse_isomorphisms = []
    coordinates = [str(n) for n in range(number_of_bits)]
    for delta in bgc_delta:
        for potential_match in bgc_delta:
            if delta == potential_match:
                continue

            rev_potential_match = potential_match[::-1]
            perms = permutations(coordinates, number_of_bits)
            for perm in perms:
                permuted_delta = ''
                for letter in delta:
                    for i in range(number_of_bits):
                        if letter == coordinates[i]:
                            permuted_delta += perm[i]
            
                if permuted_delta == rev_potential_match and ((potential_match, delta) not in reverse_isomorphisms):
                    reverse_isomorphisms.append((delta, potential_match))
    return reverse_isomorphisms


def print_gc_delta(delta, number_of_bits):
  if len(delta) == 2**number_of_bits:
    print('C', delta)
  else:
    print('P', delta)


def print_bgc_delta(delta, number_of_bits):
    if len(delta) == 2**number_of_bits:
        print('B', delta)
    else:
        print('U', delta)


def print_reverse_isomorphisms(reverse_isomorphisms):
    for delta_1, delta_2 in reverse_isomorphisms:
        print(delta_1, '<=>', delta_2)


def print_in_binary(gc, ctype, number_of_bits):
    print(ctype, end=' ')
    for element in gc:
        print(convert_to_binary(element, number_of_bits), end=' ')
    print()


def print_as_matrix(gc, number_of_bits):
  gc_binary = []
  for element in gc:
    gc_binary.append(convert_to_binary(element, number_of_bits))

  for i in range(number_of_bits - 1, -1, -1):
    for element in gc_binary:
      print(element[i], end=' ')
    print()


if __name__ == '__main__':
    number_of_bits = int(sys.argv[-1])

    a, b, u, c, p, r, f, m = False, False, False, False, False, False, False, False
    for arg in sys.argv:
        if arg == '-a':
            a = True
        if arg == '-b':
            b = True
        if arg == '-u':
            u = True
        if arg == '-c':
            c = True
        if arg == '-p':
            p = True
        if arg == '-r':
            r = True
        if arg == '-f':
            f = True
        if arg == '-m':
            m = True
    
    if a == True or c == True or p == True or len(sys.argv) == 2:
        all_codes = []
        gc = [0]
        visited = [False] * (2**number_of_bits)
        visited[0] = True
        
        gc_dfs(1, 0, 0, number_of_bits, visited, gc, all_codes)

        gc_delta_qualified = [] # needed to find reverse isomorphisms
        for gc in all_codes:
            delta = convert_to_delta(gc, number_of_bits)
            if c == True:
                if len(delta) == 2**number_of_bits:
                    gc_delta_qualified.append(delta)
                    print_gc_delta(delta, number_of_bits)
                    if f == True:
                        print_in_binary(gc, 'C', number_of_bits)
                    if m == True:
                        print_as_matrix(gc, number_of_bits)
            elif p == True:
                if len(delta) != 2**number_of_bits:
                    gc_delta_qualified.append(delta)
                    print_gc_delta(delta, number_of_bits)
                    if f == True:
                        print_in_binary(gc, 'P', number_of_bits)
                    if m == True:
                        print_as_matrix(gc, number_of_bits)
            else: # -a or no arg
                gc_delta_qualified.append(delta)
                print_gc_delta(delta, number_of_bits)
                ctype = ''
                if len(delta) == 2**number_of_bits:
                    ctype = 'C'
                else:
                    ctype = 'P'

                if f == True:
                    print_in_binary(gc, ctype, number_of_bits)
                if m == True:
                    print_as_matrix(gc, number_of_bits)
        
        if r == True:
            reverse_isomorphisms = find_reverse_isomorphisms(gc_delta_qualified, number_of_bits)
            print_reverse_isomorphisms(reverse_isomorphisms)
    
    if b == True or u == True:
        all_codes = []
        gc = [0]
        visited = [False] * (2**number_of_bits)
        visited[0] = True
        queue = deque()

        bgc_dfs(1, 0, 0, number_of_bits, visited, gc, queue, all_codes)

        bgc_delta_qualified = [] # needed to find reverse isomorphisms
        for bgc in all_codes:
            delta = convert_to_delta(bgc, number_of_bits)
            if b == True and len(delta) == 2**number_of_bits:
                bgc_delta_qualified.append(delta)
                print_bgc_delta(delta, number_of_bits)
                if f == True:
                    print_in_binary(bgc, 'B', number_of_bits)
                if m == True:
                    print_as_matrix(bgc, number_of_bits)
            if u == True and len(delta) != 2**number_of_bits:
                bgc_delta_qualified.append(delta)
                print_bgc_delta(delta, number_of_bits)
                if f == True:
                    print_in_binary(bgc, 'U', number_of_bits)
                if m == True:
                    print_as_matrix(bgc, number_of_bits)
        
        if r == True:
            reverse_isomorphisms = find_reverse_isomorphisms(bgc_delta_qualified, number_of_bits)
            print_reverse_isomorphisms(reverse_isomorphisms)