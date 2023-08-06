#!pythonw
# -*- coding: ISO-8859-15 -*-
#===============================================================================
# $Id: graphcreation.py 5128 2019-09-16 12:06:08Z jeanluc $
#
# Copyright 2016 Jean-Luc PLOIX
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Utilitaire d'affichage des modeles limites
#===============================================================================
'''
Created on 7 nov. 2014

@author: jeanluc
'''
import os
import networkx as nx
from networkx.classes.function import get_node_attributes

from metaphor.nntoolbox.utils import ReverseConfigString
from metaphor.monal.util.monalbase import importXML
from metaphor.chem_gm.core.GMmodel import smiles2model
from metaphor.chem_gm.core.metamolecule import MetaMolecule

#from metaphor.monal.monalconst import SF_XML


"""Commands which take color arguments can use several formats to specify
the colors.  For the basic builtin colors, you can use a single letter

    - b  : blue
    - g  : green
    - r  : red
    - c  : cyan
    - m  : magenta
    - y  : yellow
    - k  : black
    - w  : white

Gray shades can be given as a string encoding a float in the 0-1
range, e.g.::

    color = '0.75'

For a greater range of colors, you have two options.  You can specify
the color using an html hex string, as in::

      color = '#eeefff'

or you can pass an *R* , *G* , *B* tuple, where each of *R* , *G* , *B*
are in the range [0,1].

Finally, legal html names for colors, like 'red', 'burlywood' and
'chartreuse' are supported.

"""

AtomColor = {
    'C': 'k',
    'N': 'g',
    'O': 'y',
    'F': 'c',         
    'Cl': 'c',         
    'Br': 'c',         
    'I': 'c',         
             }

def createGraph(reseau):
    G = nx.DiGraph(name=reseau.name)
    G.reseau = reseau
#    oldlayer = 0
#    numerostart = 0
    node = reseau.bias
    node.atom = ""
    dico = {}
    dico["neuron"] = node
    dico["pos"] = (0, 0)
    dico["atom"] = ""
    G.add_node(node.nodeid, **dico)
    for node in reseau.nodes:
        if not hasattr(node, "atom"):
            node.atom = ""
        dico = {}
        dico["neuron"] = node
        dico["pos"] = node.getIndexes()
        dico["atom"] = node.atom
        G.add_node(node.nodeid, **dico)

    for key in G.nodes():
        node = G.node[key]['neuron']
        for link in node.links:
            dico = {}
            dico["link"] = link
            if link.isFix():
                dico["label"] = str(link.value)
            else:
                dico["label"] = link.name
            G.add_edge(link.source.nodeid, node.nodeid, **dico)         
    return G

def initpos(G):
    for key in G.nodes_iter():
        if not key:
            G.node[key]['pos'] = 0,0
            continue
        node = G.node[key]['neuron']
        pos = node.getIndexes()
        G.node[key]['pos'] = pos

def balanceLayerGraph(G):
    layerlengths = G.reseau.layerlengthlist()
    layerlengths[0] +=1
    llmax = max(layerlengths)
    deltas = [float(llmax - layerlengths[ind]) / 2 for ind in range(G.reseau.layerCount)]
    if layerlengths[0] > 1:
        deltas[0] = llmax -0.5
    else:
        deltas[0] = llmax - 1.25
    for ind, key in enumerate(G.nodes()):
        oldpos = G.node[key]['pos']
        layer = oldpos[0]
        G.node[key]['pos'] = (oldpos[0], oldpos[1] + deltas[layer])

def getLabelPos(G, delta=(0, 0.10), node_pos=None):
    posl = {}
    labels = {}
    for key in nx.get_node_attributes(G, 'pos'):
        gnode = G.node[key]
        if node_pos:
            pos = node_pos[key]
        else:
            pos = gnode["pos"]
        posl[key] = (pos[0] + delta[0] , pos[1] + delta[1])
        #gnode = G.node[key]
        origin = gnode["neuron"]
        labels[key] = origin.name
    return labels, posl

