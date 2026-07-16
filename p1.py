import openseespy.opensees as ops
import opsvis as opsv
import matplotlib.pyplot as plt
import numpy as np

# --------------------------------------------------
# MODEL
# --------------------------------------------------

ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Geometry
L = 1.0          # Beam length (m)
nEle = 20        # Number of elements

# Material/Section properties
E = 2e11         # Pa
A = 0.01         # m²
I = 8.33e-6      # m^4

# Applied load
P = 10000.0      # N

# --------------------------------------------------
# NODES
# --------------------------------------------------

for i in range(nEle + 1):
    x = i * L / nEle
    ops.node(i + 1, x, 0.0)

# --------------------------------------------------
# SUPPORTS
# Left = roller
# Right = pin
# --------------------------------------------------

ops.fix(1, 0, 1, 0)           # ux free, uy fixed
ops.fix(nEle + 1, 1, 1, 0)    # ux fixed, uy fixed

# --------------------------------------------------
# ELEMENTS
# --------------------------------------------------

ops.geomTransf('Linear', 1)

for i in range(nEle):
    ops.element('elasticBeamColumn',
                i + 1,
                i + 1,
                i + 2,
                A, E, I, 1)

# --------------------------------------------------
# LOADS
# --------------------------------------------------

midNode = nEle // 2 + 1

ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

ops.load(midNode, 0.0, -P, 0.0)

# --------------------------------------------------
# ANALYSIS
# --------------------------------------------------

ops.constraints('Plain')
ops.numberer('RCM')
ops.system('BandGeneral')
ops.algorithm('Newton')
ops.integrator('LoadControl', 1.0)
ops.analysis('Static')

ops.analyze(1)

# --------------------------------------------------
# REACTIONS
# --------------------------------------------------

ops.reactions()

R1 = ops.nodeReaction(1, 2)
R2 = ops.nodeReaction(nEle + 1, 2)

print("\nSupport Reactions")
print("-------------------")
print(f"Left Reaction  = {R1:.2f} N")
print(f"Right Reaction = {R2:.2f} N")
print(f"Total Reaction = {R1 + R2:.2f} N")

# --------------------------------------------------
# PLOT MODEL
# --------------------------------------------------

plt.figure(figsize=(8, 3))
opsv.plot_model()
plt.title("Beam Geometry")
plt.grid(True)

# --------------------------------------------------
# PLOT DEFORMED SHAPE
# --------------------------------------------------

plt.figure(figsize=(8, 3))
opsv.plot_defo()
plt.title("Deformed Shape")
plt.grid(True)

# --------------------------------------------------
# THEORETICAL SHEAR FORCE DIAGRAM
# --------------------------------------------------

x_sfd = [0, L/2, L/2, L]
V = [P/2, P/2, -P/2, -P/2]

plt.figure(figsize=(8, 4))
plt.step(x_sfd, V, where='post', linewidth=2)

plt.axhline(0, color='k')
plt.grid(True)

plt.xlim(0, L)
plt.xlabel('Beam Length (m)')
plt.ylabel('Shear Force (N)')
plt.title('Shear Force Diagram')

plt.text(0.2, P/2 + 200, f'{P/2:.0f} N')
plt.text(0.7, -P/2 - 600, f'{-P/2:.0f} N')

# --------------------------------------------------
# THEORETICAL BENDING MOMENT DIAGRAM
# --------------------------------------------------

x = np.linspace(0, L, 200)
M = []

for xi in x:
    if xi <= L/2:
        M.append((P/2) * xi)
    else:
        M.append((P/2) * (L - xi))

plt.figure(figsize=(8, 4))
plt.plot(x, M, linewidth=2)

plt.fill_between(x, M, alpha=0.3)

plt.axhline(0, color='k')
plt.grid(True)

plt.xlabel('Beam Length (m)')
plt.ylabel('Moment (N-m)')
plt.title('Bending Moment Diagram')

Mmax = P * L / 4
plt.text(L/2, Mmax + 100,
         f'Mmax = {Mmax:.0f} N-m',
         ha='center')

# --------------------------------------------------
# SHOW ALL PLOTS
# --------------------------------------------------

plt.tight_layout()
plt.show()