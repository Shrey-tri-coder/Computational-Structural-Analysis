import openseespy.opensees as ops
import opsvis as opsv
import matplotlib.pyplot as plt

# ------------------------------
# 1. Initialization
# ------------------------------
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 2)

# ------------------------------
# 2. Nodes
# ------------------------------
# Left column nodes (Y increments of 10)
ops.node(1, 0.0, 0.0)    # Base
ops.node(2, 0.0, 10.0)   # Story 1
ops.node(3, 0.0, 20.0)   # Story 2
ops.node(4, 0.0, 30.0)   # Story 3
ops.node(5, 0.0, 40.0)   # Story 4 (Apex)

# Right inclined chord nodes
ops.node(6, 30.0, 0.0)   # Base
ops.node(7, 22.5, 10.0)  # Story 1
ops.node(8, 15.0, 20.0)  # Story 2
ops.node(9, 7.5, 30.0)   # Story 3

# ------------------------------
# 3. Boundary Conditions
# ------------------------------
ops.fix(1, 1, 1) # Node 1: Pinned (Fixed X, Fixed Y)
ops.fix(6, 0, 1) # Node 6: Roller (Free X, Fixed Y)

# ------------------------------
# 4. Material & Section
# ------------------------------
E = 29000.0  # Elastic Modulus (ksi)
A = 10.0     # Cross-sectional Area (in^2)
mat_tag = 1
ops.uniaxialMaterial('Elastic', mat_tag, E)

# ------------------------------
# 5. Elements (Truss)
# ------------------------------
# Left Column
ops.element('Truss', 1, 1, 2, A, mat_tag)
ops.element('Truss', 2, 2, 3, A, mat_tag)
ops.element('Truss', 3, 3, 4, A, mat_tag)
ops.element('Truss', 4, 4, 5, A, mat_tag)

# Right Inclined Chord
ops.element('Truss', 5, 6, 7, A, mat_tag)
ops.element('Truss', 6, 7, 8, A, mat_tag)
ops.element('Truss', 7, 8, 9, A, mat_tag)
ops.element('Truss', 8, 9, 5, A, mat_tag)

# Horizontal Members
ops.element('Truss', 9, 1, 6, A, mat_tag)
ops.element('Truss', 10, 2, 7, A, mat_tag)
ops.element('Truss', 11, 3, 8, A, mat_tag)
ops.element('Truss', 12, 4, 9, A, mat_tag)

# Diagonal Braces (Bottom-Left to Top-Right of each panel)
ops.element('Truss', 13, 1, 7, A, mat_tag)
ops.element('Truss', 14, 2, 8, A, mat_tag)
ops.element('Truss', 15, 3, 9, A, mat_tag)

# ------------------------------
# 6. Loads
# ------------------------------
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Reverse-engineered load to match the 13.333 and 16.667 kip axial forces
# 10 kips applied horizontally at the top apex node
ops.load(5, 10.0, 0.0)

# ------------------------------
# 7. Analysis Settings
# ------------------------------
ops.system('BandSPD')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')
ops.analyze(1)

# ------------------------------
# 8. Output and Printing
# ------------------------------
print("=== SUPPORT REACTIONS ===")
ops.reactions()
print(f"Node 1 (Pin)    - Rx: {ops.nodeReaction(1, 1):>8.3f} kips, Ry: {ops.nodeReaction(1, 2):>8.3f} kips")
print(f"Node 6 (Roller) - Rx: {ops.nodeReaction(6, 1):>8.3f} kips, Ry: {ops.nodeReaction(6, 2):>8.3f} kips")

print("\n=== MEMBER AXIAL FORCES ===")
print("  (+ is Tension, - is Compression)")
for ele in ops.getEleTags():
    force = ops.basicForce(ele)[0]
    print(f"Element {ele:2d}: {force:>8.3f} kips")

# ------------------------------
# 9. Visualization (opsvis)
# ------------------------------
# A. Geometry Plot
plt.figure(figsize=(14, 8))
opsv.plot_model(node_labels=1, element_labels=1)
plt.title('Truss Geometry with Node and Element Labels', fontsize=16)
plt.grid(True)
plt.show()

# B. Deformed Shape Plot
plt.figure(figsize=(14, 8))
# sfac (scale factor) scales the visualization of the deformation
opsv.plot_defo(sfac=50.0, fmt_undef='b--', fmt_defo='r-') 
plt.title('Deformed Shape (Scale Factor = 50)', fontsize=16)
plt.grid(True)
plt.show()

# C. Axial Force Diagram
plt.figure(figsize=(14, 10))
# sfac here scales the thickness of the force diagram relative to member lengths
opsv.section_force_diagram_2d('N', sfac=0.15)
plt.title('Axial Force Diagram [kips]', fontsize=16)
plt.grid(True)
plt.show()