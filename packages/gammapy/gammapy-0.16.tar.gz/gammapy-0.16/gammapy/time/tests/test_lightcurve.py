# Licensed under a 3-clause BSD style license - see LICENSE.rst
import datetime
import pytest
import numpy as np
from numpy.testing import assert_allclose
import astropy.units as u
from astropy.table import Column, Table
from astropy.time import Time
from gammapy.data import GTI
from gammapy.modeling.models import PowerLawSpectralModel, SkyModel
from gammapy.spectrum.tests.test_flux_point_estimator import (
    simulate_map_dataset,
    simulate_spectrum_dataset,
)
from gammapy.time import LightCurve, LightCurveEstimator
from gammapy.utils.testing import mpl_plot_check, requires_data, requires_dependency

# time time_min time_max flux flux_err flux_ul
# 48705.1757 48705.134 48705.2174 0.57 0.29 nan
# 48732.89195 48732.8503 48732.9336 0.39 0.29 nan
# 48734.0997 48734.058 48734.1414 0.48 0.29 nan
# 48738.98535 48738.9437 48739.027 nan nan 0.97
# 48741.0259 48740.9842 48741.0676 0.34 0.29 nan


@pytest.fixture(scope="session")
def lc():
    meta = dict(TIMESYS="utc")

    table = Table(
        meta=meta,
        data=[
            Column(Time(["2010-01-01", "2010-01-03"]).mjd, "time_min"),
            Column(Time(["2010-01-03", "2010-01-10"]).mjd, "time_max"),
            Column([1e-11, 3e-11], "flux", unit="cm-2 s-1"),
            Column([0.1e-11, 0.3e-11], "flux_err", unit="cm-2 s-1"),
            Column([np.nan, 3.6e-11], "flux_ul", unit="cm-2 s-1"),
            Column([False, True], "is_ul"),
        ],
    )

    return LightCurve(table=table)


def test_lightcurve_repr(lc):
    assert repr(lc) == "LightCurve(len=2)"


def test_lightcurve_properties_time(lc):
    assert lc.time_scale == "utc"
    assert lc.time_format == "mjd"

    # Time-related attributes
    time = lc.time
    assert time.scale == "utc"
    assert time.format == "mjd"
    assert_allclose(time.mjd, [55198, 55202.5])

    assert_allclose(lc.time_min.mjd, [55197, 55199])
    assert_allclose(lc.time_max.mjd, [55199, 55206])

    # Note: I'm not sure why the time delta has this scale and format
    time_delta = lc.time_delta
    assert time_delta.scale == "tai"
    assert time_delta.format == "jd"
    assert_allclose(time_delta.jd, [2, 7])


def test_lightcurve_properties_flux(lc):
    flux = lc.table["flux"].quantity
    assert flux.unit == "cm-2 s-1"
    assert_allclose(flux.value, [1e-11, 3e-11])


# TODO: extend these tests to cover other time scales.
# In those cases, CSV should not round-trip because there
# is no header info in CSV to store the time scale!


@pytest.mark.parametrize("format", ["fits", "ascii.ecsv", "ascii.csv"])
def test_lightcurve_read_write(tmp_path, lc, format):
    lc.write(tmp_path / "tmp", format=format)
    lc = LightCurve.read(tmp_path / "tmp", format=format)

    # Check if time-related info round-trips
    time = lc.time
    assert time.scale == "utc"
    assert time.format == "mjd"
    assert_allclose(time.mjd, [55198, 55202.5])


@requires_dependency("matplotlib")
def test_lightcurve_plot(lc):
    with mpl_plot_check():
        lc.plot()


@pytest.mark.parametrize("flux_unit", ["cm-2 s-1"])
def test_lightcurve_plot_flux(lc, flux_unit):
    f, ferr = lc._get_fluxes_and_errors(flux_unit)
    assert_allclose(f, [1e-11, 3e-11])
    assert_allclose(ferr, ([0.1e-11, 0.3e-11], [0.1e-11, 0.3e-11]))


@pytest.mark.parametrize("flux_unit", ["cm-2 s-1"])
def test_lightcurve_plot_flux_ul(lc, flux_unit):
    is_ul, ful = lc._get_flux_uls(flux_unit)
    assert_allclose(is_ul, [False, True])
    assert_allclose(ful, [np.nan, 3.6e-11])


