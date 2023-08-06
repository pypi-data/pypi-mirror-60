from skidl import *

vcc, gnd = Net("VCC"), Net("GND")
r1, r2, r3, r4 = Part("Device", "R", dest=TEMPLATE) * 4
par_ntwk = vcc & (r1 | r2 | r3 | r4) & gnd
dot = generate_graph()
dot.format = "svg"
dot.render("par_ntwk")
