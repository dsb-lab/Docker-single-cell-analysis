import scanpy as scp
import numpy as np
import sklearn.cluster as cluster
import scipy.stats as st
from sklearn.linear_model import LinearRegression
import numba
import scipy as sp
import matplotlib.pyplot as plt
import seaborn as sb
import pandas as pd
import networkx as nx
from pygam import LinearGAM, s, f

def loadData(name="./dataOut/Raw.h5ad",QC_basic=False,Normalized=False,Log1=False,QC_Doublets_Stripped=False,Log=False,sample="All",stage="All"):
    
    a = scp.read(name)
    
    if QC_basic:
        a = a[np.invert(a.obs.loc[:,"QC_basic_trimmed"]),np.invert(a.var.loc[:,"QC_basic_trimmed"])]
        
    if Normalized:
        scp.pp.normalize_total(a,target_sum=a.obs["nCounts"].mean())
        
    if Log1:
        scp.pp.log1p(a)
        
    if stage != "All":
        s = np.array([False for i in range(a.shape[0])])
        for i in stage:
            s += (a.obs["stage"]==i).values
        a = a[s,:]
        
    if sample != "All":
        s = np.array([False for i in range(a.shape[0])])
        for i in sample:
            s += (a.obs["sample"]==i).values
        a = a[s,:]            

    return a

def generateSamples(Ncells=250,Ngenes=10000,DEgenes=1000,psList=[0.2,0.5,0.8]):

    DElist = np.array(range(Ngenes))
    np.random.shuffle(DElist)
    DElist = [DElist[i*DEgenes:(i+1)*DEgenes] for i in range(3)]
    r = np.random.rand(DEgenes)

    sample = np.zeros([3*Ncells,Ngenes])
    trueFactors = np.zeros(3*Ncells)
    ids = np.zeros(3*Ncells)
    for i,ps in enumerate(psList):
        #theta0
        theta0 = 2**st.norm.rvs(0,0.5,size=Ncells)
        #phis
        phis = np.ones(Ngenes)
        phis[DElist[i][r<ps]] = 5
        phis[DElist[i][r>ps]] = 0.00001
        #lambda0
        lambda0 = st.gamma.rvs(2,scale=1/2,size=Ngenes)
        #lamda
        lamda = lambda0*phis
        #nbinomial
        m = np.dot(theta0.reshape(-1,1),lamda.reshape(-1,1).transpose())
        v = m+m**2/1
        p = 1-m/v
        n = m*(1-p)/p

        sample[i*Ncells:(i+1)*Ncells] = st.nbinom.rvs(n=n,p=p)
        trueFactors[i*Ncells:(i+1)*Ncells] = theta0
        ids[i*Ncells:(i+1)*Ncells] = i
        
    return sample, trueFactors, ids

def quickCluster(adata,use_pcs=True,n_components=np.Inf,minCluster=1,maxCluster=1000):
        
    if use_pcs:
        try:
            if n_components <= adata.obsm["X_pca"].shape[0]:
                X = adata.obsm["X_pca"][n_components,:]
            else:
                X = adata.obsm["X_pca"]            
        except:
            print("Run scanpy.pp.pca function first")   
    else:
        X = adata.X.toarray()


    l1 = np.random.choice(range(X.shape[0]),size=10000)
    l2 = np.random.choice(range(X.shape[0]),size=10000)

    d = []
    for i,j in zip(l1,l2):
        d.append(np.sqrt(np.sum((X[i,:]-X[j,:])**2)))

    t = np.mean(d)
    nC = X.shape[0]//maxCluster+1

    nClusters = 1
    while nClusters < nC:
        t *= 0.8
        model = cluster.Birch(threshold=t,n_clusters=nC)
        model.fit(X)

        nClusters = np.copy(model.subcluster_centers_.shape[0])
        clusterCenters = np.copy(model.subcluster_centers_)
        clusterLabels = np.copy(model.labels_)

    #Agregate minimums
    hist = np.histogram(clusterLabels,bins=np.arange(-0.5,nClusters+1.5,1))[0]

    removed = []

    while hist.min() < minCluster:

        m = np.where(hist == hist.min())[0][0]

        dmin = np.Inf
        posmin = 0
        for i in range(model.n_clusters):
            d = np.sqrt(np.sum((clusterCenters[m,:][0]-clusterCenters[i,:][0])**2))
            if d < dmin and (i not in removed):
                dmin = d
                posmin = i

        clusterLabels[clusterLabels==m] = posmin
        if m < nClusters:
            clusterLabels[clusterLabels==nClusters] = m
        nClusters -= 1

        hist = np.histogram(clusterLabels,bins=np.arange(-0.5,nClusters+1.5,1))[0]

    hist = np.histogram(clusterLabels,bins=np.arange(-0.5,nClusters+1.5,1))[0]

    #Disgregate maximums
    for m in np.where(hist >= maxCluster)[0]:

        l = np.sum(clusterLabels == m)
        n = l//maxCluster

        for i in range(n):
            change = np.random.choice(np.where(clusterLabels==m)[0],size=maxCluster,replace=False)
            nClusters += 1
            clusterLabels[change] = nClusters

    return clusterLabels

