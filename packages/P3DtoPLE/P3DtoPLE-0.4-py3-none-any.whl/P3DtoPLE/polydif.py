# polydif.py - manages the interaction with the compiled isogen data and the polydif excel-sheet.

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

# import openpyxl
from P3DtoPLE import isoconfig
from P3DtoPLE import dotproduct as dp
import numpy as np
import editpyxl
import sys
import os


def open_wb(polydif_filename):

    current_directory = os.path.dirname(
        os.path.abspath(__file__))   # Current directory
    input_file = os.path.join(current_directory, polydif_filename)

    try:
        print('Opening workbook')
        return editpyxl.Workbook().open(input_file)
    except:
        print("ERROR polydif.py! '"+str(sys.exc_info()
                                        [0])+"' occured. File '"+input_file+"' probably not found.")
        exit()


def check_output_file(output_filename):
    current_directory = os.path.dirname(
        os.path.abspath(__file__))   # Current directory
    output_file = os.path.join(current_directory, output_filename)

    try:
        if os.path.exists(output_file):
            wb = editpyxl.Workbook().open(output_file)
            wb.save(output_file)
    except:
        print("ERROR polydif.py! '"+str(sys.exc_info()
                                        [0])+"' occured. Please close '" + output_file + "'.")
        exit()


def save_output_file(wb, output_filename):
    current_directory = os.path.dirname(
        os.path.abspath(__file__))   # Current directory
    output_file = os.path.join(current_directory, output_filename)

    try:
        print('Saving polydif')
        wb.save(output_file)
        wb.close()

        return output_file
    except:
        print("ERROR polydif.py! '"+str(sys.exc_info()
                                        [0])+"' occured. Please check '" + output_file + "'.")
        exit()

# For two points, find the length between them


def find_length(i, j):
    return sum([(a - b)**2 for a, b in zip(i, j)])**0.5


# Determine all node Z-angles relative to the previous node for polydiff


def find_angles_and_lengths(all_sequences, all_nodes):

    num_subs = len(all_sequences)
    # To save the mosst recently used X-Y-vector, in case the next (few) lines move up-/downrwards.
    previous_v1 = None

    for num_seq, s in enumerate(all_sequences):
        for num, node in enumerate(s):

            z_coordinate = all_nodes[s[num]].centre_coordinates()[-1]
            all_nodes[node].z_coordinate = round(z_coordinate, 1)

            angle = 0  # Reset angle

            try:
                # If last node in a sub
                if num == len(s)-1:
                    z_angle_change = 0                                  # Always give angle 0
                    # Use previous point for distance
                    c1 = all_nodes[s[num-1]].centre_coordinates()[:-1]
                    c2 = all_nodes[s[num]].centre_coordinates()[:-1]
                    XY = find_length(c1, c2)

                else:

                    # Find coordinate points
                    if num == 0 and num_seq != 0:   # If starting node, aka a Tee
                        for i in range(num_subs-1, -1, -1):
                            try:
                                # Find node diverging from tee as defined in a previous sub.
                                index = all_sequences[i].index(node)+1
                                n_prev = all_sequences[i][index]
                            except:
                                pass
                        c1 = all_nodes[n_prev].centre_coordinates()[:-1]
                    else:   # If random node, use previous node coordinates
                        c1 = all_nodes[s[num-1]].centre_coordinates()[:-1]

                    # Current and next node coordinates
                    c2 = all_nodes[s[num]].centre_coordinates()[:-1]
                    c3 = all_nodes[s[num+1]].centre_coordinates()[:-1]

                    # Determine vectors
                    if num == 0:  # If we're dealing with a tee
                        # Approach from the other side for correct angle sign
                        v1 = dp.u_vector(c2, c1)
                    else:
                        v1 = dp.u_vector(c1, c2)

                    v2 = dp.u_vector(c2, c3)

                    # Calculate length between nodes
                    try:
                        if num == 0:  # If initial node, no length is possible.
                            XY = 0
                        else:
                            XY = find_length(c1, c2)
                    except:
                        pass

                    # Calculate angle and direction

                    # Check if vectors are moving up-/downwards

                    # If previous line has no angle-change, use the most recently defined vector
                    if np.isnan(v1).any():
                        v1 = previous_v1

                    if np.isnan(v2).any():  # If next line moves up-/downards
                        z_angle_change = 0
                        previous_v1 = v1  # Save for later use
                    else:
                        try:
                            dot_product = np.dot(v1, v2)
                            if dot_product > 1:
                                dot_product = 1.0
                            angle = np.arccos(dot_product)/(np.pi/180)
                            direction = np.cross(v1, v2)
                            try:
                                if direction > 0:
                                    sign = 1
                                elif direction < 0:
                                    sign = -1
                                else:
                                    print(
                                        "Error with determining direction of angle for node " + str(node) + ".")
                                    pass
                            except:
                                pass

                            z_angle_change = int(round(angle*sign))

                        except:
                            # If points are on top of each other, hence no Z-angle
                            # print("Points only differ in Z-coordinate, make angle = 0")
                            if np.isnan(v1).any() or np.isnan(v2).any():
                                z_angle_change = 0

                # print(node)
                # print(XY)

                # print(node)
                # print(z_angle_change)

                all_nodes[node].z_angle_write(z_angle_change)
                all_nodes[node].xy_length_write(int(round(XY)))

            except:
                pass


