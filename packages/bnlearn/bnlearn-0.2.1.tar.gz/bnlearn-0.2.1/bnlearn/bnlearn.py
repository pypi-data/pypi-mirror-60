"""This package provides several bayesian techniques for structure learning, sampling and parameter learning.

import bnlearn

model            = bnlearn.import_DAG('sprinkler')
df               = bnlearn.import_example()
df               = bnlearn.sampling(model)
q                = bnlearn.inference.fit(model)
model_sl         = bnlearn.structure_learning.fit(df)
model_pl         = bnlearn.parameter_learning.fit(model_sl, df)
[scores, adjmat] = bnlearn.compare_networks(model_sl, model)


Description
-----------
Learning a Bayesian network can be split into two problems:
    * Parameter learning: Given a set of data samples and a DAG that captures the dependencies between the variables,
      estimate the (conditional) probability distributions of the individual variables.
    * Structure learning: Given a set of data samples, estimate a DAG that captures the dependencies between the variables.
Currently, the library supports:
    * Parameter learning for *discrete* nodes:
    * Maximum Likelihood Estimation
    * Bayesian Estimation
Structure learning for *discrete*, *fully observed* networks:
    * Score-based structure estimation (BIC/BDeu/K2 score; exhaustive search, hill climb/tabu search)
    * Constraint-based structure estimation (PC)
    * Hybrid structure estimation (MMHC)


Requirements
------------
see requirements.txt

"""
# ------------------------------------
# Name        : bnlearn.py
# Author      : E.Taskesen
# Contact     : erdogant@gmail.com
# Licence     : See licences
# ------------------------------------


# %% Libraries
import os
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import json
# DAG
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
# SAMPLING
from pgmpy.sampling import BayesianModelSampling  # GibbsSampling
from pgmpy import readwrite
# MICROSERVICES
import bnlearn.helpers.network as network
curpath = os.path.dirname(os.path.abspath(__file__))
PATH_TO_DATA = os.path.join(curpath,'DATA')


# %% Sampling from model
def sampling(model, n=1000, verbose=3):
    """Sample based on DAG.

    Parameters
    ----------
    model : dict
        Contains model and adjmat

    n : int
        Number of samples to generate
        n=1000 (default)

    verbose : int [0-5] (default: 3)
        Print messages to screen.
        0: NONE
        1: ERROR
        2: WARNING
        3: INFO (default)
        4: DEBUG
        5: TRACE

    Returns
    -------
    Pandas DataFrame
    

    Example
    -------
    import bnlearn
    model = bnlearn.import_DAG('sprinkler')
    df = bnlearn.sampling(model, n=1000)

    """
    assert n>0, 'n must be 1 or larger'
    assert 'BayesianModel' in str(type(model['model'])), 'Model must contain DAG from BayesianModel. Note that <misarables> example does not include DAG.'
    if verbose>=3: print('[BNLEARN][sampling] Forward sampling for %.0d samples..' %(n))

    # http://pgmpy.org/sampling.html
    inference = BayesianModelSampling(model['model'])
    # inference = GibbsSampling(model)
    # Forward sampling and make dataframe
    df=inference.forward_sample(size=n, return_type='dataframe')
    return(df)