def adjacency_matrix_max_knn_distance(adata, cut, obsp_key = "", add_key=""):
    try: 
        dmatrix = adata.obsp["distances"+obsp_key].copy()
        wmatrix = adata.obsp["connectivities"+obsp_key].copy()
    except:
        print("Compute first neighbours.")
        
    pos = dmatrix.nonzero()
    distances = np.array(dmatrix[pos])[0]

    dmatrix[pos[0][distances>cut],pos[1][distances>cut]] = 0
    dmatrix[pos[1][distances>cut],pos[0][distances>cut]] = 0
    
    wmatrix[pos[0][distances>cut],pos[1][distances>cut]] = 0
    wmatrix[pos[1][distances>cut],pos[0][distances>cut]] = 0

    if add_key == "":
        adata.obsp["connectivities_flexible"] = wmatrix
        adata.obsp["distances_flexible"] = dmatrix
    else:
        adata.obsp["_connectivities_flexible"] = wmatrix
        adata.obsp["_distances_flexible"] = dmatrix

    return

def flexible_neighbors(adata, cut, obsp_key = "", add_key = ""):
    try:
        dmatrix = adata.obsp["distances"+obsp_key].copy()
    except:
        print("Compute first neighbours first.")
        
    pos = dmatrix.nonzero()
    distances = np.array(dmatrix[pos])[0]

    dmatrix[pos[0][distances>cut],pos[1][distances>cut]] = 0
    dmatrix[pos[1][distances>cut],pos[0][distances>cut]] = 0

    dmatrix.eliminate_zeros()

    retained = np.array(np.sum(dmatrix!=0,axis=1))[:,0]
    
    if add_key == "":
        name = "flexible_neighbors_cluster_size"
        name2 = "connectivities_flexible"
        adata.obs["flexible_neighbors_nn"] = retained
        adata.obs["flexible_neighbors_cluster_size"] = 0
        adata.uns["flexible_neighbors"] = {"cut":cut}
    else:
        name = add_key+"_flexible_neighbors_cluster_size"
        name2 = add_key+"_connectivities_flexible"
        adata.obs[add_key+"_flexible_neighbors_nn"] = retained
        adata.obs[add_key+"_flexible_neighbors_cluster_size"] = 0
        adata.uns[add_key+"_flexible_neighbors"] = {"cut":cut}

    #Make adjacency
    adjacency_matrix_max_knn_distance(adata, cut, obsp_key = obsp_key, add_key=add_key)
    
    #Add cluster size
    g = nx.convert_matrix.from_scipy_sparse_matrix(adata.obsp[name2]>0, create_using=nx.MultiGraph)
    l = list(nx.connected_components(g))
    for i in l:
        s = len(i)
        adata.obs.loc[adata.obs.iloc[list(i)].index,name] = s
    
    return

