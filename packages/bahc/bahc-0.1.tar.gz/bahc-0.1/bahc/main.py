import numpy as np
import fastcluster

def flatten(container):
    for i in container:
        if isinstance(i, (list,tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i
def flatx(x):
    return tuple(sorted(flatten(x)))

def dist(R):
	N = R.shape[0]
	d = R[np.triu_indices(N,1)]

	out = fastcluster.average(d)

	outI = out.astype(int)
	dend = {i:(i,) for i in range(N)}

	for i in range(len(outI)):
		dend[i+N] = (dend[outI[i][0]],dend[outI[i][1]])
	for i in range(N):
		dend.pop(i,None)

	dend = [(flatx(a),flatx(b)) for a,b in dend.values()]

	dend ={flatx((a,b)):(np.array(a),np.array(b)) for a,b in dend}
	return dend


import sys
if  sys.version_info >= (3, 0):
	def AvLinkC(Dend,R):
		C = dict.fromkeys(Dend)

		N = R.shape[0]
		Rs = np.zeros((N,N))

		for c,(a,b) in Dend.items():
			if not tuple(sorted(c)) in C: continue
			p = R[a][:,b].mean()
	 
			Rs[np.ix_(a,b)] = p

		Rs = Rs+Rs.T

		np.fill_diagonal(Rs,1)
		return Rs	

else:	
	def AvLinkC(Dend,R):
		C = dict.fromkeys(Dend)

		N = R.shape[0]
		Rs = np.zeros((N,N))

		for c,(a,b) in Dend.items():
			if not C.has_key(tuple(sorted(c))): continue
			p = R[a][:,b].mean()
	 
			Rs[np.ix_(a,b)] = p

		Rs = Rs+Rs.T

		np.fill_diagonal(Rs,1)
		return Rs
    

def filterCorrelation(x,Nboot=100):

	tin = x.shape[1]
	rn = range(x.shape[1])

	Rvx = np.zeros((x.shape[0],x.shape[0]))
	for _ in range(Nboot):
		xx = x[:,np.random.choice(rn,size=tin,replace=True)]+np.random.normal(0,1e-10,size=(x.shape[0],tin))
		Rx  = np.corrcoef(xx)
		DendAv = dist(1-Rx)
		Rvx += AvLinkC(DendAv,Rx)

	Rvx = Rvx/Rvx[0,0]
	return Rvx

def filterCovariance(x,Nboot=100):

	tin = x.shape[1]
	rn = range(x.shape[1])

	Cvx = np.zeros((x.shape[0],x.shape[0]))
	for _ in range(Nboot):
		xx = x[:,np.random.choice(rn,size=tin,replace=True)]+np.random.normal(0,1e-10,size=(x.shape[0],tin))
		Rx  = np.corrcoef(xx)
		DendAv = dist(1-Rx)
		s = xx.std(axis=1)
		Cvx += AvLinkC(DendAv,Rx)*np.outer(s,s)

	Cvx = Cvx/Nboot
	return Cvx

