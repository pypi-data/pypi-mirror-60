"""
ePSproc basic plotting functions

Some basic functions for 2D/3D plots.

19/11/19        Adding plotting routines for matrix elements & beta values, to supercede existing basic methods.

07/11/19    v1  Molecular plotter for job info.


TODO
----


"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# For Arrow3D class
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

# Package functions
from epsproc.sphPlot import plotTypeSelector
# from epsproc.util import matEleSelector  # Throws error, due to circular import refs?

# Additional plotters
try:
    import seaborn as sns
    import epsproc._sns_matrixMod as snsMatMod  # SNS code with modified clustermap
except ImportError as e:
    if e.msg != "No module named 'seaborn'":
        raise
    print('* Seaborn not found, clustermap plots not available. ')



# Arrow3D class from https://stackoverflow.com/questions/22867620/putting-arrowheads-on-vectors-in-matplotlibs-3d-plot
# Code: https://stackoverflow.com/a/22867877
# Builds on existing 2D arrow class, projects into 3D.
# From StackOverflow user CT Zhu, https://stackoverflow.com/users/2487184/ct-zhu
class Arrow3D(FancyArrowPatch):
    """
    Define Arrow3D plotting class

    Code verbatim from StackOverflow post https://stackoverflow.com/a/22867877
    Thanks to CT Zhu, https://stackoverflow.com/users/2487184/ct-zhu

    """

    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)


# Basic plotting for molecular structure
# TODO: replace with more sophisticated methods!
def molPlot(molInfo):
    """Basic 3D scatter plot from molInfo data."""

    #*** Plot atoms
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(molInfo['atomTable'][:,2], molInfo['atomTable'][:,3], molInfo['atomTable'][:,4], s = 100* molInfo['atomTable'][:,0], c = molInfo['atomTable'][:,0])
    ax.axis('off');

    # Add labels + bonds for small systems (need more logic for larger systems!)
    if molInfo['atomTable'].shape[0] < 4:
        ax.plot(molInfo['atomTable'][:,2], molInfo['atomTable'][:,3], molInfo['atomTable'][:,4])

        lShift = 0.01* np.array([1., 1., 1.])
        for row in molInfo['atomTable']:
            # ax.text(row[2] + lShift[0], row[3] + lShift[1], row[4] + lShift[2], f"Z = {row[0]}") # molInfo['atomTable'][:,0])
            ax.text(row[2] + lShift[0], row[3] + lShift[1], row[4] + lShift[2], f"Z = {row[0].data}") # Version for Xarray input

    else:
        # Generate legend from scatter data, as per https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/scatter_with_legend.html
        legend1 = ax.legend(*scatter.legend_elements(), loc="lower left", title="Z")
        ax.add_artist(legend1)


    #*** Plot axes with direction vecs

    dirs = ('x','y','z')  # Labels
    oV = np.zeros([3,3])   # Generate origin
    xyzV = np.identity(3)  # Generate unit vectors

    # Scale for lines, check axis limits & molecular extent
    # sf = 1
    axLims = np.asarray([ax.get_xlim(), ax.get_ylim(), ax.get_zlim()])
    sfAxis = np.asarray([ax.get_xlim()[1], ax.get_ylim()[1], ax.get_zlim()[1]])  # Get +ve axis limits
    sfMol = 1.8* np.asarray([molInfo['atomTable'][:,2].max(), molInfo['atomTable'][:,3].max(), molInfo['atomTable'][:,4].max()]) # Get max atom position

    # Set sensible limits
    mask = sfMol > 0
    sfPlot = sfMol*mask + (sfAxis/2)*(~mask)

    for n, xyz in enumerate(xyzV):
        sf = sfPlot[n]
    #     ax.plot([oV[n,0], sf*xyz[0]], [oV[n,1], sf*xyz[1]], [oV[n,2], sf*xyz[2]])  # Basic line
    #     ax.quiver(oV[n,0],oV[n,1],oV[n,2],sf*xyz[0],sf*xyz[1],sf*xyz[2], arrow_length_ratio = 0.05, lw=2)  # Use quiver for arrows - not very pleasing as arrow heads suck
        a = Arrow3D([oV[n,0], sf*xyz[0]], [oV[n,1], sf*xyz[1]], [oV[n,2], sf*xyz[2]], mutation_scale=10,
                    lw=4, arrowstyle="-|>", color="r", alpha=0.5)  # With Arrow3D, defined above
        ax.add_artist(a)
        ax.text(sf*xyz[0], sf*xyz[1], sf*xyz[2], dirs[n])


    # Add (y,z) plane as a surface plot
    yy, zz = np.meshgrid(range(-1, 2), range(-1, 2))
    xx = np.zeros([3,3])
    ax.plot_surface(xx*sfPlot[0],yy*sfPlot[1],zz*sfPlot[2], alpha=0.1)

    # Reset plot limits (otherwise rescales to arrows!)
    ax.set_xlim(axLims[0,:])
    ax.set_ylim(axLims[1,:])
    ax.set_zlim(axLims[2,:])

    # TO CONSIDER:
    # See https://matplotlib.org/mpl_toolkits/mplot3d/api.html#mpl_toolkits.mplot3d.axes3d.Axes3D
    # ax.get_proj()  # Get projection matrix
    # ax.view_init(0,20)  # Set view, (az,el)

    plt.show()



#*** BLM surface plots

def BLMplot(BLM, thres = 1e-2, thresType = 'abs', xDim = 'Eke', backend = 'xr'):
    """
    Plotting routines for BLM values from Xarray.
    Plot line or surface plot, with various backends available.

    Parameters
    ----------
    BLM : Xarray
        Input data for plotting, dims assumed to be as per :py:func:`ePSproc.util.BLMdimList()`

    thres : float, optional, default 1e-2
        Value used for thresholding results, only values > thres will be included in the plot.
        Either abs or relative (%) value, according to thresType setting.

    thresType : str, optional, default = 'abs'
        Set to 'abs' or 'pc' for absolute threshold, or relative value (%age of max value in dataset)

    xDim : str, optional, default = 'Eke'
        Dimension to use for x-axis, also used for thresholding. Default plots (Eke, BLM) surfaces with subplots for (Euler).
        Change to 'Euler' to plot (Euler, BLM) with (Eke) subplots.

    backend : str, optional, default = 'xr'
        Plotter to use. Default is 'xr' for Xarray internal plotting. May be switched according to plot type in future...

    """

    # Check dims, and set facet dim
    dims = BLMdimList()
    dims.remove(xDim)
    cDims = dims.remove('BLM')

    # For %age case
    if thresType is 'pc':
        thres = thres * BLM.max()

    # Threshold results. Set to check along Eke dim, but may want to pass this as an option.
    BLMplot = ep.matEleSelector(BLM, thres=thres, dims = xDim)

    # Set BLM index for plotting.
    # Necessary for Xarray plotter with multi-index categories it seems.
    BLMplot['BLMind'] = ('BLM', np.arange(0, BLMplot.BLM.size))

    #*** Plot
    if backend is 'xr':
        BLMplot.real.squeeze().plot(x=xDim, y='BLMind', col=cDims, size = 5)



#************************* Routines for matrix element plotting

# Function for getting list of unique syms
def symListGen(data):
    symList = []
    [symList.append(list(item)) for item in data.get_index('Sym').to_list()]

    return np.ravel(symList)

def lmPlot(data, pType = 'a', thres = 1e-2, thresType = 'abs', SFflag = True, logFlag = False, eulerGroup = True,
        selDims = None, sumDims = None, plotDims = ('l','m','mu','Cont','Targ','Total','it','Type'),
        xDim = 'Eke', backend = 'sns', cmap = None, figsize = None, verbose = False):
    """
    Plotting routine for ePS matrix elements & BLMs.

    First pass - based on new codes + util functions from sphPlot.py, and matE sorting codes.

    Parameters
    -----------
    data : Xarray, data to plot.
        Should work for any Xarray, but optimised for dataTypes:
        - matE, matrix elements
        - BLM paramters
        - ADMs

    pType : char, optional, default 'a' (abs values)
        Set (data) type to plot. See :py:func:`plotTypeSelector`.

    thres : float, optional, default 1e-2
        Value used for thresholding results, only values > thres will be included in the plot.
        Either abs or relative (%) value, according to thresType setting.

    thresType : str, optional, default = 'abs'
        Set to 'abs' or 'pc' for absolute threshold, or relative value (%age of max value in dataset)

    SFflag : bool, optional, default = True
        For dataType = matE: Multiply by E-dependent scale factor.
        For dataType = BLM: Multiply by cross-section (XS) (I.e. if False, normalised BLMs are plotted, with B00 = 1)

    logFlag : bool, optional, default = False
        Plot values on log10 scale.

    eulerGroup : bool, optional, default = True
        Group Euler angles by set and use labels (currenly a bit flakey...)

    selDims : dict, optional, default = {'Type':'L'}
        Dimensions to select from input Xarray.

    sumDims : tuple, optional, default = None
        Dimensions to sum over from the input Xarray.

    plotDims : tuple, optional, default = ('l','m','mu','Cont','Targ','Total','it','Type')
        Dimensions to stack for plotting, also controls order of stacking (hence sorting and plotting).
        TO DO: auto generation for different dataType, also based on selDims and sumDims selections.

    xDim : str, optional, default = 'Eke'
        Dimension to use for x-axis, also used for thresholding. Default plots (Eke, LM) surfaces.

    backend : str, optional, default = 'sns'
        Plotter to use. Default is 'sns' for Seaborn clustermap plot.
        Set to 'xr' for Xarray internal plotting (not all passed args will be used in this case). May be switched according to plot type in future...

    cmap : str, optional, default = None
        Cmap option to pass to sns clustermap plot.

    figsize : tuple, optional, default None
        Tuple for Seaborn figure size (ratio), e.g. figsize = (15,5).
        Useful for setting a long axis explicitly in cases with large dimensional disparity.
        Default results in a square (ish) aspect.

    verbose : bool, optional, default False
        Print debug info.

    Returns
    -------
    daPlot : Xarray
        Data subset as plotted.

    legendList : list
        Labels & colour maps

    g : figure object


    Notes
    -----
    * Data is automagically sorted by dims in order set in plotDim.
    * For clustermap use local version - code from Seaborn, version from PR1393 with Cluster plot fixes.
        * https://github.com/mwaskom/seaborn/pull/1393
        * https://github.com/mwaskom/seaborn/blob/fb1f87e800e69ba2e9309f922f9dac470e3a6c78/seaborn/matrix.py
    * Currently only set for single colourmap choice, should set as dict.
    * Clustermap methods from:
        * https://stackoverflow.com/questions/27988846/how-to-express-classes-on-the-axis-of-a-heatmap-in-seaborn
        * https://seaborn.pydata.org/examples/structured_heatmap.html
    * Seaborn global settings currently included here:
        * sns.set(rc={'figure.dpi':(120)})
        * sns.set_context("paper")
        * These are reset at end of routine, apart from dpi.

    To do
    -----
    - Improved dim handling, maybe use :py:func:`epsproc.util.matEdimList()` (and related functions) to avoid hard-coding multiple cases here.
    - Improved handling of sets of polarization geometries (angles).

    Examples
    --------
    (See https://github.com/phockett/ePSproc/blob/master/epsproc/tests/ePSproc_demo_matE_plotting_Nov2019.ipynb)

    """
    # Local/deferred import to avoid circular import issues at module level.
    # TO DO: Should fix with better __init__!
    from epsproc.util import matEleSelector, matEdimList, BLMdimList

    # Set Seaborn style
    # TO DO: should pass args here or set globally.
    # sns.set()
    sns.set_context("paper")  # "paper", "talk", "poster", sets relative scale of elements
                            # https://seaborn.pydata.org/tutorial/aesthetics.html
    # sns.set(rc={'figure.figsize':(11.7,8.27)})  # Set figure size explicitly (inch)
                            # https://stackoverflow.com/questions/31594549/how-do-i-change-the-figure-size-for-a-seaborn-plot
                            # Wraps Matplotlib rcParams, https://matplotlib.org/tutorials/introductory/customizing.html
    sns.set(rc={'figure.dpi':(120)})

#*** Data prep
    # Make explicit copy of data
    daPlot = data.copy()
    daPlot.attrs = data.attrs
#     daPlot = data

    # Set filename if missing
    if 'file' not in daPlot.attrs:
        daPlot.attrs['file'] = '(No filename)'

    # Use SF (scale factor)
    # Write to data.values to make sure attribs are maintained.
    if SFflag and (daPlot.attrs['dataType'] is 'matE'):
        daPlot.values = daPlot * daPlot.SF

    if SFflag and (daPlot.attrs['dataType'] is 'BLM'):
        daPlot.values = daPlot * daPlot.XS

    # For %age case
    if thresType is 'pc':
        thres = thres * np.abs(daPlot.max()).values  # Take abs here to ensure thres remains real (float)
                                              # However, does work without this for xr.where() - supports complex comparison.

    # Get full dim list
    if daPlot.attrs['dataType'] is 'matE':
        dimMap = matEdimList(sType = 'sDict')
    else:
        dimMap = BLMdimList(sType = 'sDict')

    # Eulers >>> Labels
    if eulerGroup and ('Euler' in daPlot.dims):
        if 'Labels' in daPlot.drop('Euler').dims:
            daPlot = daPlot.drop('Euler').swap_dims({'Euler':'Labels'})   # Set Euler dim to labels
        else:
            pass
            # TODO: add labels here if missing. See setPolGeoms()
            # Set labels if missing, alphabetic or numeric
            # if eulerAngs.shape[0] < 27:
            #     labels = list(string.ascii_uppercase[0:eulerAngs.shape[0]])
            # else:
            #     labels = np.arange(1,eulerAngs.shape[0]+1)



# Restack code from mfblm()
    # # Unstack & sub-select data array
    # daUnStack = da.unstack()
    # daUnStack = matEleSelector(daUnStack, thres = thres, inds = selDims, sq = True)
    #
    # # Check dims vs. inds selection and/or key dims in output
    # for indTest in sumDims:
    #     # if (indTest in inds) or (indTest not in unstackTest.dims):
    #     if indTest not in daUnStack.dims:
    #         daUnStack = daUnStack.expand_dims(indTest)
    #
    # # Restack array along sumInds dimensions, drop NaNs and squeeze.
    # daSumDim = daUnStack.stack(SumDim = sumDims).dropna('SumDim').squeeze()

    # Sum & threshold
    if sumDims is not None:
        daPlot = daPlot.sum(sumDims).squeeze()
        daPlot.attrs = data.attrs  # Reset attribs

    # Threshold on abs() value before setting type, otherwise all terms will appear for some cases (e.g. phase plot)
    daPlot = matEleSelector(daPlot, thres=thres, inds = selDims, dims = xDim) # , sq = True)  # Squeeze may cause issues here if a singleton dim is used for xDim.
    daPlot = plotTypeSelector(daPlot, pType = pType, axisUW = xDim)

    # daPlot = ep.util.matEleSelector(daPlot, thres=thres, inds = selDims, dims = 'Eke', sq = True)

    if logFlag:
        daPlot.values = daPlot.pipe(np.log10)

#*** Plotting routines
    # Rough code for xr plotter.
    if backend is 'xr':
        # Set index for plotting
        daPlot['LMind'] = ('LM',np.arange(0, daPlot.LM.size))

        # Plot abs values, with faceting on symmetry (all mu)
        # TODO: faceting with passed or smart dims.
        daPlot.plot(x='Eke', y='LMind', col='Sym', row='Type', robust = True)


    if backend is 'sns':

        print(f"Plotting data {daPlot.attrs['file']}, pType={pType}, thres={thres}, with Seaborn")

        # *** Dims & cmaps
        # Get sym list if applicable, this is used for unique colour-mapping over dims and legends.
        if 'Sym' in daPlot.dims:
            symList = symListGen(daPlot)
            symFlag = True
            palSym = sns.color_palette("hls", np.unique(symList).size)  # Generate unified cmap
            lutSym = dict(zip(map(str, np.unique(symList)), palSym))
        else:
            symFlag = False

        # Set unified cmap for (m,mu)
        # Switch for matE or BLM data type.
#         if ('m' in daPlot.dims) and ('mu' in daPlot.dims):
        if 'LM' in daPlot.dims:
            mList = np.unique(daPlot.LM.m)
        if 'BLM' in daPlot.dims:
            mList = np.unique(daPlot.BLM.m)
        if 'ADM' in daPlot.dims:
            mList = np.unique([daPlot.ADM.Q, daPlot.ADM.S])
        mColours = mList.size

        if mColours < 3:  # Minimal value to ensure mu mapped - may be better to generate without ref here?
            mColours = 3

#         palM = sns.diverging_palette(220, 20, n=mColours) # sns.color_palette("hls", mList.size)
        palM = sns.color_palette("coolwarm", mColours)
        lutM = dict(zip(map(str, mList), palM))


        # Convert to Pandas 2D array, stacked along plotDims - these will be used for colour bar.
        # TO DO: fix hard-coded axis number for dropna()

        # Check plotDims exist, otherwise may throw errors with defaults
        plotDimsRed = []
        # for dim in daPlot.unstack().dims:
        #     if dim in plotDims:
        #         plotDimsRed.append(dim)
        for dim in plotDims:
            if dim in daPlot.unstack().dims:
                plotDimsRed.append(dim)

        daPlotpd = daPlot.unstack().stack(plotDim = plotDimsRed).to_pandas().dropna(axis = 1).T

        # Set multi-index indicies & colour mapping
        cList = []
        legendList = []
        for dim in daPlotpd.index.names:
            Labels = daPlotpd.index.get_level_values(dim) #.astype('str')

            if verbose:
                print(dim)
                print(Labels.unique().size)

            # For (l,m,mu) set colour scales as linear (l), and diverging (m,mu)
            # May want to modify (m,mu) mappings to be shared?
            if dim in ['l','K']:
                pal = sns.light_palette("green", n_colors=Labels.unique().size)
                lut = dict(zip(map(str, Labels.unique()), pal))
                cList.append(pd.Series(Labels.astype('str'), index=daPlotpd.index).map(lut))  # Mapping colours to rows
                legendList.append((Labels.unique(), lut))

            elif dim in ['m', 'mu', 'Q', 'S']:
#                 pal = sns.diverging_palette(220, 20, n=Labels.unique().size)
#                 lut = dict(zip(map(str, Labels.unique().sort_values()), pal))  # Note .sort_values() required here.
                pal = palM
                lut = lutM
                cList.append(pd.Series(Labels.astype('str'), index=daPlotpd.index).map(lut))  # Mapping colours to rows
                legendList.append((Labels.unique().sort_values(), lut))

            # If mapping symmetries, use flattened list set above for colour mapping
            # This will keep things consistent over all sym sub-labels
            # NOTE - symFlag setting allows for case when dimMap['Sym'] is missing (will throw an error otherwise)
            elif symFlag and (dim in dimMap['Sym']):
#                 pal = sns.color_palette("hls", np.unique(symList).size)
#                 lut = dict(zip(map(str, np.unique(symList)), pal))
                pal = palSym
                lut = lutSym
                cList.append(pd.Series(Labels.astype('str'), index=daPlotpd.index).map(lut))  # Mapping colours to rows
                legendList.append((Labels.unique(), lut))

            # For other dims, set to categorical mapping.
            # Should check for shared dims here, e.g. Syms, for mapping...?
            else:
#                 pass
#                 print(dim)
#                 print(Labels.unique().size)
#                 pal = sns.color_palette("hls", Labels.unique().size)
                pal = sns.color_palette("dark", Labels.unique().size)
#                 pal = sns.light_palette("blue", n_colors=Labels.unique().size)
                lut = dict(zip(map(str, Labels.unique()), pal))
                cList.append(pd.Series(Labels.astype('str'), index=daPlotpd.index).map(lut))  # Mapping colours to rows
                legendList.append((Labels.unique(), lut))

            # For legend, keep also Labels.unique, lut, pairs
#             legendList.append((Labels.unique(), lut, dim))  # Include dim... redundant if Labels is pd.index with name
#             legendList.append((Labels.unique(), lut))


        # Stack to dataframe
        colors = pd.DataFrame(cList[0])
        for c in cList[1:]:
            colors = colors.join(pd.DataFrame(c))

        # *** Plot with modified clustermap code.
        g = snsMatMod.clustermap(daPlotpd,
                  # cmap="vlag", center = 0,
                  # Turn off the clustering
                  row_cluster=False, col_cluster=False,
                  # Add colored class labels
                  row_colors=colors, col_colors=None, # )  # ,
                  # Make the plot look better when many rows/cols
                  linewidths=0, xticklabels=True, yticklabels=False,
                  # Some other additional, optional, args...
                  figsize = figsize, cmap = cmap)


        # Add keys for each label - loop over all sets of variables assigned previously as (labels, lut) pairs and set as (invisible) bar plots
        # Using this method it's only possible to set two sets of legends, split these based on n here.
        # Method from https://stackoverflow.com/questions/27988846/how-to-express-classes-on-the-axis-of-a-heatmap-in-seaborn
        # TO DO: For further control over legend layout may need to add dummy items: https://stackoverflow.com/questions/34212241/control-the-number-of-rows-within-a-legend
        for n, item in enumerate(legendList):
            # To avoid issues with long floats, round to 3dp
            # TODO: fix this, currently fails for Euler angles case?
            # if item[0].dtype == np.float:
            #     item[0] = np.round(item[0],3)

            for label in item[0].astype('str'):
#                 label = string(label)
#                 if n%2:
                if item[0].name in ['l','m','K','Q']:
                    g.ax_col_dendrogram.bar(0, 0, color=item[1][label],label=label, linewidth=0)
                elif item[0].name in ['mu','S']:  # Skip to avoid repetition, assuming m or Q already plotted on same colour scale.
                    pass
#                 elif symFlag and (item[0].name is 'Cont'):
#                     g.ax_row_dendrogram.bar(0, 0, color=item[1][label],label=label, linewidth=0)
                elif symFlag and (item[0].name in dimMap['Sym']):  # Skip symmetries
                    pass
                else:
                    g.ax_row_dendrogram.bar(0, 0, color=item[1][label],label=label, linewidth=0)

        # Add symmetry labels separately from master list to avoid repetition
        if symFlag:
            for label in np.unique(symList):
                g.ax_row_dendrogram.bar(0, 0, color=lutSym[label],label=label, linewidth=0)

#             g.ax_col_dendrogram.legend(title=n, loc="center") #, ncol=n+1) # , bbox_to_anchor=(0.47, 0.8), bbox_transform=plt.gcf().transFigure)

        # Add legends for the bar plots
        ncol = 2  #np.unique(daPlot.LM.l).size
        if 'ADM' in daPlot.dims:
            QNlabels = 'K,(Q,S)'
        else:
            QNlabels = 'l,(m,mu)'

        g.ax_col_dendrogram.legend(title=QNlabels, loc="center", ncol = ncol, bbox_to_anchor=(0.1, 0.6), bbox_transform=plt.gcf().transFigure)
        g.ax_row_dendrogram.legend(title='Categories', loc="center", ncol = 2, bbox_to_anchor=(0.1, 0.4), bbox_transform=plt.gcf().transFigure)

        # Additional anootations etc.
        # Plot titles: https://stackoverflow.com/questions/49254337/how-do-i-add-a-title-to-a-seaborn-clustermap
        # g.fig.suptitle(f"{daPlot.attrs['file']}, pType={pType}, thres={thres}")  # Full figure title
        g.ax_heatmap.set_title(f"{daPlot.attrs['file']}, plot type = {daPlot.attrs['pTypeDetails']['Type']}, threshold = {np.round(thres, 2)}, inc. cross-section {SFflag}, log10 {logFlag}")  # Title heatmap subplot

        # sns.reset_orig()  # Reset gloabl plot params - leaves rc settings, also triggers Matplotlib errors
        sns.reset_defaults()

        return daPlot, daPlotpd, legendList, g

    return daPlot
