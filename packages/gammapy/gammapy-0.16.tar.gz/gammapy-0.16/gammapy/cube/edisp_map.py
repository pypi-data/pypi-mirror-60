# Licensed under a 3-clause BSD style license - see LICENSE.rst
from copy import deepcopy
import numpy as np
from scipy.interpolate import interp1d
import astropy.io.fits as fits
from gammapy.irf import EDispKernel
from gammapy.maps import Map, MapAxis, MapCoord, WcsGeom
from gammapy.utils.random import InverseCDFSampler, get_random_state

__all__ = ["make_edisp_map", "EDispMap"]


def make_edisp_map(edisp, pointing, geom, exposure_map=None):
    """Make a edisp map for a single observation

    Expected axes : migra and true energy in this specific order
    The name of the migra MapAxis is expected to be 'migra'

    Parameters
    ----------
    edisp : `~gammapy.irf.EnergyDispersion2D`
        the 2D Energy Dispersion IRF
    pointing : `~astropy.coordinates.SkyCoord`
        the pointing direction
    geom : `~gammapy.maps.Geom`
        the map geom to be used. It provides the target geometry.
        rad and true energy axes should be given in this specific order.
    exposure_map : `~gammapy.maps.Map`, optional
        the associated exposure map.
        default is None

    Returns
    -------
    edispmap : `~gammapy.cube.EDispMap`
        the resulting EDisp map
    """
    energy_axis = geom.get_axis_by_name("energy")
    energy = energy_axis.center

    migra_axis = geom.get_axis_by_name("migra")
    migra = migra_axis.center

    # Compute separations with pointing position
    offset = geom.separation(pointing)

    # Compute EDisp values
    edisp_values = edisp.data.evaluate(
        offset=offset,
        e_true=energy[:, np.newaxis, np.newaxis, np.newaxis],
        migra=migra[:, np.newaxis, np.newaxis],
    )

    # Create Map and fill relevant entries
    data = edisp_values.to_value("")
    edispmap = Map.from_geom(geom, data=data, unit="")
    return EDispMap(edispmap, exposure_map)


