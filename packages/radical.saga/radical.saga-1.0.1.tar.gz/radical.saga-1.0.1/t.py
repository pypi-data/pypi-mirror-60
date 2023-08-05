# --------------------------------------------------------------------
#
import os
import sys
import radical.saga as rs

rsfs = rs.filesystem

fs = rsfs.Directory('ssh://mnmda047@lxlogin5.lrz.de/dss/dsshome1/lxc0F/mnmda047/')
try:
    print([str(f) for f in fs.list(pattern='data_*')])
except:
    print('no data files')

fs.copy('file://localhost/etc/passwd', 'data_0.dat')
print([str(f) for f in fs.list(pattern='data_*')])

js_loc  = rs.job.Service(rm='fork://localhost')
jd = rs.job.Description()
jd.executable    =  'find'
jd.arguments     = ['/etc/']
jd.output        =  '%s/data_1.dat' % os.getcwd()
jd.error         =  '%s/data_1.err' % os.getcwd()
jd.file_transfer = ['data_1.dat < data_1.dat',
                    'data_1.err < data_1.err']

j_loc_1 = js_loc.create_job(jd)
j_loc_1.run()
j_loc_1.wait()
print(j_loc_1.state)
os.system('ls -l data_1.dat')
os.system('cat   data_1.err')

js_rem = rs.job.Service(rm='slurm+ssh://mnmda047@lxlogin5.lrz.de')

jd = rs.job.Description()
jd.executable    =  'wc'
jd.arguments     = ['data_0.dat', 'data_1.dat']
jd.output        =  'data_2.dat'
jd.error         =  'data_2.err'
jd.file_transfer = ['data_1.dat > data_1.dat',
                    'data_2.dat < data_2.dat',
                    'data_2.err < data_2.err']

j_rem_1 = js_rem.create_job(jd)
j_rem_1.run()
j_rem_1.wait()
print(j_rem_1.state)
os.system('cat data_2.dat')

# --------------------------------------------------------------------


