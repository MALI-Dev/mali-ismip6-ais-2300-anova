import re
import shutil
import tarfile
import xarray as xr

from pathlib import Path
from typing import Literal, NoReturn, overload
from xarray import Dataset

StatsTypes = Literal["global", "regional"]
FieldTypes = Literal["state", "flux"]

time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)

archive_dir = Path("/pscratch/sd/a/anolan/ismip6_ais_anova_ensemble_archive")
zenodo_dir = Path("/pscratch/sd/a/anolan/ismip6_ais_anova_files_4_zenodo")

def write_tarred_zarr(ds: Dataset, out_fp: Path) -> NoReturn:
    # write the zarr file, which is untarred
    ds.to_zarr(out_fp, mode='w', consolidated=False)

    # tar the contents of the zarr file
    with tarfile.open(out_fp.with_suffix(".zarr.tar"), "w") as tar:
        for name in out_fp.iterdir():
            tar.add(name, arcname=name.relative_to(out_fp.parent))

    # remove the untarred zarr file
    shutil.rmtree(out_fp)

def process_timeseries(
    archive_dir: Path, zenodo_dir: Path, stats_type: StatsTypes
) -> NoReturn:

    files = archive_dir.glob(f"*/expAE*_04/output/{stats_type}Stats.nc")
    output_dir = zenodo_dir / "Timeseries" / f"{stats_type}"

    output_dir.mkdir(exist_ok=True, parents=True)

    for fp in files:
        q = re.search(r'q(\d{2})', str(fp)).group(1)
        m = re.search(r'm(\d{2})', str(fp)).group(1)
        e = re.search(r'expAE(\d{2})_04', str(fp)).group(1)

        out_fp = output_dir / f"q{q}m{m}_expAE{e}_{stats_type}Stats.nc"

        shutil.copy(fp, out_fp)

    if stats_type == "regional":
        region_mask = (
            archive_dir / "mesh/AIS_4to20km_r01_20220907.regionMask_ismip6.nc"
        )

        if not region_mask.exists():
            raise FileNotFoundError(f"{region_mask}")

        out_fp = output_dir / region_mask.name

        shutil.copy(region_mask, out_fp)

def process_spatial_files(
    archive_dir: Path, zenodo_dir: Path, with_hydro: bool, field_type: FieldTypes
) -> NoReturn:

    if with_hydro:
        files = archive_dir.glob(f"*/expAE1*_04/output/{field_type}.nc")
        output_dir = zenodo_dir / f"ExpAE11-ExpAE14_{field_type}"
    else:
        files = archive_dir.glob(f"*/expAE0*_04/output/{field_type}.nc")
        output_dir = zenodo_dir / f"ExpAE02-ExpAE05_{field_type}"

    # make the zenodo repo dir, if it does not exist already
    output_dir.mkdir(exist_ok=True)
    (output_dir / "mesh").mkdir(exist_ok=True)

    relaxed_fp = archive_dir / "mesh/relaxed_10yrs_4km.nc"
    mesh_ds = xr.open_dataset(relaxed_fp)
    mesh_ds = mesh_ds.drop_vars("forcingTimeStamp")

    for m in [3, 5, 10]:

        out_fp = output_dir / f"mesh/AIS_4to20km_r01_20220907_relaxed_q{m}.zarr"

        if m != 5:
            mu_fp = archive_dir.glob(f"mesh/AIS_4to20km_r01_20220907_m{m}*.nc")
            mu_ds = xr.open_dataset(list(mu_fp)[0])
            mesh_ds["muFriction"] = mu_ds["muFriction"]

        write_tarred_zarr(mesh_ds, out_fp)

    for fp in list(files):
        q = re.search(r'q(\d{2})', str(fp)).group(1)
        m = re.search(r'm(\d{2})', str(fp)).group(1)
        e = re.search(r'(expAE\d{2}_04)', str(fp)).group(1)

        # path to the historial simulation for the ensemble member
        hist_fp = archive_dir / f"q{q}m{m}/hist_04/output/{field_type}.nc"

        # open and concat historical and projection simulations
        ds = xr.open_mfdataset([hist_fp, fp], decode_times=time_coder)
        # rechunk the Time so it's continous
        ds = ds.chunk(Time=-1)

        #ds = ds.expand_dims("q").assign_coords({"q": ("q", [q])})
        #ds = ds.expand_dims("m").assign_coords({"m": ("m", [m])})
        #ds = ds.expand_dims("e").assign_coords({"e": ("e", [e])})

        out_fp = output_dir / f"{e}_q{q}m{m}_{field_type}.zarr"

        write_tarred_zarr(ds, out_fp)

process_timeseries(archive_dir, zenodo_dir, "global")
process_timeseries(archive_dir, zenodo_dir, "regional")

for hydro in [True, False]:
    process_spatial_files(archive_dir, zenodo_dir, hydro, "state")
    process_spatial_files(archive_dir, zenodo_dir, hydro, "flux")
