""" This function return the cluster labels for the optimal cutt-off based on the choosen hierarchical clustering method

	out = silhouette.fit(X)
	fig = silhouette.plot(out, X)

 INPUT:
   X:             datamatrix
                   rows    = features
                   colums  = samples
 OPTIONAL

 metric=         String: Distance measure for the clustering 
                 'euclidean' (default)
                 'kmeans' (prototypes)

 linkage=        String: Linkage type for the clustering 
                 'ward' (default)
                 'ward' (default)
                 'single
                 'complete'
                 'average'
                 'weighted'
                 'centroid'
                 'median'

 minclusters=    Integer: Minimum or more number of clusters >=
                 [2] (default)

 maxclusters=    Integer: Maximum or less number of clusters <=
                 [25] (default)

 savemem=        Boolean [0,1]: This works only for KMeans
                 [False]: No (default)
                 [True]: Yes

 showfig=        Boolean [0,1]:
                 [0]: No (default)
                 [1]: Yes (silhoutte plot)
                   
 height=         Integer:  Height of figure
                 [5]: (default)

 width=          Integer:  Width of figure
                 [5]: (default)

 verbose=        Boolean [0,1]: Progressbar
                 [0]: No (default)
                 [1]: Yes

 OUTPUT
	output

 DESCRIPTION
  This function return the cluster labels for the optimal cutt-off based on the choosen clustering method
  
 EXAMPLE
   import clusteval.silhouette as silhouette

   from sklearn.datasets.samples_generator import make_blobs
   [X, labels_true] = make_blobs(n_samples=750, centers=5, n_features=10)
   out = silhouette.fit(X)
   out = silhouette.fit(X, metric='kmeans', savemem=True)
   silhouette.plot(out, X)


 SEE ALSO
   silhouette_plot
"""
#print(__doc__)

#--------------------------------------------------------------------------
# Name        : silhouette.py
# Author      : E.Taskesen
# Contact     : erdogant@gmail.com
# Date        : Feb. 2018
#--------------------------------------------------------------------------

#%% Libraries
import numpy as np
import pandas as pd
from tqdm import tqdm
from scipy.cluster.hierarchy import fcluster
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import silhouette_score
from clusteval.silhouette_plot import silhouette_plot
import matplotlib.pyplot as plt

#%% plot
def plot(out, X=None, width=15, height=8):
    idx = np.argmax(out['fig']['silscores'])
    # Make figure
    [fig, ax1] = plt.subplots(figsize=(width,height))
    # Plot
    ax1.plot(out['fig']['sillclust'], out['fig']['silscores'], color='k')
    # Plot optimal cut
    ax1.axvline(x=out['fig']['clustcutt'][idx], ymin=0, ymax=out['fig']['sillclust'][idx], linewidth=2, color='r',linestyle="--")
    # Set fontsizes
    plt.rc('axes', titlesize=14)     # fontsize of the axes title
    plt.rc('xtick', labelsize=10)     # fontsize of the axes title
    plt.rc('ytick', labelsize=10)     # fontsize of the axes title
    plt.rc('font', size=10)
    # Set labels
    ax1.set_xticks(out['fig']['clustcutt'])
    ax1.set_xlabel('#Clusters')
    ax1.set_ylabel('Score')
    ax1.set_title("Silhoutte score versus number of clusters")
    ax1.grid(color='grey', linestyle='--', linewidth=0.2)

    # Plot silhoutte samples plot
    if not isinstance(X, type(None)):
        silhouette_plot(X,out['labx'])

#%% Main
def fit(X, metric='euclidean', linkage='ward', minclusters=2, maxclusters=25, Z=[], savemem=False, verbose=3):
	# DECLARATIONS
    out ={}
    
    # Make dictionary to store Parameters
    Param = {}
    Param['verbose']     = verbose
    Param['metric']      = metric
    Param['linkage']     = linkage
    Param['minclusters'] = minclusters
    Param['maxclusters'] = maxclusters
    Param['savemem']     = savemem

    # Savemem for kmeans
    if Param['metric']=='kmeans':
        if Param['savemem']:
            kmeansmodel=MiniBatchKMeans
            if Param['verbose']>=3: print('[SILHOUETTE]>Save memory enabled for kmeans.')
        else:
            kmeansmodel=KMeans
    
    # Cluster hierarchical using on metric/linkage
    if len(Z)==0 and Param['metric']!='kmeans':
        from scipy.cluster.hierarchy import linkage
        Z=linkage(X, method=Param['linkage'], metric=Param['metric'])

    # Make all possible cluster-cut-offs
    if Param['verbose']>=3: print('[SILHOUETTE] Determining optimal [%s] clustering by Silhoutte score..' %(Param['metric']))

    # Setup storing parameters
    clustcutt = np.arange(Param['minclusters'],Param['maxclusters'])
    silscores = np.zeros((len(clustcutt)))*np.nan
    sillclust = np.zeros((len(clustcutt)))*np.nan
    clustlabx = []

    # Run over all cluster cutoffs
    for i in tqdm(range(len(clustcutt))):
        # Cut the dendrogram for i clusters
        if Param['metric']=='kmeans':
            labx=kmeansmodel(n_clusters=clustcutt[i], verbose=0).fit(X).labels_
        else:
            labx = fcluster(Z, clustcutt[i], criterion='maxclust')

        # Store labx for cluster-cut
        clustlabx.append(labx)
        # Store number of unique clusters
        sillclust[i]=len(np.unique(labx))
        # Compute silhoutte (can only be done if more then 1 cluster)
        if sillclust[i]>1:
            silscores[i]=silhouette_score(X, labx)

    # Convert to array
    clustlabx = np.array(clustlabx)
    
    # Store only if agrees to restriction of input clusters number
    I1 = np.isnan(silscores)==False
    I2 = sillclust>=Param['minclusters']
    I3 = sillclust<=Param['maxclusters']
    I  = I1 & I2 & I3

    # Get only clusters of interest
    silscores = silscores[I]
    sillclust = sillclust[I]
    clustlabx = clustlabx[I,:]
    clustcutt = clustcutt[I]
    idx = np.argmax(silscores)
    
    # Store results
    out['methodtype']='silhoutte'
    out['score'] = pd.DataFrame(np.array([sillclust,silscores]).T, columns=['clusters','score'])
    out['score']['clusters'] = out['score']['clusters'].astype(int)
    out['labx']  = clustlabx[idx,:]-1
    out['fig']=dict()
    out['fig']['silscores']=silscores
    out['fig']['sillclust']=sillclust
    out['fig']['clustcutt']=clustcutt
    
    # Return
    return(out)
