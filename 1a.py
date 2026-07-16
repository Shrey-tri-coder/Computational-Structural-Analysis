import openseespy.opensees as ops

# ----------------------------
# Start a new model
# ----------------------------
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

# ----------------------------
# Nodes
# ----------------------------
ops.node(1, 0.0, 0.0)      # Fixed base
ops.node(2, 0.0, 432.0)    # Top of column (36 ft = 432 in)

# ----------------------------
# Boundary condition
# ----------------------------
ops.fix(1, 1, 1, 1)

# ----------------------------
# Material/Section properties
# ----------------------------
A = 25.0          # Cross-sectional area (in²)
E = 29000.0       # Steel modulus (ksi)
Iz = 520.83       # Moment of inertia (in⁴)

# ----------------------------
# Transformation
# ----------------------------
ops.geomTransf("Linear", 1)

# ----------------------------
# Element
# ----------------------------
ops.element("elasticBeamColumn",
            1,      # Element tag
            1, 2,   # End nodes
            A,
            E,
            Iz,
            1)

# ----------------------------
# Load
# ----------------------------
ops.timeSeries("Linear", 1)
ops.pattern("Plain", 1, 1)

# Apply 10 kip horizontal load at top
ops.load(2, 10.0, 0.0, 0.0)

# ----------------------------
# Analysis
# ----------------------------
ops.constraints("Plain")
ops.numberer("Plain")
ops.system("BandGeneral")
ops.algorithm("Newton")
ops.integrator("LoadControl", 1.0)
ops.analysis("Static")

ops.analyze(1)

# ----------------------------
# Results
# ----------------------------
ux = ops.nodeDisp(2, 1)
uy = ops.nodeDisp(2, 2)
rz = ops.nodeDisp(2, 3)

print("Top Node Displacement")
print(f"UX = {ux:.5f} in")
print(f"UY = {uy:.5f} in")
print(f"Rotation = {rz:.6f} rad")

# Base reactions
ops.reactions()
Rx = ops.nodeReaction(1, 1)
Ry = ops.nodeReaction(1, 2)
Mz = ops.nodeReaction(1, 3)

print("\nBase Reactions")
print(f"Horizontal Reaction = {Rx:.2f} kip")
print(f"Vertical Reaction   = {Ry:.2f} kip")
print(f"Moment Reaction     = {Mz:.2f} kip-in")