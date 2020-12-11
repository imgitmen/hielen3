# coding: utf-8
import pandas as pd
import numpy as np
from scipy.spatial import KDTree
from matplotlib.colors import Normalize, Colormap, LinearSegmentedColormap
from matplotlib.cm import ScalarMappable

import open3d as o3d


def valorize(basecld, valcld, distance=10, group=1, degree=0):

    """
    Assigns values to input base cloud points, overlapping the input
    values cloud and calculating, for each point in base cloud, the
    [distance based, weighted] mean of the values of N nearest
    neighbours, taken from the input values cloud.

    returns:
    pandas.Series containing calculated values for all the points in the
    base cloud which has at least one neighbour within the fixed distance

    params:
    basecld -  pandas.DataFrame or numpy.ndarray with shape (n,3),
               representing the coordinates of the points of the base
               cloud. ['x','y','z']

    valcld -   pandas.DataFrame or numpy.ndarray with shape (n,4),
               representing the coordinates of the points of the value
               cloud and the value of each of them. ['x','y','z','v']

    distance - maximum search range for neighbours

    group -    maximum number of neighbours to search for

    degree -   degree of contribution loss over the distance for each
               neighbour value. Each value of the neighbours is weighted
               as:

                    1/d**degree

               where d is the distance between the neighbour and the
               base cloud point. Degree 0 implies the arithmetic mean of
               all the neighbour values found, regardless the relative
               distance.

               i.e:
                   N1----------P----N2

               Given two neighbours, N1 and N2, for a fixed point P

               where:

                   d(N1)=10; v(N1)=-15
                   d(N2)=4; v(N2)=3

                   v(P) = (-15/10**d+3/4**d)/(1/10**d+1/4**d)

               being d the degree, we have:

                   d=0 : v(P) = -6    <-- arimetic mean
                   d=1 : v(P) = -2.14
                   d=2 : v(P) = 0.51
                   d=3 : v(P) = 1.91
                   d=4 : v(P) = 2.55
                   d=5 : v(P) = 2.81
                   ..
                   d=9 : v(P) = 2.99
                   ..
                   d(x): v(P) = 3  <-- convergence to the closest's value

    Note: with group=1 and degree=0, each base cloud point assumes the
          exact value of the unique closest neighbour, if it exists.

    """
    basecld = pd.DataFrame(basecld)
    basecld.columns = ["x", "y", "z"]
    valcld = pd.DataFrame(valcld)
    valcld.columns = ["x", "y", "z", "v"]

    ## Calculating the Series of distance (dist) and value clouds relative
    ## ids (idsv). the position of each cell in the arrays reflects the cells
    ## in the base cloud.
    k = KDTree(valcld[["x", "y", "z"]].values)
    dist, idsv = k.query(basecld.values, group, distance_upper_bound=distance)
    dist = pd.DataFrame(dist).stack()
    dist.name = "dist"
    idsv = pd.DataFrame(idsv).stack()
    idsv.name = "idsv"

    ## Here we construct the DataFrame contains relation beetween each point
    ## in base cloud (base cloud index) and his neighbous (value cloud ids,
    ## distance and neighbour group progressive). Then we clean the infinite
    ## distances (points with no neighbours)
    values = dist.to_frame().join(idsv)
    values = values[values["dist"] != np.inf]

    # Indexind on 'idsv', allows to join with the value cloud and add the 'v'
    # info
    values = values.reset_index().set_index("idsv").sort_index()
    values = values.join(valcld["v"], how="left")
    values.columns = ["cldid", "instance", "dist", "displ"]

    ## Indexing on 'cldid' and 'instance', allow to make DataFrame comparable
    ## with base cloud
    values = values.set_index(["cldid", "instance"]).sort_index()

    ## Here we calculte the [distance based, weighted] mean
    values["weight"] = 1 / np.power(values["dist"], degree)
    values["contrib"] = values["displ"] * values["weight"]
    values = values.groupby("cldid").apply(
        lambda x: sum(x["contrib"]) / sum(x["weight"])
    )

    return values


