#!/usr/bin/env python3
"""
A script to easily generate surface means of FESOM output and automatically
interpolate to a regular 0.25x0.25 grid.

Example Usage
-------------

From inside the ``analysis/fesom`` directory ::

    ./ANALYSIS_fesom_sfc_timseries <variable_name>

This is the most simple use case. If you use ``esm-tools``, the script will
automatically be able to detect the mesh directory and output directories.
"""

# Python Standard Library
import argparse
import datetime
import os
import re
import socket
import sys
import textwrap
import warnings
import pandas as pd
import math
from itertools import zip_longest
from numpy.linalg import inv

# Third-Party Packages
import numpy as np
import pyfesom as pf
import xarray as xr

import f90nml

# Optional Imports
try:
    from dask.distributed import Client, progress
    from dask.diagnostics import ProgressBar
    from dask_jobqueue import SLURMCluster

    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False


def get_list_of_relevant_files(odir, variable, naming_convention):
    """
    Gets a list of all the files for variable in the odir

    Parameters:
    -----------
    odir : str
        The directory to look in
    variable : str
        The variable name to match for


    Returns:
    --------
    var_list : list
        A list of filenames with the pattern ``<variable>_fesom_\d+.nc``,
        sorted by modification time.

    Known Improvements:
    -------------------
    This is pretty specific for how output is saved in ``FESOM``.
    """
    r = re.compile(determine_regex_from_naming_convention(naming_convention, variable))
    olist = [odir + "/" + f for f in os.listdir(odir) if r.match(f)]
    olist.sort(key=lambda x: os.path.getmtime(x))
    return olist


def determine_regex_from_naming_convention(naming, variable):
    if naming == "esm_classic":
        return variable + "_fesom_\d+.nc"
    elif naming == "esm_new":
        return ".*_fesom_" + variable + "_\d+.nc"
    elif naming == "xiaoxu":
        return "fesom.\d+.oce.mean.nc"
    elif naming == "monmean":
        return ".*_fesom_" + variable + "_\d+.nc.monmean"
    raise ValueError("Unknown naming convention specified!")


def full_size_of_filelist(flist):
    """ Given a list of files, gets the full size (in bytes) """
    total_size = 0
    for f in flist:
        total_size += os.stat(f).st_size
    return total_size


def sizeof_fmt(num, suffix="B"):
    """ Formats a size in bytes to human readable """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, "Y", suffix)


################################################################################
# Break up the main function into various small tasks to get a better overview:


class MainProgram:
    def __init__(
        self,
        variable,
        data_dir,
        output_file=None,
        output_file_mask=None,
        expid=None,
        naming_convention=None,
        force=False,
        run_on_cluster=False,
        mesh_rotated=False,
        levelwise=False,
        localhost_multiprocessing=False,
        box=None,
        box_nodes=[],
        mask=[],
        save_mask=False,
        rotate_matrix=[],
        ds = None,
        depth = 0,
        grid_file_name = ""
    ):
        self.variable = variable
        self.data_dir = data_dir
        self.box = box
        self.depth = depth

        self.expid = expid or data_dir.split("/")[-4]
        self.output_file = (
            output_file or self.expid + "_fesom_" + self.variable + "_timseries_" + 
                str(self.box[0]) + "_" + str(self.box[1]) + "_" + str(self.box[2]) + "_" + str(self.box[3]) + 
                "_depth_" + str(self.depth) + ".nc"
        )
        self.output_file_mask = (
            output_file_mask or self.expid + "_fesom_" + self.variable + "_mask_" + 
                str(self.box[0]) + "_" + str(self.box[1]) + "_" + str(self.box[2]) + "_" + str(self.box[3]) +
                "_depth_" + str(self.depth) + ".nc"
        )

        self.naming_convention = naming_convention or "esm_classic"
        if DASK_AVAILABLE:
            self.run_on_cluster = run_on_cluster
        else:
            self.run_on_cluster = False
        self.localhost_multiprocessing = localhost_multiprocessing
        self.mesh_rotated = mesh_rotated
        self.levelwise = levelwise
        self.force = force
        self.box_nodes = box_nodes
        self.mask = mask
        self.save_mask = save_mask
        self.rotate_matrix = rotate_matrix
        self.ds = ds
        self.depth = depth
        self.grid_file_name = grid_file_name

    def __call__(self):
        print(80 * "-")
        print("Start of ANALYSIS_fesom_sfc_timseries.py")

        self._early_exit_if_output_exists()
        self._determine_data_to_load()
        
        self._load_mesh_information()
        if self.mesh_rotated:
            self._generate_rotation_matrix()
            self._back_rotate()
        self._get_box_nodes()
        self._get_box_cell_areas()
       
        if len(self.olist) > 10:
            print("Loading data in chunks of 10")
            for self.olist_tmp in self._grouper(self.olist, 10):
                #print("Loading files: ", self.olist)
                full_size = full_size_of_filelist(list(filter(None, self.olist_tmp[:])))
                self.full_size_str = sizeof_fmt(full_size)
                print("Total size = ", self.full_size_str)
                self._load_data()
        else:
            self._load_data()

        # Seperate into two operations to avoid memory errors:
        self.ds_ = self.ds[self.variable].rename({'nodes_3d': 'ncells'}) #.dropna(dim='ncells', how='all')
        self.tmp = self.ds_ * self.box_cell_areas
        self.tmp = self.tmp.sum(dim='ncells')

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.tmp = self.tmp / self.box_cell_areas.sum(dim='ncells')

        self.ds_timseries = self.tmp.to_dataset(name=self.variable)

        if self.run_on_cluster:
            self._prepare_on_cluster()
        else:
            self._prepare_on_localhost()

        print("\nPerforming weighted fldmean over 'nod3d' dimension and selecting uppermost level:")

        if self.run_on_cluster:
            self._compute_on_cluster()
        else:
            self._compute_on_localhost()

        if self.save_mask:
            self._generate_mask()
            self._select_appropriate_level()
            self._prepare_for_interpolation()
            self._interpolate_to_regular_grid()
            self._interpolation_to_dataarray()
        self._save_results()

        if self.run_on_cluster:
            self._cleanup_on_cluster()

        print("\nAll done, goodbye!")
        sys.exit(0)

    def _grouper(self, iterable, n, fillvalue=None):
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    def _early_exit_if_output_exists(self):
        if not self.force:
            if os.path.isfile(self.output_file):
                print("Output file ", self.output_file, "already exists!")
                sys.exit(0)

    def _determine_data_to_load(self):
        self.olist = get_list_of_relevant_files(
            self.data_dir, self.variable, self.naming_convention
        )[:]
        print("\nLoading metadata of " + str(len(self.olist)) + " files...")
        full_size = full_size_of_filelist(self.olist[:])
        self.full_size_str = sizeof_fmt(full_size)
        print("Total size = ", self.full_size_str)

    def _load_data_preprocess(self, fl):
        #print('fl.time: ', fl['time'])
        fl_ = fl.mean(dim='time').assign_coords(time=fl.time[0]).expand_dims('time')
        return fl_

    def _load_data(self):
        print("(Be patient, this may take a while)")
        # Load the data:
        now = datetime.datetime.now()

        # The context manager is used to filter warnings regarding time step
        # information, which appear to be safely ignorable:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            #print("Process files: ", self.olist_tmp)
            if self.ds is None:
                self.ds = xr.open_mfdataset(
                    list(filter(None, self.olist_tmp)), parallel=False, concat_dim="time",
                    preprocess=self._load_data_preprocess #, decode_times=False
                ).sel(nodes_3d=self.box_nodes, depth=self.depth) # , combine="by_coords")
            else:
                ds_tmp = xr.open_mfdataset(
                    list(filter(None, self.olist_tmp)), parallel=False, concat_dim="time",
                    preprocess=self._load_data_preprocess #, decode_times=False
                ).sel(nodes_3d=self.box_nodes, depth=self.depth) # , combine="by_coords")
                self.ds = xr.concat([self.ds, ds_tmp], 'time')
        # Process 5 years at once --> smaller number of years: more I/O, less change of memory error:
        # self.ds = self.ds.chunk({"time": 365*5, })

        print(
            "Loaded all files (",
            self.full_size_str,
            ") in",
            datetime.datetime.now() - now,
        )

        print("Loaded multi-file information:", self.ds)

    if DASK_AVAILABLE:

        def _prepare_on_cluster(self):
            print("\nSpinning up requested supercomputer nodes")

            self.cluster = SLURMCluster(local_directory=".")

            # Use one prepost node for this computation:
            self.cluster.scale(n=1)

            # This might lead to memory failure:
            # self.cluster.adapt(minimum_jobs=1, maximum_jobs=8)

            # You can also scale to memory
            # Request a specific number of nodes needed to handle this much memory:
            # self.cluster.scale(memory=self.full_size_str)

            print("* Connecting client:")
            self.client = Client(self.cluster)

            print("* Client information:")
            print(self.client)

            print("* You may consider opening an SSH tunnel to the following link:")
            print(self.cluster.dashboard_link)

    def _prepare_on_localhost(self):
        print("* Running on localhost: ", socket.gethostname())
        if self.localhost_multiprocessing:
            print("* You may consider opening an SSH tunnel to the following link:")
            self.client = Client()
            print(self.client)

    if DASK_AVAILABLE:

        def _compute_on_cluster(self):

            print("* Cluster information:")
            print(self.cluster)

            # Perform the computation:
            self.ds_top = self.ds_top.persist()
            progress(self.ds_top)  # watch progress
            self.ds_timseries = self.ds_timseries.persist(
                retries=5
            )  # start computation in the background
            progress(self.ds_timseries)  # watch progress
            self.ds_timseries.compute()

    def _compute_on_localhost(self):
        with ProgressBar():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.ds_timseries.compute()

    def _load_mesh_information(self):
        print("\nLoading mesh information:")
        # Load the mesh
        abg = [0, 0, 0] if not self.mesh_rotated else [50, 15, -90]
        self.mesh = pf.load_mesh(ARGS.mesh_dir, usepickle=False, get3d=True, abg=abg) #, usejoblib=True)
        self.grid_file = os.path.join(ARGS.mesh_dir, self.grid_file_name)
        self.nod_file = os.path.join(ARGS.mesh_dir, "nod2d.out")

    def _generate_rotation_matrix(self):
        alphaEuler=50
        betaEuler=15
        gammaEuler=-90
        
        al = np.radians(alphaEuler)
        be = np.radians(betaEuler)
        ga = np.radians(gammaEuler)
       
        rotate_matrix = np.zeros((3,3))
        rotate_matrix[0,0]=np.cos(ga)*np.cos(al)-np.sin(ga)*np.cos(be)*np.sin(al)
        rotate_matrix[0,1]=np.cos(ga)*np.sin(al)+np.sin(ga)*np.cos(be)*np.cos(al)
        rotate_matrix[0,2]=np.sin(ga)*np.sin(be)
        rotate_matrix[1,0]=-np.sin(ga)*np.cos(al)-np.cos(ga)*np.cos(be)*np.sin(al)
        rotate_matrix[1,1]=-np.sin(ga)*np.sin(al)+np.cos(ga)*np.cos(be)*np.cos(al)
        rotate_matrix[1,2]=np.cos(ga)*np.sin(be)
        rotate_matrix[2,0]=np.sin(be)*np.sin(al) 
        rotate_matrix[2,1]=-np.sin(be)*np.cos(al)  
        rotate_matrix[2,2]=np.cos(be)
        
        self.rotate_matrix = rotate_matrix

    def _g2r(self):
        lon1 = np.radians(self.box[0])
        lon2 = np.radians(self.box[1])
        lat1 = np.radians(self.box[2])
        lat2 = np.radians(self.box[3])

        v1_ = np.zeros((3,1))
        v1_[0]=np.cos(lat1)*np.cos(lon1)
        v1_[1]=np.cos(lat1)*np.sin(lon1)
        v1_[2]=np.sin(lat1) 
        vr1 = np.dot(self.rotate_matrix, v1_)

        v2_ = np.zeros((3,1))
        v2_[0]=np.cos(lat2)*np.cos(lon2)
        v2_[1]=np.cos(lat2)*np.sin(lon2)
        v2_[2]=np.sin(lat2) 
        vr2 = np.dot(self.rotate_matrix, v2_)
        
        self.box[0] = np.degrees(math.atan2(vr1[1], vr1[0]))
        self.box[2] = np.degrees(math.asin(vr1[2]))
        self.box[1] = np.degrees(math.atan2(vr2[1], vr2[0]))
        self.box[3] = np.degrees(math.asin(vr2[2]))

    def _r2g(self, lon_r, lat_r):

        A = inv(self.rotate_matrix)

        lon_ = np.radians(lon_r)
        lat_ = np.radians(lat_r)

        v_ = np.zeros((3,1))
        v_[0]=np.cos(lat_)*np.cos(lon_)
        v_[1]=np.cos(lat_)*np.sin(lon_)
        v_[2]=np.sin(lat_) 
        vr = np.dot(A, v_)

        lon_g = np.degrees(math.atan2(vr[1], vr[0]))
        lat_g = np.degrees(math.asin(vr[2]))
        return  lon_g, lat_g

    def _back_rotate(self):
        r2g_v = np.vectorize(self._r2g)

        with open(self.nod_file, 'r') as csvfile:
            nodes = pd.read_csv(csvfile, header=None, sep=r'\s* \s*', skiprows=1, engine='python')
            nodes.drop(nodes.index[0], inplace=True)
            nodes.columns = ['index', 'lon', 'lat', 'mask']
            [lon_tmp, lat_tmp] = r2g_v(np.array(nodes['lon'].values[:], dtype=float).transpose(), 
                                       np.array(nodes['lat'].values[:], dtype=float).transpose())
            nodes['lon'] = lon_tmp
            nodes['lat'] = lat_tmp
            nodes.to_csv('nodes_back_rotated.csv', sep=' ', header=True, index=False)
            self.nod_file = 'nodes_back_rotated.csv'
    
    def _get_box_nodes(self):
        with open(self.nod_file, 'r') as csvfile:
            nodes = pd.read_csv(csvfile, header=None, sep=r'\s* \s*', skiprows=1, engine='python')
            nodes.columns = ['index', 'lon', 'lat', 'mask']
            new_box = [min(self.box[0], self.box[1]), max(self.box[0], self.box[1]),
                       min(self.box[2], self.box[3]), max(self.box[2], self.box[3])]
            self.box = new_box

            #print("Checking for node IDs inside:", self.box)
            if self.box[0] > 180 and self.box[1] < 180:
                for ind, nod in nodes.iterrows():
                    if ((nod['lon'] >= self.box[0] or nod['lon'] <= self.box[1]) \
                        and nod['lat'] >= self.box[2] and nod['lat'] <= self.box[3] \
                        ):
                        self.box_nodes.append(int(nod['index']) - 1)
            else:
                for ind, nod in nodes.iterrows():
                    if (nod['lon'] >= self.box[0] and nod['lon'] <= self.box[1] \
                        and nod['lat'] >= self.box[2] and nod['lat'] <= self.box[3] \
                        ):
                        self.box_nodes.append(int(nod['index']) - 1)

    def _get_box_cell_areas(self):
        self.box_cell_areas = xr.open_dataset(self.grid_file).sel(ncells=self.box_nodes).cell_area.squeeze()

    def _generate_mask(self):
        tmp = xr.open_dataset(self.olist[0])
        box_nodes_ = np.array(self.box_nodes)
        self.mask = np.zeros(len(tmp.nodes_3d))
        self.mask[box_nodes_] = 1
        self.fl_mask = tmp.variables[self.variable] * self.mask

    def _select_appropriate_level(self):
        print("\nLoading calculations into actual memory for saving:")
        if not self.levelwise:
            level_data, elem_no_nan = pf.get_data(
                self.fl_mask[0],
                self.mesh,
                self.depth
            )
        else:
            level_data = self.fl_mask[0,0].values
            #timestep = np.expand_dims(self.ds.time.mean().values, 0)
        #self.timestep = timestep
        self.level_data = level_data

    def _prepare_for_interpolation(self):
        self.lon = np.linspace(-180, 180, 1440)
        self.lat = np.linspace(-90, 90, 720)
        self.lons, self.lats = np.meshgrid(self.lon, self.lat)

    def _interpolate_to_regular_grid(self):
        print(
            "\nPerforming nearest-neighbor interpolation onto a 0.25 x 0.25 degree regular grid:"
        )
        nearest = pf.fesom2regular(
            self.level_data, self.mesh, self.lons, self.lats, how="nn"
        )
        # Add an empty array dimension for the timestep
        self.nearest = nearest #np.expand_dims(nearest, axis=0)

    def _interpolation_to_dataarray(self):
        print("\n Generating an DataArray object for saving")
        self.interpolated_ds = xr.DataArray(
            self.nearest,
            dims=["lat", "lon"],
            coords=[self.lat, self.lon],
            name=ARGS.variable,
        )

    def _save_results(self):
        print("\nSaving results:")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.ds_timseries.to_netcdf(self.output_file)
            if self.save_mask: 
                self.interpolated_ds.to_netcdf(self.output_file_mask)
            print("File saved:", self.output_file)

    def _cleanup_on_cluster(self):
        # close the client:
        self.client.close()
        self.cluster.close()