def test_lightcurve_plot_time(lc):
    t, terr = lc._get_times_and_errors("mjd")
    assert np.array_equal(t, [55198.0, 55202.5])
    assert np.array_equal(terr, [[1.0, 3.5], [1.0, 3.5]])

    t, terr = lc._get_times_and_errors("iso")
    assert np.array_equal(
        t, [datetime.datetime(2010, 1, 2), datetime.datetime(2010, 1, 6, 12)]
    )
    assert np.array_equal(
        terr,
        [
            [datetime.timedelta(1), datetime.timedelta(3.5)],
            [datetime.timedelta(1), datetime.timedelta(3.5)],
        ],
    )


def get_spectrum_datasets():
    model = SkyModel(spectral_model=PowerLawSpectralModel())
    dataset_1 = simulate_spectrum_dataset(model=model, random_state=0)
    dataset_1._name = "dataset_1"
    gti1 = GTI.create("0h", "1h", "2010-01-01T00:00:00")
    dataset_1.gti = gti1

    dataset_2 = simulate_spectrum_dataset(model, random_state=1)
    dataset_2._name = "dataset_2"
    gti2 = GTI.create("1h", "2h", "2010-01-01T00:00:00")
    dataset_2.gti = gti2

    return [dataset_1, dataset_2]


@requires_data()
@requires_dependency("iminuit")
def test_group_datasets_in_time_interval():
    # Doing a LC on one hour bin
    datasets = get_spectrum_datasets()
    time_intervals = [
        Time(["2010-01-01T00:00:00", "2010-01-01T01:00:00"]),
        Time(["2010-01-01T01:00:00", "2010-01-01T02:00:00"]),
    ]
    estimator = LightCurveEstimator(
        datasets, norm_n_values=3, time_intervals=time_intervals
    )
    steps = ["err", "counts", "ts", "norm-scan"]
    estimator.run(e_ref=10 * u.TeV, e_min=1 * u.TeV, e_max=100 * u.TeV, steps=steps)

    assert len(estimator.group_table_info) == 2
    assert estimator.group_table_info["Name"][0] == "dataset_1"
    assert_allclose(estimator.group_table_info["Tstart"], [55197.0, 55197.04166666667])
    assert_allclose(
        estimator.group_table_info["Tstop"], [55197.04166666667, 55197.083333333336]
    )
    assert_allclose(estimator.group_table_info["Group_ID"], [0, 1])


@requires_data()
@requires_dependency("iminuit")
def test_group_datasets_in_time_interval_outflows():
    datasets = get_spectrum_datasets()
    # Check Overflow
    time_intervals = [
        Time(["2010-01-01T00:00:00", "2010-01-01T00:55:00"]),
        Time(["2010-01-01T01:00:00", "2010-01-01T02:00:00"]),
    ]
    estimator = LightCurveEstimator(
        datasets, norm_n_values=3, time_intervals=time_intervals
    )
    steps = ["err", "counts", "ts", "norm-scan"]
    estimator.run(e_ref=10 * u.TeV, e_min=1 * u.TeV, e_max=100 * u.TeV, steps=steps)
    assert estimator.group_table_info["Bin_type"][0] == "Overflow"

    # Check underflow
    time_intervals = [
        Time(["2010-01-01T00:05:00", "2010-01-01T01:00:00"]),
        Time(["2010-01-01T01:00:00", "2010-01-01T02:00:00"]),
    ]
    estimator = LightCurveEstimator(
        datasets, norm_n_values=3, time_intervals=time_intervals
    )
    steps = ["err", "counts", "ts", "norm-scan"]
    estimator.run(e_ref=10 * u.TeV, e_min=1 * u.TeV, e_max=100 * u.TeV, steps=steps)
    assert estimator.group_table_info["Bin_type"][0] == "Underflow"


