#!/usr/bin/env python

# This code should allow for scanner triggering at any point during the breath cycle
# as well as control of the breath cycle. May 23, 2016 by TA

# Import required libraries
import threading
import time
from Tkinter import *
from PIL import Image, ImageTk
from itertools import cycle
from math import *
import RPi.GPIO as io


# GPIO pin assignment and initialization
N2=17
O2=4
HP=22
CAPT=19
VENT=5
Trigger=16

io.setmode(io.BCM)
io.setup(O2,io.OUT)
io.setup(N2,io.OUT)
io.setup(HP,io.OUT)
io.setup(VENT,io.OUT)
io.setup(Trigger,io.OUT)

io.output(Trigger,1)

# GUI stuff

class MyApp(Tk):
    global tk
    tk = Tk()
    tk.geometry("1200x800")
    tk.configure(background='white')


    def __init__(self): 
        self.my_widgets()
        self.event= threading.Event()
        
        
    # All GUI entry and building
    def my_widgets(self):
        # Logo entry
        image=Image.open("/home/pi/Desktop/noulsmatic_v2/logo2.jpg")
        photo=ImageTk.PhotoImage(image)
        label=Label(image=photo)
        label.image=photo
        label.grid(row=59, column=1)

        # Setting breath rate
        Label(tk,text="Breath Rate (Br/min)",fg="blue",bg="white",font=('Arial',10,'bold')).grid(
            row=45, column =1,pady=20)
        tk.BrRate_var=StringVar(tk,value='100')
        tk.BrRate_var.trace("w",self.callback)
        tk.BrRate=Entry(tk,textvariable=tk.BrRate_var,state='normal',disabledforeground="red")
        tk.BrRate.grid(row=46, column =1)
        tk.BrRate.bind('<Return>',self.variableupdt)
        tk.submit_button=Button(tk,text="Get Single Breath Duration",fg="blue",bg="white",font=('Arial',12,'bold'),
                            command=self.calc_breathduration).grid(
                                row=48, column =1,pady=10)
    
        # Setting inhalation duration
        Label(tk,text="Inhalation Duration (msec)",fg="blue",bg="white",font=('Arial',10,'bold')).grid(
            row=50, column =1,pady=10)
        tk.InDuration_var=StringVar(tk,value='150')
        tk.InDuration_var.trace("w",self.callback)
        tk.InDuration=Entry(tk,textvariable=tk.InDuration_var,state='normal',disabledforeground="red")
        tk.InDuration.bind('<Return>',self.variableupdt)
        tk.InDuration.grid(row=51, column =1)

        # Setting breath hold duration
        Label(tk,text="Breath Hold Duration (msec)",fg="blue",bg="white",font=('Arial',10,'bold')).grid(
            row=52, column =1,pady=10)
        tk.BrHold_var=StringVar(tk,value='150')
        tk.BrHold_var.trace("w",self.callback)
        tk.BrHold=Entry(tk,textvariable=tk.BrHold_var,state='normal',disabledforeground="red")
        tk.BrHold.bind('<Return>',self.variableupdt)
        tk.BrHold.grid(row=53, column =1)


        tk.vari=IntVar()
        Checkbutton(tk, text="Freeze Breath Parameters",variable=tk.vari,fg="Red",bg="white",font=('Arial',10,'bold'),
                    command=self.nancheck).grid(
                        row=53, column =2,padx=20,pady=20)

  

        submit_button=Button(tk,text="Get Exhalation Duration",fg="blue",bg="white",font=('Arial',10,'bold'),
                         command=self.calc_exhalation).grid(
                             row=54, column =1,pady=10)
        

        Label(tk,text="Trigger delay (msec)",fg="blue",bg="white",font=('Arial',10,'bold')).grid(
            row=48, column =10,padx=20,pady=10)
        tk.Trig_var=StringVar(tk,value='5')
        tk.Trig_var.trace("w",self.callback)
        tk.Trig=Entry(tk,textvariable=tk.Trig_var)
        tk.Trig.bind('<Return>',self.variableupdt)
        tk.Trig.grid(row=49, column =10,padx=20)
        

        Label(tk,text="Trigger length(msec)",fg="blue",bg="white",font=('Arial',10,'bold')).grid(
            row=50, column =10,padx=20,pady=10)
        tk.TrigL_var=StringVar(tk,value='10')
        tk.TrigL_var.trace("w",self.callback)
        tk.TrigL=Entry(tk,textvariable=tk.TrigL_var)
        tk.TrigL.bind('<Return>',self.variableupdt)
        tk.TrigL.grid(row=51, column =10,padx=20)
        


        tk.var=IntVar()
        Checkbutton(tk, text="Trigger1",variable=tk.var,fg="Red",bg="white",font=('Arial',10,'bold'),onvalue=1,
                    command=self.cb,offvalue=0).grid(
                        row=48, column =12,padx=20,pady=20)
        

        StartN2=Button(tk,text="Start",fg="Blue",bg="white",font=('Arial',12,'bold'),
                       command=self.startN2).grid(row=49, column =12,padx=10,pady=10)
        
        StopN2=Button(tk,text="Stop",fg="Blue",bg="white",font=('Arial',12,'bold'),
                      command=self.stopN2).grid(row=51, column =12,padx=20,pady=10)

        #ResetParameters=Button(tk,text="Reset Parameters",fg="black",bg="green",font=('Arial',12,'bold'),
                               #command=self.resetParameters).grid(row=55,column=2,padx=10,pady=10)

       # ResetTrigger=Button(tk,text="Reset Trigger",fg="Green",bg="white",font=('Arial',12,'bold'),command=self.resetTrigger).grid(row=50,column=12,padx=10,pady=10)
       

        Xnuc=Button(tk,text="X-Nuclei",bg="yellow",font=('Arial',12,'bold'),
                    command=self.startHP).grid(row=55, column =10,padx=20,pady=20)
        
        n2=Button(tk,text="Nitrogen",fg="white",bg="black",font=('Arial',12,'bold'),
                  command=self.runn2).grid(row=55, column =12,padx=20,pady=20)
    

        Exit=Button(tk,text="Exit",bg="red",font=('Arial',12,'bold'),command=self.terminate).grid(row=0, column =30,padx=10,pady=10)


    def callback(self, *args):
        print "Variable Change!"

    def variableupdt(self,*args):
        global gas, Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen
        Inhalation=float(tk.InDuration_var.get())/1000
        Hold=float(tk.BrHold_var.get())/1000
        breaths=float(tk.BrRate_var.get())
        rateperiod=float(60) #1 min in sec
        singleduration=float(rateperiod/breaths)
        Exhalation=float(singleduration-(Inhalation+Hold))
        triggerdelay=float(tk.Trig_var.get())/1000
        triglen=float(tk.TrigL_var.get())/1000
                 
    def nancheck(self):
          print "check"
          if tk.vari.get() == 1:
              tk.BrRate.configure(state='disabled')
              tk.BrHold.configure(state='disabled')
              tk.InDuration.configure(state='disabled')
          else:
              tk.BrRate.configure(state='normal')
              tk.BrHold.configure(state='normal')
              tk.InDuration.configure(state='normal')
        
        
    def cb(self):
        print "trigger is", tk.var.get()   

    def calc_breathduration(self):
        breaths=float(tk.BrRate_var.get())
        rateperiod=float(60) #1 min in sec
        singleduration=float(rateperiod/breaths)
        labelresult=Label(tk,text="Breath Duration =  %g  sec" %singleduration,bg="white",font=('Arial',12,'bold')).grid(row=1, column =10)
        return singleduration

    def calc_exhalation(self):
        Inhalation=float(tk.InDuration_var.get())/1000
        Hold=float(tk.BrHold_var.get())/1000
        breaths=float(tk.BrRate_var.get())
        rateperiod=float(60) #1 min in sec
        singleduration=float(rateperiod/breaths)
        Exhalation=float(singleduration-(Inhalation+Hold))
        labelresult=Label(tk,text="Exhalation Duration = %g  sec" %Exhalation,bg="white",font=('Arial',12,'bold')).grid(row=2, column =10)
        return Exhalation

    def TrigInhal(self):
        global gas, Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen
        self.variableupdt()
        LeftInhalation=Inhalation-(triggerdelay+triglen)
        while not self.event.is_set():
            #Start the breath cycle
            print "In"
            io.output(O2,1)
            io.output(gas,1)
            time.sleep(triggerdelay)
            io.output(Trigger,0)
            print "trigger on"
            time.sleep(triglen)
            io.output(Trigger,1)
            print "trigger off"
            time.sleep(LeftInhalation)
            print "Hold"
            io.output(O2,0)
            io.output(gas,0)
            time.sleep(Hold)
            io.output(VENT,1)
            print "Out "
            time.sleep(float( Exhalation))
            io.output(VENT,0)

    def triggerhold(self):
        global gas, Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen
        self.variableupdt()
        T1=triggerdelay-Inhalation
        LeftHold=Hold-(T1+triglen)
        while not self.event.is_set():
            print "In"
            io.output(O2,1)
            io.output(gas,1)
            time.sleep(Inhalation)
            print "Hold"
            io.output(O2,0)
            io.output(gas,0)
            time.sleep(T1)
            io.output(Trigger,0)
            print "trigger on"
            time.sleep(triglen)
            io.output(Trigger,1)
            print "trigger off"
            time.sleep(LeftHold)
            io.output(VENT,1)
            print "Out "
            time.sleep(float( Exhalation))
            io.output(VENT,0)

    def triggerexhl(self):
        global gas, Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen
        self.variableupdt()
        T2=triggerdelay-(Hold+Inhalation)
        Leftexhl=singleduration-(Hold+Inhalation+T2+triglen)

        while not self.event.is_set():
            print "In"
            io.output(O2,1)
            io.output(gas,1)
            time.sleep(Inhalation)
            print "Hold"
            io.output(O2,0)
            io.output(gas,0)
            time.sleep(Hold)
            io.output(VENT,1)
            time.sleep(T2)
            io.output(Trigger,0)
            print "trigger on"
            time.sleep(triglen)
            io.output(Trigger,1)
            print "trigger off"
            print "Out "
            time.sleep(float( Leftexhl))
            io.output(VENT,0)

    def choosetrigcycle(self):
         global gas, Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen
         #while not self.event.is_set():
         if (triggerdelay >= Inhalation) and ((triggerdelay + triglen)<=(Inhalation+Hold)): #using less than or equal to allows imaging at end br hold              
             print "trigger in hold"               
             self.triggerhold()
         elif ((triggerdelay+triglen)<=Inhalation): #using less than or equal to allows imaging at end inhalation
             print "trigger in inhalation"
             self.TrigInhal()
         elif (triggerdelay >= Inhalation+Hold) and ((triggerdelay+triglen)<=(singleduration)):#using less than or equal to allows imaging at end exhalation
             print "trigger in exhalation"   
             self.triggerexhl()
         else:
             self.TrigInhal()
         return Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen
         

    def threadsup(self):
        global breath
        breath=threading.Thread(target=self.choosetrigcycle)
        breath.setDaemon(True)
        if (tk.var.get()==0):
              breath.start()
        else:
            breath=threading.Thread(target=self.choosetrigcycle)
            breath.start()
                    
                       
    def startN2(self):
        global gas, running
        io.output(O2,0)
        io.output(N2,0)
        io.output(VENT,0)
        io.output(HP,0)
        io.output(Trigger,0)
        self.variableupdt()
        gas=N2     
        self.threadsup()
        self.event.clear()
        print ("N2 starting")
  

    def stopN2(self):
        global tN2, trig, Hp, running
        io.output(N2,0)
        self.event.set()

    def resetParameters(self):
        global gas, Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen
        Inhalation=float(tk.InDuration_var.get())/1000
        Hold=float(tk.BrHold_var.get())/1000
        breaths=float(tk.BrRate_var.get())
        rateperiod=float(60) #1 min in sec
        singleduration=float(rateperiod/breaths)
        Exhalation=float(singleduration-(Inhalation+Hold))
        triggerdelay=float(tk.Trig_var.get())/1000
        triglen=float(tk.TrigL_var.get())/1000

    def resetTrigger(self):
        global triggerdelay, triglen
        #self.event.clear()
        #self.event.set()
        triggerdelay=float(tk.Trig_var.get())/1000
        triglen=float(tk.TrigL_var.get())/1000
    
    def startHP(self):
        global gas, running, Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen
        Inhalation=float(tk.InDuration_var.get())/1000
        Hold=float(tk.BrHold_var.get())/1000
        breaths=float(tk.BrRate_var.get())
        rateperiod=float(60) #1 min in sec
        singleduration=float(rateperiod/breaths)
        Exhalation=float(singleduration-(Inhalation+Hold))
        triggerdelay=float(tk.Trig_var.get())/1000
        triglen=float(tk.TrigL_var.get())/1000
        io.output(N2,0)
        gas=HP
        print ("Hp starting")
        #self.threadsup()
        self.event.clear()
        #print ("N2 starting")
          
        
    def runn2(self):
        global gas
        io.output(HP,0)
        gas=N2
        print ("N2 starting")
        
    
    def terminate(self):
        io.output(O2,0)
        io.output(N2,0)
        io.output(VENT,0)
        io.output(HP,0)
        io.output(Trigger,0)
        
        global tk
        tk.destroy()


def main():
   
    app = MyApp()
    tk.mainloop()
    io.cleanup()

if __name__ == "__main__":
    main()
    
