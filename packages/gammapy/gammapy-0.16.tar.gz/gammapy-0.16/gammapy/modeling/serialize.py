# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Utilities to serialize models."""
from gammapy.cube.fit import MapDataset
from gammapy.spectrum import FluxPointsDataset, SpectrumDatasetOnOff
from .models import Registry, SkyDiffuseCube, SkyModel

# TODO: move this elsewhere ?
DATASETS = Registry([MapDataset, SpectrumDatasetOnOff, FluxPointsDataset])

__all__ = ["models_to_dict", "dict_to_models", "dict_to_datasets", "datasets_to_dict"]


def models_to_dict(models):
    """Convert list of models to dict.

    Parameters
    ----------
    models : list
        Python list of Model objects
    """
    # update shared parameters names for serialization
    _update_link_reference(models)

    models_data = []
    for model in models:
        model_data = model.to_dict()
        # De-duplicate if model appears several times
        if model_data not in models_data:
            models_data.append(model_data)

    return {"components": models_data}


def _update_link_reference(models):
    params_list = []
    params_shared = []
    for model in models:
        for param in model.parameters:
            if param not in params_list:
                params_list.append(param)
            elif param not in params_shared:
                params_shared.append(param)
    for k, param in enumerate(params_shared):
        param._link_label_io = param.name + "@shared_" + str(k)


def dict_to_models(data, link=True):
    """De-serialise model data to Model objects.

    Parameters
    ----------
    data : dict
        Serialised model information
    link : bool
        check for shared parameters and link them
    """
    models = []
    for component in data["components"]:
        # background models are created separately
        if component["type"] == "BackgroundModel":
            continue

        if component["type"] == "SkyDiffuseCube":
            model = SkyDiffuseCube.from_dict(component)

        if component["type"] == "SkyModel":
            model = SkyModel.from_dict(component)

        models.append(model)

    if link:
        _link_shared_parameters(models)
    return models


def _link_shared_parameters(models):
    shared_register = {}
    for model in models:
        if isinstance(model, SkyModel):
            submodels = [
                model.spectral_model,
                model.spatial_model,
                model.temporal_model,
            ]
            for submodel in submodels:
                if submodel is not None:
                    shared_register = _set_link(shared_register, submodel)
        else:
            shared_register = _set_link(shared_register, model)


def _set_link(shared_register, model):
    for param in model.parameters:
        name = param.name
        link_label = param._link_label_io
        if link_label is not None:
            if link_label in shared_register:
                new_param = shared_register[link_label]
                model.parameters.link(name, new_param)
            else:
                shared_register[link_label] = param
    return shared_register


def datasets_to_dict(datasets, path, prefix, overwrite):
    """Convert datasets to dicts for serialization.

    Parameters
    ----------
    datasets : `~gammapy.modeling.Datasets`
        Datasets
    path : `pathlib.Path`
        path to write files
    prefix : str
        common prefix of file names
    overwrite : bool
        overwrite datasets FITS files
    """
    unique_models = []
    unique_backgrounds = []
    datasets_dictlist = []

    for dataset in datasets:
        filename = path / f"{prefix}_data_{dataset.name}.fits"
        dataset.write(filename, overwrite)
        datasets_dictlist.append(dataset.to_dict(filename=filename))

        if dataset.models is not None:
            for model in dataset.models:
                if model not in unique_models:
                    unique_models.append(model)

        try:
            if dataset.background_model not in unique_backgrounds:
                unique_backgrounds.append(dataset.background_model)
        except AttributeError:
            pass

    datasets_dict = {"datasets": datasets_dictlist}
    components_dict = models_to_dict(unique_models + unique_backgrounds)
    return datasets_dict, components_dict


def dict_to_datasets(data_list, components):
    """add models and backgrounds to datasets

    Parameters
    ----------
    datasets : `~gammapy.modeling.Datasets`
        Datasets
    components : dict
        dict describing model components
    """
    models = dict_to_models(components)
    datasets = []

    for data in data_list["datasets"]:
        dataset = DATASETS.get_cls(data["type"]).from_dict(data, components, models)
        datasets.append(dataset)
    return datasets