class EDispMap:
    """Energy dispersion map.

    Parameters
    ----------
    edisp_map : `~gammapy.maps.Map`
        the input Energy Dispersion Map. Should be a Map with 2 non spatial axes.
        migra and true energy axes should be given in this specific order.
    exposure_map : `~gammapy.maps.Map`, optional
        Associated exposure map. Needs to have a consistent map geometry.

    Examples
    --------
    ::

        import numpy as np
        from astropy import units as u
        from astropy.coordinates import SkyCoord
        from gammapy.maps import WcsGeom, MapAxis
        from gammapy.irf import EnergyDispersion2D, EffectiveAreaTable2D
        from gammapy.cube import make_edisp_map, make_map_exposure_true_energy

        # Define energy dispersion map geometry
        energy_axis = MapAxis.from_edges(np.logspace(-1, 1, 4), unit="TeV", name="energy")
        migra_axis = MapAxis.from_edges(np.linspace(0, 3, 100), name="migra")
        pointing = SkyCoord(0, 0, unit="deg")
        max_offset = 4 * u.deg
        geom = WcsGeom.create(
            binsz=0.25 * u.deg,
            width=10 * u.deg,
            skydir=pointing,
            axes=[migra_axis, energy_axis],
        )

        # Extract EnergyDispersion2D from CTA 1DC IRF
        filename = "$GAMMAPY_DATA/cta-1dc/caldb/data/cta/1dc/bcf/South_z20_50h/irf_file.fits"
        edisp2D = EnergyDispersion2D.read(filename, hdu="ENERGY DISPERSION")
        aeff2d = EffectiveAreaTable2D.read(filename, hdu="EFFECTIVE AREA")

        # Create the exposure map
        exposure_geom = geom.to_image().to_cube([energy_axis])
        exposure_map = make_map_exposure_true_energy(pointing, "1 h", aeff2d, exposure_geom)

        # create the EDispMap for the specified pointing
        edisp_map = make_edisp_map(edisp2D, pointing, geom, max_offset, exposure_map)

        # Get an Energy Dispersion (1D) at any position in the image
        pos = SkyCoord(2.0, 2.5, unit="deg")
        e_reco = np.logspace(-1.0, 1.0, 10) * u.TeV
        edisp = edisp_map.get_edisp_kernel(pos=pos, e_reco=e_reco)

        # Write map to disk
        edisp_map.write("edisp_map.fits")
    """

    def __init__(self, edisp_map, exposure_map):
        if edisp_map.geom.axes[1].name.upper() != "ENERGY":
            raise ValueError("Incorrect energy axis position in input Map")

        if edisp_map.geom.axes[0].name.upper() != "MIGRA":
            raise ValueError("Incorrect migra axis position in input Map")

        self.edisp_map = edisp_map
        self.exposure_map = exposure_map

    @classmethod
    def from_hdulist(
        cls,
        hdulist,
        edisp_hdu="EDISPMAP",
        edisp_hdubands="BANDSEDISP",
        exposure_hdu="EXPMAP",
        exposure_hdubands="BANDSEXP",
    ):
        """Convert to `~astropy.io.fits.HDUList`.

        Parameters
        ----------
        edisp_hdu : str
            Name or index of the HDU with the edisp_map data.
        edisp_hdubands : str
            Name or index of the HDU with the edisp_map BANDS table.
        exposure_hdu : str
            Name or index of the HDU with the exposure_map data.
        exposure_hdubands : str
            Name or index of the HDU with the exposure_map BANDS table.
        """
        edisp_map = Map.from_hdulist(hdulist, edisp_hdu, edisp_hdubands, "auto")
        if exposure_hdu in hdulist:
            exposure_map = Map.from_hdulist(
                hdulist, exposure_hdu, exposure_hdubands, "auto"
            )
        else:
            exposure_map = None

        return cls(edisp_map, exposure_map)

    @classmethod
    def read(cls, filename, **kwargs):
        """Read an edisp_map from file and create an EDispMap object"""
        with fits.open(filename, memmap=False) as hdulist:
            return cls.from_hdulist(hdulist, **kwargs)

    def to_hdulist(
        self,
        edisp_hdu="EDISPMAP",
        edisp_hdubands="BANDSEDISP",
        exposure_hdu="EXPMAP",
        exposure_hdubands="BANDSEXP",
    ):
        """Convert to `~astropy.io.fits.HDUList`.

        Parameters
        ----------
        edisp_hdu : str
            Name or index of the HDU with the edisp_map data.
        edisp_hdubands : str
            Name or index of the HDU with the edisp_map BANDS table.
        exposure_hdu : str
            Name or index of the HDU with the exposure_map data.
        exposure_hdubands : str
            Name or index of the HDU with the exposure_map BANDS table.

        Returns
        -------
        hdu_list : `~astropy.io.fits.HDUList`
        """
        hdulist = self.edisp_map.to_hdulist(hdu=edisp_hdu, hdu_bands=edisp_hdubands)
        if self.exposure_map is not None:
            new_hdulist = self.exposure_map.to_hdulist(
                hdu=exposure_hdu, hdu_bands=exposure_hdubands
            )
            hdulist.extend(new_hdulist[1:])
        return hdulist

    def write(self, filename, overwrite=False, **kwargs):
        """Write to fits"""
        hdulist = self.to_hdulist(**kwargs)
        hdulist.writeto(filename, overwrite=overwrite)

    def get_edisp_kernel(self, position, e_reco):
        """Get energy dispersion at a given position.

        Parameters
        ----------
        position : `~astropy.coordinates.SkyCoord`
            the target position. Should be a single coordinates
        e_reco : `~astropy.units.Quantity`
            Reconstructed energy axis binning

        Returns
        -------
        edisp : `~gammapy.irf.EnergyDispersion`
            the energy dispersion (i.e. rmf object)
        """
        if position.size != 1:
            raise ValueError(
                "EnergyDispersion can be extracted at one single position only."
            )

        energy_axis = self.edisp_map.geom.get_axis_by_name("energy")
        migra_axis = self.edisp_map.geom.get_axis_by_name("migra")

        coords = {
            "skycoord": position,
            "migra": migra_axis.center.reshape((-1, 1, 1, 1)),
            "energy": energy_axis.center.reshape((1, -1, 1, 1)),
        }

        # Interpolate in the EDisp map. Squeeze to remove dimensions of length 1
        values = self.edisp_map.interp_by_coord(coords) * self.edisp_map.unit
        edisp_values = values.squeeze()

        data = []

        for idx, e_true in enumerate(energy_axis.center):
            # migration value of e_reco bounds
            migra = e_reco / e_true

            cumsum = np.insert(edisp_values[:, idx], 0, 0).cumsum()
            with np.errstate(invalid="ignore"):
                cumsum = np.nan_to_num(cumsum / cumsum[-1])

            f = interp1d(
                migra_axis.edges.value,
                cumsum,
                kind="linear",
                bounds_error=False,
                fill_value=(0, 1),
            )

            # We compute the difference between 2 successive bounds in e_reco
            # to get integral over reco energy bin
            integral = np.diff(np.clip(f(migra), a_min=0, a_max=1))
            data.append(integral)

        return EDispKernel(
            e_true_lo=energy_axis.edges[:-1],
            e_true_hi=energy_axis.edges[1:],
            e_reco_lo=e_reco[:-1],
            e_reco_hi=e_reco[1:],
            data=data,
        )

    def stack(self, other, weights=None):
        """Stack EDispMap with another one in place.

        Parameters
        ----------
        other : `~gammapy.cube.EDispMap`
            Energy dispersion map to be stacked with this one.

        """
        if self.exposure_map is None or other.exposure_map is None:
            raise ValueError("Missing exposure map for PSFMap.stack")

        cutout_info = other.edisp_map.geom.cutout_info

        if cutout_info is not None:
            slices = cutout_info["parent-slices"]
            parent_slices = Ellipsis, slices[0], slices[1]
        else:
            parent_slices = None

        self.edisp_map.data[parent_slices] *= self.exposure_map.data[parent_slices]
        self.edisp_map.stack(other.edisp_map * other.exposure_map.data, weights=weights)

        # stack exposure map
        self.exposure_map.stack(other.exposure_map, weights=weights)

        with np.errstate(invalid="ignore"):
            self.edisp_map.data[parent_slices] /= self.exposure_map.data[parent_slices]
            self.edisp_map.data = np.nan_to_num(self.edisp_map.data)

    def copy(self):
        """Copy EDispMap"""
        return deepcopy(self)

    @classmethod
    def from_geom(cls, geom):
        """Create edisp map from geom.

        By default a diagonal edisp matrix is created.

        Parameters
        ----------
        geom : `Geom`
            Edisp map geometry.

        Returns
        -------
        edisp_map : `EDispMap`
            Energy dispersion map.
        """
        geom_exposure_edisp = geom.squash(axis="migra")
        exposure_edisp = Map.from_geom(geom_exposure_edisp, unit="m2 s")

        migra_axis = geom.get_axis_by_name("migra")
        edisp_map = Map.from_geom(geom, unit="")
        migra_0 = migra_axis.coord_to_pix(1)

        # distribute over two pixels
        migra = geom.get_idx()[2]
        data = np.abs(migra - migra_0)
        data = np.where(data < 1, 1 - data, 0)
        edisp_map.quantity = data
        return cls(edisp_map, exposure_edisp)

    def sample_coord(self, map_coord, random_state=0):
        """Apply the energy dispersion corrections on the coordinates of a set of simulated events.

        Parameters
        ----------
        map_coord : `~gammapy.maps.MapCoord` object.
            Sequence of coordinates and energies of sampled events.
        random_state : {int, 'random-seed', 'global-rng', `~numpy.random.RandomState`}
            Defines random number generator initialisation.
            Passed to `~gammapy.utils.random.get_random_state`.

        Returns
        -------
        `~gammapy.maps.MapCoord`.
            Sequence of Edisp-corrected coordinates of the input map_coord map.
        """
        random_state = get_random_state(random_state)
        migra_axis = self.edisp_map.geom.get_axis_by_name("migra")

        coord = {
            "skycoord": map_coord.skycoord.reshape(-1, 1),
            "energy": map_coord["energy"].reshape(-1, 1),
            "migra": migra_axis.center,
        }

        pdf_edisp = self.edisp_map.interp_by_coord(coord)

        sample_edisp = InverseCDFSampler(pdf_edisp, axis=1, random_state=random_state)
        pix_edisp = sample_edisp.sample_axis()
        migra = migra_axis.pix_to_coord(pix_edisp)

        energy_reco = map_coord["energy"] * migra

        return MapCoord.create({"skycoord": map_coord.skycoord, "energy": energy_reco})

    @classmethod
    def from_diagonal_response(cls, energy_axis_true, migra_axis=None):
        """Create an allsky EDisp map with diagonal response.

        Parameters
        ----------
        energy_axis_true : `MapAxis`
            True energy axis
        migra_axis : `MapAxis`
            Migra axis

        Returns
        -------
        edisp_map : `EDispMap`
            Energy dispersion map.
        """
        migra_res = 1e-5
        migra_axis_default = MapAxis.from_bounds(
            1 - migra_res, 1 + migra_res, nbin=3, name="migra", node_type="edges"
        )

        migra_axis = migra_axis or migra_axis_default

        geom = WcsGeom.create(
            npix=(2, 1), proj="CAR", binsz=180, axes=[migra_axis, energy_axis_true]
        )

        return cls.from_geom(geom)

    def cutout(self, position, width, mode="trim"):
        """Cutout edisp map.

        Parameters
        ----------
        position : `~astropy.coordinates.SkyCoord`
            Center position of the cutout region.
        width : tuple of `~astropy.coordinates.Angle`
            Angular sizes of the region in (lon, lat) in that specific order.
            If only one value is passed, a square region is extracted.
        mode : {'trim', 'partial', 'strict'}
            Mode option for Cutout2D, for details see `~astropy.nddata.utils.Cutout2D`.

        Returns
        -------
        cutout : `EdispMap`
            Cutout edisp map.
        """
        edisp_map = self.edisp_map.cutout(position, width, mode)
        exposure_map = self.exposure_map.cutout(position, width, mode)
        return self.__class__(edisp_map=edisp_map, exposure_map=exposure_map)
