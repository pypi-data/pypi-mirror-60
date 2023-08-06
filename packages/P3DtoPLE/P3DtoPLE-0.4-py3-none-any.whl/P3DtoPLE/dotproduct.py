# dotproduct.py - Based on a set of random components coordinates, find connections based on the dot product
# of 1) the component direction vector and 2) an inter-component vector. If the direction is the same, choose
# the shortest solution.

# This file is part of the program P3DtoPLE.
# Copyright (C) 2020 E.A. Haselhoff - alexander.haselhoff@outlook.com
#
# P3DtoPLE is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as 
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# P3DtoPLE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import itertools


def sparse_list(length, slots):

    # Find all bend links
    s_list = [[]]*length

    if slots == 1:
        for num, val in enumerate(s_list):
            # Predefine structure to ensure different memory allocation
            s_list[num] = []
    elif slots == 3:
        for num, val in enumerate(s_list):
            # Predefine structure to ensure different memory allocation
            s_list[num] = [[], [], []]
    return s_list


def u_vector(coordinates_1, coordinates_2):
    vector = [j-i for i, j in zip(coordinates_1, coordinates_2)]
    unit_vector = vector/np.linalg.norm(vector)
    return unit_vector


def find_links(raw_data):

    bend_links = sparse_list(len(raw_data), 3)
    same_component = 0

    for count, node in enumerate(raw_data):
        # Define a vector from the centre to the edge of the component
        if None in node:                                # If e.g. coupling, reducer or flange
            if same_component == 0:
                same_component += 1                     # Next node is the same component!
            else:
                same_component = 0

            unit_vectors = [u_vector(node[0], node[2])]
        elif len(node) == 3:
            if len(node[0]) == 0:                       # If it is an end_connection
                continue
            else:                                       # If it is a bend
                unit_vectors = [
                    u_vector(node[2], node[0]), u_vector(node[2], node[1])]
        elif len(node) == 4:                            # If it is a tee
            unit_vectors = [u_vector(node[2], node[0]), u_vector(
                node[2], node[1]), u_vector(node[2], node[3])]

        # Define a vector "unit_vector_next_centre" from the current node centre to all next nodes centres
        for count2, next_node in enumerate(raw_data[(count+1):]):

            # Find unit vector pointing to the next node by using the midpoints
            if None in node:
                if count2 == 0 and same_component == 1:
                    unit_vector_next_centre = u_vector(next_node[2], node[2])
                else:  # Normaal
                    unit_vector_next_centre = u_vector(node[2], next_node[2])

            else:
                unit_vector_next_centre = u_vector(node[2], next_node[2])

            # Calculate the dot product of the two vectors
            num_ends = len(unit_vectors)
            for k in range(num_ends):
                check = np.dot(unit_vectors[k], unit_vector_next_centre)

                # If dot product is 1, the vectors allign
                if check > 0.9999:
                    connecting_node_number = count+count2+1

                    # Check which end of the other node it connected to
                    connecting_node = raw_data[connecting_node_number]

                    marker = None
                    # same_component_marker = None

                    if None in connecting_node:                                 # If coupling or reducer
                        unit_vectors_next = [
                            u_vector(connecting_node[0], connecting_node[2])]
                    elif len(connecting_node) == 3:
                        # If it is an end_connection
                        if len(connecting_node[0]) == 0:
                            unit_vectors_next = []
                            marker = 2
                        else:                                                   # If it is a bend
                            unit_vectors_next = [u_vector(connecting_node[2], connecting_node[0]), u_vector(
                                connecting_node[2], connecting_node[1])]

                    elif len(connecting_node) == 4:                             # If it is a tee
                        unit_vectors_next = [u_vector(connecting_node[2], connecting_node[0]), u_vector(
                            connecting_node[2], connecting_node[1]), u_vector(connecting_node[2], connecting_node[3])]

                    num_ends_connecting = len(unit_vectors_next)

                    for l in range(num_ends_connecting):
                        check2 = np.dot(unit_vectors[k], unit_vectors_next[l])

                        if check2 < -0.9999:
                            marker = l
                            break  # If correct there is only one possibility

                    if marker is None:  # If a possible connecting node has no 'looking' end, pass!
                        pass
                    # If same component, no check needed; save info
                    elif None in node and same_component == 1 and count2 == 0:
                        bend_links[count][2].append(connecting_node_number)
                        bend_links[connecting_node_number][2].append(count)
                    else:               # If a possible connecting node has a 'looking' bend, append solutions!
                        bend_links[count][k].append(
                            connecting_node_number)     # Save bend number
                        bend_links[connecting_node_number][marker].append(
                            count)

    # Remove double solutions
    for num, i in enumerate(bend_links):
        # For every vector direction
        for num2, j in enumerate(i):
            if len(j) == 1:
                # Flatten list if it contains 1 value
                bend_links[num][num2] = bend_links[num][num2][0]
            if len(j) > 1:
                length = sparse_list(len(j), 1)
                # Do for every solution found
                for num3, k in enumerate(j):
                    # Determine all coordinates
                    length[num3] = [
                        abs(i-j) for i, j in zip(raw_data[k][2], raw_data[num][2])]
                # Determine all lengths
                length = [np.linalg.norm(x) for x in length]
                # Determine the minimum length, this is the solution
                index = length.index(min(length))

                # Overwrite with correct solution
                bend_links[num][num2] = bend_links[num][num2][index]

            # Also remove previously defined links if they're still present
            try:
                for k in j:
                    if k is not j[index] and k < num:
                        bend_links[k].remove(num)
            except:
                pass

        # Flatten list
        current = bend_links[num]
        bend_links[num] = [x for x in current if not isinstance(x, list)]

    return bend_links


