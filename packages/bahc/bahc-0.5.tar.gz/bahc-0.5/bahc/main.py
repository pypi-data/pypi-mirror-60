import numpy as np
import fastcluster


def dist(R):
    N = R.shape[0]
    d = R[np.triu_indices(N,1)]
    out = fastcluster.average(d).astype(int)

    #Genealogy Set
    dend = {i: (np.array([i]),) for i in range(N)}
    for i,(a,b,_,_) in enumerate(out):
        dend[i+N] = (np.concatenate(dend[a]),np.concatenate(dend[b]))

    
    [dend.pop(i,None) for i in range(N)]

    return dend.values()

def AvLinkC(Dend,R):

    N = R.shape[0]
    Rs = np.zeros((N,N))

    for (a,b) in Dend:
        Rs[np.ix_(a,b)] = R[a][:,b].mean()

    Rs = Rs+Rs.T

    np.fill_diagonal(Rs,1)
    return Rs	
    
def noise(N,T,epsilon=1e-10):
    return np.random.normal(0,epsilon ,size=(N,T))

def filterCorrelation(x,Nboot=100):

    N,T = x.shape
    rT = range(T)

    Cbav = np.zeros((N,N))
    for _ in range(Nboot):
        xboot = x[:,np.random.choice(rT,size=T,replace=True)] + noise( N,T ) 
        Cboot  = np.corrcoef(xboot)
        Dend = dist(1-Cboot)
        Cbav += AvLinkC(Dend,Cboot)

    Cbav = Cbav/Nboot
    return Cbav

def filterCovariance(x,Nboot=100):

    N,T = x.shape
    rT = range(T)

    Sbav = np.zeros((N,N))
    for _ in range(Nboot):
        xboot = x[:,np.random.choice(rT,size=T,replace=True)] + noise( N,T ) 
        Cboot  = np.corrcoef(xboot)
        Dend = dist(1-Cboot)
        std = xboot.std(axis=1)
        Sbav += AvLinkC(Dend,Cboot)*np.outer(std,std)

    Sbav = Sbav/Nboot
    return Sbav


def filterCovarianceArmonic(x,Nboot=100):

    N,T = x.shape
    rT = range(T)

    Sbav = np.zeros((N,N))
    for _ in range(Nboot):
        xboot = x[:,np.random.choice(rT,size=T,replace=True)] + noise( N,T ) 
        Cboot  = np.corrcoef(xboot)
        Dend = dist(1-Cboot)
        std = xboot.std(axis=1)
        Sbav += np.linalg.pinv(AvLinkC(Dend,Cboot)*np.outer(std,std))

    Sbav = Sbav/Nboot
    return np.linalg.pinv(Sbav)
