# isoconfig.py - extracts data from isoconfig files to generate polydif information.

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

from P3DtoPLE import dotproduct as dp
from P3DtoPLE.components import Bend, Tee, Coupling, Valve, Flange, Reducer, GOS_connection
from P3DtoPLE import visualise as v
import numpy as np
import matplotlib.pyplot as plt
import copy  # to use deepcopy
import glob
import os



# Extract coordinates as float


def extract_coordinates(data):
    data_split = [i.split() for i in data]  # Split string values
    coordinates = [[float(x) for x in i[1:4]] for i in data_split]

    return coordinates

# Create an object


def classify(data, list_of_obj, chosen_class):
    coordinates = extract_coordinates(data)
    list_of_obj.append(chosen_class(coordinates))

# Clone structure of input


def clone(components):
    detected = 0
    for num, c in enumerate(components):
        if detected == 1:
            detected = 0
            components[num].coordinates = [
                components[num].coordinates[2], None, components[num].coordinates[1]]
            continue
        else:
            detected = 1
            components.insert(num, copy.deepcopy(c))
            components[num].coordinates = [
                components[num].coordinates[2], None, components[num].coordinates[0]]

    return components


def collect_input():
    current_directory = os.path.dirname(os.path.abspath(__file__))   # Current directory
    working_directory = os.getcwd()
    input_files = os.path.join(working_directory, 'isogen\*pcf')
    return glob.glob(input_files)

# Filter component data from the raw isogen input files


def extract_number(data_split):
    try:
        number = float(data_split[-1].split("_")[2])
    except:
        number = None

    return number

# Remove duplicate coordinates from a list


def remove_duplicates(raw_data):
    # Find duplicate bends
    duplicates = []

    centrepoints = [x.coordinates[2] for x in raw_data]
    for count, x in enumerate(centrepoints):
        for count2, y in enumerate(centrepoints[count+1:]):
            delta = ([i-j for i, j in zip(x, y)])
            if abs(sum(delta)) < 0.00000001:
                duplicates.append(count+count2+1)

    # Delete duplicate values
    for d in duplicates:
        raw_data[d] = None
    raw_data = [i for i in raw_data if i]

    return raw_data


def read_isogen(filenames):

    bends = []
    tees = []
    couplings = []
    flanges = []
    valves = []
    reducers = []
    gos_connections = []

    timer = 15

    # Load all bend data from file
    for filename in filenames:
        with open(filename) as f:
            for line in f:
                if 'BEND' == line.strip() or 'ELBOW' == line.strip():
                    # Create class based on coordinates
                    # Save three rows
                    data = [next(f), next(f), next(f)]
                    classify(data, bends, Bend)

                    # Find other data
                    go = timer
                    while go > 0:
                        go -= 1
                        data = next(f)
                        data_split = data.split()

                        if data_split[0] == 'BEND-RADIUS':
                            bends[-1].radius = int(float(data_split[1]))
                            continue
                        if data_split[0] == 'COMPONENT-ATTRIBUTE4':
                            bends[-1].wall_thickness = extract_number(
                                data_split)
                            continue
                        # elif data_split[0] == 'COMPONENT-ATTRIBUTE5':
                        #     radius = extract_number(data_split)
                        #     continue
                        elif data_split[0] == 'COMPONENT-ATTRIBUTE7':
                            bends[-1].diameter = extract_number(data_split)
                            continue

                if 'TEE' == line.strip():
                    # Create class based on coordinates
                    data = [next(f), next(f), next(f), next(f)]
                    classify(data, tees, Tee)
                if 'COUPLING' == line.strip():
                    # Create class based on coordinates
                    data = [next(f), next(f)]
                    classify(data, couplings, Coupling)
                if 'FLANGE' == line.strip():
                    # Create class based on coordinates
                    data = [next(f), next(f)]
                    classify(data, flanges, Flange)
                if 'VALVE' == line.strip():
                    # Create class based on coordinates
                    data = [next(f), next(f)]
                    classify(data, valves, Valve)

                    # Find other data
                    go = timer
                    while go > 0:
                        go -= 1
                        data = next(f)
                        data_split = data.split()
                        if data_split[0] == 'COMPONENT-ATTRIBUTE2':
                            if data_split[1].find('Kog') > 0:
                                valves[-1].tag = 'KA'
                            elif data_split[1].find('Plug') > 0:
                                valves[-1].tag = 'PA'

                if 'REDUCER-CONCENTRIC' == line.strip():  # TODO: Zijn er ook andere reducers?
                    # Create class based on coordinates
                    data = [next(f), next(f)]
                    classify(data, reducers, Reducer)

                    # Find other data
                    go = timer
                    while go > 0:
                        go -= 1
                        data = next(f)
                        data_split = data.split()

                        if data_split[0] == 'COMPONENT-ATTRIBUTE4':
                            reducers[-1].wall_thickness = extract_number(
                                data_split)
                            continue
                        elif data_split[0] == 'COMPONENT-ATTRIBUTE7':
                            reducers[-1].diameter = extract_number(data_split)
                            continue
                        # TODO: Later twee attributes gebruiken om twee diameters door te nemen. Later gebruiken ter referentie bij de juiste node.

                # ONLY SAVE GOS ENDINGS FOR NOW.
                if 'END-CONNECTION-PIPELINE' == line.strip():
                    # Create class based on coordinates
                    data = [next(f), next(f)]

                    data_split = data[1].split()
                    if data_split[0] == 'PIPELINE-REFERENCE':
                        if data_split[1] == 'GOS':
                            classify([data[0]], gos_connections,
                                     GOS_connection)
                            gos_connections[-1].reference = data_split[1]

    # Determine other useful information
    [b.calculate_properties() for b in bends]
    [c.calculate_properties() for c in couplings]
    [f.calculate_properties() for f in flanges]
    [v.calculate_properties() for v in valves]
    [r.calculate_properties() for r in reducers]
    [e.calculate_properties() for e in gos_connections]

    # Remove duplicates based on corner coordinate #TODO: Can this go wrong? If yes, how and what to do?
    bends = remove_duplicates(bends)
    tees = remove_duplicates(tees)
    couplings = remove_duplicates(couplings)
    flanges = remove_duplicates(flanges)
    valves = remove_duplicates(valves)
    reducers = remove_duplicates(reducers)
    gos_connections = remove_duplicates(gos_connections)

    # Split components into two nodes for couplings and reducers
    couplings = clone(couplings)
    flanges = clone(flanges)
    valves = clone(valves)
    reducers = clone(reducers)

    return bends, tees, couplings, valves, flanges, reducers, gos_connections

