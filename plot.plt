set term svg size 1280,960 font "Computer Modern, 15pt"
set output 'out.svg'
set size 100.0,0.5
set datafile separator ","

set multiplot layout 1, 2 ;

set title "Runtime vs NWorkers"
set size 0.5,0.55
plot "cilkscale.csv" using 1:2 title "Runtime" with linespoints,\
"cilkscale.csv" using 1:5 title "Runtime (perfect speedup)" with linespoints,\
"cilkscale.csv" using 1:6 title "Runtime (estimated speedup)" with linespoints

set title "Speedup vs NWorkers" ;
set size 0.5,0.55



plot "cilkscale.csv" using 1:8 title "Num Sockets" w impulse lw 4,\
"cilkscale.csv" using 1:3 title "Speedup" with linespoints,\
"cilkscale.csv" using 1:4 title "Perfect Speedup" with lines,\
"cilkscale.csv" using 1:7 title "Span Bound" with lines


unset multiplot
