# gui.py - Holds the GUI that interacts with the program.

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

from P3DtoPLE import isoconfig
from P3DtoPLE import polydif
from P3DtoPLE import visualise as v
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel
from PyQt5 import QtCore
import os
from os import path

import matplotlib
matplotlib.use('Qt5Agg')

# from mpl_toolkits.mplot3d import Axes3D


class Window(QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.title = 'P3DtoPLE'
        self.setWindowTitle(self.title)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint |
                            QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
        self.showMaximized()
        self.view_mode = 4
        self.azim = -60
        self.elev = 30
        self.lines = []
        self.x = None
        self.y = None
        self.z = None
        self.xl = None
        self.yl = None
        self.zl = None

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Below are the definitions of buttons and labels
        width = 150

        # Button to activate the plot method
        self.button = QPushButton('Run solution preview')
        self.button.clicked.connect(self.data)
        self.button.clicked.connect(self.plot_lines)

        # Empty space, bit smaller than stretch
        self.textbox_empty = QLabel(self)
        self.textbox_empty.setText('')

        # textbox to input starting node changes
        self.textbox_start_label = QLabel(self)
        self.textbox_start_label.setText('Change start')
        self.textbox_start = QLineEdit(self)
        self.textbox_start.setMaximumWidth(width)

        # Textbox to input tee changes
        self.textbox_tee_label = QLabel(self)
        self.textbox_tee_label.setText('Change tee')
        self.textbox_tee = QLineEdit(self)
        self.textbox_tee.setMaximumWidth(width)

        # textbox to input sub changes
        self.textbox_sub_label = QLabel(self)
        self.textbox_sub_label.setText('Change sub')
        self.textbox_sub = QLineEdit(self)
        self.textbox_sub.setMaximumWidth(width)

        # Button to activate polydif generation method
        self.button_generate = QPushButton('Generate Polydif')
        self.button_generate.clicked.connect(self.close)
        self.button_generate.clicked.connect(self.generate)

        # Create the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)

        hbox = QHBoxLayout()
        hbox.addWidget(self.canvas)

        vbox = QVBoxLayout()
        
        vbox.addWidget(self.textbox_start_label)
        vbox.addWidget(self.textbox_start)
        vbox.addWidget(self.textbox_tee_label)
        vbox.addWidget(self.textbox_tee)
        vbox.addWidget(self.textbox_sub_label)
        vbox.addWidget(self.textbox_sub)
        vbox.addWidget(self.textbox_empty)
        vbox.addWidget(self.button)
        vbox.addStretch(5)
        vbox.addWidget(self.button_generate)
        hbox.addLayout(vbox)

        layout.addLayout(hbox)

        self.setLayout(layout)

        # Create image
        self.ax = plt.axes(projection='3d')
        self.data()
        self.plot_lines()
        self.plot_nodes()

    def data(self):

        # Save modifications in a .txt output
        def save_settings(self, start_node, switch_tee_list, switch_sub_list):
            current_directory = os.path.dirname(os.path.abspath(__file__))   # Current directory
            working_directory = os.getcwd()
            settings_file = os.path.join(working_directory, 'output\settings.txt')
            text_file = open(settings_file, "w")
            text_file.write('Starting node:\n')
            if start_node is not None:
                text_file.write(str(start_node)[1:-1])
            text_file.write('\n\n')
            text_file.write('Changed tees:\n')
            text_file.write(str(switch_tee_list)[1:-1] + '\n\n')
            text_file.write('Changed subs:\n')
            text_file.write(str(switch_sub_list)[1:-1])
            text_file.close()

        # Options
        input_filenames = isoconfig.collect_input()
        output_filename = 'P3DtoPLE\output\output_polydif.xlsx'
        # view_mode, start_node, switch_tee_list, open_output = polydif.empty_options()
        # view_mode = 0 # VERY IMPORTANT TO KEEP 0 in polydif.initialise ELSE IT WILL BUG
        start_node = None
        switch_tee_list = []
        switch_sub_list = []
        # self.view_mode = 4

        if self.textbox_start.text():
            start_node_list = [int(x) for x in self.textbox_start.text().split(
                ',') if x.strip().isdigit()]
            if len(start_node_list) > 1:
                print("WARNING GUI: Multiple starting points given!")
            start_node = start_node_list[0]
            # start_node = int(self.textbox_start.text())

        if self.textbox_tee.text():
            switch_tee_list = [int(x) for x in self.textbox_tee.text().split(
                ',') if x.strip().isdigit()]

        if self.textbox_sub.text():
            switch_sub_list = [int(x) for x in self.textbox_sub.text().split(
                ',') if x.strip().isdigit()]

        # # Save settings to .txt
        save_settings(self, start_node, switch_tee_list, switch_sub_list)

        # Find data
        self.all_sequences, self.all_nodes, self.start_node, self.all_centre_coordinates, self.GOS_interface = polydif.initialise(
            input_filenames, output_filename, start=start_node, switch_tee=switch_tee_list, switch_sub=switch_sub_list)

    # Plot the node points and corresponding tags
    def plot_nodes(self):

        # Get data
        data = self.all_centre_coordinates
        all_sequences = self.all_sequences
        all_nodes = self.all_nodes
        ax = self.ax
        view_mode = self.view_mode

        v.plot_nodes(data, all_sequences, all_nodes, ax, view_mode)

        # Refresh canvas
        self.canvas.draw()

    # Plot the connections between the nodes
    def plot_lines(self):

        # Define data
        data = self.all_centre_coordinates
        all_sequences = self.all_sequences
        ax = self.ax
        GOS_interface = self.GOS_interface
        lines = self.lines

        v.plot_lines(data, all_sequences, GOS_interface, lines, ax, plt)

        # Use previous saved azimuth and elevation
        try:
            ax.azim = self.azim
        except:
            pass
        try:
            ax.elev = self.elev
        except:
            pass

        # List to save your projections to
        projections = []

        # This is called everytime you release the mouse button
        def on_click(event):
            azim, elev = ax.azim, ax.elev
            projections.append((azim, elev))
            self.azim = azim
            self.elev = elev

            # print(azim, elev)

        # Every time the mouse is released, save the camera orientation
        cid = self.canvas.mpl_connect('button_release_event', on_click)

        # refresh canvas
        self.canvas.draw()

    # Generate a polydif
    def generate(self):

        current_directory = os.path.dirname(os.path.abspath(__file__))   # Current directory
        working_directory = os.getcwd()

        polydif_filename = 'POLYDIF2PLE.xlsx'
        output_folder = 'output'

        polydif_filename = os.path.join(working_directory, polydif_filename)
        output_filename = os.path.join(working_directory, output_folder, 'output_polydif.xlsx')

        open_output = 1

        polydif.generate(polydif_filename, output_filename, self.all_sequences,
                         self.all_nodes, self.start_node, self.GOS_interface, open_output=open_output)

def run():

    app = QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())

if __name__ == '__main__':

    run()