# Visualise the calculates sequences in space


def visualise(data, all_sequences, all_nodes, view_mode, GOS_interface):

    ax = plt.axes(projection='3d')
    lines = []

    v.plot_nodes(data, all_sequences, all_nodes, ax, view_mode)
    v.plot_lines(data, all_sequences, GOS_interface, lines, ax, plt)

    # Show final result
    plt.show()

# Based on class base tag, find unique tag per node


def create_tags(all_sequences, nodes):

    d_tags = dict()

    for sub in all_sequences:
        for node_nr in sub:

            # Find base tag of object
            tag = nodes[node_nr].tag

            # Add angle to a bend
            if tag == 'KN':
                tag = tag + str(nodes[node_nr].angle) + '-'

            # If a previously passed tee, only change the ending to '-2'
            if tag[-2:] == '-1':
                nodes[node_nr].tag = tag[:-2] + '-2'

            # Determine the next component number
            else:
                try:  # Find next number based on the tag counter in the dictionary
                    num = d_tags[tag] + 1
                    d_tags[tag] = num
                except:  # If a new tag, add to dictionary
                    num = 1
                    d_tags[tag] = num

                # If tag is the chosen start, it's already tagged
                if tag == 'START':
                    pass
                # If first occurance of a tee, give a number and -1 ending
                elif tag[0] == 'T':
                    nodes[node_nr].tag = tag + str(num) + '-1'
                # If coupling or reducer
                elif tag == 'IK' or tag == 'RED' or tag == 'FL' or tag == 'A' or tag == 'PA' or tag == 'KA':
                    if (num/2).is_integer():    # Ending point
                        nodes[node_nr].tag = tag + str(int(num/2)) + 'e'
                    else:                       # Starting points
                        nodes[node_nr].tag = tag + \
                            str(int(np.ceil(num/2))) + 's'
                # If correct, only bends remain. Give the next number.
                else:
                    nodes[node_nr].tag = tag + str(num)
    return 0



# Find a node with only one connection, mark it as starting point