def correlate(inputList):

    # Find possible connections to all upstream nodes in the list
    upstream_links = find_links(inputList)

    # output = sparse_list(len(upstream_links),1)           # Create empty list with the same format

# Onderstaand moest al gebeuren in de find_links om alle afwegingen van korte afstanden correct mee te kunnen nemen.
    # for count, b in enumerate(upstream_links):
    #     for index in b:
    #         output[index].append(count)
    #         output[count].append(index)

    # return output

    return upstream_links


def find_previous_connections(current_node, sequence):

    old_nodes = []
    for s in sequence:
        for num, node in enumerate(s):
            if node == current_node:
                try:
                    old_nodes.append(s[num-1])
                except:
                    pass
                try:
                    old_nodes.append(s[num+1])
                except:
                    pass

    return old_nodes


def trace_sequence(data, **kwargs):

    for key, value in kwargs.items():
        if key == 'start':
            start = value
        if key == 'switch_tee':
            switch_tee = value
        if key == 'GOS_present':
            GOS_present = value

    try:
        # Check if specified starting node exists
        start
    except:
        print('ERROR: No start found at trace_sequence point, should not happen!')
        input()

    # Initialise

    old_node = start
    current_node = start
    sequence = [[start]]  # To contain the entire sequence
    choices = []

    GOS_interface = False
    GOS_in_node = None
    GOS_out_node = None

    try:
        range_num = 0

        while range_num >= 0:

            # Cleanup
            next_node = None

            # If there is a GOS, mark if we enter or exit it.
            if GOS_present == 1:
                # ASSUMING THERE ARE ONLY TWO GOS CONNECTIONS
                if current_node >= len(data)-2:
                    if GOS_interface is True:
                        GOS_out_node = current_node  # THis node exits the GOS
                    else:
                        GOS_interface = True  # One node has entered the GOS
                        GOS_in_node = current_node
            else:
                GOS_interface = False    # If no GOS, there is no interface

            # Check if a single link node is found:
            if range_num == 0:
                pass  # If starting node, it will pass
            elif len(data[current_node]) == 1:
                try:
                    # go back to previous tee choice
                    current_node = choices[-1]

                except:
                    break  # If no choices, this really is the end. Break!

            # Detect Tees
            if len(data[current_node]) > 2:
                # print("{} is a Tee!".format(current_node))
                if current_node in choices:
                    # Remove choice from checklist
                    choices.remove(current_node)

                    # Find already used values of Tee
                    old_node = find_previous_connections(
                        current_node, sequence)

                    try:
                        if len(set(old_node)) == 3:             # If Tee circles back on itself
                            current_node = choices[-1]
                            # Remove choice from checklist
                            choices.remove(current_node)
                            old_node = find_previous_connections(
                                current_node, sequence)

                        # Remove doubles, just to be sure
                        old_node = list(set(old_node))

                        sequence.append([])                 # Create new sub
                        # Add first continuation node
                        sequence[-1].append(current_node)
                    except:
                        print('ERROR DP: tee logic not valid')
                        break

                else:
                    # print("New choice! Save!")
                    choices.append(current_node)

            # Find correct next node in the sequence, keeps looping hence last possible option is always chosen.
            for j in data[current_node]:
                try:
                    if j not in old_node:
                        next_node = j
                except:
                    if j != old_node:
                        next_node = j

                # Give the first possible solution, except when the switch for a tee is activated.
                # This seems to yield a better result, since the connections are more inclined to go forward instead of taking corners.
                if next_node is not None:
                    try:
                        switch_tee  # Check if exists
                        if current_node not in switch_tee:
                            break   # Stop at first solution
                        else:
                            # Go to next solution when a switch is activated for this tee.
                            pass
                    except:
                        pass

            # Move to next node and save to sequence
            old_node = current_node
            current_node = next_node

            if next_node is None:
                # diff = len(data) - len(sequence) # TODO: Count inaccurate since Tee/starts are counted double, fix.
                # if diff > 0:
                    # print('WARNING: floating nodes detected!')

                # If an end is reached and there were no choices any more, break the loop.
                break
            else:
                sequence[-1].append(next_node)
                range_num += 1
    except:
        pass

    return sequence, [GOS_in_node, GOS_out_node]


