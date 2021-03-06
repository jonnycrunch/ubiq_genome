#!/usr/bin/python

import sys
from glob import glob
import h5py
import numpy
import matplotlib.pyplot as plot
from scipy.stats.stats import pearsonr

fns= glob(sys.argv[1]+'/pass/*.fast5')

for k in range(6):
    data=numpy.zeros( (len(fns)*2, 4**k) )
    durs=numpy.matrix(numpy.zeros( (len(fns)*2, 1) ))

    nv={'A':0, 'C':1, 'G':2, 'T':3}
    vn='ACGT'
    places=[4**x for x in range(k)]

    def l2n(seq):
        return numpy.dot([nv[l] for l in seq], places)

    def n2l(n):
        o=''
        for i in range(k):
            o+=vn[n%4]
            n/=4
        return o

    fnc=0
    for fn in fns:
        f=h5py.File(fn,'r')
        for side in ['template','complement']:
            dur=f['Analyses']['Basecall_2D_000']['BaseCalled_'+side]['Events'].attrs['duration']
            seq=f['Analyses']['Basecall_2D_000']['BaseCalled_'+side]['Fastq'].value.split('\n')[1]
            for i in range(len(seq)-k):
                data[fnc][l2n(seq[i:i+k])]+=1
            durs[fnc][0] = dur
            fnc+=1

    costs = numpy.linalg.pinv(data)*durs
#    print costs

    pred = data * costs

    size=max(durs.max(),pred.max())
    size=50*((int(size/50)+1))
    plot.clf()
    plot.scatter(durs, pred, c=['red','blue']*len(fns))
    plot.axis([0,size,0,size])
    plot.xlabel('Actual Duration (seconds)')
    plot.ylabel('Predicted Duration (seconds)')
    #plot.show()
    plot.savefig('part11scatter%dmer.eps'%k,format='eps')
    (r2,p)=pearsonr(durs,pred)
    if k==0:
        plot.clf()
        x=data[:,0].tolist()
        y=sum(durs.tolist(),[])
        plot.scatter(x,y)
        mx=max(x)
        plot.axis([0, mx, 0, max(y)])
        plot.xlabel('Read Length (bases)')
        plot.ylabel('Duration (seconds)')
        plot.savefig('part11scatterbd.eps',format='eps')

        print '\\subsection*{Simple Model}'
        print '''
        The simplest possible model is the one in which the number of nucleotides determines the read duration,
        possibly with some constant term for getting started.  To consider this, we start with a scatterplot of
        bases against time with a linear fit.

        \\begin{centering}
        \\includegraphics[width=\\textwidth]{part11scatterbd}
        \\end{centering}

        We might be tempted to include a constant term in our fitting, but as should be apparent, it would be
        negative.  How long it would take to sequence an extremely short read is unclear.  Fortunately, there 
        are none in our sample.

        \\newpage
        This allows us to construct a trivial (and still pretty effective) model based on a fixed cost per nucleotide.

        Cost per nucleotide: %.2fms
        ''' % (costs[0][0]*1e3)
    if k==1:
        print '\\newpage'
        print '\\subsection*{Nucleotide Model}'
        print 'A slightly more complex model uses a differend cost for each type of nucleotide: '
        for i in range(4):
            print '%s=%.2dms ' % (vn[i], costs[i][0]*1e3)
        print '\n'
    if k>1:
        plot.clf()
        plot.hist(costs[0:((4**k)-1)], bins=4**(k-1))
        plot.xlabel('Cost (seconds)')
        plot.ylabel('# of %d-mers'%k)
        plot.savefig('part11hist%d.eps'%k,format='eps')
        print '''
        \\newpage
        \\subsection*{%dmer Model}
        \\begin{wrapfigure}{R}{2in}
        \\vspace{-50pt}
        \\includegraphics[width=3in]{part11hist%d}
        \\vspace{-70pt}
        \\end{wrapfigure}
        We can use a model in which each the time to extend by one nucleotide is determined by the %d-mer in the middle of the
        pore.  We can not list all the costs, but here's a histogram:

        \\vspace{1.5in}

        And here's the resulting predictions:
        ''' % (k,k,k)


        
    print '\\includegraphics[width=\\textwidth]{part11scatter%dmer}\n\n$r^2=%.2f$\n' % (k,r2**2)

    if k==0:
        print '\n(Red circles are template strand; blue are complement.  There appears to be no significant difference between them.)\n'

print '\n\nAt this point our model has 1024 degrees of freedom for %d datapoints, so a good fit may reveal more overfitting than model appropriateness.' % (2*len(fns))
