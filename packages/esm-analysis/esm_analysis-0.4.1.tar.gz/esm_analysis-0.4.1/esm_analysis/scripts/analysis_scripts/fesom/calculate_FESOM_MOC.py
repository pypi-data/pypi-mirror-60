#!/usr/bin/env python3
"""
A script adaption of Thomas Rackow's AMOC Plotting Notebooks, for batch use.

Dr. Paul Gierz
May 2019
"""


import warnings

warnings.filterwarnings("ignore")

import argparse
import logging
import datetime
import os
import re
import sys

sys.path.append("/pf/a/a270088/pyfesom")
import pyfesom

# Ensure that you are only using one OpenMP Thread
os.environ["OMP_NUM_THREADS"] = "1"

try:
    from dask.diagnostics import ProgressBar
    import numpy as np
    import pandas as pd
    import pyfesom as pf
    import xarray as xr
    import matplotlib.pyplot as plt
    from tqdm import trange, tqdm
    import joblib
    from joblib import Parallel, delayed
    from dask.distributed import Client

except:
    raise ImportError("You need numpy, pandas, pyfesom, and xarray for this!")


# If you have a remote cluster running Dask
# client = Client('tcp://scheduler-address:8786')

# If you want Dask to set itself up on your personal computer
client = Client(processes=False)
# Set up logging to be a useful info
def set_up_logging(loglevel):
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % loglevel)
    logging.basicConfig(
        level=numeric_level, format="     - %(levelname)s : %(message)s"
    )


def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate FESOM MOC from output data.")
    parser.add_argument("outdata_dir", help="The output directory of FESOM")
    parser.add_argument("mesh_dir", help="The mesh directory use for this run")
    parser.add_argument(
        "mask_file",
        default="",
        nargs="?",
        help="If provided, uses only these element IDs to calculate the MOC (Default is to use all elements in the file",
    )
    parser.add_argument(
        "--log", default="ERROR", help="Logging level. Choose from DEBUG, INFO, ERROR"
    )
    parser.add_argument("--f_prefix", default="", help="Output filename prefix")
    return parser.parse_args()


def _load_fesom_mfdataset(filepattern, outdata_dir, return_count=False):
    """
        Loads all FESOM files matching a particular pattern in a directory

        Parameters
        ----------
        filepattern : str
                The pattern to match
        outdata_dir : str
                Where to look

        Returns
        -------
        xarray.Dataset
                The dataset object with all information.
        """
    starting_time = datetime.datetime.now()
    r = re.compile(filepattern)
    for root, dirs, files in os.walk(outdata_dir):
        l = [os.path.join(root, x) for x in files if r.match(x)]
    if return_count:
        return len(l)
    # print(" " * 4, "*   Loading velocity data...")
    return l


def load_velocity(outdata_dir):
    """
        Load all the FESOM velocities.

        Parameters
        ----------
        outdata_dir : str
                Where to look for the files

        Returns
        -------
        xarray.Dataset
                The dataset object with all the vertical velocity information.
        """
    # NOTE: We make a filepattern to match velocity files. This is assuming
    # coupled simulations using ESM-Tools:
    filepattern = "wo_fesom_\d+.nc"
    return _load_fesom_mfdataset(filepattern, outdata_dir)


def count_velocity_files(outdata_dir):
    filepattern = "wo_fesom_\d+.nc"
    return _load_fesom_mfdataset(filepattern, outdata_dir, return_count=True)


def mesh_to_dataset(mesh):
    """
        Generates an xarray dataset out of the mesh attributes; useful for
        merging this with other datarrays to attach mesh information to a
        dataset
        """


