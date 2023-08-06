"""
Lucifer Monao, copyright 2020.1.29, for more infos see README.md

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

See LICENCE.txt for more information
"""

from tkinter import messagebox
from colorama import *
import sys
import math
import psutil
import platform
from datetime import datetime
from string import *
import random


#PRINT

def pa(arg1,arg2):
    #initializing back as info if back argument is used.
    back = False
    #initializing above5 as info if arg1 is has 6 charakters without c, clear, r and reset
    above5 = False
    CURSOR_UP_ONE = '\x1b[1A'
    ERASE_LINE = '\x1b[2K'
    if len(arg1) > 0:
        if arg1[0] == "f":
            if arg1[1] == "b":
                print(Fore.BLACK)
            elif arg1[1] == "r":
                print(Fore.RED)
            elif arg1[1] == "g":
                print(Fore.GREEN)
            elif arg1[1] == "y":
                print(Fore.YELLOW)
            elif arg1[1] == "l":
                print(Fore.BLUE)
            elif arg1[1] == "m":
                print(Fore.MAGENTA)
            elif arg1[1] == "c":
                print(Fore.CYAN)
            elif arg1[1] == "w":
                print(Fore.WHITE)
            else:
                return("Error")
                print(Fore.RED, Back.MAGENTA, "Error, no Color")
            if len(arg1) > 2:
                if arg1[2] == "b":
                    sys.stdout.write(CURSOR_UP_ONE)
                    sys.stdout.write(ERASE_LINE)
                    back = True
                    if arg1[3] == "b":
                        if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                            print(Back.BLACK,arg2, Style.RESET_ALL)
                        else:
                            print(Back.BLACK,arg2)
                    elif arg1[3] == "r":
                        if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                            print(Back.RED,arg2, Style.RESET_ALL)
                        else:
                            print(Back.RED,arg2)
                    elif arg1[3] == "g":
                        if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                            print(Back.GREEN,arg2, Style.RESET_ALL)
                        else:
                            print(Back.GREEN,arg2)
                    elif arg1[3] == "y":
                        if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                            print(Back.YELLOW,arg2, Style.RESET_ALL)
                        else:
                            print(Back.YELLOW,arg2)
                    elif arg1[3] == "l":
                        if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                            print(Back.BLUE,arg2, Style.RESET_ALL)
                        else:
                            print(Back.BLUE,arg2)
                    elif arg1[3] == "m":
                        if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                            print(Back.MAGENTA,arg2, Style.RESET_ALL)
                        else:
                            print(Back.MAGENTA,arg2)
                    elif arg1[3] == "c":
                        if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                            print(Back.CYAN,arg2, Style.RESET_ALL)
                        else:
                            print(Back.CYAN,arg2)
                    elif arg1[3] == "w":
                        if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                            print(Back.WHITE,arg2, Style.RESET_ALL)
                        else:
                            print(Back.WHITE,arg2)
                    else:
                        return("Error")
                        print(Fore.RED, Back.MAGENTA, "Error, no Color")
                    if len(arg1) > 4: 
                        if arg1[4] == "s":
                            above5 = True
                            if arg1[5] == "d":
                                print(Style.DIM)
                            elif arg1[5] == "n":
                                print(Style.NORMAL)
                            elif arg1[5] == "b":
                                print(Style.BRIGHT)
                            else:
                                return("Error")
                                print(Fore.RED, Back.MAGENTA, "Error, no Style")
                elif arg1[2] == "s":
                    if arg1[3] == "d":
                        print(Style.DIM)
                    elif arg1[3] == "n":
                        print(Style.NORMAL)
                    elif arg1[3] == "b":
                        print(Style.BRIGHT)
                    else:
                        return("Error")
                        print(Fore.RED, Back.MAGENTA, "Error, no Style")
        elif arg1[0] == "b":
            back = True
            if arg1[1] == "b":
                if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                    print(Back.BLACK,arg2, Style.RESET_ALL)
                else:
                    print(Back.BLACK,arg2)
            elif arg1[1] == "r":
                if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                    print(Back.RED,arg2, Style.RESET_ALL)
                else:
                    print(Back.RED,arg2)
            elif arg1[1] == "g":
                if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                    print(Back.GREEN,arg2, Style.RESET_ALL)
                else:
                    print(Back.GREEN,arg2)
            elif arg1[1] == "y":
                if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                    print(Back.YELLOW,arg2, Style.RESET_ALL)
                else:
                    print(Back.YELLOW,arg2)
            elif arg1[1] == "l":
                if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                    print(Back.BLUE,arg2, Style.RESET_ALL)
                else:
                    print(Back.BLUE,arg2)
            elif arg1[1] == "m":
                if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                    print(Back.MAGENTA,arg2, Style.RESET_ALL)
                else:
                    print(Back.MAGENTA,arg2)
            elif arg1[1] == "c":
                if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                    print(Back.CYAN,arg2, Style.RESET_ALL)
                else:
                    print(Back.CYAN,arg2)
            elif arg1[1] == "w":
                if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                    print(Back.WHITE,arg2, Style.RESET_ALL)
                else:
                    print(Back.WHITE,arg2)
            else:
                return("Error")
                print(Fore.RED, Back.MAGENTA, "Error, no Color")
            if len(arg1) > 2:
                if arg1[2] == "s":
                    if arg1[3] == "d":
                        print(Style.DIM)
                    elif arg1[3] == "n":
                        print(Style.NORMAL)
                    elif arg1[3] == "b":
                        print(Style.BRIGHT)
                    else:
                        return("Error")
                        print(Fore.RED, Back.MAGENTA, "Error, no Style")
        elif arg1[0] == "s":
            if arg1[1] == "d":
                print(Style.DIM)
            elif arg1[1] == "n":
                print(Style.NORMAL)
            elif arg1[1] == "b":
                print(Style.BRIGHT)
            else:
                return("Error")
                print(Fore.RED, Back.MAGENTA, "Error, no Style")
        if back == False:
            if arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset":
                print(arg2, Style.RESET_ALL)
            else:
                print(arg2)
    
    if len(arg1) > 3 and (not (arg1[-1] == "r" or arg1[-1] == "c" or arg1[-1:-6] == "clear" or arg1[-1:-6] == "reset") or above5 == True):
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)
    
