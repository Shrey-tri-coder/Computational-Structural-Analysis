import openseespy.opensees as ops
import opsvis as opsv
import matplotlib.pyplot as plt

# --------------------------------------------------
# START MODEL
# --------------------------------------------------
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 2)

# --------------------------------------------------
# GEOMETRY
# --------------------------------------------------

L = 1030.0      # Total span (ft)
H = 4.0         # Height at apex (ft)

# Bottom chord nodes
bottom_nodes = {
    1: (0.0, 0.0),          # Left support A
    2: (171.67, 0.0),
    3: (343.33, 0.0),
    4: (515.0, 0.0),        # Midspan
    5: (686.67, 0.0),
    6: (858.33, 0.0),
    7: (1030.0, 0.0)        # Right support C
}

# Top chord nodes
top_nodes = {
    8:  (128.75, 1.0),
    9:  (257.50, 2.0),
    10: (386.25, 3.0),

    11: (515.0, 4.0),       # Apex

    12: (643.75, 3.0),
    13: (772.50, 2.0),
    14: (901.25, 1.0)
}

nodes = {}
nodes.update(bottom_nodes)
nodes.update(top_nodes)

for n, coord in nodes.items():
    ops.node(n, *coord)

# --------------------------------------------------
# SUPPORTS
# --------------------------------------------------

# Left support = pin
ops.fix(1, 1, 1)

# Right support = roller
ops.fix(7, 0, 1)

# --------------------------------------------------
# MATERIAL
# --------------------------------------------------

E = 29000.0      # ksi
A = 5.0          # in²

ops.uniaxialMaterial('Elastic', 1, E)

# --------------------------------------------------
# ELEMENTS
# --------------------------------------------------

members = [

    # Bottom chord
    (1,2),(2,3),(3,4),
    (4,5),(5,6),(6,7),

    # Top chord
    (1,8),(8,9),(9,10),(10,11),
    (11,12),(12,13),(13,14),(14,7),

    # Web members (Warren type)
    (2,8),(2,9),
    (3,9),(3,10),
    (4,10),(4,11),
    (5,11),(5,12),
    (6,12),(6,13),
    (6,14)
]

for tag, (i, j) in enumerate(members, start=1):
    ops.element('Truss', tag, i, j, A, 1)

# --------------------------------------------------
# LOADS
# --------------------------------------------------

ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Left top chord nodes
for node in [8, 9, 10]:
    ops.load(node, 2.0, -1.0)

# Apex
ops.load(11, 0.0, -2.0)

# Right top chord nodes
for node in [12, 13, 14]:
    ops.load(node, 3.0, -1.0)

# Bottom intermediate nodes
for node in [2, 3, 4, 5, 6]:
    ops.load(node, 0.0, -0.5)

# --------------------------------------------------
# ANALYSIS
# --------------------------------------------------

ops.system('BandGeneral')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')

ops.analyze(1)

# --------------------------------------------------
# REACTIONS
# --------------------------------------------------

ops.reactions()

print("\n" + "="*50)
print("SUPPORT REACTIONS")
print("="*50)

print(f"Node 1 (Pin Support A)")
print(f"Rx = {ops.nodeReaction(1,1):10.3f}")
print(f"Ry = {ops.nodeReaction(1,2):10.3f}")

print()

print(f"Node 7 (Roller Support C)")
print(f"Rx = {ops.nodeReaction(7,1):10.3f}")
print(f"Ry = {ops.nodeReaction(7,2):10.3f}")

# --------------------------------------------------
# MEMBER AXIAL FORCES
# --------------------------------------------------

print("\n" + "="*50)
print("MEMBER AXIAL FORCES")
print("="*50)

for e in range(1, len(members)+1):

    force = ops.eleResponse(e, 'axialForce')[0]

    if force > 0:
        status = "Tension"
    else:
        status = "Compression"

    print(f"Element {e:2d} : {force:10.3f}   {status}")

# --------------------------------------------------
# PLOT GEOMETRY
# --------------------------------------------------

plt.figure(figsize=(20,6))

opsv.plot_model(
    node_labels=1,
    element_labels=1
)

plt.title("TRUSS GEOMETRY")
plt.xlim(-50, 1080)
plt.ylim(-2, 8)

ax = plt.gca()
ax.set_aspect(50)      # exaggerate height

plt.grid(True)
plt.tight_layout()
plt.show()

# --------------------------------------------------
# PLOT DEFORMED SHAPE
# --------------------------------------------------

plt.figure(figsize=(20,6))

opsv.plot_defo(
    sfac=10000          # large scale factor
)

plt.title("DEFORMED SHAPE")
plt.xlim(-50, 1080)
plt.ylim(-20, 20)

ax = plt.gca()
ax.set_aspect(25)

plt.grid(True)
plt.tight_layout()
plt.show()