@requires_data()
@requires_dependency("iminuit")
def test_lightcurve_estimator_spectrum_datasets():
    # Doing a LC on one hour bin
    datasets = get_spectrum_datasets()
    time_intervals = [
        Time(["2010-01-01T00:00:00", "2010-01-01T01:00:00"]),
        Time(["2010-01-01T01:00:00", "2010-01-01T02:00:00"]),
    ]
    estimator = LightCurveEstimator(
        datasets, norm_n_values=3, time_intervals=time_intervals
    )
    lightcurve = estimator.run(e_ref=10 * u.TeV, e_min=1 * u.TeV, e_max=100 * u.TeV)
    assert_allclose(lightcurve.table["time_min"], [55197.0, 55197.041667])
    assert_allclose(lightcurve.table["time_max"], [55197.041667, 55197.083333])
    assert_allclose(lightcurve.table["e_ref"], [10, 10])
    assert_allclose(lightcurve.table["e_min"], [1, 1])
    assert_allclose(lightcurve.table["e_max"], [100, 100])
    assert_allclose(lightcurve.table["ref_dnde"], [1e-14, 1e-14])
    assert_allclose(lightcurve.table["ref_flux"], [9.9e-13, 9.9e-13])
    assert_allclose(lightcurve.table["ref_eflux"], [4.60517e-12, 4.60517e-12])
    assert_allclose(lightcurve.table["ref_e2dnde"], [1e-12, 1e-12])
    assert_allclose(lightcurve.table["stat"], [23.302288, 22.457766], rtol=1e-5)
    assert_allclose(lightcurve.table["norm"], [0.988127, 0.948108], rtol=1e-5)
    assert_allclose(lightcurve.table["norm_err"], [0.043985, 0.043498], rtol=1e-4)
    assert_allclose(lightcurve.table["counts"], [2281, 2222])
    assert_allclose(lightcurve.table["norm_errp"], [0.044231, 0.04377], rtol=1e-5)
    assert_allclose(lightcurve.table["norm_errn"], [0.04374, 0.043226], rtol=1e-5)
    assert_allclose(lightcurve.table["norm_ul"], [1.077213, 1.036237], rtol=1e-5)
    assert_allclose(lightcurve.table["sqrt_ts"], [26.773925, 25.796426], rtol=1e-4)
    assert_allclose(lightcurve.table["ts"], [716.843084, 665.455601], rtol=1e-4)
    assert_allclose(lightcurve.table[0]["norm_scan"], [0.2, 1.0, 5.0])
    assert_allclose(
        lightcurve.table[0]["stat_scan"],
        [444.426957, 23.375417, 3945.382802],
        rtol=1e-5,
    )


@requires_data()
@requires_dependency("iminuit")
def test_lightcurve_estimator_spectrum_datasets_withmaskfit():
    # Doing a LC on one hour bin
    datasets = get_spectrum_datasets()
    time_intervals = [
        Time(["2010-01-01T00:00:00", "2010-01-01T01:00:00"]),
        Time(["2010-01-01T01:00:00", "2010-01-01T02:00:00"]),
    ]

    e_min_fit = 1 * u.TeV
    e_max_fit = 3 * u.TeV
    for dataset in datasets:
        mask_fit = dataset.counts.energy_mask(emin=e_min_fit, emax=e_max_fit)
        dataset.mask_fit = mask_fit

    steps = ["err", "counts", "ts", "norm-scan"]
    estimator = LightCurveEstimator(
        datasets, norm_n_values=3, time_intervals=time_intervals
    )
    lightcurve = estimator.run(
        e_ref=10 * u.TeV, e_min=1 * u.TeV, e_max=100 * u.TeV, steps=steps
    )
    assert_allclose(lightcurve.table["time_min"], [55197.0, 55197.041667])
    assert_allclose(lightcurve.table["time_max"], [55197.041667, 55197.083333])
    assert_allclose(lightcurve.table["stat"], [6.60304, 0.421047], rtol=1e-5)
    assert_allclose(lightcurve.table["norm"], [0.885082, 0.967022], rtol=1e-5)


@requires_data()
@requires_dependency("iminuit")
def test_lightcurve_estimator_spectrum_datasets_default():
    # Test default time interval: each time interval is equal to the gti of each dataset, here one hour
    datasets = get_spectrum_datasets()
    estimator = LightCurveEstimator(datasets, norm_n_values=3)
    steps = ["err", "counts", "ts", "norm-scan"]
    lightcurve = estimator.run(
        e_ref=10 * u.TeV, e_min=1 * u.TeV, e_max=100 * u.TeV, steps=steps
    )
    assert_allclose(lightcurve.table["time_min"], [55197.0, 55197.041667])
    assert_allclose(lightcurve.table["time_max"], [55197.041667, 55197.083333])
    assert_allclose(lightcurve.table["norm"], [0.988127, 0.948108], rtol=1e-5)


