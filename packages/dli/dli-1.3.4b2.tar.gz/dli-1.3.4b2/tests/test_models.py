import os
import io
import threading
import pytest
import tempfile
import pyarrow
import pandas
import numpy
import random
import json

from dli.client.exceptions import DataframeStreamingException
from dli.models import DictionaryModel
from dli.client.dli_client import DliClient
from unittest.mock import MagicMock

def test_sync(benchmark):
    client = MagicMock()
    item_count = 1000
    lock = threading.Lock()

    def returnList():
        def sideeffect():
            for i in range(item_count):
                yield {
                    'data': {
                        'attributes': {
                            'fields': [{str(i): i}]
                        }
                    },
                    'meta': {'total_count': item_count}
                }

        generator = sideeffect()

        def effect():
            with lock:
                return next(generator)

        return effect


    client.session.get().json.side_effect = returnList()

    model = benchmark.pedantic(lambda: DictionaryModel(
        {'attributes':{}, 'id': '123'}, client
    ), iterations=1)

    assert (len(model.fields)== item_count)

def test_dictionary_with_fields():
    client = MagicMock()
    model = DictionaryModel(
            {'attributes':{'fields': []}, 'id': '123'}, client
    )

    assert not client.session.get.called


def test_dictionary_fields():
    client = MagicMock()
    model = DictionaryModel(
        {'attributes':{}, 'id': '123'}, client
    )

    assert client.session.get.called


def test_dictionary_field_pagination():
    client = MagicMock()

    def _response():
        i = 0
        while True:
            yield {
                'meta': {'total_count': 3},
                'data': {
                    'attributes': {
                        'fields': [{
                            'test': i
                        }]
                    }
                }
            }
            i += 1

    client.session.get().json.side_effect = _response()

    model = DictionaryModel(
        {'attributes':{}, 'id': '123'}, client
    )

    assert len(model.fields) == 3


class TestClient(DliClient):
    def __init__(self):
        self._session = MagicMock()
        self._environment = MagicMock()

    @property
    def session(self):
        return self._session


@pytest.fixture
def client():
    yield TestClient()


class TestDataset:

    def test_dataset_instances_is_iterable(self, client):
        dataset = client.Dataset._from_v2_response({
            'data': {
                'id': '1234',
                'attributes': {
                    'location': {},
                }
            }
        })

        datafiles = dataset.instances.all()
        assert hasattr(datafiles, '__iter__')

    def test_dataset_instances_make_requests_on_iteration(self, client):
        client._session.get().json.side_effect = [
            {
                'properties': {'pages_count': 3},
                'entities': [{
                    'properties': {'datasetId': 1}
                }]
            },
            {
                'properties': {'pages_count': 3},
                'entities': [{
                    'properties': {'datasetId': 2}
                }]
            },
            {
                'properties': {'pages_count': 3},
                'entities': [{
                    'properties': {'datasetId': 3}
                }]
            },
        ]
        dataset = client.Dataset._from_v2_response({
            'data': {
                'id': '1234',
                'attributes': {
                    'location': {},
                }
            }
        })

        instances = list(dataset.instances.all())
        assert len(instances) == 3


