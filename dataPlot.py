#!/usr/bin/env python

# Simple canula pressure vs. time plotting script for use with the
# CCHMC CPIR mouse ventilator and related software. Takes a CSV log
# file and produces a 2D plot within the desired range.

import Tkinter
import csv
import matplotlib.pyplot as plt

time = []
canula = []

with open('VentilatorData.csv','rb') as f:
    reader = csv.reader(f)
    for row in reader:
        time.append(row[0])
        canula.append(row[1])

class Application(Tkinter.Frame):
    def scale_data(self,time_domain,pressure_range,upper_bound,lower_bound):
        for value in time_domain:
            if (value > lower_bound) and (value < upper_bound):
                new_domain.append(time_domain[value])
                new_range.append(pressure_range[value])

    def create_widgets(self):
        self.QUIT = Tkinter.Button(self)
        self.QUIT['text'] = "Quit"
        self.QUIT['fg'] = "red"
        self.QUIT['command'] = self.quit

        self.QUIT.pack({'side':'left'})

        self.SCALE = Tkinter.Scale(self)
        self.SCALE[
    
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        self.pack()
        self.create_widgets()

def main():
    # plt.plot(time, canula)
    # plt.show()

    root = Tkinter.Tk()
    app = Application(master=root)
    app.mainloop()
    root.destroy()

if __name__ == "__main__":
    main()
    
