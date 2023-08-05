import concurrent
import os
import warnings
import contextlib
import email.parser
import shutil
import multiprocessing
from typing import List

import pyarrow
import humps
import json

from pathlib import Path
from urllib.parse import urljoin, urlparse
from requests_toolbelt.multipart.decoder import MultipartDecoder
from collections.abc import Mapping, Iterable
from collections import UserDict
from concurrent.futures import ThreadPoolExecutor

from dli.client.components.urls import dataset_urls, consumption_urls
from dli.client.exceptions import DataframeStreamingException

THREADS = multiprocessing.cpu_count()


class AttributesDict(UserDict):

    def __init__(self, *args, **kwargs):
        # recurisvely provide the rather silly attribute
        # access
        data = {}

        for arg in args:
            data.update(arg)

        data.update(**kwargs)

        for key, value in data.items():
            if isinstance(value, Mapping):
                self.__dict__[key] = AttributesDict(value)
            else:
                self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def _asdict(self, *args, **kwargs):
        warnings.warn(
            'This method is deprecated as it returns itself.',
            DeprecationWarning
        )

        return self

    def __repr__(self):
        attributes = ' '.join([
            '{}={}'.format(k, v) for k,v in self.__dict__.items()
            if not k.startswith('_')
        ])

        return "{}({})".format(self.__class__.__name__, attributes)


class SampleData:
    def __init__(self, parent):
        self._parent = parent
        self._client = parent._client

    def schema(self):
        """
        Returns the schema data and first rows of sample data.

        :returns: attributes dictionary
        """
        response = self._client.session.get(
            dataset_urls.v2_sample_data_schema.format(id=self._parent.id)
        )

        return AttributesDict(**response.json()['data']['attributes'])

    @contextlib.contextmanager
    def file(self):
        """
        Provides a file like object containing sample data.

        Example usage:

        .. code-block:: python

            dataset = self.client.get_dataset(dataset_id)
            with dataset.sample_data.file() as f:
                dataframe = pandas.read_csv(f)
        """
        response = self._client.session.get(
            dataset_urls.v2_sample_data_file.format(id=self._parent.id),
            stream=True
        )
        # otherwise you get raw secure
        response.raw.decode_content = True
        yield response.raw
        response.close()


class FileModel(AttributesDict):

    @contextlib.contextmanager
    def open(self):
        response = self._client.session.get(
            urljoin(
                self._client._environment.consumption,
                consumption_urls.consumption_download.format(
                    id=self.datafile_id,
                    path=self.path
                )
            ),
            stream=True
        )
        # otherwise you get raw secure
        response.raw.decode_content = True
        yield response.raw
        response.close()

    def download(self, to='./'):
        to = os.path.join(
            to, urlparse(self.path).path.lstrip('/')
        )

        directory, _ = os.path.split(to)
        os.makedirs(directory, exist_ok=True)

        with self.open() as download_stream:
            with open(to, 'wb') as target_download:
                # copyfileobj is just a simple buffered
                # file copy function with some sane
                # defaults and optimisations.
                shutil.copyfileobj(
                    download_stream, target_download
                )

        return to


class InstanceModel(AttributesDict):

    def __init__(self, **kwargs):
        # Ignore the datafile's files
        kwargs.pop('files', [])
        super().__init__(**kwargs)

    def files(self):
        response = self._client.session.get(
            urljoin(
                self._client._environment.consumption,
                consumption_urls.consumption_manifest.format(
                    id=self.datafile_id
                )
            )
        )

        return [
            self._client.File(
                datafile_id=self.datafile_id,
                **d['attributes']
            )

            for d in response.json()['data']
        ]

    @classmethod
    def _from_v1_entity(cls, entity):
        properties = humps.decamelize(entity['properties'])
        return cls(**properties)

    def download_all(self, to='./'):
        files = self.files()

        def _download(file_):
            return file_.download(to=to)

        threads = min(THREADS, len(files))
        with ThreadPoolExecutor(max_workers=threads) as executor:
            return list(executor.map(_download, files))


class _DliV1InstancePagination(Iterable):
    def __init__(self, dataset_id, page=1):
        self.page = page
        self.dataset_id = dataset_id

    def _request(self):
        return self._client.session.get(
            dataset_urls.datafiles.format(id=self.dataset_id),
            params={
                'page_size': 100,
                'page': self.page,
            }
        ).json()

    def __iter__(self):
        while True:
            datafiles = self._request()
            for entity in datafiles['entities']:
                yield self._client.Instance._from_v1_entity(entity)

            self.page += 1

            if datafiles['properties']['pages_count'] < self.page:
                break


class InstancesCollection(AttributesDict):

    def __init__(self, dataset=None):
        self._dataset = dataset

    def latest(self):
        response = self._client.session.get(
            dataset_urls.latest_datafile.format(id=self._dataset.id)
        ).json()

        return self._client.Instance._from_v1_entity(response)

    def all(self):
        return self._client.DliV1DatafilePagination(
            self._dataset.id
        )