def find_starting_point(ends, all_connections, start, all_nodes):

    try:
        if start is None:
            for num, ac in enumerate(all_connections):
                if len(ac) == 1:  # Find first node with only one connection
                    start = num
                    all_nodes[start].tag = 'START'
                    break
        else:
            if len(all_connections[start]) == 1:
                all_nodes[start].tag = 'START'
            else:
                print(
                    "WARNING IC: not a valid starting node; picking first one instead.")
                for num, ac in enumerate(all_connections):
                    if len(ac) == 1:  # Find first node with only one connection
                        start = num
                        all_nodes[start].tag = 'START'
                        break
    except:
        print("ERROR IC: No starting point found.")

    return start

# Compile the raw isogen data to a useful data for the polydiff


def compile(input_filenames, **kwargs):

    # Detect options
    view = None
    start = None
    switch_tee = None
    switch_sub = None

    for key, value in kwargs.items():
        if key == 'view':
            view = value
        if key == 'start':
            start = value
        if key == 'switch_tee':
            switch_tee = value
        if key == 'switch_sub':
            switch_sub = value

    print("Reading isogen files...")
    bends, tees, couplings, valves, flanges, reducers, gos_connections = read_isogen(
        input_filenames)   # Extract useful data from isogen files

    # Determine if a GOS is present in the isogen files
    num_GOS_connections = len(gos_connections)

    if num_GOS_connections > 0:

        if num_GOS_connections == 2:
            GOS_present = 1
        else:
            input("WARNING: THERE ARE NO 2 GOS CONNECTIONS. FIX THIS!")
            # del gos_connections[-3:]  # Enschede MOD2: - fix amount of GOS points, ideally we only want to have TWO.
            # GOS_present = 1
            GOS_present = 0
    else:
        GOS_present = 0

    # Find all possible connections
    all_nodes = bends + tees + couplings + valves + flanges + reducers + \
        gos_connections          # List containing all coordinates of bends and tees
    all_coordinates = [i.coordinates for i in all_nodes]
    # Create full list of links, showing all connections for every node.
    all_connections = dp.find_links(all_coordinates)

    # TODO: TEMP: fix GOS together
    if GOS_present == 1:
        all_connections[-2].append(len(all_connections)-1)
        all_connections[-1].append(len(all_connections)-2)

    # ends, all_nodes, all_connections  = find_endings(all_connections, all_nodes, input_filenames)   # Find ending points + determine start
    ends = []

    # Give all nodes with one connection only a start category tag for plotting selection later on
    for num, c in enumerate(all_connections):
        if len(c) == 1:
            all_nodes[num].category = 'start'

    # Initilaise starting point
    start = find_starting_point(ends, all_connections, start, all_nodes)

    # Create the node sequence.

    # Allow modification by choice of switching tees or subs

    try:
        if switch_tee is not None:
            for st_num, st in enumerate(switch_tee):
                try:
                    num_connections_st = all_connections[st]

                    if len(num_connections_st) < 3:
                        print('WARNING: chosen node ' + str(st) +
                              ' is not a tee! Value removed.')
                        del switch_tee[st_num]
                except:  # If value is out of the list range
                    print('WARNING: chosen node ' + str(st) +
                          ' is not a tee! Value removed.')
                    del switch_tee[st_num]

        # Trace the link connections and list the correct sequence with swiched tees
        all_sequences, GOS_interface = dp.trace_sequence(
            all_connections, start=start, GOS_present=GOS_present, switch_tee=switch_tee)
    except:
        print("ERROR IC: Calculation sequence not valid; ignore switch tees.")
        switch_tee = []
        all_sequences, GOS_interface = dp.trace_sequence(
            all_connections, start=start, GOS_present=GOS_present, switch_tee=switch_tee)

    # Switch order of subs if required
    changed_subs = []
    if switch_sub is not None:
        for ss in switch_sub:
            all_sequences.append(all_sequences[ss])
            del all_sequences[ss]

    # Create tags for all nodes
    create_tags(all_sequences, all_nodes)

    # Visualise node corner points
    try:
        all_centre_coordinates = [
            i[2] for i in all_coordinates] + [i.coordinates for i in ends]  # Update

        if view > 0:
            visualise(all_centre_coordinates, all_sequences,
                      all_nodes, view, GOS_interface)
    except:
        pass

    return all_sequences, all_nodes, start, all_centre_coordinates, GOS_interface


def main():

    input_filenames = collect_input()

    view = 6
    start_node = None
    all_sequences, all_nodes, start_node, all_centre_coordinates, GOS_interface = compile(
        input_filenames, view=view, start=start_node)


if __name__ == "__main__":
    main()
