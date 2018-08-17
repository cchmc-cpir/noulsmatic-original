#!/usr/bin/env python

# data_display.py
# Application designed to generate 2D plots from ventilator data
# saved to CSV files. Part of the "noulsmatic_v2" package.
# Written by Alex Cochran, 2017

import os
import sys
import Tkinter
import csv
import matplotlib.pyplot as plt
import datetime

# application wrap
class Application(Tkinter.Frame):
    # initialize lists for each important data type (found in the csv file)
    time = []
    canula = []

    # truncate file at last line (in case of incomplete data)
    # temporary solution- would be more efficient if this could be done during CSV reading
    def trunc_file(self):
        # open the file for reading/updating
        filename = self.FILE_ENTRY.get()
        data_file = open(filename,'r+')

        # move pointer to end of file
        data_file.seek(0,os.SEEK_END)

        # if last line is null, delete last AND penultimate lines
        pos = data_file.tell() - 1

        # read backwards until hitting a newline, then exit the search
        while pos > 0 and data_file.read(1) != '\n':
            pos -= 1
            data_file.seek(pos,os.SEEK_SET)

        # if not at the start of the file, delete all characters ahead of the current position 
        if pos > 0:
            data_file.seek(pos,os.SEEK_SET)
            data_file.truncate()

        # close the file    
        data_file.close()

    # read the selected data file
    def read_file(self):
        filename = self.FILE_ENTRY.get()
        with open(filename,'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                if (row[0] != '') and (row[1] != ''):
                    self.time.append(row[0])
                    self.canula.append(row[1])

    # generate a plot based using the selected data file
    def plot_data(self):
        plt.plot(self.time,self.canula)
        plt.title("Pressure vs. Time [{:%Y-%m-%d %H:%M:%S}]".format(datetime.datetime.now()))
        plt.xlabel("Time [s]")
        plt.ylabel("Canula Pressure [cm H2O]")
        plt.savefig("/home/pi/Desktop/noulsmatic_v2/plots/p-vs-t_{:%Y-%m-%d_%H-%M-%S}".format(datetime.datetime.now()))
        plt.show()

    # GUI
    def create_widgets(self):
        # header
        self.HEADER = Tkinter.Label(self)
        self.HEADER['text'] = "To plot 2D data, enter the FULL PATH of the CSV file, click CONFIRM, then PLOT."
        self.HEADER.grid(row=0,column=0,columnspan=5)
        
        # quit button
        self.QUIT = Tkinter.Button(self)
        self.QUIT['text'] = "Quit"
        self.QUIT['fg'] = 'red'
        self.QUIT['command'] = self.quit
        self.QUIT.config(width=28)
        self.QUIT.grid(row=2,column=2,columnspan=2,sticky='w')
        
        # plot button
        self.PLOT = Tkinter.Button(self)
        self.PLOT['text'] = "Plot"
        self.PLOT['fg'] = 'blue'
        self.PLOT['command'] = self.plot_data
        self.PLOT.config(width=28)
        self.PLOT.grid(row=2,column=0,columnspan=2,sticky='e')
        
        # data file location: label
        self.FILE_ENTRY_LABEL = Tkinter.Label(self)
        self.FILE_ENTRY_LABEL['text'] = "File name: "
        self.FILE_ENTRY_LABEL['fg'] = 'blue'
        self.FILE_ENTRY_LABEL.grid(row=1,column=0,sticky='w')
        
        # data file location: entry
        self.FILE_ENTRY = Tkinter.Entry(self)
        self.FILE_ENTRY.config(width=44)
        self.FILE_ENTRY.insert(0,"home/pi/Desktop/noulsmatic_v2/")
        self.FILE_ENTRY.grid(row=1,column=1,columnspan=2,sticky='w')
        
        # data file location: confirm & pass
        self.FILE_ENTRY_CONFIRM = Tkinter.Button(self)
        self.FILE_ENTRY_CONFIRM['text'] = "Confirm"
        self.FILE_ENTRY_CONFIRM['fg'] = 'green'
        self.FILE_ENTRY_CONFIRM['command'] = lambda: [func() for func in [self. trunc_file, self.read_file]]
        self.FILE_ENTRY_CONFIRM.grid(row=1,column=3,sticky='e')

    # initialize object
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        self.pack()
        self.create_widgets()

# main function wrap
def main():
    root = Tkinter.Tk()
    app = Application(master=root)
    app.mainloop()
    root.destroy()

if __name__ == "__main__":
    main()
