# Copyright (c) 2022 Jared Rathbun and Katie O'Neil. 
#
# This file is part of STEM Data Dashboard.
# 
# STEM Data Dashboard is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free 
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# STEM Data Dashboard is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more 
# details.
#
# You should have received a copy of the GNU General Public License along with 
# STEM Data Dashboard. If not, see <https://www.gnu.org/licenses/>.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from app.models import *
import pytest


@pytest.mark.parametrize(
    'class_str, expected', [
        ('FR', ClassEnum.FRESHMAN),
        ('SO', ClassEnum.SOPHOMORE),
        ('JR', ClassEnum.JUNIOR),
        ('SR', ClassEnum.SENIOR),
        ('XX', ClassEnum.FRESHMAN)
], indirect=False)
def test_parse_class(class_str, expected):
    try:
        res = ClassEnum.parse_class(class_str)

        assert (res is not None)
        assert (expected == res)
    except InvalidClassException as ex:
        assert (class_str == 'XX')
        assert (expected == ClassEnum.FRESHMAN)