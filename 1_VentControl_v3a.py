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
#PJN - Setup an additional "Pin" to deal with wash in and wash out - This isn't actually a pin number, but just a trigger to run wash in and wash out
#WIO = 0

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
    #PJN edit size of application
    tk.geometry("800x1200")
    tk.configure(background='white')


    def __init__(self): 
        self.my_widgets()
        self.event= threading.Event()
        self.IKEDEBUGMODE = 1
        self.LABELTOGGLE = 0
        
    # All GUI entry and building
    def my_widgets(self):
        # Logo entry
        image=Image.open("/home/pi/Desktop/noulsmatic_v2/logo2.jpg")
        photo=ImageTk.PhotoImage(image)
        label=Label(image=photo)
        label.image=photo
        label.grid(row=1, column=1)
        label.grid(columnspan = 2)
#PJN try a different method of placing this that might be better
        #label.place(relx=0.25,rely=0.05)
        # Setting breath rate
        Label(tk,text="Breath Rate (Br/min)",fg="blue",bg="white",font=('Arial',12,'bold')).grid(
            row=45, column =1,pady=10)
        #PJN Change method of setting location to make this prettier
        #Label(tk,text="Breath Rate (Br/min)",fg="blue",bg="white",font=('Arial',10,'bold')).place(
        #    relx=0.1, rely = 0.25)
        #PJN change default breath rate from 100 to 80
        tk.BrRate_var=StringVar(tk,value='80')
        tk.BrRate_var.trace("w",self.callback)
        tk.BrRate=Entry(tk,textvariable=tk.BrRate_var,state='normal',disabledforeground="red")
        tk.BrRate.grid(row=46, column =1)
        tk.BrRate.bind('<Return>',self.variableupdt)
        tk.submit_button=Button(tk,text="Get Single Breath Duration",fg="black",bg="white",font=('Arial',12,'bold'),
                            command=self.calc_breathduration).grid(
                                row=47, column =1,pady=10)
        #PJN Change Location to make this prettier
      #  tk.submit_button=Button(tk,text="Get Single Breath Duration",fg="blue",bg="white",font=('Arial',12,'bold'),
       #                     command=self.calc_breathduration).place(
        #                        relx=0.1, rely=0.28)
    
        # Setting inhalation duration
        Label(tk,text="Inhalation Duration (msec)",fg="blue",bg="white",font=('Arial',12,'bold')).grid(
            row=49, column =1,pady=10)
        #PJN try a different method of placing this that might be better
        #Label(tk,text="Inhalation Duration (msec)",fg="blue",bg="white",font=('Arial',10,'bold')).place(
        #    relx=0.1, rely = 0.32)
        #PJN change default value from 150 to 200
        tk.InDuration_var=StringVar(tk,value='200')
        tk.InDuration_var.trace("w",self.callback)
        tk.InDuration=Entry(tk,textvariable=tk.InDuration_var,state='normal',disabledforeground="red")
        tk.InDuration.bind('<Return>',self.variableupdt)
        tk.InDuration.grid(row=50, column =1)
        #PJN Change method of placing this to make this prettier
        #tk.InDuration.place(relx=0.1, rely =0.35)

        # Setting breath hold duration
        Label(tk,text="Breath Hold Duration (msec)",fg="blue",bg="white",font=('Arial',12,'bold')).grid(
            row=51, column =1,pady=10)
        #PJN Change Default Breathhold from 150 to 200
        tk.BrHold_var=StringVar(tk,value='200')
        tk.BrHold_var.trace("w",self.callback)
        tk.BrHold=Entry(tk,textvariable=tk.BrHold_var,state='normal',disabledforeground="red")
        tk.BrHold.bind('<Return>',self.variableupdt)
        tk.BrHold.grid(row=52, column =1)