def colorize(vals, cmap=["red", "green", "blue"], vmin=None, vmax=None):
    """
    Maps each value in the input array with the appropriate
    RGBA color. See matplotlib.colors.Colormap

    returns:

    ndarray with shape (n,4) containing the color tuples ['r','g','b','a']
    color channels values are normalized in range (0,1)

    params:
    vals - array of values.
    cmap - See matplotlib.colors.Colormap object or colour list.
           default ['red','green','blue'].
    vmax - max limit value for colormap. If None is passed, vals.max().
           will be assumed, otherwise vals exceding this parameter will
           be clipped
    vmin - min limit value for colormap. If None is passed, vals.min()
           will be assumed, otherwise vals under this parameter will
           be clipped

    """

    vmin = vmin or vals.min()
    vmax = vmax or vals.max()

    norm = Normalize(vmin=vmin, vmax=vmax, clip=True)

    if not isinstance(cmap, Colormap):
        cmap = LinearSegmentedColormap.from_list("mycmap", cmap)

    mapper = ScalarMappable(norm=norm, cmap=cmap)

    cols = mapper.to_rgba(vals)

    return cols


def paint(
    basecld,
    valcld,
    distance=10,
    group=1,
    degree=0,
    cmap=["red", "green", "blue"],
    vmin=None,
    vmax=None,
):
    """
    Assigns a color to each point of a base cloud, merging the information
    of a second valorized cloud overlapping the first one.
    See cloudpainter.valorize and cloudpainter.colorize for futher informations

    result:

    pandas.DataFrame containing ['x','y','z','v','r','g','b'] tuples for
    each point in the base cloud. Points with no neighbours will be
    assigned with [0.9,0.9,0.9] for ['r','g','b'] and np.nan for ['v']

    params:
    basecld -  pandas.DataFrame or numpy.ndarray with shape (n,3),
               representing the coordinates of the points of the base
               cloud. ['x','y','z']

    valcld -   pandas.DataFrame or numpy.ndarray with shape (n,4),
               representing the coordinates of the points of the value
               cloud and the value of each of them. ['x','y','z','v']

    distance - maximum search range for neighbours

    group -    maximum number of neighbours to search for

    degree -   degree of contribution loss over the distance for each
               neighbour value. Each value of the neighbours is weighted
               as:

                    1/d**degree

               where d is the distance between the neighbour and the
               base cloud point. Degree 0 implies the arithmetic mean of
               all the neighbour values found, regardless the relative
               distance.

    cmap -     matplotlib.colors.Colormap object or colour list.
               default ['red','green','blue'].
    vmax -     max limit value for colormap. If None is passed, vals.max().
               will be assumed, otherwise vals exceding this parameter will
               be clipped
    vmin -     min limit value for colormap. If None is passed, vals.min()
               will be assumed, otherwise vals under this parameter will
               be clipped

    """

    basecld = pd.DataFrame(basecld)
    basecld.columns = ["x", "y", "z"]
    valcld = pd.DataFrame(valcld)
    valcld.columns = ["x", "y", "z", "v"]

    values = valorize(basecld, valcld, distance=distance, group=group, degree=degree)
    values.name = "v"

    colors = pd.DataFrame(
        colorize(values, cmap=cmap, vmin=vmin, vmax=vmax),
        columns=["r", "g", "b", "a"],
        index=values.index,
    )[["r", "g", "b"]]

    result = basecld.join(colors, how="left").replace(np.nan, 0.9)
    result = result.join(values, how="left")

    return result[["x", "y", "z", "v", "r", "g", "b"]]


def main():

    cld = pd.read_csv("./cloud.orig.csv", header=None, sep=" ")
    rea = pd.read_csv("./nuvola_spost_utm.csv", sep=";", decimal=",")[
        ["X_UTM", "Y_UTM", "Height", "Spostament"]
    ]

    # ESEMPIO 1
    # Smooth --- Il peso dei vicini è alto, la distanza di influenza è alta e i limiti di colore sono
    # impostati tra min e max dei valori in ingresso
    #
    res = paint(
        cld,
        rea,
        distance=10,
        group=10,
        degree=2,
        cmap=["red", "green", "blue"],
        vmin=None,
        vmax=None,
    )

    # ESEMPIO 2
    # N-N secco --- Un solo vicino che assegna il colore. I limiti di colore più stretti del range dei
    # valori in ingresso
    #
    ### res=paint(cld,rea,distance=10,group=1,degree=0,cmap=['red','orange','yellow'],vmin=-2.5,vmax=2.5)

    # QUI USO open3d perchè è molto comodo
    pcl = o3d.geometry.PointCloud()
    pcl.points = o3d.utility.Vector3dVector(res[["x", "y", "z"]].values)
    pcl.colors = o3d.utility.Vector3dVector(res[["r", "g", "b"]].values)
    o3d.visualization.draw_geometries([pcl])


if __name__ == "__main__":
    main()
