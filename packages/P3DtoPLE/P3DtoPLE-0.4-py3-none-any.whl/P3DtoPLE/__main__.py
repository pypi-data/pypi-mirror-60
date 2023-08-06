#__main__.py - used to define how start the P3DtoPLE package

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

from P3DtoPLE import gui
import os
from os import path

if __name__ == '__main__':

    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # print('*******************')
    # print(dir_path)
    working_directory = os.getcwd()
    output_folder = 'output'
    output_folder = os.path.join(working_directory, output_folder)

    if path.exists(output_folder):
        pass
    else:
        os.mkdir(output_folder)

    gui.run()