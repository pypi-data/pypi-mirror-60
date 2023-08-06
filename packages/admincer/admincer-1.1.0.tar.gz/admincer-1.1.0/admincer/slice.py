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

"""Slice full page screenshots into viewport screenshots."""

import logging
import os

import admincer.util as util


def _slice_boxes(width, height, step):
    """Yield coordinates of possible slices."""
    if width >= height:
        yield (0, 0, width, height)
        return
    for y_offset in range(0, height - width + 1, step):
        yield (0, y_offset, width, y_offset + width)


def _intersect(box1, box2):
    """Compute intersection of two boxes."""
    x0 = max(box1[0], box2[0])
    y0 = max(box1[1], box2[1])
    x1 = min(box1[2], box2[2])
    y1 = min(box1[3], box2[3])

    if x0 >= x1 or y0 >= y1:
        return None

    return (x0, y0, x1, y1) + box1[4:]


def _box_area(box):
    """Compute the area of the box."""
    x0, y0, x1, y1 = box[:4]
    return (x1 - x0) * (y1 - y0)


def _relative_to(box, region):
    """Translate region coordinates to be relative to box."""
    x_org, y_org = box[:2]
    x0, y0, x1, y1 = region[:4]
    return (x0 - x_org, y0 - y_org, x1 - x_org, y1 - y_org) + region[4:]


def _crop_regions(regions, box, min_part):
    """Crop regions to box.
    
    Discards the ones of which less than min_part remains. Translates the
    remaining ones so that their coordinates are relative to the box.
    """
    result = []

    for region in regions:
        intersected = _intersect(region, box)
        if intersected is None:
            continue
        if _box_area(intersected) / _box_area(region) < min_part:
            continue
        result.append(_relative_to(box, intersected))

    return result


def slice_all(src_index, tgt_index, step=10, min_part=0.5, no_empty=False):
    """Slice images with regions into square sub-images.

    Note: at the moment only vertical slicing of tall images is supported.

    Parameters
    ----------
    src_index : RegIndex
        Source of images and region maps are taken.
    tgt_index : RegIndex
        Target index (and directory) for the output images and region maps.
    step : int
        The distance to shift the viewport between slices (in pixels).
    min_part : float
        If a region overlaps the viewport by this percentage, it will be
        included in the slice (appropriately cropped and translated).
    no_empty : bool
        If this is True, slices without regions will be skipped.

    Raises
    ------
    KeyError
        If tgt_index already contains any of the slices.

    """
    for image_name, regions in sorted(src_index.items()):
        image = src_index.load_image(image_name)
        size = image.size
        logging.info('## %s (%dx%d)', image_name, *size)
        width, height = image.size

        for box in _slice_boxes(width, height, step):
            slice_regions = _crop_regions(regions, box, min_part)
            if no_empty and slice_regions == []:
                continue
            base_name = os.path.splitext(image_name)[0]
            slice_name = '{}-{}.png'.format(base_name, box[1])
            slice_image = image.crop(box)

            logging.info('### slice %s', util.format_box(box))
            if slice_regions:
                for region in slice_regions:
                    logging.info('- region %s type %s',
                                 util.format_box(region[:4]), region[4])
            else:
                logging.info('- no regions')
            logging.info('- saved as %s', slice_name)

            tgt_index.add_image(slice_name, slice_image, slice_regions)
