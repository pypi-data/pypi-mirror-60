# @Author: Paul Gierz <pgierz>
# @Date:   2020-01-31T19:07:40+01:00
# @Email:  pgierz@awi.de
# @Filename: ANALYSIS_fesom_sfc_timmean.py
# @Last modified by:   pgierz
# @Last modified time: 2020-02-03T13:29:58+01:00


#!/usr/bin/env python3
"""
A script to easily generate surface means of FESOM output and automatically
interpolate to a regular 0.25x0.25 grid.

Example Usage
-------------

From inside the ``analysis/fesom`` directory ::

    ./ANALYSIS_fesom_sfc_timmean <variable_name>

This is the most simple use case. If you use ``esm-tools``, the script will
automatically be able to detect the mesh directory and output directories.
"""

# Python Standard Library
import argparse
import datetime
import logging
import os
import re
import socket
import sys
import textwrap
import warnings

# Third-Party Packages
import numpy as np
import pyfesom as pf
import xarray as xr

import f90nml

from regex_engine import generator
from dask.diagnostics import ProgressBar

# Optional Imports
try:
    from dask.distributed import Client, progress
    from dask_jobqueue import SLURMCluster

    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False


def get_list_of_relevant_files(odir, variable, naming_convention, years):
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
    r = re.compile(
        determine_regex_from_naming_convention(naming_convention, variable, years)
    )
    olist = [odir + "/" + f for f in os.listdir(odir) if r.match(f)]
    olist.sort(key=lambda x: os.path.getmtime(x))
    if years == 0:
        olist = olist[-30:]
    return olist


