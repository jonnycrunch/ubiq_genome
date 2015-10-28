#!/usr/bin/python
import sys
import os
from collections import defaultdict
import matplotlib.pyplot as plot
import warnings


warnings.simplefilter("ignore")


def rr(readtype, path, failorpass, histname):
	os.system("poretools fastq --type "+readtype+" "+path+"downloads/"+failorpass+"/ >histfileanalyzer.txt")
	data = open('histfileanalyzer.txt').readlines()
	prev=False
	ct=0
	analyzer=defaultdict(lambda:0)
	for line in data:
		if prev:
			line=line.strip()
			prev = False
			analyzer[ct]=len(line)
			ct+=1
		else:
			if "fast5" in line:
				prev = True
	os.remove('histfileanalyzer.txt')

	plot.clf()
	plot.hist(analyzer.values(), bins=20)
	plot.xlabel('Read Length')
	plot.ylabel('Number of Reads')
        plot.title('%s %s' % (readtype, failorpass))
	plot.savefig(''+histname+'.png',format='png')


path=sys.argv[1]
rr("fwd,rev", path, "fail", "1Dfailures")
print '1D failure histogram generated'
rr("fwd,rev", path, "pass", "1Dpasses")
print '1D pass histogram generated'
rr("2D", path, "fail", "2Dfailures")
print '2D failure histogram generated'
rr("2D", path, "pass", "2Dpasses")
print '2D pass histogram generated'

#Creating histograms for both 1D and 2D in the pass and fail folder
print "Creating 1D and 2D failure histogram"
os.system("poretools hist --saveas histallfail.png "+path+"downloads/fail/")
print "Creating 1D and 2D pass histogram"
os.system("poretools hist --saveas histallpass.png "+path+"downloads/pass/")
