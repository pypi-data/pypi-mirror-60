import os

import pytest

from esmcol_validator import validator

here = os.path.abspath(os.path.dirname(__file__))


def _run_validate(url, esmcol_spec_dirs=None, version='master', log_level='DEBUG'):
    esmcol = validator.EsmcolValidate(url, esmcol_spec_dirs, version, log_level)
    esmcol.run()
    return esmcol


def test_invalid_log_level():
    with pytest.raises(ValueError):
        _ = _run_validate(
            os.path.join(here, 'test_data/good_collection.json'), log_level='DEBUGGING'
        )


def test_schema_incompatibility():
    esmcol = _run_validate(
        os.path.join(here, 'test_data/schema_incompatible.json'),
        esmcol_spec_dirs=os.path.join(here, 'spec-dir/json-schema'),
    )
    assert (
        esmcol.message[0]['error_message']
        == "[{'column_name': 'path'}, {'format': 'zarr'}, {'format_column_name': 'foo'}] is not of type 'object' of ['assets']"
    )


def test_good_collection_local():
    esmcol = _run_validate(os.path.join(here, 'test_data/good_collection.json'))
    expected = {
        'collections': {'valid': 1, 'invalid': 0},
        'catalogs': {'valid': 1, 'invalid': 0},
        'unknown': 0,
    }
    assert esmcol.status == expected


def test_bad_spec():
    with pytest.raises(SystemExit):
        _ = _run_validate(
            os.path.join(here, 'test_data/good_collection.json'), esmcol_spec_dirs='./'
        )


def test_bad_catalog_file():
    esmcol = _run_validate(os.path.join(here, 'test_data/bad_collection.json'))
    assert esmcol.status['catalogs']['invalid'] == 1


def test_catalog_file_not_found():
    esmcol = _run_validate(
        'https://raw.githubusercontent.com/NCAR/esm-collection-spec/master/collection-spec/examples/sample-glade-cmip6-netcdf-collection.json'
    )
    expected = {
        'collections': {'valid': 1, 'invalid': 0},
        'catalogs': {'valid': 0, 'invalid': 1},
        'unknown': 0,
    }
    assert esmcol.status == expected


@pytest.mark.parametrize(
    'collection',
    ['test_data/good_collection.json', 'test_data/simple_collection_with_catalog_dict.json'],
)
def test_spec_dir(collection):
    url = os.path.join(here, collection)
    spec_dir = os.path.join(here, 'spec-dir/json-schema')
    esmcol = _run_validate(url, esmcol_spec_dirs=spec_dir)
    expected = {
        'collections': {'valid': 1, 'invalid': 0},
        'catalogs': {'valid': 1, 'invalid': 0},
        'unknown': 0,
    }
    assert esmcol.status == expected


def test_bad_collection():
    spec_dir = os.path.join(here, 'spec-dir/json-schema')
    url = os.path.join(here, 'test_data/simple_bad_collection_with_catalog_dict.json')
    esmcol = _run_validate(url, esmcol_spec_dirs=spec_dir)
    expected = "'format' and 'format_column_name' are mutually exclusive"
    assert esmcol.message[0]['cat_error_message'] == expected

    with pytest.raises(Exception):
        _ = _run_validate(url, version='0.0.0')

    esmcol = _run_validate(url=os.path.join(here, 'test_data/does_not_exist.json'))
    assert esmcol.message[0]['error_type'] == 'FileNotFoundError'
