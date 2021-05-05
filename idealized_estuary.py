import os
import sys
import xarray as xr
sys.path.append(os.environ['HOME']+"/work/mpasview/")
from mpasview import *

def idealized_estuary_along_channel(ds, varname, time=None, nxc=4):
    ncells = ds.dataset.dims['nCells']
    da = ds.load_variable_profile(varname).isel(nCells=slice(0,ncells,nxc))
    if 'Time' in da.dims:
        if time:
            da = da.sel(Time=np.datetime64(time), method='nearest')
        else:
            da = da.isel(Time=-1)
    if 'nVertLevels' in da.dims:
        z = da.nVertLevels.values
    elif 'nVertLevelsP1' in da.dims:
        z = da.nVertLevelsP1.values
    y = ds.mesh.ycell[slice(0,ncells,nxc)]
    # y = y.max() - y
    depth = xr.DataArray(
        z,
        dims={'z'},
        coords={'z': z},
        attrs={'units': 'm', 'long_name': 'Depth'}
        )
    dist = xr.DataArray(
        y,
        dims=('y'),
        coords={'y': y},
        attrs={'units': 'm', 'long_name': 'Along channel distance'}
        )
    out = xr.DataArray(
        da.values,
        dims=('z', 'y'),
        coords={'z': depth, 'y': dist},
        attrs={'units': da.attrs['units'], 'long_name': da.attrs['long_name']}
        )
    return out

def plot_along_channel_overview(mpasdata, var, levels, label, time, nxc=4, cmap='viridis'):
    fig, axarr = plt.subplots(2,1, sharex='col', sharey='row')
    fig.set_size_inches([8,3])
    axarr[0].set_position([0.1, 0.78, 0.77, 0.2])
    axarr[1].set_position([0.1, 0.18, 0.77, 0.6])

    da = idealized_estuary_along_channel(mpasdata, var, time=time, nxc=nxc)
    im = da.plot(ax=axarr[1], add_colorbar=False, levels=levels, cmap=cmap)
    if time is not None:
        axarr[1].text(0.05, 0.1, str(time), transform=axarr[1].transAxes)

    da0 = mpasdata.load_variable_map(var, idepth=0, time=time)
    da0.plot(axis=axarr[0], ptype='pcolor', swap_xy=True, colorbar=False, levels=levels, cmap=cmap)
    axarr[0].set_aspect(1)
    

    # colorbar
    cax = plt.axes([0.77, 0.18, 0.15, 0.73])
    cax.set_visible(False)
    cb = plt.colorbar(im, ax=cax, aspect=25, extend='both')
    cb.set_label(label)
    cb.ax.set_xticklabels(cb.ax.get_xticklabels(), rotation=40)
    cb.ax.xaxis.set_ticks_position('top')
    cb.ax.xaxis.set_label_position('top')
    
    da.close()
    del da0
    return fig