#PJN Change column from 2 to 1 for the "Freeze Breath Parameters Button
        tk.vari=IntVar()
        Checkbutton(tk, text="Freeze Breath Parameters",variable=tk.vari,fg="black",bg="white",font=('Arial',12,'bold'),
                    command=self.nancheck).grid(
                        row=55, column =1,padx=20,pady=20)

  

        submit_button=Button(tk,text="Get Exhalation Duration",fg="black",bg="white",font=('Arial',12,'bold'),
                         command=self.calc_exhalation).grid(
                             row=53, column =1,pady=10)
        

        Label(tk,text="Trigger delay (msec)",fg="Red",bg="white",font=('Arial',12,'bold')).grid(
            row=45, column =3,padx=20,pady=10)
        tk.Trig_var=StringVar(tk,value='250')
        tk.Trig_var.trace("w",self.callback)
        tk.Trig=Entry(tk,textvariable=tk.Trig_var)
        tk.Trig.bind('<Return>',self.variableupdt)
        tk.Trig.grid(row=46, column =3,padx=20)
        

        Label(tk,text="Trigger length(msec)",fg="Red",bg="white",font=('Arial',12,'bold')).grid(
            row=47, column =3,padx=20,pady=10)
        tk.TrigL_var=StringVar(tk,value='10')
        tk.TrigL_var.trace("w",self.callback)
        tk.TrigL=Entry(tk,textvariable=tk.TrigL_var)
        tk.TrigL.bind('<Return>',self.variableupdt)
        tk.TrigL.grid(row=48, column =3,padx=20)
        


        tk.var=IntVar()
        Checkbutton(tk, text="Trigger1",variable=tk.var,fg="Red",bg="white",font=('Arial',12,'bold'),onvalue=1,
                    command=self.cb,offvalue=0).grid(
                        row=49, column =3,padx=20,pady=10)
        
        
        tk.StartVent=Button(tk,text="Start",fg="Black",bg="green",font=('Arial',20,'bold'),state='normal',
                       command=self.startvent)
        tk.StartVent.grid(row=55, column =2,padx=10,pady=10) #MC tag

        tk.StopVent=Button(tk,text="Stop",fg="Black",bg="Red",font=('Arial',20,'bold'), state='normal',
                      command=self.stopvent)
        tk.StopVent.grid(row=56, column =2,padx=20,pady=10)

        #ResetParameters=Button(tk,text="Reset Parameters",fg="black",bg="green",font=('Arial',12,'bold'),
                               #command=self.resetParameters).grid(row=55,column=2,padx=10,pady=10)

       # ResetTrigger=Button(tk,text="Reset Trigger",fg="Green",bg="white",font=('Arial',12,'bold'),command=self.resetTrigger).grid(row=50,column=12,padx=10,pady=10)
       #PJN 5/19/2020 - add stuff for washin/washout
        tk.wiocb=IntVar()
        Checkbutton(tk, text="Wash in/Wash Out",variable=tk.wiocb,fg="Red",bg="white",font=('Arial',12,'bold'),onvalue=1,
                    command=self.wiocheck,offvalue=0).grid(
                        row=57, column =1,padx=20,pady=20)
        
        Label(tk,text="Number Wash in Breaths",fg="blue",bg="white",font=('Arial',12,'bold')).grid(
            row=58, column =1,pady=10)

        tk.NWashin_var=StringVar(tk,value='5')
        tk.NWashin_var.trace("w",self.callback)
        tk.NWashin=Entry(tk,textvariable=tk.NWashin_var,state='disabled',disabledforeground="red")
        tk.NWashin.bind('<Return>',self.variableupdt)
        tk.NWashin.grid(row=59, column =1)
        
        Label(tk,text="Number Wash out Breaths",fg="blue",bg="white",font=('Arial',12,'bold')).grid(
            row=60, column =1,pady=10)

        tk.NWashout_var=StringVar(tk,value='5')
        tk.NWashout_var.trace("w",self.callback)
        tk.NWashout=Entry(tk,textvariable=tk.NWashout_var,state='disabled',disabledforeground="red")
        tk.NWashout.bind('<Return>',self.variableupdt)
        tk.NWashout.grid(row=61, column =1)
        
        tk.StartWIWO=Button(tk,text="Start Wash in/out",fg="Black",bg="cyan",state='disabled',font=('Arial',20,'bold'),
                       command=self.startwiwo)
        tk.StartWIWO.grid(row=57, column =3,padx=10,pady=10)

        tk.StartHP=Button(tk,text="X-Nuclei",bg="yellow",font=('Arial',20,'bold'),state='disabled',
                    command=self.starthp)
        tk.StartHP.grid(row=55, column =3,padx=20,pady=20)
        
      #  tk.WIO_var=StringVar(tk,value='0')
      # tk.WIO_var.trace("w",self.callback)
      #  tk.WIO=Entry(tk,textvariable=tk.WIO_var,state='disabled',disabledforeground="red")
      #  tk.WIO.bind('<Return>',self.variableupdt)
      #  tk.WIO.grid(row=57, column =2)
        
        tk.StartN2=Button(tk,text="Nitrogen",fg="white",bg="black", state='disabled',font=('Arial',20,'bold'),
                  command=self.startn2)
        tk.StartN2.grid(row=56, column =3,padx=20,pady=20)
    

        Exit=Button(tk,text="Exit",bg="red",font=('Arial',12,'bold'),command=self.terminate).grid(row=100, column =3,padx=10,pady=10)

    def callback(self, *args):
        print "Variable Change!"

    def variableupdt(self,*args):
        global gas, Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen, WashIn, WashOut, WIO
        Inhalation=float(tk.InDuration_var.get())/1000
        Hold=float(tk.BrHold_var.get())/1000
        breaths=float(tk.BrRate_var.get())
        rateperiod=float(60) #1 min in sec
        singleduration=float(rateperiod/breaths)
        Exhalation=float(singleduration-(Inhalation+Hold))
        triggerdelay=float(tk.Trig_var.get())/1000
        triglen=float(tk.TrigL_var.get())/1000
        WashIn = int(tk.NWashin_var.get())
        WashOut = int(tk.NWashout_var.get())
        #WIO = int(tk.WIO_var.get())
                 
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
        #PJN Add for washin washout
    def wiocheck(self):
          #print "check"
          if tk.wiocb.get() == 0:
              tk.NWashout.configure(state='disabled')
              tk.NWashin.configure(state='disabled')
              tk.StartWIWO.configure(state='disabled')
          else:
              tk.NWashin.configure(state='normal')
              tk.NWashout.configure(state='normal')
              if self.LABELTOGGLE == 1:
                  tk.StartWIWO.configure(state='normal')    
        
    def cb(self):
        print "trigger is", tk.var.get()   

    def calc_breathduration(self):
        breaths=float(tk.BrRate_var.get())
        rateperiod=float(60) #1 min in sec
        singleduration=float(rateperiod/breaths)
        labelresult=Label(tk,text="Breath Duration =  %g  sec" %singleduration,bg="white",font=('Arial',12,'bold')).grid(row=48, column =1)
        return singleduration

    def calc_exhalation(self):
        Inhalation=float(tk.InDuration_var.get())/1000
        Hold=float(tk.BrHold_var.get())/1000
        breaths=float(tk.BrRate_var.get())
        rateperiod=float(60) #1 min in sec
        singleduration=float(rateperiod/breaths)
        Exhalation=float(singleduration-(Inhalation+Hold))
        labelresult=Label(tk,text="Exhalation Duration = %g  sec" %Exhalation,bg="white",font=('Arial',12,'bold')).grid(row=54, column =1)
        return Exhalation

    def TrigInhal(self):
        global gas, Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen, WashIn, WashOut, WIO
        self.variableupdt()
        LeftInhalation=Inhalation-(triggerdelay+triglen)
        while not self.event.is_set():
            #self.variableupdt()
            if WIO == 1:
                io.output(N2,0)
                for x in range(0,WashIn):
                    y = x+1
                    print "Begin Wash In Breath ",y
                    io.output(O2,1)
                    io.output(HP,1)
                    time.sleep(triggerdelay)
                    io.output(Trigger,0)
                    print "trigger on"
                    time.sleep(triglen)
                    io.output(Trigger,1)
                    print "trigger off"
                    time.sleep(LeftInhalation)
                    print "Hold"
                    io.output(O2,0)
                    io.output(HP,0)
                    time.sleep(Hold)
                    io.output(VENT,1)
                    print "End Wash In Breath ",y
                    time.sleep(float( Exhalation))
                    io.output(VENT,0)
                for x in range(0,WashOut):
                    y = x+1
                    print "Begin Wash Out Breath ",y
                    io.output(O2,1)
                    io.output(N2,1)
                    time.sleep(triggerdelay)
                    io.output(Trigger,0)
                    print "trigger on"
                    time.sleep(triglen)
                    io.output(Trigger,1)
                    print "trigger off"
                    time.sleep(LeftInhalation)
                    print "Hold"
                    io.output(O2,0)
                    io.output(N2,0)
                    time.sleep(Hold)
                    io.output(VENT,1)
                    print "End Wash Out Breath ",y
                    time.sleep(float( Exhalation))
                    io.output(VENT,0)
            else:      
            
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
        global gas, Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen, WashIn, WashOut, WIO
        self.variableupdt()
        T1=triggerdelay-Inhalation
        LeftHold=Hold-(T1+triglen)
        while not self.event.is_set():
            #self.variableupdt()
            #print WIO
            if WIO == 1:
                io.output(N2,0)
                for x in range(0,WashIn):
                    y = x+1
                    print "Begin Wash In Breath ",y
                    io.output(O2,1)
                    io.output(HP,1)
                    time.sleep(Inhalation)
                    print "Hold"
                    io.output(O2,0)
                    io.output(HP,0)
                    time.sleep(T1)
                    io.output(Trigger,0)
                    print "trigger on"
                    time.sleep(triglen)
                    io.output(Trigger,1)
                    print "trigger off"
                    time.sleep(LeftHold)
                    io.output(VENT,1)
                    print "End Wash In Breath ",y
                    time.sleep(float( Exhalation))
                    io.output(VENT,0)
                for x in range(0,WashOut):
                    y = x+1
                    print "Begin Wash Out Breath ",y
                    io.output(O2,1)
                    io.output(N2,1)
                    time.sleep(Inhalation)
                    print "Hold"
                    io.output(O2,0)
                    io.output(N2,0)
                    time.sleep(T1)
                    io.output(Trigger,0)
                    print "trigger on"
                    time.sleep(triglen)
                    io.output(Trigger,1)
                    print "trigger off"
                    time.sleep(LeftHold)
                    io.output(VENT,1)
                    print "End Wash Out Breath ",y
                    time.sleep(float( Exhalation))
                    io.output(VENT,0)
            else:
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
        global gas, Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen, WashIn, WashOut, WIO
        self.variableupdt()
        T2=triggerdelay-(Hold+Inhalation)
        Leftexhl=singleduration-(Hold+Inhalation+T2+triglen)
        while not self.event.is_set():
            #self.variableupdt()
            if WIO == 1:    
                io.output(N2,0)
                for x in range(0,WashIn):
                    y = x+1
                    print "Begin Wash In Breath ",y
                    io.output(O2,1)
                    io.output(HP,1)
                    time.sleep(Inhalation)
                    print "Hold"
                    io.output(O2,0)
                    io.output(HP,0)
                    time.sleep(Hold)
                    io.output(VENT,1)
                    time.sleep(T2)
                    io.output(Trigger,0)
                    print "trigger on"
                    time.sleep(triglen)
                    io.output(Trigger,1)
                    print "trigger off"
                    print "End Wash In Breath ",y
                    time.sleep(float( Leftexhl))
                    io.output(VENT,0)
                for x in range(0,WashOut):
                    y = x+1
                    print "Begin Wash Out Breath ",y
                    io.output(O2,1)
                    io.output(N2,1)
                    time.sleep(Inhalation)
                    print "Hold"
                    io.output(O2,0)
                    io.output(N2,0)
                    time.sleep(Hold)
                    io.output(VENT,1)
                    time.sleep(T2)
                    io.output(Trigger,0)
                    print "trigger on"
                    time.sleep(triglen)
                    io.output(Trigger,1)
                    print "trigger off"
                    print "End Wash Out Breath ",y
                    time.sleep(float( Leftexhl))
                    io.output(VENT,0)
            else:
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
         global gas, Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen, WashIn, WashOut, WIO
         #while not self.event.is_set():
         if (triggerdelay >= Inhalation) and ((triggerdelay + triglen)<=(Inhalation+Hold)): #using less than or equal to allows imaging at end br hold              
             if self.IKEDEBUGMODE ==1:
                 print "triggerdelay = "+str(triggerdelay)
                 print "triglen = "+str(triglen)
                 print "Inhalation = "+str(Inhalation)
                 print "Hold = "+str(Hold)
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
         return Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen, WashIn, WashOut, WIO
         

    def threadsup(self):
        global breath
        breath=threading.Thread(target=self.choosetrigcycle)
        breath.setDaemon(True)
        if (tk.var.get()==0):
              breath.start()
        else:
            breath=threading.Thread(target=self.choosetrigcycle)
            breath.start()
    

    def startvent(self):
        global gas, running, WIO
        io.output(O2,0)
        io.output(N2,0)
        io.output(VENT,0)
        io.output(HP,0)
        io.output(Trigger,0)
        #tk.WIO_var.set(value='0')
        self.variableupdt()
        gas=N2
        WIO=0
        self.threadsup()
        #self.switchbutton()
        #print ("N2 starting")
        self.LABELTOGGLE =1
        #if self.LABELTOGGLE == 1:
        labelresult=Label(tk,text="Ventilating with N2/O2!",fg="red",bg="white",font=('Arial',24,'bold')).grid(row=58, column =3)
        tk.StartVent.configure(state='disabled')
        tk.StartHP.configure(state='normal')
        tk.StartN2.configure(state='disabled')
        if tk.wiocb.get() == 1:
            tk.StartWIWO.configure(state='normal')
        self.event.clear()
        #tk.StopVent.configure(state='normal')


    def stopvent(self):
        global tN2, trig, Hp, running, WIO
        io.output(N2,0)
        #tk.WIO_var.set(value='0')
        WIO = 0
        self.event.set()
        labelresult=Label(tk,text="   Ventilation Stopped!   ",bg="white",font=('Arial',24,'bold')).grid(row=58, column =3)
        tk.StartVent.configure(state='normal')
        tk.StartHP.configure(state='disabled')
        tk.StartN2.configure(state='disabled')
        tk.StartWIWO.configure(state='disabled')
        
        self.LABELTOGGLE = 0



    def resetParameters(self):
        global gas, Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen, WashIn, WashOut, WIO
        Inhalation=float(tk.InDuration_var.get())/1000
        Hold=float(tk.BrHold_var.get())/1000
        breaths=float(tk.BrRate_var.get())
        rateperiod=float(60) #1 min in sec
        singleduration=float(rateperiod/breaths)
        Exhalation=float(singleduration-(Inhalation+Hold))
        triggerdelay=float(tk.Trig_var.get())/1000
        triglen=float(tk.TrigL_var.get())/1000
        WashIn = int(tk.NWashin_var.get())
        WashOut = int(tk.NWashout_var.get())
        #WIO = int(tk.WIO_var.get())

    def resetTrigger(self):
        global triggerdelay, triglen
        #self.event.clear()
        #self.event.set()
        triggerdelay=float(tk.Trig_var.get())/1000
        triglen=float(tk.TrigL_var.get())/1000
    
    def starthp(self):  #"start HP"
        global gas, running, Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen, WashIn, WashOut, WIO
        Inhalation=float(tk.InDuration_var.get())/1000
        Hold=float(tk.BrHold_var.get())/1000
        breaths=float(tk.BrRate_var.get())
        rateperiod=float(60) #1 min in sec
        singleduration=float(rateperiod/breaths)
        Exhalation=float(singleduration-(Inhalation+Hold))
        triggerdelay=float(tk.Trig_var.get())/1000
        triglen=float(tk.TrigL_var.get())/1000
        WashIn = int(tk.NWashin_var.get())
        WashOut = int(tk.NWashout_var.get())
        #tk.WIO_var.set(value='0')
        WIO = 0
        io.output(N2,0)
        gas=HP
        #print ("Hp starting")
        if self.LABELTOGGLE == 1:
            labelresult=Label(tk,text="Ventilating with Xe/O2!",fg="green",bg="white",font=('Arial',24,'bold')).grid(row=58, column =3)
        #self.threadsup()
        self.event.clear()
        #print ("N2 starting")
        tk.StartHP.configure(state='disable')
        tk.StartN2.configure(state='normal')
        if tk.wiocb.get() == 1:
            tk.StartWIWO.configure(state='normal')
        
   #PJN function to do washin-washout       
    def startwiwo(self):  #"wash in wash out"
        global gas, running, Inhalation, Hold, breaths, rateperiod, singleduration, Exhalation, triggerdelay, triglen, WashIn, WashOut, WIO
        Inhalation=float(tk.InDuration_var.get())/1000
        Hold=float(tk.BrHold_var.get())/1000
        breaths=float(tk.BrRate_var.get())
        rateperiod=float(60) #1 min in sec
        singleduration=float(rateperiod/breaths)
        Exhalation=float(singleduration-(Inhalation+Hold))
        triggerdelay=float(tk.Trig_var.get())/1000
        triglen=float(tk.TrigL_var.get())/1000
        WashIn = int(tk.NWashin_var.get())
        WashOut = int(tk.NWashout_var.get())
        #tk.WIO_var.set(value='1')
        WIO=1
        #io.output(N2,0)
        #gas=WIO
        #print ("Hp starting")
        labelresult=Label(tk,text="    Wash in/Wash Out    ",fg="cyan",bg="white",font=('Arial',24,'bold')).grid(row=58, column =3)
        #self.threadsup()
        self.event.clear()
        tk.StartHP.configure(state='normal')
        tk.StartN2.configure(state='normal')
        tk.StartWIWO.configure(state='disabled')
        
        #print ("N2 starting")
        
    def startn2(self): 
        global gas, WIO
        io.output(HP,0)
        #tk.WIO_var.set(value='0')
        WIO=0
        gas=N2
        #print ("N2 starting")
        #self.switchbutton() #tag MC
        if self.LABELTOGGLE == 1:
            labelresult=Label(tk,text="Ventilating with N2/O2!",fg="red",bg="white",font=('Arial',24,'bold')).grid(row=58, column =3)
        tk.StartN2.configure(state='disabled')
        tk.StartHP.configure(state='normal')
        if tk.wiocb.get() == 1:
            tk.StartWIWO.configure(state='normal')
                
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
    
