# This file is part of AdMincer,
# Copyright (C) 2019 eyeo GmbH
#
# AdMincer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# AdMincer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with AdMincer. If not, see <http://www.gnu.org/licenses/>.

"""Tests for slicing."""

import pytest

import admincer.index as idx
import admincer.slice as slc

from conftest import image_to_chars, SLICE_STRINGS


SLICE_EXPECT = {}

SLICE_EXPECT['default'] = {
    '0-0.png': {
        'chars': SLICE_STRINGS[0],
        'regions': [(0, 0, 10, 10, 'r1'), (20, 10, 30, 30, 'r2')],
    },
    '1-0.png': {
        'chars': SLICE_STRINGS[1],
        'regions': [],
    },
    '2-0.png': {
        'chars': SLICE_STRINGS[2][:9],
        'regions': [(0, 0, 10, 10, 'r1'), (20, 0, 30, 20, 'r3')],
    },
    '2-10.png': {
        'chars': SLICE_STRINGS[2][3:],
        'regions': [(20, 0, 30, 10, 'r3'), (20, 20, 30, 30, 'r1')],
    },
    '3-0.png': {
        'chars': SLICE_STRINGS[3][:9],
        'regions': [(20, 10, 30, 30, 'r1')],
    },
    '3-10.png': {
        'chars': SLICE_STRINGS[3][3:12],
        'regions': [(20, 0, 30, 20, 'r1')],
    },
    '3-20.png': {
        'chars': SLICE_STRINGS[3][6:15],
        'regions': [(20, 0, 30, 10, 'r1')],
    },
    '3-30.png': {
        'chars': SLICE_STRINGS[3][9:18],
        'regions': [],
    },
    '3-40.png': {
        'chars': SLICE_STRINGS[3][12:21],
        'regions': [(20, 20, 30, 30, 'r2')],
    },
    '3-50.png': {
        'chars': SLICE_STRINGS[3][15:],
        'regions': [(20, 10, 30, 30, 'r2')],
    },
}

SLICE_EXPECT['no_empty'] = {
    name: SLICE_EXPECT['default'][name]
    for name in [
        '0-0.png',
        '2-0.png', '2-10.png',
        '3-0.png', '3-10.png', '3-20.png', '3-40.png', '3-50.png',
    ]
}

SLICE_EXPECT['no_empty_80'] = {
    name: SLICE_EXPECT['default'][name]
    for name in ['0-0.png', '2-0.png', '3-0.png', '3-10.png', '3-50.png']
}
SLICE_EXPECT['no_empty_80']['2-10.png'] = {
    'chars': SLICE_STRINGS[2][3:],
    'regions': [(20, 20, 30, 30, 'r1')],
}

SLICE_EXPECT['step_30'] = {
    name: SLICE_EXPECT['default'][name]
    for name in ['0-0.png', '1-0.png', '2-0.png', '3-0.png', '3-30.png']
}


def check_results(results, expect):
    """Compare the contents of target index with expectations."""
    assert set(results) == set(expect)
    for img_name in results:
        image = results.load_image(img_name)
        assert image.size == (30, 30)
        assert image_to_chars(image, 10, 3, 3) == expect[img_name]['chars']
        assert results[img_name] == expect[img_name]['regions']


@pytest.mark.parametrize('expect_key,kw', [
    ('default', {}),
    ('no_empty', {'no_empty': True}),
    ('no_empty_80', {'no_empty': True, 'min_part': 0.8}),
    ('step_30', {'step': 30}),
])
def test_slice(slice_source, tmpdir, expect_key, kw):
    """Test slice sub-command."""
    target = tmpdir.mkdir('output')
    source = idx.reg_index(str(slice_source))
    output = idx.reg_index(str(target))
    slc.slice_all(source, output, **kw)
    check_results(output, SLICE_EXPECT[expect_key])


def test_double_slice_fail(slice_source, tmpdir):
    target = tmpdir.mkdir('output')
    source = idx.reg_index(str(slice_source))
    output = idx.reg_index(str(target))
    output['0-0.png'] = []
    with pytest.raises(KeyError):
        slc.slice_all(source, output)
