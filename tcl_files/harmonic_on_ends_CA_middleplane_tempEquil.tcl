mol load psf before_mini/structure.psf pdb before_mini/coordmini.pdb
set all [atomselect top all]
set sel [atomselect top "protein and name CA and segname PQ1 QP1"]
$all set beta 0
$sel set beta 0.5
$all writepdb before_mini/coordminicons.pdb
exit