def fill_polydif(wb, all_sequences, all_nodes, start_node):

    print('Creating polydif')
    num_subs = len(all_sequences)
    names = wb.get_sheet_names()

    for num, sheet in enumerate(names[3:3+num_subs]):

        ws = wb[sheet]
        idents = [all_nodes[s].tags() for s in all_sequences[num]]
        angle = [all_nodes[s].z_angle_read() for s in all_sequences[num]]
        xy_length = [all_nodes[s].xy_length_read() for s in all_sequences[num]]
        z_coordinates = [all_nodes[s].z_coordinate for s in all_sequences[num]]
        start_coordinates = all_nodes[start_node].coordinates
        if len(start_coordinates) > 1:
            start_coordinates = start_coordinates[2]
        radius = [all_nodes[s].radius for s in all_sequences[num]]

        # Determine and fill in the starting ident
        if num == 0:
            start_ident = idents[0]

            ws['D10'] = 0
            ws['F10'] = start_coordinates[0]
            ws['H10'] = start_coordinates[1]
            ws['J10'] = z_coordinates[0]

            del idents[0]
            del angle[0]
            del xy_length[0]
            del z_coordinates[0]
            del radius[0]

        else:
            start_ident = idents[0][:-2] + '-1'

        ws['B10'] = start_ident

        # TODO: Temp invullen diameter en elastische straal

        ws['O3'] = 100
        ws['O5'] = 1000

        # Fill in the idents of this sub
        len_idents = len(idents)
        for num2, i in enumerate(range(14, 14+len_idents)):
            j = 2  # Idents
            cell_name = ws.row_col_to_cell(i, j)
            ws.cell(cell_name).value = idents[num2]

            j = 4  # Angle
            cell_name = ws.row_col_to_cell(i, j)
            ws.cell(cell_name).value = angle[num2]

        if num == 0:
            row_start = 14
        else:
            row_start = 15
            del xy_length[0]
            del z_coordinates[0]
            del radius[0]
            len_idents -= 1

        for num2, i in enumerate(range(row_start, row_start+len_idents)):

            j = 6  # Bendradius
            cell_name = ws.row_col_to_cell(i, j)
            ws.cell(cell_name).value = radius[num2]

            j = 8  # xy-distance
            cell_name = ws.row_col_to_cell(i, j)
            ws.cell(cell_name).value = xy_length[num2]

            j = 10  # z
            cell_name = ws.row_col_to_cell(i, j)
            ws.cell(cell_name).value = z_coordinates[num2]

# Initialise the compilation of data required for the polydif


def initialise(input_filenames, output_filename, **kwargs):

    # Quick check to see if output file has been closed
    # check_output_file(output_filename)

    # Get isogen data

    all_sequences, all_nodes, start_node, all_centre_coordinates, GOS_interface = isoconfig.compile(
        input_filenames, **kwargs)

    return all_sequences, all_nodes, start_node, all_centre_coordinates, GOS_interface

# Use the initialised data to generate a polydif


def generate(polydif_filename, output_filename, all_sequences, all_nodes, start_node, GOS_interface, **kwargs):

    # Determine all node Z-angles and lengths relative to the previous node for polydiff
    find_angles_and_lengths(all_sequences, all_nodes)

    # Remove radius of GOS entering node to create a weak in the same sub later on
    if GOS_interface[1] is not None:
        all_nodes[GOS_interface[1]].radius = ''

    # Detect optional commands
    open_output = None
    for key, value in kwargs.items():
        if key == 'open_output':
            open_output = value

    # Put data in polydif
    wb = open_wb(polydif_filename)
    fill_polydif(wb, all_sequences, all_nodes, start_node)
    output_file = save_output_file(wb, output_filename)

    # Open polydif
    if open_output == 1:
        print("Opening output file...")
        os.startfile(output_file)


def empty_options():
    view_mode = None
    start_node = None
    switch_tee_list = None
    open_output = None

    return view_mode, start_node, switch_tee_list, open_output


def main():
    # Files
    input_filenames = isoconfig.collect_input()
    polydif_filename = 'POLYDIF2PLE.xlsx'
    output_filename = 'output/polydif_output.xlsx'

    # Options
    view_mode, start_node, switch_tee_list, open_output = empty_options()

    view_mode = 5
    # start_node = 18
    switch_tee_list = None
    open_output = 0

    # Generate a polydif based on the isogens
    all_sequences, all_nodes, start_node, _, GOS_interface = initialise(
        input_filenames, output_filename, view=view_mode, start=start_node, switch_tee=switch_tee_list, open_output=open_output)
    generate(polydif_filename, output_filename,
             all_sequences, all_nodes, start_node, GOS_interface)


if __name__ == "__main__":
    main()
