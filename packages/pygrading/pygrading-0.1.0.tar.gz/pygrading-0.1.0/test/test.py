from pygrading.html import *

a = table(border="1")

for i in range(4):
    b = tr()
    for j in range(4):
        b << td(font(color="red").set_text("(" + str(i) + "," + str(j) + ")"))
    a << b

a.print()
