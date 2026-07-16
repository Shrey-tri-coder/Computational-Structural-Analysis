import os
import openseespy.opensees as ops

# --------------------------------------------------
# SET UP
# --------------------------------------------------
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

os.makedirs("Data", exist_ok=True)

# --------------------------------------------------
# GEOMETRY
# --------------------------------------------------

ops.node(1, 0.0,   0.0)
ops.node(2, 504.0, 0.0)
ops.node(3, 0.0,   432.0)
ops.node(4, 504.0, 432.0)

# --------------------------------------------------
# BOUNDARY CONDITIONS
# --------------------------------------------------

ops.fix(1, 1, 1, 1)
ops.fix(2, 1, 1, 1)
ops.fix(3, 0, 0, 0)
ops.fix(4, 0, 0, 0)

# --------------------------------------------------
# MASSES
# --------------------------------------------------

ops.mass(3, 5.18, 0.0, 0.0)
ops.mass(4, 5.18, 0.0, 0.0)

# --------------------------------------------------
# ELEMENTS
# --------------------------------------------------

ops.geomTransf('Linear', 1)

ops.element(
    'elasticBeamColumn',
    1,
    1, 3,
    3600000000.0,
    4227.0,
    1080000.0,
    1
)

ops.element(
    'elasticBeamColumn',
    2,
    2, 4,
    3600000000.0,
    4227.0,
    1080000.0,
    1
)

ops.element(
    'elasticBeamColumn',
    3,
    3, 4,
    5760000000.0,
    4227.0,
    4423680.0,
    1
)

# --------------------------------------------------
# RECORDERS
# --------------------------------------------------

ops.recorder(
    'Node',
    '-file', 'Data/DFree.out',
    '-time',
    '-node', 3, 4,
    '-dof', 1, 2, 3,
    'disp'
)

ops.recorder(
    'Node',
    '-file', 'Data/DBase.out',
    '-time',
    '-node', 1, 2,
    '-dof', 1, 2, 3,
    'disp'
)

ops.recorder(
    'Node',
    '-file', 'Data/RBase.out',
    '-time',
    '-node', 1, 2,
    '-dof', 1, 2, 3,
    'reaction'
)

ops.recorder(
    'Drift',
    '-file', 'Data/Drift.out',
    '-time',
    '-iNode', 1, 2,
    '-jNode', 3, 4,
    '-dof', 1,
    '-perpDirn', 2
)

ops.recorder(
    'Element',
    '-file', 'Data/FCol.out',
    '-time',
    '-ele', 1, 2,
    'globalForce'
)

ops.recorder(
    'Element',
    '-file', 'Data/FBeam.out',
    '-time',
    '-ele', 3,
    'globalForce'
)

# --------------------------------------------------
# GRAVITY LOAD
# --------------------------------------------------

ops.timeSeries('Linear', 1)

ops.pattern('Plain', 1, 1)

ops.eleLoad(
    '-ele', 3,
    '-type',
    '-beamUniform',
    -7.94
)

# --------------------------------------------------
# GRAVITY ANALYSIS
# --------------------------------------------------

ops.constraints('Plain')
ops.numberer('Plain')
ops.system('BandGeneral')

ops.test('NormDispIncr', 1.0e-8, 6)
ops.algorithm('Newton')

ops.integrator('LoadControl', 0.1)
ops.analysis('Static')

ops.analyze(10)

ops.loadConst('-time', 0.0)

# --------------------------------------------------
# LATERAL LOAD
# --------------------------------------------------

ops.timeSeries('Linear', 2)

ops.pattern('Plain', 2, 2)

ops.load(3, 2000.0, 0.0, 0.0)
ops.load(4, 2000.0, 0.0, 0.0)

# --------------------------------------------------
# PUSHOVER ANALYSIS
# --------------------------------------------------

ops.integrator(
    'DisplacementControl',
    3,      # Control node
    1,      # DOF (X-direction)
    0.1     # Increment
)

ops.analyze(100)

print("Done!")