def networkDraw(source, ax=None, config=None, hidden=0, modelname="",
    connect=None, classif=False, fullH=False, outputname="property", centraux=3, 
    node_pos=None, labelfhift=(0, 0.2), biascolor='w', fixcolor='r', 
    biasparamcolor='#00e00e', balance=True, squeleton=0, withmodel=False):
    if isinstance(source, nx.Graph):
        G = source
    else:
        try:
            G = createGraph(source)
        except:
#    elif isSmiles(source):
            smiles = source
            iso = 0
            grade = 0
            chargelist = []
            if config is None:
                tokens = MetaMolecule(smiles)
                atoms, grade, iso, _, occurs, _, _, chargelist = tokens.analyse()
                for key in occurs:
                    if not key in connect:
                        connect[key] = -1
            compactness = 3
            if squeleton== 1:
                hidden = 0
            elif squeleton == 2:
                hidden = 1
                compactness = 1
            #diststruct, tokens, atomlist, 
            driver = smiles2model( 
                smiles,
                connect=connect,
                atoms=atoms,
                outputindex=10,
                modelname=modelname,
                outputname=outputname,
                config=config,
                hidden=hidden,
                centraux=centraux,
                isomer=iso,
                maxgrade=grade,
                chargelist=chargelist,
                compactness=compactness,
                forcehidden=squeleton,
                fullH=fullH,
                classif=classif)
            try:
                hidden = config.getint("model", "hidden")
            except: pass
            G = createGraph(driver.mainModel)
#     elif isinstance(source, Basenetwork):
#     else:
#         G = createGraph(source)
        
    if balance:
        balanceLayerGraph(G)
    if node_pos is None:
        node_pos = get_node_attributes(G, 'pos')
    dic = {}
    #nl = driver.mainModel.layerCount
    nl = max([val[0] for val in node_pos.values()])
    if hidden:
        for key, value in node_pos.items():
            if value[0] in [0, nl]:
                continue
            test = (nl - value[0]) % 4
            if test in [1, 2]:
                dic[key] = (value[0], value[1] + 0.1)
            else:
                dic[key] = (value[0], value[1] - 0.1)
    else:
        for key, value in node_pos.items():
            if value[0] in [0, nl]:
                continue
            if value[0] % 2:
                dic[key] = (value[0], value[1] + 0.1)
            else:
                dic[key] = (value[0], value[1] - 0.1)
    node_pos.update(dic)
    labels, posl = getLabelPos(G, labelfhift, node_pos)
    #for key in posl.keys():
        
#     Fixlist = [key for key in nx.edges_iter(G) if G[key[0]][key[1]]["link"].isFix()]
    Fixlist = [key for key in nx.edges(G) if G[key[0]][key[1]]["link"].isFix()]
    FixBiaslist = [key for key in Fixlist if not key[0]]
#     Biaslist = [key for key in nx.edges_iter(G) if not key[0] and not key in FixBiaslist]
    Biaslist = [key for key in nx.edges(G) if not key[0] and not key in FixBiaslist]
    BiasParamlist = [key for key in Biaslist if not G[key[0]][key[1]]["label"].startswith("bias")]
    nx.draw(G, ax=ax, pos=node_pos, node_size=200, node_color='0.75')
#    pos=nx.spring_layout(G)
    nx.draw_networkx_nodes(G, node_pos, ax=ax, node_size= 300, nodelist=[0], node_color='#eeefff', node_shape='s')
    for atom in AtomColor:
        AtomList = [key for key in nx.nodes(G) if G.node[key]["neuron"].atom == atom]
        nx.draw_networkx_nodes(G, node_pos, ax=ax, node_size= 200, nodelist=AtomList, 
                               node_color=AtomColor[atom])
    nx.draw_networkx_labels(G, posl, labels, ax=ax)
    
    #if not withbias:
    nx.draw_networkx_edges(G, node_pos, ax=ax, edgelist=Biaslist, edge_color=biascolor)
    nx.draw_networkx_edges(G, node_pos, ax=ax, edgelist=BiasParamlist, edge_color=biasparamcolor)
    nx.draw_networkx_edges(G, node_pos, ax=ax, edgelist=Fixlist, edge_color=fixcolor)
    nx.draw_networkx_edges(G, node_pos, ax=ax, edgelist=FixBiaslist, edge_color="#e000f0")
    #draw_networkx_edges(G, pos, edgelist=None, width=1.0, edge_color='k', style='solid', alpha=None, edge_cmap=None, edge_vmin=None, edge_vmax=None, ax=None, arrows=True, label=None, **kwds)[source]
    
    edge_labels = nx.get_edge_attributes(G, "label")
    nx.draw_networkx_edge_labels(G, node_pos, ax=ax, edge_labels=edge_labels, label_pos=0.250)#, font_size=10, font_color='k', font_family='sans-serif', font_weight='normal', alpha=1.0, bbox=None, ax=None, rotate=True, **kwds)
    if withmodel:
        return G, driver
    return G

