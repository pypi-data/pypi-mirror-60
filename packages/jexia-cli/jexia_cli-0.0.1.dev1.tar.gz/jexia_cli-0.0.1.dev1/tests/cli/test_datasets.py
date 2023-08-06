import os
import pytest

from tests.cli import run_cmd


@pytest.mark.integration
def test_datasets_integration():
    project_id = os.environ['JEXIA_CLI_TEST_PAID_PROJECT']
    # create new dataset
    dataset = run_cmd(['dataset create',
                       '-f=json',
                       '--project=%s' % project_id,
                       '--name=test'])
    columns = ['id', 'name', 'type', 'immutable', 'properties', 'inputs',
               'outputs']
    for column in columns:
        assert column in dataset
    # list of datasets
    datasets = run_cmd(['dataset list',
                        '-f=json',
                        '--project=%s' % project_id])
    assert 1 == len(datasets)
    # list of dataset fields
    fields = run_cmd(['dataset field list',
                      '-f=json',
                      '--project=%s' % project_id,
                      '--dataset=%s' % dataset['id']])
    assert 3 == len(fields)
    # create dataset field
    field = run_cmd(['dataset field create',
                     '-f=json',
                     '--project=%s' % project_id,
                     '--dataset=%s' % dataset['id'],
                     '--name=test',
                     '--type=string',
                     '--constraint=min_length=1000',
                     '--constraint=required=true',
                     '--constraint=default=some-val'])
    columns = ['id', 'name', 'type', 'immutable', 'properties', 'constraints']
    for column in columns:
        assert column in field
    assert 'min_length=1000' in field['constraints']
    assert 'required=True' in field['constraints']
    assert 'default=some-val' in field['constraints']

    # update dataset field
    field = run_cmd(['dataset field update',
                     '-f=json',
                     '--project=%s' % project_id,
                     '--dataset=%s' % dataset['id'],
                     '--constraint=required=false',
                     '--constraint=default=',
                     field['id']])
    columns = ['id', 'name', 'type', 'immutable', 'properties', 'constraints']
    for column in columns:
        assert column in field
    assert 'min_length=1000' == field['constraints']
    # delete dataset field
    output = run_cmd(['dataset field delete',
                      '--project=%s' % project_id,
                      '--dataset=%s' % dataset['id'],
                      field['id']])
    assert '' == output
    # check deletion
    fields = run_cmd(['dataset field list',
                      '-f=json',
                      '--project=%s' % project_id,
                      '--dataset=%s' % dataset['id']])
    assert 3 == len(fields)
    # delete dataset
    output = run_cmd(['dataset delete',
                      '--project=%s' % project_id,
                      dataset['id']])
    assert '' == output
    # check deletion
    datasets = run_cmd(['dataset list',
                        '-f=json',
                        '--project=%s' % project_id])
    assert 0 == len(datasets)
