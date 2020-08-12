
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
from fate_arch.computing import ComputingType
from fate_arch.common.address import StandaloneAddress, EggRollAddress, HDFSAddress, MysqlAddress





class Relationship(object):
    CompToStore = {
        ComputingType.STANDALONE: [StorageEngine.STANDALONE],
        ComputingType.EGGROLL: [StorageEngine.EGGROLL],
        ComputingType.SPARK: [StorageEngine.HDFS]
    }
    EngineToAddress = {
        StorageEngine.STANDALONE: StandaloneAddress,
        StorageEngine.EGGROLL: EggRollAddress,
        StorageEngine.HDFS: HDFSAddress,
        StorageEngine.MYSQL: MysqlAddress
    }