@requires_data()
@requires_dependency("iminuit")
def test_lightcurve_estimator_spectrum_datasets_notordered():
    # Test that if the time intervals given are not ordered in time, it is first ordered correctly and then
    # compute as expected
    datasets = get_spectrum_datasets()
    time_intervals = [
        Time(["2010-01-01T01:00:00", "2010-01-01T02:00:00"]),
        Time(["2010-01-01T00:00:00", "2010-01-01T01:00:00"]),
    ]
    estimator = LightCurveEstimator(
        datasets, norm_n_values=3, time_intervals=time_intervals
    )
    steps = ["err", "counts", "ts", "norm-scan"]
    lightcurve = estimator.run(
        e_ref=10 * u.TeV, e_min=1 * u.TeV, e_max=100 * u.TeV, steps=steps
    )
    assert_allclose(lightcurve.table["time_min"], [55197.0, 55197.041667])
    assert_allclose(lightcurve.table["time_max"], [55197.041667, 55197.083333])
    assert_allclose(lightcurve.table["norm"], [0.988127, 0.948108], rtol=1e-5)


@requires_data()
@requires_dependency("iminuit")
def test_lightcurve_estimator_spectrum_datasets_largerbin():
    # Test all dataset in a single LC bin, here two hours
    datasets = get_spectrum_datasets()
    time_intervals = [Time(["2010-01-01T00:00:00", "2010-01-01T02:00:00"])]
    estimator = LightCurveEstimator(
        datasets, norm_n_values=3, time_intervals=time_intervals
    )
    steps = ["err", "counts", "ts", "norm-scan"]
    lightcurve = estimator.run(
        e_ref=10 * u.TeV, e_min=1 * u.TeV, e_max=100 * u.TeV, steps=steps
    )

    assert_allclose(lightcurve.table["time_min"], [55197.0])
    assert_allclose(lightcurve.table["time_max"], [55197.083333])
    assert_allclose(lightcurve.table["e_ref"], [10])
    assert_allclose(lightcurve.table["e_min"], [1])
    assert_allclose(lightcurve.table["e_max"], [100])
    assert_allclose(lightcurve.table["ref_dnde"], [1e-14])
    assert_allclose(lightcurve.table["ref_flux"], [9.9e-13])
    assert_allclose(lightcurve.table["ref_eflux"], [4.60517e-12])
    assert_allclose(lightcurve.table["ref_e2dnde"], [1e-12])
    assert_allclose(lightcurve.table["stat"], [46.177981], rtol=1e-5)
    assert_allclose(lightcurve.table["norm"], [0.968049], rtol=1e-5)
    assert_allclose(lightcurve.table["norm_err"], [0.030929], rtol=1e-4)
    assert_allclose(lightcurve.table["ts"], [1381.880757], rtol=1e-4)


@requires_data()
@requires_dependency("iminuit")
def test_lightcurve_estimator_spectrum_datasets_timeoverlaped():
    # Check that it returns a ValueError if the time intervals overlapped
    datasets = get_spectrum_datasets()
    time_intervals = [
        Time(["2010-01-01T00:00:00", "2010-01-01T01:30:00"]),
        Time(["2010-01-01T01:00:00", "2010-01-01T02:00:00"]),
    ]
    with pytest.raises(ValueError) as excinfo:
        LightCurveEstimator(datasets, norm_n_values=3, time_intervals=time_intervals)
    msg = "LightCurveEstimator requires non-overlapping time bins."
    assert str(excinfo.value) == msg


@requires_data()
@requires_dependency("iminuit")
def test_lightcurve_estimator_spectrum_datasets_gti_not_include_in_time_intervals():
    # Check that it returns a ValueError if the time intervals are smaller than the dataset GTI.
    datasets = get_spectrum_datasets()
    time_intervals = [
        Time(["2010-01-01T00:00:00", "2010-01-01T00:05:00"]),
        Time(["2010-01-01T01:00:00", "2010-01-01T01:05:00"]),
    ]
    estimator = LightCurveEstimator(
        datasets, norm_n_values=3, time_intervals=time_intervals
    )
    with pytest.raises(ValueError) as excinfo:
        steps = ["err", "counts", "ts", "norm-scan"]
        estimator.run(e_ref=10 * u.TeV, e_min=1 * u.TeV, e_max=100 * u.TeV, steps=steps)
    msg = "LightCurveEstimator: No datasets in time intervals"
    assert str(excinfo.value) == msg


