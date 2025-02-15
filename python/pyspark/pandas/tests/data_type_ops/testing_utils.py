#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime
import decimal
from distutils.version import LooseVersion

import numpy as np
import pandas as pd

import pyspark.pandas as ps
from pyspark.pandas.typedef import extension_dtypes

from pyspark.pandas.typedef.typehints import (
    extension_dtypes_available,
    extension_float_dtypes_available,
    extension_object_dtypes_available,
)

if extension_dtypes_available:
    from pandas import Int8Dtype, Int16Dtype, Int32Dtype, Int64Dtype

if extension_float_dtypes_available:
    from pandas import Float32Dtype, Float64Dtype

if extension_object_dtypes_available:
    from pandas import BooleanDtype, StringDtype


class TestCasesUtils(object):
    """A utility holding common test cases for arithmetic operations of different data types."""

    @property
    def numeric_psers(self):
        dtypes = [np.float32, float, int, np.int32]
        sers = [pd.Series([1, 2, 3], dtype=dtype) for dtype in dtypes]
        sers.append(pd.Series([decimal.Decimal(1), decimal.Decimal(2), decimal.Decimal(3)]))
        return sers

    @property
    def numeric_pssers(self):
        return [ps.from_pandas(pser) for pser in self.numeric_psers]

    @property
    def decimal_withnan_pser(self):
        return pd.Series([decimal.Decimal(1.0), decimal.Decimal(2.0), decimal.Decimal(np.nan)])

    @property
    def decimal_withnan_psser(self):
        return ps.from_pandas(self.decimal_withnan_pser)

    @property
    def float_withnan_pser(self):
        return pd.Series([1, 2, np.nan], dtype=float)

    @property
    def float_withnan_psser(self):
        return ps.from_pandas(self.float_withnan_pser)

    @property
    def numeric_pser_psser_pairs(self):
        return zip(self.numeric_psers, self.numeric_pssers)

    @property
    def numeric_withnan_pser_psser_pairs(self):
        return zip(
            self.numeric_psers + [self.decimal_withnan_pser, self.float_withnan_pser],
            self.numeric_pssers + [self.decimal_withnan_psser, self.float_withnan_psser],
        )

    @property
    def non_numeric_psers(self):
        psers = {
            "string": pd.Series(["x", "y", "z"]),
            "datetime": pd.to_datetime(pd.Series([1, 2, 3])),
            "bool": pd.Series([True, True, False]),
            "date": pd.Series(
                [datetime.date(1994, 1, 1), datetime.date(1994, 1, 2), datetime.date(1994, 1, 3)]
            ),
            "categorical": pd.Series(["a", "b", "a"], dtype="category"),
        }
        return psers

    @property
    def non_numeric_pssers(self):
        pssers = {}

        for k, v in self.non_numeric_psers.items():
            pssers[k] = ps.from_pandas(v)
        return pssers

    @property
    def non_numeric_pser_psser_pairs(self):
        return zip(self.non_numeric_psers.values(), self.non_numeric_pssers.values())

    @property
    def pssers(self):
        return self.numeric_pssers + list(self.non_numeric_pssers.values())

    @property
    def psers(self):
        return self.numeric_psers + list(self.non_numeric_psers.values())

    @property
    def pser_psser_pairs(self):
        return zip(self.psers, self.pssers)

    @property
    def string_extension_dtype(self):
        return ["string", StringDtype()] if extension_object_dtypes_available else []

    @property
    def object_extension_dtypes(self):
        return (
            ["boolean", "string", BooleanDtype(), StringDtype()]
            if extension_object_dtypes_available
            else []
        )

    @property
    def fractional_extension_dtypes(self):
        return (
            ["Float32", "Float64", Float32Dtype(), Float64Dtype()]
            if extension_float_dtypes_available
            else []
        )

    @property
    def integral_extension_dtypes(self):
        return (
            [
                "Int8",
                "Int16",
                "Int32",
                "Int64",
                Int8Dtype(),
                Int16Dtype(),
                Int32Dtype(),
                Int64Dtype(),
            ]
            if extension_dtypes_available
            else []
        )

    @property
    def extension_dtypes(self):
        return (
            self.object_extension_dtypes
            + self.fractional_extension_dtypes
            + self.integral_extension_dtypes
        )

    def check_extension(self, psser, pser):
        """
        Compare `psser` and `pser` of numeric ExtensionDtypes.

        This utility is to adjust an issue for comparing numeric ExtensionDtypes in specific
        pandas versions. Please refer to https://github.com/pandas-dev/pandas/issues/39410.
        """
        if LooseVersion("1.1") <= LooseVersion(pd.__version__) < LooseVersion("1.2.2"):
            self.assert_eq(psser, pser, check_exact=False)
            self.assertTrue(isinstance(psser.dtype, extension_dtypes))
        else:
            self.assert_eq(psser, pser)
