import subprocess
import sys
import os
import time
data_filename = "cilkscale-" + "-".join(sys.argv[1:])+".csv"
data_filename = data_filename.replace("/","")
plot_filename = "cilkscale-" + "-".join(sys.argv[1:]) + ".plt"
plot_filename = plot_filename.replace("/","")

def run_command(cmd, asyn = False):
  proc = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if not asyn:
    out,err=proc.communicate()
    return out,err
  else:
    return ""


def get_cilk_tool_helper_dir():
  out,err = run_command("which clang")
  path =  ("/".join(out.split("/")[:-1])).strip()
  return path+"/cilk_tool_helpers"


helper_dir = get_cilk_tool_helper_dir()

def convert_path_to_cilkscale(arguments):
  found_it = False
  new_list = []
  for x in sys.argv[1:]:
      binary = x.split("/")[-1]
      new_binary = "."+binary+".cilkscale"
      cilkview_path = "/".join(x.split("/")[:-1])+"/"+new_binary
      if os.path.exists("/".join(x.split("/")[:-1])+"/"+new_binary):
          found_it = True
          new_list.append(cilkview_path)
      else:
          new_list.append(x)
  if not found_it:
      print 'echo "failed to bind a cilkscale instrumented binary."'
      quit()
  return " ".join(new_list)


RUN_COMMAND_CILKSCALE = convert_path_to_cilkscale(sys.argv)


def get_parallelism():
  out,err = run_command(RUN_COMMAND_CILKSCALE)
  return float(err.split('parallelism')[-1].strip())

parallelism = get_parallelism()

RUN_COMMAND = "perf stat " + " ".join(sys.argv[1:])

#MAKE_COMMAND = "make clean; make"
#RUN_COMMAND = "time -p ./fib 40"

#subprocess.call(MAKE_COMMAND, shell=True);

def run_command(cmd, asyn = False):
  proc = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if not asyn:
    out,err=proc.communicate()
    return out,err
  else:
    return ""


def get_n_cpus():
  return len(get_cpu_ordering())
  #proc = subprocess.Popen(["cat /proc/cpuinfo | awk '/^processor/{print $3}' | wc -l"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  #out,err=proc.communicate()
  #return int(out.strip())