if __name__ == "__main__":
    master_start = datetime.datetime.now()
    print(80 * "-")
    print("S T A R T   O F   calculate_FESOM_MOC.py".center(80))
    # Get user arguments
    args = parse_arguments()
    set_up_logging(args.log)
    print("\n")
    # print("-" * 5 + "|", "(1)   L O A D I N G   D A T A")
    # Load the required data
    # print(" " * 4, "*   Loading mesh...")
    start_loadmesh = datetime.datetime.now()
    mesh = pf.load_mesh(args.mesh_dir, usepickle=False, abg=[0, 0, 0])
    # print(mesh)
    # sys.exit()

    for file_name in tqdm(
        load_velocity(args.outdata_dir), total=count_velocity_files(args.outdata_dir)
    ):
        vertical_velocity = xr.open_dataset(file_name)
        # Determine if the user gave a mask:
        if args.mask_file:
            with open(args.mask_file) as f:
                #  Subtract one from the mask file, Python is 0 indexed and Fortran
                #  1:
                node_ids = [int(l) - 1 for l in f.read().splitlines()]
        else:
            node_ids = []

        # Fix up the xr.Dataset:
        vertical_velocity = vertical_velocity.assign_coords(
            nodes_2d=(["nodes_2d"], range(mesh.n2d))
        )
        vertical_velocity = vertical_velocity.assign(
            variables={
                "Latitude_nodes": (["nodes_2d"], mesh.y2),
                "Longitude_nodes": (["nodes_2d"], mesh.x2),
            }
        )
        vertical_velocity = vertical_velocity.rename({"nodes_3d": "nodes_2d"})
        vertical_velocity = vertical_velocity.assign_attrs(
            {
                "wo": {"units": "m/s"},
                "Latitude_nodes": {"units": "degrees North"},
                "Longitude_nodes": {"units": "degrees East"},
            }
        )

        mask = vertical_velocity.nodes_2d.isin(node_ids).values

        # print("\n")
        # print("-" * 5 + "|", "(2)   D E T E R M I N G   M E S H   P R O P E R T I E S")
        start_mesh_props = datetime.datetime.now()

        # print(" " * 4, "*   Determing mesh properties for binning...")
        for mesh_property in [
            "mesh.path",
            "mesh.alpha",
            "mesh.beta",
            "mesh.gamma",
            "mesh.n2d",
            "mesh.e2d",
            "mesh.n3d",
            "mesh.x2",
            "mesh.y2",
            "mesh.zlevs",
        ]:
            logging.info(
                "%s: %s" % (mesh_property, getattr(mesh, mesh_property.split(".")[-1]))
            )

        # print(mesh.alpha, mesh.beta, mesh.gamma)
        mesh.alpha = 0.0
        mesh.beta = 0.0
        mesh.gamma = 0.0
        # print(mesh.alpha, mesh.beta, mesh.gamma)

        # Which domain to integrate over:
        total_nlats = 90  # 90 #180 #1800
        lats = np.linspace(-89.95, 89.95, total_nlats)
        logging.info("lats: %s", lats)
        dlat = lats[1] - lats[0]
        logging.info("dlat: %s", dlat)

        # Get values needed in the computation
        nlevels = np.shape(mesh.zlevs)[0]
        depth = mesh.zlevs

        # How many timesteps do we have?
        total_timesteps = vertical_velocity.time.size
        # The triangle areas
        el_area = mesh.voltri

        # Node indices for every element
        el_nodes = mesh.elem

        # Mesh coordinates
        nodes_x = mesh.x2  # -180 ... 180
        nodes_y = mesh.y2  # -90 ... 90
        logging.info("nodes_x.shape: %s", nodes_x.shape)
        logging.info("nodes_y.shape: %s", nodes_y.shape)

        # Compute lon/lat coordinate of an element required later for binning
        elem_x = nodes_x[el_nodes].sum(axis=1) / 3.0
        elem_y = nodes_y[el_nodes].sum(axis=1) / 3.0

        # Number of local vertical levels for every grid point
        nlevels_local = np.sum(mesh.n32[:, :] != -999, axis=1)
        hittopo_at = (
            np.min(nlevels_local[el_nodes[:, 0:3]], axis=1) - 1
        )  # hit topo at this level

        # print(" " * 4, "*   Attaching mesh information to velocity data...")

        # Compute positions of elements in zonalmean-array for binning
        pos = ((elem_y - lats[0]) / dlat).astype("int")
        if (datetime.datetime.now() - start_mesh_props) > datetime.timedelta(seconds=2):
            pass
            # print(" " * 9, "...done in %s" % (datetime.datetime.now() - start_mesh_props))
        else:
            pass
            # print(" " * 9, "...done.")

        # print("\n")
        # print("-" * 5 + "|", "(3)   A L L O C A T E   B I N N E D   M O C   A R R A Y")
        # Allocate binned array
        binned = np.zeros((nlevels, total_nlats, total_timesteps)) * np.nan

        # print("\n")
        # print("-" * 5 + "|", "(4)   C R U N C H I N G   T H E   I N T E G R A T I O N")
        # To start from the bottom, use reversed(range(nlevels)):
        def calculate_moc_for_ts_levelwise_output(ts):
            local_binned = np.zeros((nlevels, total_nlats)) * np.nan
            for lev in range(nlevels):
                logging.info("Binning for level: %s", mesh.zlevs[lev])
                # Make the weighted average in the dataset:
                W = vertical_velocity.wo.isel(time=ts, depth=lev)
                W.load()
                W[~mask] = 0
                # for index in range(len(W.data)):
                #    if index not in node_ids:
                #        W.data[index] = 0.0
                W_elem_mean_weight = el_area * np.mean(W.data[el_nodes[:, 0:3]], axis=1)
                W_elem_mean_weight *= 10.0 ** -6
                W_elem_mean_weight[hittopo_at] = 0.0

                for lat in range(pos.min(), pos.max() + 1):
                    indices = np.logical_and(pos == lat, lev <= hittopo_at)
                    if np.sum(indices) == 0.0:
                        local_binned[lev, lat] = np.nan  # only topo
                    else:
                        local_binned[lev, lat] = np.nansum(W_elem_mean_weight[indices])
            return (ts, local_binned)

        def calculate_moc_for_ts_no_levelwise_output(ts):
            local_binned = np.zeros((nlevels, total_nlats)) * np.nan
            for lev in range(nlevels):
                logging.info("Binning for level: %s", mesh.zlevs[lev])
                # Make the weighted average in the dataset:
                # W = vertical_velocity.wo.isel(time=ts, depth=lev)
                # Load Data without levelwise output
                # print(vertical_velocity.wo.data[ts, :])
                W, dummy = pf.get_data(
                    vertical_velocity.wo.data[ts, :], mesh, depth=mesh.zlevs[lev]
                )
                # import pdb; pdb.set_trace()
                # W.load()
                W[~mask] = 0
                # for index in range(len(W.data)):
                #    if index not in node_ids:
                #        W.data[index] = 0.0
                W_elem_mean_weight = el_area * np.mean(W[el_nodes[:, 0:3]], axis=1)
                W_elem_mean_weight *= 10.0 ** -6
                W_elem_mean_weight[hittopo_at] = 0.0

                for lat in range(pos.min(), pos.max() + 1):
                    indices = np.logical_and(pos == lat, lev <= hittopo_at)
                    if np.sum(indices) == 0.0:
                        local_binned[lev, lat] = np.nan  # only topo
                    else:
                        local_binned[lev, lat] = np.nansum(W_elem_mean_weight[indices])
            return (ts, local_binned)

        if "depth" in vertical_velocity.dims:
            calculate_moc_for_ts = calculate_moc_for_ts_levelwise_output
        else:
            calculate_moc_for_ts = calculate_moc_for_ts_no_levelwise_output

        parallel_execution = False
        if parallel_execution:
            sys.exit("Parallel Exection is not yet done!")
            # [calculate_moc_for_ts(timestep) for timestep in trange(total_timesteps)]
            # Parallel processing:
            binned_gather = []
            with ProgressBar():
                with joblib.parallel_backend("dask"):
                    binned_gather.append(
                        Parallel(n_jobs=-2, verbose=10, prefer="processes")(
                            # PG: Change this
                            delayed(calculate_moc_for_ts)(ts)
                            for ts in trange(100)
                        )
                    )

            import pickle

            pickle.dump(binned_gather, open("binned_gather.p", "wb"))
        else:
            # for ts in trange(10):
            for ts in range(total_timesteps):
                tsstr = str(vertical_velocity.time.data[ts])
                raw_ts = vertical_velocity.time.data[ts]
                try:
                    new_tsstr = raw_ts.strftime("%Y%m%d")
                except AttributeError:
                    if isinstance(raw_ts, np.datetime64):
                        new_ts = datetime.datetime.strptime(
                            str(raw_ts).split(".")[0], "%Y-%m-%dT%H:%M:%S"
                        )
                        try:
                            new_tsstr = new_ts.strftime("%Y%m%d")
                        except AttributeError:
                            print(str(raw_ts))
                            raise
                    else:
                        raise

                # print(raw_ts, new_tsstr)
                if args.f_prefix:
                    args.f_prefix += "_"
                if os.path.isfile(args.f_prefix + "MOC_" + tsstr + ".nc"):
                    os.rename(
                        args.f_prefix + "MOC_" + tsstr + ".nc",
                        args.f_prefix + "MOC_" + new_tsstr + ".nc",
                    )
                    continue
                if os.path.isfile(args.f_prefix + "MOC_" + new_tsstr + ".nc"):
                    continue
                # Figure out if we have levelwise output or not:
                _, binned = calculate_moc_for_ts(ts)
                # Integrate from the north:
                binned = np.ma.cumsum(np.fliplr(np.ma.masked_invalid(binned)), axis=1)
                # Get the array the right way around again:
                binned = np.fliplr(binned)
                # Sign change since we integrated north to south:
                binned *= -1

                # print("\n")
                # print("-" * 5 + "|", "(6)   S A V I N G   R E S U L T S")
                binned_ds = xr.Dataset(
                    {
                        "MOC": (
                            ("Time", "Depth", "Latitude"),
                            np.expand_dims(binned, axis=0),
                        )
                    },
                    coords={
                        "Latitude": (
                            ["Latitude"],
                            np.linspace(-89.95, 89.95, total_nlats),
                        ),
                        "Depth": (["Depth"], depth),
                        "Time": (["Time"], [raw_ts]),
                    },
                )
                binned_ds.to_netcdf(args.f_prefix + "MOC_" + new_tsstr + ".nc")
    print("\n")
    print("F I N I S H E D !".center(80))
    print(80 * "-")
    print("Total time %s" % (datetime.datetime.now() - master_start))