def main():

    all_coordinates = [[[596135.1417, -69037.3972, 6170.0], [595983.1416, -68885.3999, 6169.1103], [595983.1417, -69037.3973, 6170.0]],
                       [[599531.1417, -69037.3954, 6170.0], [599683.1416, -68885.3953, 6170.0], [599683.1417, -69037.3953, 6170.0]],
                       [[596633.1412, -68169.397, 6170.0], [596785.1412, -68017.3969, 6170.0], [596633.1412, -68017.397, 6170.0]],
                       [[599033.1412, -68169.3956, 6170.0], [598881.1412, -68017.3957, 6170.0], [599033.1412, -68017.3956, 6170.0]],
                       [[589729.9486, -43899.1858, 6553.5095], [589583.1279, -44051.1859, 6592.85], [589583.1278, -43899.1859, 6592.85]],
                       [[592312.312, -43899.1844, 6022.85], [591128.9913, -43899.1851, 6178.6371], [591710.3968, -43899.1847, 6022.85]],
                       [[595983.128, -44299.1755, 6025.1914], [595583.1278, -43899.1826, 6022.85], [595983.1278, -43899.1824, 6022.85]],
                       [[596785.1408, -67367.3969, 6170.0], [596633.1407, -67215.4006, 6168.9484], [596633.1408, -67367.397, 6170.0]],
                       [[599683.1409, -67519.3953, 6170.0], [599531.1408, -67367.3954, 6170.0], [599683.1408, -67367.3953, 6170.0]],
                       [[596633.1293, -46499.1724, 6025.6174], [597033.129, -46099.1818, 6022.85], [596633.129, -46099.182, 6022.85]],
                       [[598903.108, -46099.1808, 6022.85], [599303.1078, -45699.1805, 6022.85], [599303.108, -46099.1805, 6022.85]],
                       [[596738.1417, -69037.3969, 6170.0], [596528.1417, -69037.397, 6170.0], [596633.1417, -69037.397, 6170.0], [596633.1417, -68932.397, 6170.0]],
                       [[598928.1417, -69037.3957, 6170.0], [599138.1417, -69037.3956, 6170.0], [599033.1417, -69037.3956, 6170.0], [599033.1417, -68932.3956, 6170.0]],
                       [[597938.1412, -68017.3963, 6170.0], [597728.1412, -68017.3964, 6170.0], [597833.1412, -68017.3963, 6170.0], [597833.1412, -68017.3963, 6275.0]]]

    # Create full list of links, showing all connections for every node.
    all_connections = correlate(all_coordinates)

    # Trace the link connections and list the correct sequence
    all_links = trace_sequence(all_connections)

    print(all_links)


if __name__ == "__main__":
    main()