class TestFileDownload:

    @pytest.fixture
    def instance_file(self, client):
        client._environment.consumption = 'consumption-test.local'

        instance = client.Instance(
            datafile_id='123'
        )

        client._session.get().json.return_value = {
            'data': [{
                'attributes': {
                    'path': 'prefix/test.001.csv',
                    'metadata': {}
                }
            }]
        }

        files = instance.files()
        file_ = files[0]

        client.session.reset_mock()

        client._session.get().raw.read.side_effect = [
            b'hello world',
            b''
        ]

        yield file_

    def test_instance_file_download_simple(self, client, instance_file):
        old_dir = os.path.abspath(os.curdir)

        with tempfile.TemporaryDirectory() as target_dest:
            os.chdir(os.path.abspath(target_dest))
            instance_file.download()
            with open(os.path.join(target_dest, 'prefix/test.001.csv')) as f:
                assert f.read() == 'hello world'

        os.chdir(old_dir)


    def test_instance_file_download_with_path(self, client, instance_file):
        with tempfile.TemporaryDirectory() as target_dest:
            instance_file.download(target_dest)
            with open(os.path.join(target_dest, 'prefix/test.001.csv')) as f:
                assert f.read() == 'hello world'


    def test_instance_file_download_non_existant_path(
        self, client, instance_file
    ):
        with tempfile.TemporaryDirectory() as target_dest:
            target_dest = os.path.join(target_dest, 'a/b/c/')
            instance_file.download(target_dest)
            with open(os.path.join(
                target_dest, 'prefix/test.001.csv'
            )) as f:
                assert f.read() == 'hello world'

    def test_instance_file_download_non_existant_file(
        self, client, instance_file
    ):
        with tempfile.TemporaryDirectory() as target_dest:
            target_dest = os.path.join(target_dest, 'a')
            instance_file.download(target_dest)
            with open(os.path.join(
                target_dest, 'prefix/test.001.csv'
            )) as f:
                assert f.read() == 'hello world'


    def test_instance_file_overwrites(
        self, client, instance_file
    ):
        with tempfile.TemporaryDirectory() as target_dest:
            target_dest = os.path.join(target_dest, 'a')
            instance_file.download(target_dest)
            with open(os.path.join(
                target_dest, 'prefix/test.001.csv'
            )) as f:
                assert f.read() == 'hello world'


        client.session.reset_mock()
        client._session.get().raw.read.side_effect = [
            b'brave new world',
            b''
        ]

        with tempfile.TemporaryDirectory() as target_dest:
            target_dest = os.path.join(target_dest, 'a')
            instance_file.download(target_dest)
            with open(os.path.join(
                target_dest, 'prefix/test.001.csv'
            )) as f:
                assert f.read() == 'brave new world'


class TestInstanceDownloadAll:

    @pytest.fixture
    def instance(self, client):
        client._environment.consumption = 'consumption-test.local'

        instance = client.Instance(
            datafile_id='123'
        )

        client._session.get().json.return_value = {
            'data': [{
                'attributes': {
                    'path': f's3://bucket/prefix/test.00{i}.csv',
                    'metadata': {}
                }
            } for i in range(3)
            ]
        }

        yield instance

    def test_instance_download_all(self, client, monkeypatch, instance):
        client._session.get().raw = io.BytesIO(b'abc')

        with tempfile.TemporaryDirectory() as target_dest:
            target_dest = os.path.join(target_dest, 'a')
            instance.download_all(target_dest)

            assert (
                sorted(os.listdir(os.path.join(target_dest, 'prefix'))) ==
                ['test.000.csv', 'test.001.csv', 'test.002.csv']
            )


