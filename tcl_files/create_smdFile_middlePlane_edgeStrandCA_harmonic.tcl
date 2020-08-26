mol load pdb before_mini/equilibrated.pdb
set allatoms [atomselect top all]
$allatoms set beta 0
set harmatom [atomselect top "chain 'F' 'G' 'A' 'B' 'D' 'E' and name CA"]
$harmatom set beta 0.1

$allatoms set occupancy 0
set smdatom [atomselect top "resid 7 and chain 'C' and name CA"]
$smdatom set occupancy 1
set fixdummy [atomselect top "chain 'C' and resid 2 and name CA"] 
$allatoms writepdb before_mini/ref_smd_from_T_equilibrated.pdb

set smdpos [lindex [$smdatom get {x y z}] 0] 	 
set fixedposdummy [lindex [$fixdummy get {x y z}] 0]
set vecdec [vecnorm [vecsub $smdpos $fixedposdummy]]
puts $vecdec
exit