################################################################################


if __name__ == "__main__":
    OUTDATA_DIR = os.path.abspath("../../outdata/fesom")
    CONFIG_DIR = os.path.abspath("../../config/fesom/")

    namelist_config = f90nml.read(CONFIG_DIR + "/namelist.config")
    #LEVELWISE_OUTPUT = namelist_config["inout"]["levelwise_output"]
    MESH_DIR_GUESS = namelist_config["paths"]["meshpath"]

    # Ensure that you are only using one OpenMP Thread
    os.environ["OMP_NUM_THREADS"] = "1"

    def parse_arguments():
        """
        Figure out command line arguments given to this script.

        Returns:
        --------
        args
            Args is a namespace with the following things:
                + mesh_dir : the directory where the mesh can be found
                + variable : Thee variablee that should be timmeaened
                + outdata_dir : Where the output data is stored

        Note:
        -----
        Please call like this, since it returns a **constant** ::

            ARGS = parse_arguments()
        """
        parser = argparse.ArgumentParser(
            "Calculates timseries of an entire experiment for a surface variable",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument("variable")
        parser.add_argument("--expid", default=None)
        parser.add_argument("--mesh_dir", default=MESH_DIR_GUESS)
        parser.add_argument("--outdata_dir", default=OUTDATA_DIR)
        parser.add_argument(
            "--localhost_multiprocessing",
            default=False,
            action="store_true",
            help="Uses multiple python instances for localhost processing (not applicable if using the compute nodes)",
        )
        parser.add_argument(
            "--run_on_cluster",
            default=False,
            action="store_true",
            help="Tries to run on the compute node(s)",
        )
        parser.add_argument(
            "--force",
            default=False,
            action="store_true",
            help="Redoes computation, even if file is already present",
        )
        parser.add_argument(
            "--naming_convention",
            default="esm_new",
            help=textwrap.dedent(
                """Determine the naming convention used for output files. Available options implemented:

                    esm_classic = '<variable>_fesom_<date>.nc'
                    esm_new = '<EXPID>_fesom_<variable>_<date>.nc'
                    xiaoxu = 'fesom.<year>.oce.mean.nc'
                    """
            ),
        )
        parser.add_argument(
            "--mesh_rotated",
            default=False,
            action="store_true",
            help="Add this switch if your mesh is rotated",
        )
        parser.add_argument(
            "--levelwise",
            default=False,
            action="store_true",
            help="Add this switch if your output is levelwise",
        )
        parser.add_argument(
            "--box",
            default=[0,360,-90,90],
            nargs='+',
            type=int,
            help="Box [lon1,lon2,lat1,lat2] to average over",
        )
        parser.add_argument(
            "--depth",
            default=0,
            type=int,
            help="Depth from which to take value (only if levelwise=True)",
        )
        parser.add_argument(
            "--save_mask",
            default=False,
            action="store_true",
            help="Add this switch if you want to save a masked file",
        )
        parser.add_argument(
            "--grid_file_name",
            default="griddes.nc",
            help="Give filename of grid file",
        )
        args = parser.parse_args()
        # TODO: There is probably a better way to handle filepaths in Python
        if not args.outdata_dir.endswith("/"):
            args.outdata_dir += "/"
        return args

    ARGS = parse_arguments()

    m = MainProgram(
        ARGS.variable,
        ARGS.outdata_dir,
        expid=ARGS.expid,
        force=ARGS.force,
        localhost_multiprocessing=ARGS.localhost_multiprocessing,
        mesh_rotated=ARGS.mesh_rotated,
        levelwise=ARGS.levelwise,
        naming_convention=ARGS.naming_convention,
        run_on_cluster=ARGS.run_on_cluster,
        box=ARGS.box,
        save_mask=ARGS.save_mask,
        depth=ARGS.depth,
        grid_file_name=ARGS.grid_file_name
    )
    m()
