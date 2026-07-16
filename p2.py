import openseespy.opensees as ops
import opsvis as opsv
import matplotlib.pyplot as plt

# -------------------------------------------------
# MODEL
# -------------------------------------------------
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Node coordinates (m)
x = [0.0, 0.70, 1.10, 1.80, 2.20, 2.60, 3.20]

for i, xi in enumerate(x, start=1):
    ops.node(i, xi, 0.0)

# Supports
# B = node 2, F = node 6
ops.fix(2, 1, 1, 0)   # pin
ops.fix(6, 0, 1, 0)   # roller

# -------------------------------------------------
# MATERIAL / SECTION
# -------------------------------------------------
E = 2.0e8      # kN/m2 (dummy value)
A = 0.02       # m2
I = 8e-5       # m4

ops.geomTransf('Linear', 1)

for ele in range(1, 7):
    ops.element('elasticBeamColumn',
                ele, ele, ele+1,
                A, E, I, 1)

# -------------------------------------------------
# LOADS
# -------------------------------------------------
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Point loads (downward negative)
ops.load(1, 0, -1.0, 0)   # A
ops.load(5, 0, -4.0, 0)   # E
ops.load(7, 0, -2.0, 0)   # G

# UDL 5 kN/m on CD (element 3)
# local y load
ops.eleLoad('-ele', 3,
            '-type', '-beamUniform',
            -5.0)

# -------------------------------------------------
# ANALYSIS
# -------------------------------------------------
ops.system('BandGeneral')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')

ops.analyze(1)

# -------------------------------------------------
# REACTIONS
# -------------------------------------------------
ops.reactions()

print("\nSUPPORT REACTIONS")
print("---------------------")

RBx = ops.nodeReaction(2, 1)
RBy = ops.nodeReaction(2, 2)

RFx = ops.nodeReaction(6, 1)
RFy = ops.nodeReaction(6, 2)

print(f"B : Rx = {RBx:.3f} kN")
print(f"B : Ry = {RBy:.3f} kN")

print(f"F : Rx = {RFx:.3f} kN")
print(f"F : Ry = {RFy:.3f} kN")

# -------------------------------------------------
# PLOTS
# -------------------------------------------------

# Beam geometry
plt.figure(figsize=(10, 2))
opsv.plot_model(node_labels=1,
                element_labels=1)
plt.title("Beam Geometry")
plt.show()

# Deformed shape
plt.figure(figsize=(10, 2))
opsv.plot_defo(sfac=100)
plt.title("Deformed Shape")
plt.show()

# Shear Force Diagram
plt.figure(figsize=(10, 3))
opsv.section_force_diagram_2d('T', sfac=0.15)
plt.title("Shear Force Diagram")
plt.grid(True)
plt.show()

# Bending Moment Diagram
plt.figure(figsize=(10, 3))
opsv.section_force_diagram_2d('M', sfac=0.15)
plt.title("Bending Moment Diagram")
plt.grid(True)
plt.show()