# %% Make DAG
def import_DAG(filepath='sprinkler', CPD=True, verbose=3):
    """Import Directed Acyclic Graph.

    Parameters
    ----------
    filepath : String, optional (default: 'sprinkler')
        Pre-defined examples are depicted below, or provide the absolute file path to the .bif model file.
        'sprinkler'(default)
        'alarm'
        'andes'
        'asia'
        'pathfinder'
        'sachs'
        'miserables'
        'filepath/to/model.bif'

    CPD : Bool, optional (default: True)
        Directed Acyclic Graph (DAG).
        True (default)
        False

    verbose : int [0-5] (default: 3)
        Print messages to screen.
        0: NONE
        1: ERROR
        2: WARNING
        3: INFO (default)
        4: DEBUG
        5: TRACE


    Returns
    -------
    None.
    

    Example
    -------
    model = bnlearn.import_DAG('sprinkler')
    bnlearn.plot(model)

    """
    out=dict()
    model=None
    filepath=filepath.lower()

    # Load data
    if filepath=='sprinkler':
        model = _DAG_sprinkler(CPD=CPD)
    elif filepath=='asia':
        model = _bif2bayesian(os.path.join(PATH_TO_DATA,'ASIA/asia.bif'), verbose=verbose)
    elif filepath=='alarm':
        model = _bif2bayesian(os.path.join(PATH_TO_DATA,'ALARM/alarm.bif'), verbose=verbose)
    elif filepath=='andes':
        model = _bif2bayesian(os.path.join(PATH_TO_DATA,'ANDES/andes.bif'), verbose=verbose)
    elif filepath=='pathfinder':
        model = _bif2bayesian(os.path.join(PATH_TO_DATA,'PATHFINDER/pathfinder.bif'), verbose=verbose)
    elif filepath=='sachs':
        model = _bif2bayesian(os.path.join(PATH_TO_DATA,'SACHS/sachs.bif'), verbose=verbose)
    elif filepath=='miserables':
        f = open(os.path.join(PATH_TO_DATA,'miserables.json'))
        data = json.loads(f.read())
        L=len(data['links'])
        edges=[(data['links'][k]['source'], data['links'][k]['target']) for k in range(L)]
        model=nx.Graph(edges, directed=False)
    else:
        if os.path.isfile(filepath):
            model = _bif2bayesian(filepath, verbose=verbose)
        else:
            if verbose>=3: print('[BNLEARN][import_DAG] Filepath does not exist! <%s>' %(filepath))
            return(out)

    # check_model check for the model structure and the associated CPD and returns True if everything is correct otherwise throws an exception
    if not isinstance(model, type(None)) and verbose>=3:
        if CPD:
            print('[BNLEARN][import_DAG] Model correct: %s' %(model.check_model()))
            for cpd in model.get_cpds():
                print("CPD of {variable}:".format(variable=cpd.variable))
                print(cpd)

            print('[BNLEARN][import_DAG] Nodes: %s' %(model.nodes()))
            print('[BNLEARN][import_DAG] Edges: %s' %(model.edges()))
            print('[BNLEARN][import_DAG] Independencies:\n%s' %(model.get_independencies()))

    # Setup simmilarity matrix
    adjmat = pd.DataFrame(data=False, index=model.nodes(), columns=model.nodes()).astype('Bool')
    # Fill adjmat with edges
    edges=model.edges()
    for edge in edges:
        adjmat.loc[edge[0],edge[1]]=True

    out['model']=model
    out['adjmat']=adjmat
    return(out)


# %% Model Sprinkler
def _DAG_sprinkler(CPD=True):
    """Create DAG-model for the sprinkler example.

    Parameters
    ----------
    CPD : Bool, optional (default: True)
        Directed Acyclic Graph (DAG).
        True (default)
        False

    Returns
    -------
    model.

    """
    # Define the network structure
    model = BayesianModel([('Cloudy', 'Sprinkler'),
                           ('Cloudy', 'Rain'),
                           ('Sprinkler', 'Wet_Grass'),
                           ('Rain', 'Wet_Grass')])

    if CPD:
        # Cloudy
        cpt_cloudy = TabularCPD(variable='Cloudy', variable_card=2, values=[[0.5], [0.5]])
        # Sprinkler
        cpt_sprinkler = TabularCPD(variable='Sprinkler', variable_card=2,
                                   values=[[0.5, 0.9], [0.5, 0.1]],
                                   evidence=['Cloudy'], evidence_card=[2])
        # Rain
        cpt_rain = TabularCPD(variable='Rain', variable_card=2,
                              values=[[0.8, 0.2], [0.2, 0.8]],
                              evidence=['Cloudy'], evidence_card=[2])
        # Wet Grass
        cpt_wet_grass = TabularCPD(variable='Wet_Grass', variable_card=2,
                                   values=[[1, 0.1, 0.1, 0.01],
                                           [0, 0.9, 0.9, 0.99]],
                                   evidence=['Sprinkler', 'Rain'],
                                   evidence_card=[2, 2])
        # Connect DAG with CPTs
        # Associating the parameters with the model structure.
        model.add_cpds(cpt_cloudy, cpt_sprinkler, cpt_rain, cpt_wet_grass)

    return(model)


