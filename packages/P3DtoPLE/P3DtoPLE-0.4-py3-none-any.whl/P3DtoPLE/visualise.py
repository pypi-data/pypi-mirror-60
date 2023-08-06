# visualise.py - constructs the geometry for visualisation.

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


def plot_nodes(data, all_sequences, all_nodes, ax, view_mode):

    # Scatter all points
    x = [d[0] for d in data]
    y = [d[1] for d in data]
    z = [d[2] for d in data]

    # Set axes
    ax.scatter(x, y, z, s=5, c='black', marker='o')
    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')
    ax.set_zlabel('Z coordinate')

    # Attach label with node number
    xl = []
    yl = []
    zl = []

    if view_mode != 5 and view_mode != 6:
        for sub, nodes in enumerate(all_sequences):
            xl.append([])
            yl.append([])
            zl.append([])

            for node in nodes:
                xl[sub].append(x[node])
                yl[sub].append(y[node])
                zl[sub].append(z[node])

                tag = all_nodes[node].tag
                if view_mode == 1:  # Show node numbers
                    ax.text(x[node], y[node], z[node],  '%s' %
                            tag, size=10, zorder=1,  color='k')
                if view_mode == 2:  # Show node names
                    ax.text(x[node], y[node], z[node],  '%s' %
                            str(node), size=10, zorder=1,  color='k')
                if view_mode == 3:  # Show name and node numbers
                    ax.text(x[node], y[node], z[node],  '%s' % tag +
                            '\n' + str(node), size=10, zorder=1,  color='k')
                if view_mode == 4:  # Only show changable node numbers
                    if all_nodes[node].category == 'start' or all_nodes[node].category == 'tee':
                        ax.text(x[node], y[node], z[node],  '%s' %
                                str(node), size=10, zorder=1,  color='k')
    else:
        if view_mode == 5:  # Only show numbers of missing nodes
            flat_list = [item for sublist in all_sequences for item in sublist]
            flat_list.sort()

            nodes_list = [i for i in range(len(all_nodes))]

            missing_nodes = list(set(nodes_list).difference(flat_list))
            missing_nodes.sort()

            for node in missing_nodes:
                if node >= 0:
                    xl.append(x[node])
                    yl.append(y[node])
                    zl.append(z[node])

                    ax.text(x[node], y[node], z[node],  '%s' %
                            str(node), size=10, zorder=1,  color='k')
        else:
            nodes_list = [i for i in range(len(all_nodes))]

            for node in nodes_list:
                if node >= 0:
                    xl.append(x[node])
                    yl.append(y[node])
                    zl.append(z[node])

                    ax.text(x[node], y[node], z[node],  '%s' %
                            str(node), size=10, zorder=1,  color='k')


def plot_lines(data, all_sequences, GOS_interface, lines, ax, plt):

    # Coordinates

    x = [d[0] for d in data]
    y = [d[1] for d in data]
    z = [d[2] for d in data]

    # Attach label with node number
    xl = []
    yl = []
    zl = []

    for sub, nodes in enumerate(all_sequences):
        xl.append([])
        yl.append([])
        zl.append([])
        for node in nodes:
            xl[sub].append(x[node])
            yl[sub].append(y[node])
            zl[sub].append(z[node])

    # Add lines between points
    color_dict = {
        0: 'r',
        1: 'b',
        2: '#55ff4d',
        3: 'y',
        4: '#007A14',
        5: '#00B2FF',
        6: '#002A3D',
        7: '#776589',
        8: '#9F0404',
        9: '#E1854A',
        10: '#14471A',
        11: '#FE85FE',
        12: '#A6F7B0',
        13: '#FFE198',
        14: '#FFD5D5',
        15: '#75FFF9'
    }

    # Remove old lines
    for i in range(len(ax.lines)):
        ax.lines.pop(0)

    # Add lines between points
    for i, _ in enumerate(xl):
        c = color_dict[i]
        lines.append(plt.plot(xl[i], yl[i], zl[i], color=c))

    # Mark GOS
    if GOS_interface[1]:
        xg = [x[GOS_interface[0]], x[GOS_interface[1]]]
        yg = [y[GOS_interface[0]], y[GOS_interface[1]]]
        zg = [z[GOS_interface[0]], z[GOS_interface[1]]]
        plt.plot(xg, yg, zg, linestyle='--', linewidth=2, color='black')


def main():
    print('Main run')


if __name__ == "__main__":
    main()
