#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#


import abc
from typing import Iterable
from fate_arch.common.log import getLogger
from fate_arch.common import StorageTableMetaType
from arch.api.utils.core_utils import current_timestamp, serialize_b64, deserialize_b64
from fate_arch.db.db_models import DB, StorageTableMeta
from arch.api.utils import log_utils
from fate_arch.computing import ComputingType
from fate_arch.abc import StorageTableABC

logger = log_utils.getLogger()

MAX_NUM = 10000

LOGGER = getLogger()


class StorageTableBase(StorageTableABC):
    def save_as(self, name, namespace, partition=None, schema=None, **kwargs):
        if schema:
            self.save_meta(name=name, namespace=namespace, schema=schema, partitions=partition)

    @abc.abstractmethod
    def close(self):
        pass

    def destroy(self):
        # destroy schema
        self.destroy_meta()
        # subclass method needs do: super().destroy()

    """
    meta utils
    """

    def get_meta(self, _type=StorageTableMetaType.SCHEMA, name=None, namespace=None):
        if not name and not namespace:
            name = self.get_name()
            namespace = self.get_namespace()
        with DB.connection_context():
            table_metas = StorageTableMeta.select().where(StorageTableMeta.f_name == name,
                                                          StorageTableMeta.f_namespace == namespace)
            meta = None
            if table_metas:
                table_meta = table_metas[0]
                try:
                    if _type == StorageTableMetaType.SCHEMA:
                        meta = deserialize_b64(table_meta.f_schema)
                    elif _type == StorageTableMetaType.PART_OF_DATA:
                        meta = deserialize_b64(table_meta.f_part_of_data)
                    elif _type == StorageTableMetaType.COUNT:
                        meta = table_meta.f_count
                    elif _type == StorageTableMetaType.PARTITIONS:
                        meta = table_meta.f_partitions
                except:
                    meta = None
        return meta

    def save_meta(self, schema=None, name=None, namespace=None, party_of_data=None, count=0, partitions=1):
        # save metas to mysql
        if not schema:
            schema = {}
        if not party_of_data:
            party_of_data = []
        if not name or not namespace:
            name = self.get_name()
            namespace = self.get_namespace()
        with DB.connection_context():
            table_metas = StorageTableMeta.select().where(StorageTableMeta.f_name == name,
                                                          StorageTableMeta.f_namespace == namespace)
            if table_metas:
                # save schema info
                table_meta = table_metas[0]
                if table_meta.f_schema:
                    _schema_data = deserialize_b64(table_meta.f_schema)
                _schema_data.update(schema)
                table_meta.f_schema = serialize_b64(_schema_data, to_str=True)
                # save data
                if party_of_data:
                    _f_part_of_data = deserialize_b64(table_meta.f_part_of_data)
                    if len(_f_part_of_data) < 100:
                        _f_part_of_data.extend(party_of_data[:(100 - len(_f_part_of_data))])
                        table_meta.f_part_of_data = serialize_b64(party_of_data[:100], to_str=True)
                # save count
                if count:
                    table_meta.f_count = count
                if partitions:
                    table_meta.f_partitions = partitions
            else:
                raise Exception('please create table {} {} before useing'.format(name, namespace))
            table_meta.f_update_time = current_timestamp()
            table_meta.save()

    def destroy_meta(self):
        try:
            with DB.connection_context():
                StorageTableMeta \
                    .delete() \
                    .where(StorageTableMeta.f_name == self.get_name(),
                           StorageTableMeta.f_namespace == self.get_namespace()) \
                    .execute()
        except Exception as e:
            LOGGER.error("delete_table_meta {}, {}, exception:{}.".format(self.get_namespace(), self.get_name(), e))