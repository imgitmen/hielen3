# coding: utf-8
import pandas as pd
import numpy as np
import laspy
from pathlib import Path
from scipy.spatial import KDTree
from matplotlib.colors import Normalize, Colormap, LinearSegmentedColormap
from matplotlib.cm import ScalarMappable
import getopt
import sys


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

    print ("CHECK: Enter Valorize")
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

    print ("CHECK: Distance calculation done")
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

    print ("CHECK: Weight calculation done")
    return values


def colorize(vals, cmap=["red", "green", "blue"], norm=None):
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

    print ("CHECK: Enter Colorize")

    if norm is None:
        norm = Normalize(vmin=vals.min(), vmax=vals.max(), clip=True)

    if not isinstance(cmap, (Colormap,str)):
        cmap = LinearSegmentedColormap.from_list("mycmap", cmap)

    mapper = ScalarMappable(norm=norm, cmap=cmap)
#    mapper = ScalarMappable(cmap=cmap)

    cols = mapper.to_rgba(vals)

    return cols


def paint(
    valcld,
    basecld=None,
    distance=10,
    group=1,
    degree=0,
    cmap=["red", "green", "blue"],
    norm=None
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

    valcld = pd.DataFrame(valcld)
    valcld.columns = ["x", "y", "z", "v"]
    values=None

    if basecld is not None:
        basecld = pd.DataFrame(basecld)
        basecld.columns = ["x", "y", "z"]
        values = valorize(basecld, valcld, distance=distance, group=group, degree=degree)
        values.name = "v"
    else:
        values = valcld["v"] 

    colors = pd.DataFrame(
        colorize(values, cmap=cmap, norm=norm),
        columns=["r", "g", "b", "a"],
        index=values.index,
    )[['r','g','b']] * 255 
    #65536

    if basecld is not None:
        result = basecld.join(colors, how="left").replace(np.nan, 0.9)
        result = result.join(values, how="left")
    else:
        result = valcld.join(colors,how="left")

    """
    result["r"]=result["r"]*65536
    result["g"]=result["g"]*65536
    result["b"]=result["b"]*65536
    """

    return result[["x", "y", "z", "v", "r", "g", "b"]]

#65536
def makelaz(frame,filetowrite,colormult=1,scale=[0.01,0.01,0.01]):
    hdr = laspy.header.Header(point_format=2)
    frame.columns=['x','y','z','r','g','b']
    outfile = laspy.file.File(filetowrite,mode='w',header=hdr)
    x=frame['x']
    y=frame['y']
    z=frame['z']
    r=frame['r']*colormult
    g=frame['g']*colormult
    b=frame['b']*colormult
    outfile.header.scale=scale
    outfile.x=x.values
    outfile.y=y.values
    outfile.z=z.values
    outfile.Red=r.values
    outfile.Green=g.values
    outfile.Blue=b.values
    outfile.header.offset=outfile.header.min
    outfile.close()



def makemultilaz(csvfile,targetpath=None,sep=" ",basemanage='i',scale=[0.000001,0.000001,0.000001], columns=None,cmap='jet',norm=None):

    """
    o : only
    i : ignore
    a : also
    """

    try:
        targetpath = Path(targetpath)
    except Exception as e:
        targetpath = Path(".")

    #We expect header
    cloud=pd.read_csv(csvfile,sep=sep)

    cloud.columns=list(map(str.lower,cloud.columns))

    fields=[ c for c in cloud.columns if c not in ['x','y','z','r','g','b'] ]

    if basemanage == 'o' and 'r' in cloud.columns:
        fields=['base']

    if basemanage == 'a':
        fields.append('base')

    lazdone={}

    for c in fields:

        if c == 'base':
            theframe=cloud[['x','y','z','r','g','b']]
        else:
            theframe=paint(cloud[['x','y','z',c]],cmap=cmap,norm=norm)[['x','y','z','r','g','b']]

        #colors='jet'

        lazpath=str(targetpath / f'{c}.laz')

        makelaz(theframe, lazpath, scale=scale)

        lazdone[c]=lazpath


    return lazdone

    """

r=parse_colormap(make_colormap([[-100, "#ee55ee"], [ -66.6 ,"#0000ff"] , [-33.3, "#00ffff" ],[0,"#00FF00"] ,[ 33.3, "#ffff00"], [ 66.6,"#ffa500" ], [ 100, "#FF0000" ]]))

r={
        'cmap':ListedColormap(["#ee55ee", "#0000ff","#00ffff","#00FF00","#ffff00","#ffa500","#FF0000"],'Custom_map'),
        'norm':Normalize(vmin=-50,vmax=50)
        }

result=cloudpainter_new.paint(spostamento,**r)
cloudpainter_new.makelaz(result[['x','y','z','r','g','b']],'spostamento.laz',colormult=255, scale=[0.000001,0.000001,0.000001])

"""


"""
import open3d as o3d
def openpcl(res):
    #QUI USO open3d perchè è molto comodo
    pcl = o3d.geometry.PointCloud()
    pcl.points = o3d.utility.Vector3dVector(res[["x", "y", "z"]].values)
    pcl.colors = o3d.utility.Vector3dVector(res[["r", "g", "b"]].values)
    o3d.visualization.draw_geometries([pcl])
"""

def usage():
    helptext = r"""usage: cloudainter.py [option] path/to/radar/result.csv
parmeters:
path/to/radar/result.csv     : path for csv based radar cloud in the format
                               X,Y,Z,V,...
options:
-b path    --basecloud=path  : path for csv based reference cloud in the
                               format X,Y,Z,...
-g number  --group=number    : max number of neighbours to interpolate
-d number  --distance=number : nearest neighbour max radius
-D number  --degree=number   : neighbour contribute attenuation degree
                               along distance
-c csv     --colors=csv      : colormap as comma separated colors names
-o path    --outfile=path    : output file name. Ignored when --output=view
-O type    --output=type     : output types: [laz|csv|view]. Default laz
-v number  --vmin=number     : min value for the colormap range
-V number  --vmax=numner     : max value for the colormap range"""

    print (helptext)


if __name__ == "__main__":

    #DEFAULTS
    datacloud=None
    basecloud=None
    group=1
    distance=5
    degree=0
    colors=['violet','blue','cyan','green','yellow','orange','red']
    outfile=None
    output='las'
    vmin=-500
    vmax=500

    try:
        opts, args = getopt.getopt(
                sys.argv[1:], 
                "b:g:d:D:c:o:O:v:V:",
                [
                    "basecloud=",
                    "group=",
                    "distance=",
                    "degree=",
                    "colors=",
                    "outfile=",
                    "output=",
                    "vmin=",
                    "vmax="
                ])


        for o,a in opts:
            if o in ("-b", "--basecloud"):
                basecloud=a
            elif o in ("-g", "--group"):
                group=a
            elif o in ("-d", "--distance"):
                distance=a
            elif o in ("-D", "--degree"):
                degree=a
            elif o in ("-c", "--colors"):
                colors=a.split(",")
            elif o in ("-o", "--outfile"):
                outfile=a
            elif o in ("-O", "--output"):
                output=a
            elif o in ("-v", "--vmin"):
                vmin=a
            elif o in ("-V", "--vmax"):
                vmax=a
            else:
                assert False, "unhandled option"

        try:
            infile=args[0]
        except Exception:
            raise Exception(f"No file")

        try:
            norm = norm = Normalize(vmin=vmin, vmax=vmax, clip=True)
        except Exception as e:
            norm= None

        datacloud = pd.read_csv(infile)
        datacloud = datacloud[datacloud.columns[0:4]]
        datacloud.columns = ["X","Y","Z","V"]

        if basecloud is not None: 
            basecloud = pd.read_csv(basecloud)
            basecloud = basecloud[basecloud.columns[0:3]]
            basecloud.columns = ["X","Y","Z"]
    
        result = paint(
                valcld=datacloud,
                basecld=basecloud,
                distance=distance,
                degree=degree,
                group=group,
                cmap=colors,
                norm=norm
                )

        if outfile is None:
            outfile = '.'.join([infile,output])

        if output == 'las':
            makelaz(result[["x","y","z","r","g","b"]],outfile)
        elif output == 'csv':
            result.to_csv(outfile,index=False)
#        elif output == 'view':
#            openpcl(result)
        else:
            raise Exception(f'unkwnown output type:{output}')

    except Exception as err:
        # print help information and exit:
        print(err) 
        usage()
        sys.exit(2)