# %% Convert BIF model to bayesian model
def _bif2bayesian(pathname, verbose=3):
    """Return the fitted bayesian model.

    Example
    -------
    >>> from pgmpy.readwrite import BIFReader
    >>> reader = BIFReader("bif_test.bif")
    >>> reader.get_model()
    <pgmpy.models.BayesianModel.BayesianModel object at 0x7f20af154320>
    """
    if verbose>=3: print('[BNLEARN] Loading bif file <%s>' %(pathname))

    bifmodel=readwrite.BIF.BIFReader(path=pathname)

    try:
        model = BayesianModel(bifmodel.variable_edges)
        model.name = bifmodel.network_name
        model.add_nodes_from(bifmodel.variable_names)

        tabular_cpds = []
        for var in sorted(bifmodel.variable_cpds.keys()):
            values = bifmodel.variable_cpds[var]
            cpd = TabularCPD(var, len(bifmodel.variable_states[var]), values,
                             evidence=bifmodel.variable_parents[var],
                             evidence_card=[len(bifmodel.variable_states[evidence_var])
                                            for evidence_var in bifmodel.variable_parents[var]])
            tabular_cpds.append(cpd)

        model.add_cpds(*tabular_cpds)
#        for node, properties in bifmodel.variable_properties.items():
#            for prop in properties:
#                prop_name, prop_value = map(lambda t: t.strip(), prop.split('='))
#                model.node[node][prop_name] = prop_value

        return model

    except AttributeError:
        raise AttributeError('[BNLEARN] First get states of variables, edges, parents and network names')


# %% Make directed graph from adjmatrix
def to_undirected(adjmat):
    """Transform directed adjacency matrix to undirected.

    Parameters
    ----------
    adjmat : numpy aray
        Adjacency matrix.

    Returns
    -------
    Directed adjacency matrix.

    """
    num_rows=adjmat.shape[0]
    num_cols=adjmat.shape[1]
    adjmat_directed=np.zeros((num_rows, num_cols), dtype=int)
    tmpadjmat=adjmat.astype(int)

    for i in range(num_rows):
        for j in range(num_cols):
            adjmat_directed[i,j] = tmpadjmat.iloc[i,j] + tmpadjmat.iloc[j,i]

    adjmat_directed=pd.DataFrame(index=adjmat.index, data=adjmat_directed, columns=adjmat.columns, dtype=bool)
    return(adjmat_directed)


# %% Comparison of two networks
def compare_networks(model_1, model_2, pos=None, showfig=True, figsize=(15,8), verbose=3):
    """Compare networks of two models.

    Parameters
    ----------
    model_1 : dict
        Results of model 1.
    model_2 : dict
        Results of model 2.
    pos : graph, optional (default: None)
        Coordinates of the network. If there are provided, the same structure will be used to plot the network.
    showfig : Bool, optional (default: True)
        Show figure.
    figsize : tuple, optional (default: (15,8))
        Figure size.
    verbose : int [0-5], optional (default: 3)
        Print messages.
        0: (default)
        1: ERROR
        2: WARN
        3: INFO
        4: DEBUG

    Returns
    -------
    dict.

    """
    [scores, adjmat_diff] = network.compare_networks(model_1['adjmat'], model_2['adjmat'], pos=pos, showfig=showfig, width=figsize[0], height=figsize[1], verbose=verbose)
    return(scores, adjmat_diff)


