import sys
import matplotlib.pyplot as plt

# Import OpenSees (openseespy) with a helpful error on failure
try:
    import openseespy.opensees as ops
except Exception as e:
    raise RuntimeError(
        "Failed to import openseespy. On Windows this usually means the native OpenSees DLLs or a matching \n"
        "openseespywin wheel are not available for the current Python interpreter. Ensure you installed the\n"
        "correct openseespy/openseespywin wheel for your Python version and bitness (and the MSVC redistributable).\n"
        f"Original import error: {e}") from e

# Prefer the standalone opsvis package; fall back to openseespy.postprocessing if present
opsv = None
try:
    import opsvis as opsv
except Exception:
    try:
        # some openseespy installations expose the postprocessing module
        import openseespy.postprocessing.ops_vis as opsv
    except Exception:
        opsv = None

# ==========================================================
# 1. MODEL SETUP
# ==========================================================
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3) # 2D, 3 DOFs per node

# ==========================================================
# 2. DEFINE GEOMETRY (Nodes)
# ==========================================================
ops.node(1, 0.0, 0.0)    # A
ops.node(2, 5.5, 0.0)    # B
ops.node(3, 0.0, 3.66)   # C
ops.node(4, 5.5, 3.66)   # D
ops.node(5, 0.0, 7.32)   # E
ops.node(6, 5.5, 7.32)   # F

# ==========================================================
# 3. DEFINE SUPPORTS
# ==========================================================
ops.fix(1, 1, 1, 1) # Fixed at A
ops.fix(2, 1, 1, 1) # Fixed at B

# ==========================================================
# 4. DEFINE PROPERTIES & ELEMENTS
# ==========================================================
# Generic Steel Assumptions
E = 200e6      # Modulus of Elasticity (kPa)
A = 0.01       # Area (m^2)
I = 0.0002     # Moment of Inertia (m^4)

transf_tag = 1
ops.geomTransf('Linear', transf_tag)

# elasticBeamColumn elements
ops.element('elasticBeamColumn', 1, 1, 3, A, E, I, transf_tag) # Col A-C
ops.element('elasticBeamColumn', 2, 2, 4, A, E, I, transf_tag) # Col B-D
ops.element('elasticBeamColumn', 3, 3, 5, A, E, I, transf_tag) # Col C-E
ops.element('elasticBeamColumn', 4, 4, 6, A, E, I, transf_tag) # Col D-F
ops.element('elasticBeamColumn', 5, 3, 4, A, E, I, transf_tag) # Beam C-D
ops.element('elasticBeamColumn', 6, 5, 6, A, E, I, transf_tag) # Beam E-F

# ==========================================================
# 5. DEFINE LOADS
# ==========================================================
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Nodal Point Loads (Lateral)
ops.load(3, 14.0, 0.0, 0.0) # 14 kN at C
ops.load(5, 28.0, 0.0, 0.0) # 28 kN at E

# Element Distributed Loads (Gravity)
# ops.eleLoad('-ele', eleTag, '-type', '-beamUniform', Wy, Wx)
ops.eleLoad('-ele', 5, '-type', '-beamUniform', -25.25, 0.0) # Beam C-D
ops.eleLoad('-ele', 6, '-type', '-beamUniform', -24.81, 0.0) # Beam E-F

# ==========================================================
# 6. STATIC ANALYSIS
# ==========================================================
ops.system('BandSPD')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')

ops.analyze(1)

# ==========================================================
# 7. PRINT OUTPUT (Reactions & Member Forces)
# ==========================================================
print("--- SUPPORT REACTIONS ---")
ops.reactions()
print(f"Node A (1): Fx = {ops.nodeReaction(1, 1):.2f} kN, Fy = {ops.nodeReaction(1, 2):.2f} kN, Mz = {ops.nodeReaction(1, 3):.2f} kNm")
print(f"Node B (2): Fx = {ops.nodeReaction(2, 1):.2f} kN, Fy = {ops.nodeReaction(2, 2):.2f} kN, Mz = {ops.nodeReaction(2, 3):.2f} kNm")

print("\n--- BEAM END FORCES (Shear & Moment) ---")
# forces output array format: [Fxi, Fyi, Mzi, Fxj, Fyj, Mzj]
for ele in [5, 6]:
    f = ops.eleResponse(ele, 'forces')
    print(f"Beam Element {ele}:")
    print(f"  Left Node  - Shear: {f[1]:.2f} kN, Moment: {f[2]:.2f} kNm")
    print(f"  Right Node - Shear: {f[4]:.2f} kN, Moment: {f[5]:.2f} kNm")

# ==========================================================
# 8. VISUALIZATION (opsvis & matplotlib)
# ==========================================================
if opsv is None:
    print("Visualization skipped: 'opsvis' not available. Install the 'opsvis' package or the\n"
          "openseespy postprocessing modules to enable plotting.")
else:
    plt.style.use('seaborn-v0_8-whitegrid')

    # 8a. Geometry Plot
    plt.figure()
    opsv.plot_model(node_labels=1, element_labels=1, fmt_nodes='b.', fig_wi_he=(12, 8))
    plt.title('Frame Geometry and Connectivity', fontsize=16)

    # 8b. Deformed Shape Plot
    plt.figure()
    # opsv automatically scales deformation if sfac is not provided, 
    # but setting a large static factor ensures it's highly visible.
    opsv.plot_defo(sfac=20.0, fmt_interp='r-', node_labels=0, fig_wi_he=(12, 8))
    plt.title('Deformed Shape (Scale Factor = 20x)', fontsize=16)

    # 8c. Shear Force Diagram (Vy)
    plt.figure()
    opsv.section_force_diagram_2d('Vy', ew=1.5, fig_wi_he=(12, 8))
    plt.title('Shear Force Diagram (SFD)', fontsize=16)

    # 8d. Bending Moment Diagram (Mz)
    plt.figure()
    opsv.section_force_diagram_2d('Mz', ew=1.5, fig_wi_he=(12, 8))
    plt.title('Bending Moment Diagram (BMD)', fontsize=16)

    plt.show()