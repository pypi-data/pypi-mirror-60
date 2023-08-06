# Components.py - holds the classes of every component that is defined.

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


class Base:
    def __init__(self, coordinates=None, tag=None, end_node=None, z_angle_change=None, xy_length=None, z_coordinate=None, radius=None, category=None, diameter=None, wall_thickness=None):
        super(Base, self).__init__()
        self.coordinates = coordinates
        self.z_angle_change = z_angle_change
        self.end_node = end_node
        self.xy_length = xy_length
        self.z_coordinate = z_coordinate
        self.radius = radius
        self.category = category
        self.tag = tag

    def tags(self):
        return self.tag

    def check_end(self, num):
        return 0

    def centre_coordinates(self):
        return self.coordinates[2]

    def z_angle_write(self, angle):
        self.z_angle_change = angle

    def z_angle_read(self):
        return self.z_angle_change

    def xy_length_write(self, xy_length):
        self.xy_length = xy_length

    def xy_length_read(self):
        return self.xy_length


class Pipe:
    def __init__(self, diameter=None, wall_thickness=None):
        super(Pipe, self).__init__()
        self.diameter = diameter
        self.wall_thickness = wall_thickness


class Bend(Base, Pipe):
    def __init__(self, coordinates):
        super().__init__()
        self.coordinates = coordinates
        self.tag = 'KN'

    def calculate_properties(self):
        c = self.coordinates

        lenghts = [find_length(c[0], c[2]), find_length(c[1], c[2])]
        self.radius = round(lenghts[0], 0)
        self.angle = int(round(find_angle(c)))

    def check_end(self, num):
        if num < 2:
            return 1
        else:
            return 0


class Tee(Base):
    def __init__(self, coordinates):
        super().__init__()
        self.coordinates = coordinates
        self.tag = 'T'
        self.category = 'tee'
        self.radius = 0
        self.xy_length = [0, None, None]
        self.z_angle_change = [0, None, None]

    def tags(self):
        # Switcher for correctly displaying -1 and -2 tag based on request.
        if self.tag[-2:] == '-2':
            self.tag = self.tag[:-2] + '-1'
        else:
            self.tag = self.tag[:-2] + '-2'
        return self.tag

    def z_angle_write(self, angle):
        if self.z_angle_change[0] == 0:
            self.z_angle_change[0] = 1
            self.z_angle_change[1] = angle
        elif self.z_angle_change[0] == 1:
            self.z_angle_change[0] = 0
            self.z_angle_change[2] = angle

    def z_angle_read(self):
        # Apparently a Tee was present, but not fully connected; perhaps one side is on the next iso that was not present.
        if None in self.z_angle_change:
            return self.z_angle_change[1]
        else:
            if self.z_angle_change[0] == 0:
                self.z_angle_change[0] = 1
                return self.z_angle_change[1]
            elif self.z_angle_change[0] == 1:
                self.z_angle_change[0] = 0
                return self.z_angle_change[2]

    def xy_length_write(self, xy_length):
        if self.xy_length[0] == 0:
            self.xy_length[0] = 1
            self.xy_length[1] = xy_length
        elif self.xy_length[0] == 1:
            self.xy_length[0] = 0
            self.xy_length[2] = xy_length

    def xy_length_read(self):
        # Apparently a Tee was present, but not fully connected; perhaps one side is on the next iso that was not present.
        if None in self.xy_length:
            return self.xy_length[1]
        if self.xy_length[0] == 0:
            self.xy_length[0] = 1
            return self.xy_length[1]
        elif self.xy_length[0] == 1:
            self.xy_length[0] = 0
            return self.xy_length[2]


class GOS_connection(Base):
    def __init__(self, coordinates):
        super().__init__()
        self.coordinates = coordinates
        self.neighbour_node = None
        self.radius = 0
        self.z_angle_change = 0
        self.tag = "GOS"

    def calculate_properties(self):
        # Use same structure as other components
        self.coordinates = [[], [], self.coordinates[0]]

    def centre_coordinates(self):
        return self.coordinates[-1]


class Component(Base):
    def __init__(self):
        super().__init__()
        self.radius = 0

    # For two points, find the coordinates of the point in between
    def findMidpoint(self, i, j):
        return [(i[num]-j[num])/2+j[num] for num in range(len(i))]

    def calculate_properties(self):
        c = self.coordinates
        self.length = round(find_length(c[0], c[1]), 0)
        self.coordinates.append(self.findMidpoint(c[0], c[1]))


class Coupling(Component):
    def __init__(self, coordinates):
        super().__init__()
        self.coordinates = coordinates
        self.tag = "IK"


class Flange(Component):
    def __init__(self, coordinates):
        super().__init__()
        self.coordinates = coordinates
        self.tag = "FL"


class Reducer(Component, Pipe):
    def __init__(self, coordinates):
        super().__init__()
        self.coordinates = coordinates
        self.tag = "RED"


class Valve(Component, Pipe):
    def __init__(self, coordinates):
        super().__init__()
        self.coordinates = coordinates
        self.tag = "A"

# For two points, find the length between them


def find_length(i, j):
    return sum([(a - b)**2 for a, b in zip(i, j)])**0.5

# Give angle based on three coordinates -> two vectors


def find_angle(coordinates):

    a = np.array(coordinates[0])
    b = np.array(coordinates[1])
    c = np.array(coordinates[2])

    ac = a - c
    bc = b - c

    cosine_angle = np.dot(ac, bc) / \
        (np.linalg.norm(ac) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    return 180-np.degrees(angle)

# print('test')