def nmlDraw(nmlfile, withmodel=False):
    res = importXML(source=nmlfile)
    return networkDraw(res, withmodel=withmodel)
    
def doDraw(*args, **kwds):
    import matplotlib.pyplot as plt
    if len(args):
        source = args[0]
        if isinstance(source, (list, tuple)):
            source = source[0]
        G = None
        if os.path.exists(source):
            title = os.path.basename(source)
            plt.title(title)
            G = nmlDraw(source)     
        #elif isSmiles(source):
        else:
            try:
                name = kwds.pop('name', '')
                confstr = kwds.pop('configstr', '')
                title = "{}   {}   {}".format(name, source, confstr).strip()
                plt.title(title)
                connect, central, classif, hidden, fullH = ReverseConfigString(confstr)
                if 'hidden' in kwds:
                    hidden = kwds.pop('hidden')
                G, driver = networkDraw(source, connect=connect, modelname=name, 
                    centraux=central, classif=classif, hidden=hidden, 
                    fullH=fullH, withmodel=True)
                savedir = kwds.pop('savedir')
                if savedir is not None:
                    filename = name if name else 'model'
                    filename = "{}.nml".format(name)
                    filepath = os.path.join(savedir, filename)
                    driver.saveModel(filepath)  #, savingformat=SF_XML
            except:
                print("Cannot find{0}".format(source))
        if G:
            plt.show()
    else:
        print("Need a NML file to draw")

def consoleDraw():
    import argparse
    helpstr = """drawmodel.
    
    parameters:
    model                  -> nml file of model or smiles of the molecule
    --HELP                 -> this help
    following parameters are useful only if model is a Smiles
    '-H', '--hidden'       -> hidden neurons. This value has priority over the one derived from configstr parameter?
    '-c', '--configstr'    -> Configuration string
    '-n', '--name'         -> model name 
    """
#    '-am', '--atomicmodel' -> is atomic model (boolean)

    parser = argparse.ArgumentParser(prog='modelDraw')
    parser.add_argument('model', nargs='?', help='model to be drawn')
    parser.add_argument('--HELP', nargs='?', const=1, type=str, help='help to drawing process call')
#    parser.add_argument('-am', '--atomicmodel', nargs='?', type=int, help='atomic model')
    parser.add_argument('-H', '--hidden', nargs='?', type=int, help='hiden neurons')
    parser.add_argument('-c', '--configstr', nargs='?', type=str, help='chaîne de configuration')
    parser.add_argument('-n', '--name', nargs='?', type=str, help='Nom du modèle')
    parser.add_argument('-sd', '--savedir', nargs='?', const="", help='saving repertory')
    
    args = parser.parse_args()
    if hasattr(args, "HELP") and args.HELP:
        print(helpstr)
        return 
    
    if hasattr(args, "model") and args.model:
        #gmconst.ATOMICMODEL &= bool(args.atomicmodel)
        argdir = {}
        for key in ['name', 'hidden', 'configstr', 'savedir']:  #, 'atomicmodel'
            val = getattr(args, key, None)
            if val is not None:
                argdir[key] = val
        doDraw(args.model, **argdir)
        pass
    else:
        print("Need an argument to draw")
    
#-----------------------------
if __name__ == "__main__":

    consoleDraw()