def cluster_overlap(a,obs1,obs2,r=2):

    l1 = a.obs[obs1].unique().astype(float)
    l2 = a.obs[obs2].unique().astype(float)

    l1 -= 0.5
    l2 -= 0.5
    l1 = np.sort(np.append(l1,l1[-1]+1))
    l2 = np.sort(np.append(l2,l2[-1]+1))

    h = np.histogram2d(a.obs[obs1].astype(float),a.obs[obs2].astype(float),bins=(l1,l2))[0].transpose()
    p = np.histogram(a.obs[obs1].astype(float),bins=l1)[0]
    p[p==0]=1

    m = h/p

    m = m.round(r)   
    
    data = pd.DataFrame(m)
    
    #l= data.idxmax(axis=1).values
    #add = [i for i in data.columns if i not in np.unique(l)]
    #ll = []
    #for i in range(l.size):
    #    if l[i] not in l[:i]:
    #        ll.append(l[i])
    #    else:
    #        ll.append(add.pop(0))
        
    #data = data[ll]
        
    return data

def plot_cluster_overlap(a,obs1,obs2,r=1,ax=None):

    m = cluster_overlap(a,obs1,obs2,r=r)
    
    if ax == None:
        f, ax = plt.subplots(figsize=(9, 6))
        sb.heatmap(m,annot=True,ax=ax)

        ax.set_xlabel(obs1,fontsize=20)
        ax.set_ylabel(obs2,fontsize=20)
    else:
        sb.heatmap(m,annot=True,ax=ax)

        ax.set_xlabel(obs1,fontsize=20)
        ax.set_ylabel(obs2,fontsize=20)        
        
    return

def linearize_UMAP(adata,clusters_ref,clusters,map_ref,regress=True):
    
    #Make centers
    centers = []
    for i in clusters:
        subadata = adata[adata.obs.loc[:,clusters_ref]==i].obsm[map_ref]
        centers.append(np.mean(np.nan_to_num(subadata),axis=0).copy())
    #Make closeness
    select = adata.obs.loc[:,clusters_ref]==clusters[0]
    for i in clusters[1:]:
        select += adata.obs.loc[:,clusters_ref]==i

    subadata = adata[select].obsm[map_ref].copy()
    
    distanceSin = []
    distanceCos = []
    dd = 0
    for i in range(len(centers)-1):
        v = centers[i+1]-centers[i]
        d = np.sqrt(np.dot(v,v))
        v /= d
        corr = subadata-centers[i]
        #sin = np.sum(np.power(corr,2),axis=1)-np.power(np.dot(corr,v),2)
        #sin = np.sign(sin)*np.sqrt(sin)
        sin = np.dot(corr,[-v[1],v[0]])
        cos = np.dot(corr,v)

        if i < len(centers)-2:
            dist = np.sqrt(np.sum(np.power(subadata-centers[i+1],2),axis=1))
            change = np.where(cos>d)[0]
            sin[change] = dist[change]

        if i > 0:
            dist = np.sqrt(np.sum(np.power(subadata-centers[i],2),axis=1))
            change = np.where(cos<0)[0]
            sin[change] = dist[change]

        dd += d
        cos = np.dot(corr,v) + dd 

        distanceSin.append(sin.copy())
        distanceCos.append(cos.copy())

    #Obtain distances
    distanceSin = np.array(distanceSin)
    distanceCos = np.array(distanceCos)
    closer = np.argmin(distanceSin,axis=0)
    y = [distanceSin[j,i] for i,j in enumerate(closer)]
    x = [distanceCos[j,i] for i,j in enumerate(closer)]
    y=np.nan_to_num(y)
    x=np.nan_to_num(x)

    x = (x-min(x))/(max(x)-min(x))

    if regress:
        gam = LinearGAM(s(0)).fit(x, y)
        y = y-gam.predict(x)

    return x, y

