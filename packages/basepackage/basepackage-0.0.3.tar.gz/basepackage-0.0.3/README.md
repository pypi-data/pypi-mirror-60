Hi!
This package can be used to shorten some commands from tkinter and colorama.
As so, 

import basepackage.module


Use:
:basepackage.module.pa(f for fore, b for back, s for style, with arguments:
-colors: b = Black, r = Red, g = Green, y = Yellow, l = Blue, m = Magenta, c = Cyan, w = White
-styles: d = dim, n = normal, b = bright
-c, clear, reset or r to reset all colors and styles after printing the word.
all in one argument, and the text in the second.

Use:
-basepackage.module.geninf(): to get sys, node, release, version, machine, processor
-basepackage.module.bt(): to get bt.year, bt.month, bt.day, bt.hour, bt.minute, bt.second
-basepackage.module.cpucores(): to get pcores and lcores
-basepackage.module.cpufreq(): to get maxfreq, minfreq, curfreq
-basepackage.module.cpuusage(): to get cpuusge
-basepackage.module.memory(): to get totmem,avamem,usdmem
-basepackage.module.swap(): to get totswap, avaswap, usdswap

Use:
basepackage.module.error/help/info/askokcancel/askyesno/askyesnocancel/askretrycancel/askquestion(name, text)
to get answer [short for tkinter messagebox]

Use:
basepackage.module.ptest(number to test if primenumber or not)
to get n for not a primenumber and p for primenumber

Use:
rstrng(lenght)
to get random string with digits, special characters and letters

This package was made on Linux Debian 10.2 with use of the GNOME Terminal, python 3.7.4 64-bit, base anaconda, and Visual Studio Code.