def get_map_datasets():
    dataset_1 = simulate_map_dataset(random_state=0)
    dataset_1._name = "dataset_1"
    gti1 = GTI.create("0 h", "1 h", "2010-01-01T00:00:00")
    dataset_1.gti = gti1

    dataset_2 = simulate_map_dataset(random_state=1)
    gti2 = GTI.create("1 h", "2 h", "2010-01-01T00:00:00")
    dataset_2._name = "dataset_2"
    dataset_2.gti = gti2

    return [dataset_1, dataset_2]


@requires_data()
@requires_dependency("iminuit")
def test_lightcurve_estimator_map_datasets():
    datasets = get_map_datasets()

    time_intervals = [
        Time(["2010-01-01T00:00:00", "2010-01-01T01:00:00"]),
        Time(["2010-01-01T01:00:00", "2010-01-01T02:00:00"]),
    ]
    estimator = LightCurveEstimator(
        datasets, source="source", time_intervals=time_intervals
    )
    steps = ["err", "counts", "ts", "norm-scan"]
    lightcurve = estimator.run(
        e_ref=10 * u.TeV, e_min=1 * u.TeV, e_max=100 * u.TeV, steps=steps
    )
    assert_allclose(lightcurve.table["time_min"], [55197.0, 55197.041667])
    assert_allclose(lightcurve.table["time_max"], [55197.041667, 55197.083333])
    assert_allclose(lightcurve.table["e_ref"], [10, 10])
    assert_allclose(lightcurve.table["e_min"], [1, 1])
    assert_allclose(lightcurve.table["e_max"], [100, 100])
    assert_allclose(lightcurve.table["ref_dnde"], [1e-13, 1e-13])
    assert_allclose(lightcurve.table["ref_flux"], [9.9e-12, 9.9e-12])
    assert_allclose(lightcurve.table["ref_eflux"], [4.60517e-11, 4.60517e-11])
    assert_allclose(lightcurve.table["ref_e2dnde"], [1e-11, 1e-11])
    assert_allclose(lightcurve.table["stat"], [-87412.393367, -89856.129206], rtol=1e-5)
    assert_allclose(lightcurve.table["norm_err"], [0.042259, 0.043614], rtol=1e-3)
    assert_allclose(lightcurve.table["sqrt_ts"], [38.527512, 39.489968], rtol=1e-4)
    assert_allclose(lightcurve.table["ts"], [1484.369159, 1559.457547], rtol=1e-4)

    datasets = get_map_datasets()
    time_intervals2 = [Time(["2010-01-01T00:00:00", "2010-01-01T02:00:00"])]
    estimator2 = LightCurveEstimator(
        datasets, source="source", time_intervals=time_intervals2
    )
    lightcurve2 = estimator2.run(e_ref=10 * u.TeV, e_min=1 * u.TeV, e_max=100 * u.TeV)

    assert_allclose(lightcurve2.table["time_min"], [55197.0])
    assert_allclose(lightcurve2.table["time_max"], [55197.083333])
    assert_allclose(lightcurve2.table["e_ref"], [10])
    assert_allclose(lightcurve2.table["e_min"], [1])
    assert_allclose(lightcurve2.table["e_max"], [100])
    assert_allclose(lightcurve2.table["ref_dnde"], [1e-13])
    assert_allclose(lightcurve2.table["ref_flux"], [9.9e-12])
    assert_allclose(lightcurve2.table["ref_eflux"], [4.60517e-11])
    assert_allclose(lightcurve2.table["ref_e2dnde"], [1e-11])
    assert_allclose(lightcurve2.table["stat"], [-177267.775615], rtol=1e-5)
    assert_allclose(lightcurve2.table["norm_err"], [0.030358], rtol=1e-3)
    assert_allclose(lightcurve.table["counts"], [46794, 47388])
    assert_allclose(lightcurve2.table["ts"], [3042.893291], rtol=1e-4)