def plot_scatter_expression(x,adata,gene,ax,clusters_ref=None,clusters=None,bins=None,**kwargs):

    if clusters_ref != None:
        #Select data
        select = adata.obs.loc[:,clusters_ref]==clusters[0]
        for i in clusters[1:]:
            select += adata.obs.loc[:,clusters_ref]==i

        y = np.array(adata[select,gene].X.todense())[:,0]
        
    else:
        
        y = np.array(adata[:,gene].X.todense())[:,0]
    
    if bins == None:
        sb.scatterplot(x,y,hue=adata[select].obs["louvain"],ax=ax)
    else:
        bbins = np.histogram(x,bins=bins)[1]
        d = np.digitize(x,bbins)
        expression = np.zeros(bins)
        for i in range(bins):
            expression[i] = y[np.where(d==i)].mean()
            
        sb.scatterplot((bbins[:-1]+bbins[1:])/2,expression,ax=ax,**kwargs)
        
    return

def plot_line_expression(x,adata,gene,ax,clusters_ref=None,clusters=None,**kwargs):

    if clusters_ref != None:
        #Select data
        select = adata.obs.loc[:,clusters_ref]==clusters[0]
        for i in clusters[1:]:
            select += adata.obs.loc[:,clusters_ref]==i

        y = np.array(adata[select,gene].X.todense())[:,0]
        
    else:
        
        y = np.array(adata[:,gene].X.todense())[:,0]
        
    gam = LinearGAM(s(0)).fit(x, y)

    xx = np.arange(0,1,0.01)
    sb.lineplot(xx,gam.predict(xx),ax=ax,**kwargs)
        
    return

def neighbours_overlap(adata,obs1,obs2):
    knn1 = adata.uns[obs1]["params"]["n_neighbors"]
    knn2 = adata.uns[obs2]["params"]["n_neighbors"]
    if knn1 != knn2:
        print("Both observables have a different number of neighbours.")
        
    n1 = adata.obsp[str(obs1)+"_distances"].nonzero()[1]
    n2 = adata.obsp[str(obs2)+"_distances"].nonzero()[1]
    
    m = []
    for i in range(0,len(n1),knn1-1):
        m.append(len([j for j in n1[i:i+knn1-1] if j in n2[i:i+knn1-1]])/(knn1-1))

    d = pd.DataFrame(m)
    
    return d

def mnn_correct(adata,key,key_obsm="X_pca",key_added="X_MNN",order=None,**kwargs):
    
    #Sort by size
    if order == None:
        orderMerge = np.unique(adata.obs[key])
        s = []
        for j in orderMerge:
            s.append(adata[adata.obs[key]==j].shape[0])
        orderMerge = orderMerge[np.argsort(-np.array(s))]
    else:
        orderMerge = order
    
    c = scp.AnnData(adata.obsm[key_obsm].copy())
    c.obs = adata.obs.copy()
    c.var.index = c.var.index.astype(str)
    l = [c[c.obs[key]==i] for i in orderMerge]
    if len(l)>1:
        c = scp.external.pp.mnn_correct(*l)[0]
        c.obs.index = [i.split("-")[0] for i in c.obs.index]
        sort = np.sort(c.obs.index.values.astype(int)).astype(str)
        c = c[sort]
        
    adata.obsm[key_added] = c.X.copy()
    
    return

def mnn_correct_twice(adata,key1,key2,order,key_obsm="X_pca",key_added="X_MNN",**kwargs):
    
    print(key1)
    
    l = []
    for i in order:
        print(i)
        b = adata[adata.obs[key2]==i].copy()
        mnn_correct(b,key1,key_obsm="X_pca",key_added="_Aux")
        c = scp.AnnData(b.obsm["_Aux"].copy())
        c.obs = b.obs.copy()
        c.var.index = c.var.index.astype(str)
        l.append(c.copy())
        
    if len(l)>1:
        #blockPrint()#To avoid printing
        b = scp.external.pp.mnn_correct(*l,verbosity=False)[0]
        #enablePrint()#To enable printing
        b.obs.index = [i.split("-")[0] for i in b.obs.index]
        sort = np.sort(b.obs.index.values.astype(int)).astype(str)
        b = b[sort]
        
    adata.obsm[key_added] = b.X.copy()
    
    del b, c
    
    return