def run_on_p_workers(P, rcommand):
  cpu_ordering = get_cpu_ordering()
  cpu_online = cpu_ordering[:P]
  cpu_offline = cpu_ordering[P:]

  for x in cpu_offline:
    #run_command("taskset -c "+",".join([str(p) for (p,m) in cpu_offline])+" nice -n 19 "+helper_dir+"/busywait.sh &", True)
    run_command("taskset -c "+str(x[0])+" nice -n 19 "+helper_dir+"/busywait.sh &", True)

  time.sleep(0.1)
  #print cpu_online
  #print cpu_offline
  rcommand = "taskset -c " + ",".join([str(p) for (p,m) in cpu_online]) + " " + rcommand
  #print rcommand
  proc = subprocess.Popen(['CILK_NWORKERS=' + str(P) + ' ' + rcommand], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out,err=proc.communicate()
  run_command("pkill -f busywait.sh")
  for line in err.splitlines():
    if line.endswith('seconds time elapsed'):
      line = line.replace('seconds time elapsed','').strip()
      val = float(line)
      return val

    #if line.startswith('real'):
    #  line=line.replace('real ', '').strip()
    #  val = float(line)
    #  return val

# upper bound P-worker runtime for program with work T1 and parallelism PAR 
def bound_runtime(T1, PAR, P):
  Tp = T1/P + (1.0-1.0/P)*T1/PAR
  return Tp

def get_hyperthreads():
    command = "for cpunum in $(cat /sys/devices/system/cpu/cpu*/topology/thread_siblings_list | cut -s -d, -f2- | tr ',' '\n' | sort -un); do echo $cpunum; done"
    proc = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out,err=proc.communicate()
    print out


def get_cpu_ordering():
  out,err = run_command("lscpu --parse")
  

  avail_cpus = []
  for l in out.splitlines():
    if l.startswith('#'):
      continue
    #print l.strip().split(',')
    items = l.strip().split(',')
    cpu_id = int(items[0])
    node_id = int(items[1])
    socket_id = int(items[2])
    avail_cpus.append((socket_id, node_id, cpu_id))


    #print str((cpu_id, socket_id))
  avail_cpus = sorted(avail_cpus)
  ret = []
  added_nodes = dict()
  for x in avail_cpus:
    if x[1] not in added_nodes:
      added_nodes[x[1]] = True
    else:
      continue
    ret.append((x[2], x[0]))
  return ret

  num_nodes = 1
  nodes = dict()
  for l in out.splitlines():
      if l.startswith("NUMA"):
        if l.startswith("NUMA node(s):"):
          res = l.replace("NUMA node(s):", "").strip()
          num_nodes = int(res)
          for i in range(0, num_nodes):
              nodes[i] = []
          continue
      if l.startswith("NUMA node"):
          for i in range(0,num_nodes):
              if l.startswith("NUMA node"+str(i)+" CPU(s):"):
                  res = l.replace("NUMA node"+str(i)+" CPU(s):","").strip().split(",")
                  nodes[i] = res

  avail_cpus = []
  for socket in range(0,num_nodes):
    for cpu in nodes[socket]:
        avail_cpus.append((cpu,socket))
  return avail_cpus


print get_cpu_ordering() 
#quit()


#print get_cpu_ordering()
#quit()
#get_hyperthreads()
#quit()

NCPUS = get_n_cpus()
print "NCPUS is " + str(NCPUS)
#schedule = get_schedule()
#quit()

print "Generating Scalability Data for " + str(NCPUS) + " cpus."

results = dict()
for i in range(1,NCPUS+1):
  #if i <= 8:
  results[i] = run_on_p_workers(i, RUN_COMMAND)
  #else:
  #  results[i] = run_on_p_workers(i, "numactl --cpunodebind=0,1 " + RUN_COMMAND)

  #for j in range(0,4):
  #  res = run_on_p_workers(i, RUN_COMMAND)
  #  if res < results[i]:
  #    results[i] = res

plot = open(data_filename, 'w+')

for i in range(1,NCPUS+1):
    
  cpu_ordering = get_cpu_ordering()
  cpu_online = cpu_ordering[:i]
  maxsocket = None
  for x in cpu_online:
    if maxsocket == None or int(x[1])+1 > maxsocket:
        maxsocket = int(x[1])+1
       

  plot.write(str(i) + "," + str(results[i]) +","+str(results[1]/results[i]) +","+str(1.0*i)+","+str(results[1]/i)+","+str(bound_runtime(results[1],parallelism,i))+","+str(parallelism)+","+str(maxsocket)+"," +str(results[1]/(bound_runtime(results[1], parallelism, i)))+"," +str(results[1]/parallelism)+"\n")
plot.close()


print "generate plot"


plot_format = """
set term svg size 1000,500 font "Computer Modern, 15pt"
set output '@(short_app_name).svg'
set size 0.5,1.0
set datafile separator ","
set tmargin 0
#set multiplot layout 1, 2 ;
#set multiplot layout 1,2 \
#              margins 0.1,0.9,0.1,0.9 \
              spacing 0.08,0.08

set multiplot layout 1,2               margins 0.15,0.85,0.15,0.85               spacing 0.08,0.08


set title "Execution Time: @(app_name)"
set size 0.5,0.5

set grid x2tics
set grid x2tics lw 4
set x2tics format ""
set x2tics (@(x2tics))
set x2tics rotate by 90
set x2tics scale 0
set x2tics offset 0
set x2range [0:@(ncpus)]
set xrange [0:@(ncpus)]

@(numa_labels)


plot "@(data_filename)" using 1:2 title "Observed Runtime" with linespoints lw 3,"@(data_filename)" using 1:5 title "Perfect Linear Speedup" with lines lw 3,"@(data_filename)" using 1:6 title "Greedy Scheduling Bound" with lines lw 3, "@(data_filename)" using 1:10 with lines lw 3 title "Span Bound"

set title "Speedup: @(app_name)" ;
set size 0.5,0.5


set ylabel "Speedup"
set yrange[0:@(ncpus)]
plot "@(data_filename)" using 1:3 title "Observed Speedup" with linespoints lw 3,"@(data_filename)" using 1:4 title "Perfect Linear Speedup" with lines lw 3,"@(data_filename)" using 1:7 title "Span Bound" with lines lw 3,"@(data_filename)" using 1:9 title "Greedy Scheduling Bound" with lines lw 3

unset multiplot
"""


plot_format = plot_format.replace("@(app_name)", " ".join(sys.argv[1:]))
plot_format = plot_format.replace("@(short_app_name)", "-".join(sys.argv[1:]))
plot_format = plot_format.replace("@(data_filename)", data_filename)
plot_format = plot_format.replace("@(ncpus)", str(NCPUS))

cpu_ordering = get_cpu_ordering()
dividing_points = []
for i in range(0, len(cpu_ordering)):
  if i == 0:
    dividing_points.append(i)
    continue
  if i == len(cpu_ordering)-1:
    dividing_points.append(i+1)
    continue

  if cpu_ordering[i-1][1] != cpu_ordering[i][1]:
    dividing_points.append(i)

print "Dividing points: " + str(dividing_points)

num_numa_nodes = len(dividing_points)-1
print "num numa nodes:" + str(num_numa_nodes)

numa_label_format = """
set label "NUMA@(nodeid): [@(startcpu)-@(endcpu)]" at @(location), graph 0 center offset 0, char -2
"""

numa_labels = []
for i in range(0,num_numa_nodes):
  label = numa_label_format.replace("@(nodeid)", str(i))
  label = label.replace("@(startcpu)", str(dividing_points[i]+1))
  label = label.replace("@(endcpu)", str(dividing_points[i+1]))
  label = label.replace("@(location)", str((1.0*(dividing_points[i] + dividing_points[i+1]))/2))
  numa_labels.append(label)


plot_format = plot_format.replace("@(x2tics)", ",".join([str(x) for x in dividing_points]))
plot_format = plot_format.replace("@(numa_labels)", "\n".join(numa_labels))

open(plot_filename, "w").write(plot_format)

# generate the plot
#out,err=run_command("gnuplot "+helper_dir+"/plot.plt")
out,err=run_command("gnuplot " + plot_filename)
print out
print err

