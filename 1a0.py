import openseespy.opensees as ops
import os

# --------------------------------------------------------------------------------------------------
# Example 1: Cantilever 2D
# Static pushover analysis with gravity
# Units: kip, inch, second
# --------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# SET UP
# ------------------------------------------------------------------------------

ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Create output directory
os.makedirs("Data", exist_ok=True)

# ------------------------------------------------------------------------------
# GEOMETRY
# ------------------------------------------------------------------------------

# Nodes
ops.node(1, 0.0, 0.0)
ops.node(2, 0.0, 432.0)

# Boundary conditions
ops.fix(1, 1, 1, 1)

# Mass
ops.mass(2, 5.18, 0.0, 0.0)

# ------------------------------------------------------------------------------
# ELEMENT
# ------------------------------------------------------------------------------

# Geometric transformation
ops.geomTransf("Linear", 1)

# Elastic beam-column element
ops.element(
    "elasticBeamColumn",
    1,          # element tag
    1, 2,       # iNode, jNode
    3600000000.0,  # Area
    4227.0,        # Young's Modulus
    1080000.0,     # Moment of Inertia
    1              # Transformation tag
)

# ------------------------------------------------------------------------------
# RECORDERS
# ------------------------------------------------------------------------------

ops.recorder(
    "Node",
    "-file", "Data/DFree.out",
    "-time",
    "-node", 2,
    "-dof", 1, 2, 3,
    "disp"
)

ops.recorder(
    "Node",
    "-file", "Data/DBase.out",
    "-time",
    "-node", 1,
    "-dof", 1, 2, 3,
    "disp"
)

ops.recorder(
    "Node",
    "-file", "Data/RBase.out",
    "-time",
    "-node", 1,
    "-dof", 1, 2, 3,
    "reaction"
)

# ops.recorder(
#     "Drift",
#     "-file", "Data/Drift.out",
#     "-time",
#     "-iNode", 1,
#     "-jNode", 2,
#     "-dof", 1,
#     "-perpDirn", 2
# )

ops.recorder(
    "Element",
    "-file", "Data/FCol.out",
    "-time",
    "-ele", 1,
    "globalForce"
)

ops.recorder(
    "Element",
    "-file", "Data/DCol.out",
    "-time",
    "-ele", 1,
    "deformation"
)

# ------------------------------------------------------------------------------
# GRAVITY LOAD
# ------------------------------------------------------------------------------

ops.timeSeries("Linear", 1)
ops.pattern("Plain", 1, 1)

ops.load(2, 0.0, -2000.0, 0.0)

# Analysis options
ops.constraints("Plain")
ops.numberer("Plain")
ops.system("BandGeneral")
ops.test("NormDispIncr", 1.0e-8, 6)
ops.algorithm("Newton")
ops.integrator("LoadControl", 0.1)
ops.analysis("Static")

# Gravity analysis
ops.analyze(10)

# Hold gravity loads constant
ops.loadConst("-time", 0.0)

# ------------------------------------------------------------------------------
# LATERAL LOAD
# ------------------------------------------------------------------------------

ops.timeSeries("Linear", 2)
ops.pattern("Plain", 2, 2)

ops.load(2, 2000.0, 0.0, 0.0)

# ------------------------------------------------------------------------------
# PUSHOVER ANALYSIS
# ------------------------------------------------------------------------------

# Switch to displacement control
ops.integrator(
    "DisplacementControl",
    2,      # Node
    1,      # DOF (X-direction)
    0.1     # Increment
)

# Perform pushover
ops.analyze(1000)

print("Done!")