def p(text):
    if text[-5:] == "clear" or text[-5:] == "reset":
        print(text[0:(len(text)-5)], Style.RESET_ALL)
    else:
        print(text)



# INFO

def info(name, text):
    messagebox.showinfo(name, text)

def error(name, text):
    messagebox.showinfo(name, text)

def help(name, text):
    messagebox.showinfo(name, text)

def askokcancel(name, text):
    answer = messagebox.askokcancel(name, text)
    return(answer)

def askyesno(name, text):
    answer = messagebox.askyesno(name, text)
    return(answer)

def askyesnocancel(name, text):
    answer = messagebox.askyesnocancel(name, text)
    return(answer)

def askretrycancel(name, text):
    answer = messagebox.askretrycancel(name, text)
    return(answer)

def askquestion(name, text):
    answer = messagebox.askquestion(name, text)
    return(answer)


#COMPUTERINFO

#general system info
def geninf():
    uname = platform.uname()
    sys = uname.system
    node = uname.node
    release = uname.release
    version = uname.version
    machine = uname.machine
    processor = uname.processor
    return(sys, node, release, version, machine, processor)

#boot time
def bt():
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    return(bt.year, bt.month, bt.day, bt.hour, bt.minute, bt.second)

#CPU
# number of cores
def cpucores():
    pcores =  psutil.cpu_count(logical=False)
    lcores = psutil.cpu_count(logical=True)
    return(pcores, lcores)

# CPU frequencies
def cpufreq():
    cpufreq = psutil.cpu_freq()
    maxfreq = cpufreq.max
    minfreq = cpufreq.min
    curfreq = cpufreq.current
    return(maxfreq, minfreq, curfreq)

# CPU usage
def cpuusage():
    cpuusge = psutil.cpu_percent()
    return(cpuusge)

# Memory Information
# get the memory details
def memory():
    svmem = psutil.virtual_memory()
    totmem = svmem.total
    avamem = svmem.available
    usdmem = svmem.used
    return(totmem,avamem,usdmem)

# get the swap memory details (if exists)
def swap():
    swap = psutil.swap_memory()
    totswap = swap.total
    avaswap = swap.free
    usdswap = swap.used
    return(totswap,avaswap,usdswap)

#PRIMENUMBER

def ptest(num):
    a = [0]
    end = int(num)
    for x in range(2, end):
        end = int(num) / x
        if int(num) % x == 0:
                return("n")
                break
    else:
    # loop fell through without finding a factor
            return("p")

def rstring(lenght):
    letters = ascii_letters + digits + punctuation
    return(''.join(random.choice(letters) for i in range(lenght)))