class DatasetModel(AttributesDict):

    @property
    def sample_data(self):
        return SampleData(self)

    @property
    def id(self):
        return self.dataset_id

    def __init__(self, **kwargs):
        self.instances = self._client.InstancesCollection(dataset=self)
        super().__init__(**kwargs,)

    @classmethod
    def _from_v2_response(cls, response_json):
        return cls._construct_dataset_using(
            response_json['data']['attributes'], response_json['data']['id']
        )

    @classmethod
    def _from_v2_list_response(cls, response_json):
        return [
            cls._construct_dataset_using(
                dataset['attributes'], dataset['id']
            )
            for dataset in response_json['data']
        ]

    @classmethod
    def _construct_dataset_using(cls, attributes, dataset_id):
        location = attributes.pop('location')
        # In the interests of not breaking backwards compatability.
        # TODO find a way to migrate this to the new nested API.
        if not location:
            location = None
        else:
            location = location[next(iter(location))]

        return cls(
            **attributes,
            location=location,
            dataset_id=dataset_id
        )

    def _dataframe(self, nrows=None, partitions: List[str] = None, raise_=True):
        """
        Returns a pandas dataframe of the dataset.

        :param int nrows: The max number of rows to return
        :param List[str] partitions: A dict of filters (partitions) to
            apply to the dataframe request in the form of: ["a=12","b>20190110"]
            - will permit whitespace and equality operators [<=, <, =, >, >=]
        :param bool raise_: raise if the dataframe stream stopped prematurely
        """
        params = {}

        if nrows is not None:
            params['filter[nrows]'] = nrows

        if partitions is not None:
            params['filter[partitions]'] = partitions

        dataframe_url = urljoin(
            self._client._environment.consumption,
            consumption_urls.consumption_dataframe.format(id=self.id)
        )

        response = self._client.session.get(
            dataframe_url, stream=True,
        )

        if response and response.status_code != 200:
            # todo - improve error/logging
            raise Exception(f"Bad response with error code {response.status_code}")

        # Don't decode content. We would like to keep the raw
        # probably gziped steam. Otherwise the stream.read(n) will
        # return a string of length != n.
        response.raw.decode_content = False

        native_file = pyarrow.PythonFile(response.raw, mode='rb')

        # If the response is gzip we need to wrap the
        # encoding in a decompressor.
        if response.headers['Content-Encoding'] == 'gzip':
            native_file = pyarrow.CompressedInputStream(
                native_file, 'gzip'
            )

        reader = pyarrow.ipc.open_stream(native_file)
        dataframe = reader.read_pandas()

        # The pyarrow buffered stream reader stops once it
        # reaches the end of the IPC message. Afterwards we
        # get the rest of the data which contains the summary
        # of what we've downloaded including an error message.
        summary_string = native_file.read()
        if summary_string:
            summary = json.loads(summary_string)

            if (summary['status'] >= 400):
                exception = DataframeStreamingException(
                    summary, dataframe_url
                )

                # Optionally ignore bad data
                if raise_:
                    raise exception
                else:
                    warnings.warn(
                        str(exception),
                        UserWarning
                    )

        return dataframe

    def _partitions(self):
        """
        Retrieves the list of available partitions for a given dataset
        """
        response = self._client.session.get(
            urljoin(
                self._client._environment.consumption,
                consumption_urls.consumption_partitions.format(id=self.id)
            )
        )

        msg = None
        if response and response.status_code == 200:
            msg = json.loads(response.content)
            return msg
        else:
            # todo - improve error/logging
            raise Exception(f"Bad response with error code {response.status_code}")


class Field(AttributesDict):
    """
    Represents a dictionary Field. Exists
    to provide a basic class with a name.
    """


class DictionaryModel(AttributesDict):

    @property
    def id(self):
        return self.dictionary_id

    @property
    def schema_id(self):
        warnings.warn(
            'This method is deprecated. Please use DictionaryModel.id',
            DeprecationWarning
        )
        return self.id

    def _get_fields(self):
        fields = []
        tp = ThreadPoolExecutor(max_workers=10)

        def _get_page(page=1):
            resp = self._client.session.get(
                dataset_urls.dictionary_fields.format(id=self.id),
                params={'page': page}
            ).json()

            fields.extend(resp['data']['attributes']['fields'])
            return resp

        fields_json = _get_page(1)
        total_pages = fields_json['meta']['total_count'] + 1
        # We can use a with statement to ensure threads are cleaned up promptly
        rng = range(2, total_pages)
        list(tp.map(_get_page, rng))
        tp.shutdown(wait=True)

        return fields

    @property
    def fields(self):
        if 'fields' not in self.__dict__:
            self.__dict__['fields'] = self._get_fields()

        return self.__dict__['fields']

    def __init__(self, json, client=None, fetch_fields=True):
        self._client = client
        super().__init__(
            json['attributes'],
            dictionary_id=json['id'],
        )

        if fetch_fields and 'fields' not in json['attributes']:
            # DLIv2 doesn't put the fields on the attributes
            # when getting
            self.__dict__['fields'] = [
                Field(f) for f in self._get_fields()
            ]


class AccountModel(AttributesDict):
    @classmethod
    def _from_v2_response(cls, data):
        id_ = data.pop('id')
        attributes = data.pop('attributes')
        attributes.pop('ui_settings', None)
        return cls(id=id_, **attributes)
