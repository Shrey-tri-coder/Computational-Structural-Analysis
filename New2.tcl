# Clear previous model
wipe

# Create a 2D model with 3 DOFs per node (Ux, Uy, Rz)
model BasicBuilder -ndm 2 -ndf 3

# Define nodes
node 1 0.0 0.0
node 2 0.0 3.0

# Fix the base node
fix 1 1 1 1

# Define material and section properties
set E 2.0e11      ;# Young's modulus (Pa)
set A 0.02        ;# Cross-sectional area (m²)
set Iz 8.0e-5     ;# Moment of inertia (m4)

# Define geometric transformation
geomTransf Linear 1

# Create an elastic beam-column element
element elasticBeamColumn 1 1 2 $A $E $Iz 1

# Apply a horizontal load at the top node
pattern Plain 1 Linear {
    load 2 10000.0 0.0 0.0
}

# Analysis settings
system BandGeneral
constraints Plain
numberer RCM
test NormDispIncr 1.0e-6 10
algorithm Newton
integrator LoadControl 1.0
analysis Static

# Run analysis
analyze 1

# Print horizontal displacement at node 2
puts "Horizontal displacement at top = [nodeDisp 2 1] m"

set disp [nodeDisp 2 1]
puts "Horizontal displacement at top = $disp m"

puts "Press Enter to exit..."
gets stdin