def determine_regex_from_naming_convention(naming, variable, years):
    if not years == 0:
        regex_years = generator().numerical_range(years[0], years[1]).strip("^$")
    else:
        regex_years = r"\d+"

    if naming == "esm_classic":
        return variable + "_fesom_" + regex_years + "0101.nc"
    elif naming == "esm_new":
        return ".*_fesom_" + variable + "_" + regex_years + "0101.nc"
    elif naming == "xiaoxu":
        return "fesom." + regex_years + "0101" + ".oce.mean.nc"
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
        expid=None,
        naming_convention=None,
        force=False,
        run_on_cluster=False,
        mesh_rotated=False,
        localhost_multiprocessing=False,
        timintv=None,
        levelwise_output=None,
        mesh=None,
        years=0,
    ):
        self.variable = variable
        self.data_dir = data_dir
        self.timintv = timintv

        self.expid = expid or data_dir.split("/")[-4]
        if self.timintv is not None:
            self.output_file = (
                output_file
                or self.expid + "_fesom_" + self.variable + "_" + self.timintv + ".nc"
            )
        else:
            self.output_file = (
                output_file or self.expid + "_fesom_" + self.variable + "_timmean.nc"
            )

        self.naming_convention = naming_convention or "esm_classic"
        if DASK_AVAILABLE:
            self.run_on_cluster = run_on_cluster
        else:
            self.run_on_cluster = False
        self.localhost_multiprocessing = localhost_multiprocessing
        self.mesh_rotated = mesh_rotated
        self.force = force
        self.years = years
        self.mesh = mesh
        self.LEVELWISE_OUTPUT = levelwise_output
        logging.debug("Done with init!")

    def __call__(self):
        print(80 * "-")
        print("Start of ANALYSIS_fesom_sfc_timmean.py")

        logging.debug("Start of ANALYSIS_fesom_sfc_timmean.py")

        self._early_exit_if_output_exists()
        self._determine_data_to_load()
        self._load_data()

        # Seperate into two operations to avoid memory errors:

        if "depth" in self.ds.dims:
            self.ds_top = self.ds.isel(depth=0)
        else:
            self.ds_top = self.ds

        if self.timintv is not None:
            self.ds_timmean = self.ds_top.groupby("time." + self.timintv).mean(
                dim="time"
            )
        else:
            self.ds_timmean = self.ds_top.mean(dim="time")

        if self.run_on_cluster:
            self._prepare_on_cluster()
        else:
            self._prepare_on_localhost()

        print("\nPerforming mean over 'time' dimension and selecting uppermost level:")

        if self.run_on_cluster:
            self._compute_on_cluster()
        else:
            self._compute_on_localhost()

        if not self.mesh:
            self._load_mesh_information()
        self._select_appropriate_level()
        self._prepare_for_interpolation()
        self._interpolate_to_regular_grid()
        self._interpolation_to_dataarray()
        self._save_results()

        if self.run_on_cluster:
            self._cleanup_on_cluster()

        print("\nAll done, goodbye!")
        sys.exit(0)

    def _early_exit_if_output_exists(self):
        if not self.force:
            if os.path.isfile(self.output_file):
                print("Output file ", self.output_file, "already exists!")
                logging.debug("Output file %s already exists", self.output_file)
                sys.exit(0)

    def _determine_data_to_load(self):
        print("\nLoading metadata the 30 newest files...")
        logging.debug("\nLoading metadata the 30 newest files...")
        # Only get the 100 newest files:
        self.olist = get_list_of_relevant_files(
            self.data_dir, self.variable, self.naming_convention, self.years
        )
        print("self.olist: ", self.olist)
        logging.debug("self.olist: %s", self.olist)
        full_size = full_size_of_filelist(self.olist)
        self.full_size_str = sizeof_fmt(full_size)
        print("Total size = ", self.full_size_str)
        logging.debug("Total size = %s", self.full_size_str)

    def _load_data(self):
        print("(Be patient, this may take a while)")
        # Load the data:
        now = datetime.datetime.now()

        # The context manager is used to filter warnings regarding time step
        # information, which appear to be safely ignorable:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.ds = xr.open_mfdataset(self.olist, parallel=True)

        # Process 5 years at once --> smaller number of years: more I/O, less change of memory error:
        # self.ds = self.ds.chunk({"time": 365*5, })

        print(
            "Loaded 30 newest files (",
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
            self.ds_timmean = self.ds_timmean.persist(
                retries=5
            )  # start computation in the background
            progress(self.ds_timmean)  # watch progress
            self.ds_timmean.compute()

    def _compute_on_localhost(self):
        with ProgressBar():
            self.ds_timmean.compute()

    def _load_mesh_information(self):
        print("\nLoading mesh information:")
        # Load the mesh
        abg = [0, 0, 0] if self.mesh_rotated else [50, 15, -90]
        self.mesh = pf.load_mesh(ARGS.mesh_dir, usepickle=False, get3d=False, abg=abg)

    def _select_appropriate_level(self):
        print("\nLoading calculations into actual memory for saving (may take a while):")
        if not self.LEVELWISE_OUTPUT:
            level_data, elem_no_nan = pf.get_data(
                self.ds_timmean.variables[self.variable][:, :].mean(axis=0),
                self.mesh,
                0,
            )
        else:
            level_data = self.ds_timmean.variables[self.variable].values
            timestep = np.expand_dims(self.ds.time.mean().values, 0)
        self.level_data = level_data

        if self.timintv is not None:
            self.timestep = self.ds_timmean[self.timintv].values
        else:
            self.timestep = timestep

    def _prepare_for_interpolation(self):
        self.lon = np.linspace(-180, 180, 1440)
        self.lat = np.linspace(-90, 90, 720)
        self.lons, self.lats = np.meshgrid(self.lon, self.lat)

    def _interpolate_to_regular_grid(self):
        print(
            "\nPerforming nearest-neighbor interpolation onto a 0.25 x 0.25 degree regular grid:"
        )
        if self.timintv is not None:
            nearest = []

            for level_data_tmp in self.level_data:
                nearest.append(
                    pf.fesom2regular(
                        level_data_tmp, self.mesh, self.lons, self.lats, how="nn"
                    )
                )
            self.nearest = nearest
        else:
            nearest = pf.fesom2regular(
                self.level_data, self.mesh, self.lons, self.lats, how="nn"
            )
            # Add an empty array dimension for the timestep
            self.nearest = np.expand_dims(nearest, axis=0)

    def _interpolation_to_dataarray(self):
        print("\n Generating an DataArray object for saving")
        self.interpolated_ds = xr.DataArray(
            self.nearest,
            dims=["time", "lat", "lon"],
            coords=[self.timestep, self.lat, self.lon],
            name=self.variable,
        )

    def _save_results(self):
        print("\nSaving results:")
        self.interpolated_ds.to_netcdf(self.output_file)
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
    LEVELWISE_OUTPUT = namelist_config["inout"]["levelwise_output"]
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
            "Calculates timmean of an entire experiment for a surface variable",
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
            "--timintv",
            type=str,
            default=None,
            help="Time intervall over which to average. Possible inputs are 'day', 'month' and 'season' if provided by the input data",
        )
        parser.add_argument(
            "--years",
            nargs="+",
            type=int,
            default=0,
            help="Add this switch if your mesh is rotated",
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
        naming_convention=ARGS.naming_convention,
        run_on_cluster=ARGS.run_on_cluster,
        years=ARGS.years,
        timintv=ARGS.timintv,
    )
    m()