class TestInstanceDataframe:

    @pytest.fixture
    def test_dataframe(self) -> pandas.DataFrame:
        # Rows:
        # 100 -> 205.5 kB (205,548 bytes) on disk in 0.44 seconds.
        # 10000 -> 9.2 MB (9,234,131 bytes) on disk in 0.67 seconds.

        max_rows = 10000
        # Max columns should match a worst case. For CDS Single Name Pricing
        # Sensitivities and Liquidity there are 164 columns.
        max_columns = 168

        num_column_types = 6

        # Seed the random number generator so that we can reproduce the output.
        numpy.random.seed(0)

        def bools_df():
            return pandas.DataFrame(
                numpy.random.choice(
                    [False, True],
                    size=(max_rows, int(max_columns / num_column_types))
                ),
                columns=[str(f'column_bool_{x}') for x in
                         range(int(max_columns / num_column_types))],
            )

        def ints_df():
            return pandas.DataFrame(
                numpy.random.randint(
                    low=0,
                    high=1000000,
                    size=(max_rows, int(max_columns / num_column_types))
                ),
                columns=[str(f'column_int_{x}') for x in
                         range(int(max_columns / num_column_types))],
            )

        def floats_df():
            return pandas.DataFrame(
                numpy.random.rand(
                    max_rows,
                    int(max_columns / num_column_types)),
                columns=[str(f'column_float_{x}') for x in
                         range(int(max_columns / num_column_types))],
            )

        def string_df():
            import pandas.util.testing
            return pandas.DataFrame(
                numpy.random.choice(
                    pandas.util.testing.RANDS_CHARS,
                    size=(max_rows, int(max_columns / num_column_types))
                ),
                columns=[str(f'column_str_{x}') for x in
                         range(int(max_columns / num_column_types))],
            )

        def dates_df():
            dates = pandas.date_range(start='1970-01-01', end='2020-01-01')

            return pandas.DataFrame(
                numpy.random.choice(
                    dates,
                    size=(max_rows, int(max_columns / num_column_types))
                ),
                columns=[str(f'column_date_{x}') for x in
                         range(int(max_columns / num_column_types))],
            )

        def datetimes_df():
            datetimes = pandas.date_range(start='1970-01-01', end='2020-01-01',
                                          freq='H')

            return pandas.DataFrame(
                numpy.random.choice(
                    datetimes,
                    size=(max_rows, int(max_columns / num_column_types))
                ),
                columns=[str(f'column_datetime_{x}') for x in
                         range(int(max_columns / num_column_types))],
            )

        df = pandas.concat(
            [bools_df(), ints_df(), floats_df(), string_df(), dates_df(),
             datetimes_df()],
            # Concat columns axis
            axis=1,
            copy=False
        )

        # Randomise the column order so the compression cannot optimise
        # easily based on types as this will mix float columns among the int
        # columns.
        random_column_order = df.columns.tolist()
        random.shuffle(random_column_order)
        df = df[random_column_order]

        assert df.shape[0] == max_rows
        assert df.shape[1] == max_columns

        return df

    @pytest.fixture
    def arrow_ipc_stream(self, test_dataframe):
        sink = pyarrow.BufferOutputStream()
        batch = pyarrow.RecordBatch.from_pandas(test_dataframe)
        writer = pyarrow.RecordBatchStreamWriter(sink, batch.schema)
        writer.write_batch(batch)
        # It's important the IPC stream is closed
        writer.close()
        return io.BytesIO(sink.getvalue().to_pybytes())


    @pytest.fixture
    def dataset(self, client):
        return client.Dataset._from_v2_response({
            'data': {
                'id': '1234',
                'attributes': {
                    'location': {},
                }
            }
        })

    def test_dataset_dataframe(self, benchmark, client, arrow_ipc_stream,
                               test_dataframe, dataset):

        dataset._client = MagicMock()
        dataset._client._environment.consumption = 'https://test/'
        dataset._client.session.get().raw = arrow_ipc_stream
        dataset._client.session.get().status_code = 200

        def _bench():
            # reset our fake socket
            arrow_ipc_stream.seek(0)
            return dataset._dataframe()

        # The benchmark code will run several times to get an average runtime.
        df = benchmark(_bench)

        # Check that we can read from the file that was written.
        pandas.testing.assert_frame_equal(test_dataframe, df)

    @pytest.mark.parametrize('value', ['1', 0])
    def test_dataframe_nrows_validation(self, client, arrow_ipc_stream,
                                        test_dataframe, value, dataset):
        dataset._client = MagicMock()
        dataset._client._environment.consumption = 'https://test/'
        dataset._client.session.get().raw = arrow_ipc_stream
        dataset._client.session.get().status_code = 200

        # Expected to pass.
        df = dataset._dataframe(value)
        # Check that we can read from the file that was written.
        pandas.testing.assert_frame_equal(test_dataframe, df)

    @pytest.fixture
    def partitions(self):
        return json.dumps({
            'a' : ['c', 'd'],
            'b' : ['e', 'f', 'g']
        })

    def test_dataset_partitions(self, client, partitions):
        dataset = client.Dataset._from_v2_response({
            'data': {
                'id': '1234',
                'attributes': {
                    'location': {},
                }
            }
        })

        dataset._client = MagicMock()
        dataset._client._environment.consumption = 'https://test/'
        dataset._client.session.get().status_code = 200
        dataset._client.session.get().content = partitions

        msg = dataset._partitions()
        assert(msg == json.loads(partitions))

    def test_dataframe_handle_errors(self, client, arrow_ipc_stream,
                                     test_dataframe, dataset):
        error_msg = json.dumps({
            'status': 400,
        }).encode('utf')

        arrow_ipc_stream.seek(0, 2)
        arrow_ipc_stream.write(error_msg)
        arrow_ipc_stream.seek(0)

        dataset._client = MagicMock()
        dataset._client._environment.consumption = 'https://test/'
        dataset._client.session.get().raw = arrow_ipc_stream
        dataset._client.session.get().status_code = 200

        with pytest.raises(DataframeStreamingException) as exc:
            dataset._dataframe(1)