# %% PLOT
def plot(model, pos=None, scale=1, figsize=(15,8), verbose=3):
    """Plot the learned stucture.

    Parameters
    ----------
    model : dict
        Learned model from the .fit() function.
    pos : graph, optional (default: None)
        Coordinates of the network. If there are provided, the same structure will be used to plot the network.
    scale : int, optional (default: 1)
        Scaling parameter for the network. A larger number will linearily increase the network.
    figsize : tuple, optional (default: (15,8))
        Figure size.
    verbose : int [0-5], optional (default: 3)
        Print messages.
        0: (default)
        1: ERROR
        2: WARN
        3: INFO
        4: DEBUG


    Returns
    -------
    dict.

    """
    out=dict()
    G = nx.DiGraph()  # Directed graph
    layout='fruchterman_reingold'

    # Extract model if in dict
    if 'dict' in str(type(model)):
        model = model.get('model', None)

    # Bayesian model
    if 'BayesianModel' in str(type(model)) or 'pgmpy' in str(type(model)):
        if verbose>=3: print('[BNLEARN][plot] Making plot based on BayesianModel')
        # positions for all nodes
        pos = network.graphlayout(model, pos=pos, scale=scale, layout=layout)
        # Add directed edge with weigth
        # edges=model.edges()
        edges=[*model.edges()]
        for i in range(len(edges)):
            G.add_edge(edges[i][0], edges[i][1], weight=1, color='k')
    elif 'networkx' in str(type(model)):
        if verbose>=3: print('[BNLEARN][plot] Making plot based on networkx model')
        G=model
        pos = network.graphlayout(G, pos=pos, scale=scale, layout=layout)
    else:
        if verbose>=3: print('[BNLEARN][plot] Making plot based on adjacency matrix')
        G = network.adjmat2graph(model)
        # Convert adjmat to source target
#        df_edges=model.stack().reset_index()
#        df_edges.columns=['source', 'target', 'weight']
#        df_edges['weight']=df_edges['weight'].astype(float)
#
#        # Add directed edge with weigth
#        for i in range(df_edges.shape[0]):
#            if df_edges['weight'].iloc[i]!=0:
#                color='k' if df_edges['weight'].iloc[i]>0 else 'r'
#                G.add_edge(df_edges['source'].iloc[i], df_edges['target'].iloc[i], weight=np.abs(df_edges['weight'].iloc[i]), color=color)
        # Get positions
        pos = network.graphlayout(G, pos=pos, scale=scale, layout=layout)

    # Bootup figure
    plt.figure(figsize=figsize)
    # nodes
    nx.draw_networkx_nodes(G, pos, node_size=500, with_labels=True, alpha=0.85)
    # edges
    colors = [G[u][v].get('color','k') for u,v in G.edges()]
    weights = [G[u][v].get('weight',1) for u,v in G.edges()]
    nx.draw_networkx_edges(G, pos, arrowstyle='->', edge_color=colors, width=weights)
    # Labels
    nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')
    # Get labels of weights
    # labels = nx.get_edge_attributes(G,'weight')
    # Plot weights
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G,'weight'))
    # Making figure nice
    ax = plt.gca()
    ax.set_axis_off()
    plt.show()

    # Store
    out['pos']=pos
    out['G']=G
    return(out)


# %% Example data
def import_example():
    """Load sprinkler example.

    Returns
    -------
    df : pd.DataFrame
        Dataframe.

    """
    curpath = os.path.dirname(os.path.abspath(__file__))
    PATH_TO_DATA_1 = os.path.join(curpath,'data','sprinkler_data.zip')
    if os.path.isfile(PATH_TO_DATA_1):
        df=pd.read_csv(PATH_TO_DATA_1, sep=',')
        return df
    else:
        print('[KM] Oops! Example data not found! Try to get it at: www.github.com/erdogant/bnlearn/')
        return None

# %% Convert Adjmat to graph (G)
# def adjmat2graph(adjmat):
#     G = nx.DiGraph() # Directed graph
#     # Convert adjmat to source target
#     df_edges=adjmat.stack().reset_index()
#     df_edges.columns=['source', 'target', 'weight']
#     df_edges['weight']=df_edges['weight'].astype(float)

#     # Add directed edge with weigth
#     for i in range(df_edges.shape[0]):
#         if df_edges['weight'].iloc[i]!=0:
#             # Setup color
#             if df_edges['weight'].iloc[i]==1:
#                 color='k'
#             elif df_edges['weight'].iloc[i]>1:
#                 color='r'
#             elif df_edges['weight'].iloc[i]<0:
#                 color='b'
#             else:
#                 color='p'

#             # Create edge in graph
#             G.add_edge(df_edges['source'].iloc[i], df_edges['target'].iloc[i], weight=np.abs(df_edges['weight'].iloc[i]), color=color)
#     # Return
#     return(G)
