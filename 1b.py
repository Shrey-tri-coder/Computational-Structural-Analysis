import openseespy.opensees as ops

# ==========================================================
# 1. INITIALIZATION & UNITS
# ==========================================================
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3) # 2 dimensions, 3 DOFs per node

# Define units (Base units: kips, inches, seconds)
kip = 1.0
inch = 1.0
ft = 12.0 * inch

# ==========================================================
# 2. GEOMETRY & NODES
# ==========================================================
L = 42.0 * ft  # Bay width
H = 36.0 * ft  # Story height

# ops.node(nodeTag, x, y)
ops.node(1, 0.0, 0.0)
ops.node(2, L, 0.0)
ops.node(3, 0.0, H)
ops.node(4, L, H)

# Boundary Conditions (Pinned Bases)
# ops.fix(nodeTag, uX, uY, Rz)
ops.fix(1, 1, 1, 0)
ops.fix(2, 1, 1, 0)

# ==========================================================
# 3. SECTIONS & MATERIAL
# ==========================================================
# Generic Elastic Material Modulus
E = 3000.0 # ksi

# Section A-A (Columns): 5' x 5' Square
b_col = 5.0 * ft
h_col = 5.0 * ft
A_col = b_col * h_col
Iz_col = (1.0 / 12.0) * b_col * (h_col ** 3)

# Section B-B (Beam): 5' x 8' Rectangle
b_beam = 5.0 * ft
h_beam = 8.0 * ft
A_beam = b_beam * h_beam
Iz_beam = (1.0 / 12.0) * b_beam * (h_beam ** 3)

# ==========================================================
# 4. ELEMENTS
# ==========================================================
# Geometric Transformation for Linear Analysis
transfTag = 1
ops.geomTransf('Linear', transfTag)

# ops.element('elasticBeamColumn', eleTag, iNode, jNode, A, E, Iz, transfTag)
ops.element('elasticBeamColumn', 1, 1, 3, A_col, E, Iz_col, transfTag) # Left Column
ops.element('elasticBeamColumn', 2, 2, 4, A_col, E, Iz_col, transfTag) # Right Column
ops.element('elasticBeamColumn', 3, 3, 4, A_beam, E, Iz_beam, transfTag) # Top Beam

# ==========================================================
# 5. GRAVITY LOAD ANALYSIS
# ==========================================================
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# The 4000 kip load is distributed across the beam
W_total = 4000.0 * kip
w_y = -W_total / L  # Negative for downward load

# Apply uniform distributed load to element 3 (the beam)
ops.eleLoad('-ele', 3, '-type', '-beamUniform', w_y)

# Gravity Analysis Parameters
ops.system('BandGeneral')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 0.1) # Apply load in 10 steps of 0.1
ops.algorithm('Newton')
ops.analysis('Static')

print("Running Gravity Analysis...")
ops.analyze(10)

# Lock gravity loads and reset pseudotime to 0 before pushover
ops.loadConst('-time', 0.0) 

# ==========================================================
# 6. STATIC PUSHOVER ANALYSIS
# ==========================================================
# Define reference lateral load pattern
ops.timeSeries('Linear', 2)
ops.pattern('Plain', 2, 2)
# Apply a reference load of 1.0 at Node 3 in the X-direction
ops.load(3, 1.0, 0.0, 0.0) 

# Pushover Parameters (Displacement Control)
target_disp = 15.0 * inch  # Maximum displacement (Delta) to push out to
dU = 0.1 * inch            # Displacement increment per step
num_steps = int(target_disp / dU)

# Integrator: Displacement Control (Node 3, DOF 1, Increment dU)
ops.integrator('DisplacementControl', 3, 1, dU) 
ops.analysis('Static')

print(f"Running Static Pushover Analysis to Delta = {target_disp} inches...")
status = ops.analyze(num_steps)

if status == 0:
    print("Pushover Analysis completed successfully!")
else:
    print("Pushover Analysis failed to converge.")