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

"""CLI entry point."""

import argparse
import logging
import os
import sys

import admincer.index as idx
import admincer.extract as ex
import admincer.find as fnd
import admincer.place as pl
import admincer.slice as slc
import admincer.util as util

__all__ = ['main']

parser = argparse.ArgumentParser(description='Batch image editor')
subparsers = parser.add_subparsers(help='sub-command help')


def command(*args, **kw):
    """Return a decorator for command functions.

    This decorator will create a subparser for the command function passing
    all the arguments of `command()` to `.add_parser()`. If no name and help
    are provided for the command, they will be taken from the function name
    and docstring (only the first line of the docstring is used) of the
    decorated function.

    """

    def decorator(func):
        nonlocal args, kw

        if not args:
            args = [func.__name__]
        if 'help' not in kw:
            kw['help'] = func.__doc__.split('\n')[0]

        cmd = subparsers.add_parser(*args, **kw)
        for arg in reversed(getattr(func, '__args__', [])):
            cmd.add_argument(*arg['args'], **arg['kw'])
        cmd.set_defaults(func=func)

        return func

    return decorator


def arg(*args, **kw):
    """Return a decorator that will add an argument to a command function.

    All parameters passed to the decorator will be passed to `.add_argument()`
    call of the subparser corresponding to the decorated function.

    """

    def decorator(func):
        nonlocal args, kw

        if not hasattr(func, '__args__'):
            func.__args__ = []
        func.__args__.append({'args': args, 'kw': kw})

        return func

    return decorator


def verbose_arg():
    """Return a decorator for --verbose option."""
    return arg('--verbose', '-v', action='count', default=0,
               help='Output markdown-formatted log of actions to stderr')


def parse_xy_options(argitems, multivalue=False):
    """Collect options of the form x=y or x=y1:y2 into a list of tuples."""
    ret = []

    for s in argitems:
        if '=' in s:
            x, y = s.split('=')
        else:
            x, y = None, s

        if multivalue:
            y = y.split(':')

        ret.append((x, y))

    return ret


def take(n, iterable):
    """Return an iterable with n first items of the original iterable."""
    for i, item in enumerate(iterable):
        yield item
        if i >= n - 1:
            return


@command(aliases=['pl'])
@arg('source', help='Directory for source images and region maps')
@arg('target', help='Directory for output images')
@arg('--fragments', '-f', action='append', default=[],
    metavar='REGION-TYPE=DIR[:DIR...]',
    help='Add fragment directory/ies for specific region types')
@arg('--resize-mode', '-r', action='append', default=[],
    metavar='REGION-TYPE=MODE',
    help='Resize mode for region types: "scale" (default), "pad" or "crop"')
@arg('--count', '-n', default=1, type=int, help='Number of images to generate')
@verbose_arg()
def place(args):
    """Place fragments into designated regions of source images."""
    frag_dirs = parse_xy_options(args.fragments, multivalue=True)

    logging.info('# Place')
    logging.info('- source dir: %s', args.source)
    logging.info('- fragments:')
    for rt, dirs in frag_dirs:
        logging.info('  - %s: %s', rt, ', '.join(dirs))
    logging.info('- target dir: %s', args.target)

    reg_index = idx.reg_index(args.source)
    frag_indices = [(rt, map(idx.frag_index, dirs)) for rt, dirs in frag_dirs]
    resize_modes = dict(parse_xy_options(args.resize_mode))
    recipe_gen = pl.gen_recipes(reg_index, frag_indices, resize_modes)
    recipes = take(args.count, recipe_gen)
    pl.render_recipes(reg_index, recipes, args.target)


@command(aliases=['sl'])
@arg('source', help='Directory for source images and region maps')
@arg('target', help='Directory for output images and region maps')
@arg('--step', '-s', default=10, type=int,
     help='Number of pixels to shift the viewport between the slices')
@arg('--min-part', '-p', default=50, type=int,
     help='Minimal percentage of the region in the slice')
@arg('--no-empty', '-n', action='store_true',
     help='Skip slices without regions')
@verbose_arg()
def slice(args):
    """Cut viewport screenshots from full page screenshots."""

    logging.info('# Slice')
    logging.info('- source dir: %s', args.source)
    logging.info('- target dir: %s', args.target)
    logging.info('- slicing step: %d pixels', args.step)
    logging.info('- include regions that overlap the slice by at least %d%%',
                 args.min_part)
    if args.no_empty:
        logging.info('- skip slices with no regions')

    src_index = idx.reg_index(args.source)
    tgt_index = idx.reg_index(args.target, ensure_dir=True)

    slc.slice_all(
        src_index, tgt_index,
        step=args.step,
        min_part=args.min_part / 100,
        no_empty=args.no_empty,
    )


@command(aliases=['ex'])
@arg('source', help='Directory for source images')
@arg('--target-dir', '-t', action='append', default=[],
     metavar='REGION-TYPE=DIR',
     help='Target directory for extracting regions of specific type')
@verbose_arg()
def extract(args):
    """Extract the contents of fragments to directories by type."""
    target_dirs = sorted(dict(parse_xy_options(args.target_dir)).items())

    logging.info('# Extract')
    logging.info('- source dir: %s', args.source)
    logging.info('- target dirs:')

    for rt, d in target_dirs:
        logging.info('  - %s: %s', rt, d)

    reg_index = idx.reg_index(args.source)
    for region_type, target_dir in target_dirs:
        logging.info('## Type: %s to: %s', region_type, target_dir)
        os.makedirs(target_dir, exist_ok=True)
        regions = ex.extract_regions(reg_index, region_type)
        for i, (box, region) in enumerate(regions):
            out_name = '{:05d}.png'.format(i)
            out_path = os.path.join(target_dir, out_name)
            region.save(out_path)
            logging.info('- region %s to: %s', util.format_box(box), out_name)


@command(aliases=['f'])
@arg('dir', help='Directory in which to search')
@arg('--fragment', '-f', action='append', default=[],
     metavar='PATH[:T]', type=util.fragment,
     help='Look for fragments similar to specific image')
@arg('--region', '-r', action='append', default=[],
     metavar='TYPE:WxH[:T]', type=util.region,
     help='Look for regions of specific types and sizes')
def find(args):
    """Find images with regions of specific types and sizes."""
    dir_index = idx.some_index(args.dir)
    queries = args.region + args.fragment
    if not queries:
        sys.exit('find requires at least one of: -r/--region, -f/--fragment')
    for found in fnd.find(dir_index, queries):
        print(found)


def _configure_logging(args):
    """Configure logging."""
    verbosity = getattr(args, 'verbose', 0)

    if verbosity == 1:
        log_level = logging.INFO
    elif verbosity >= 2:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(stream=sys.stderr, level=log_level,
                        format='%(message)s')


def main():
    """Run the CLI."""
    args = parser.parse_args()
    if callable(getattr(args, 'func', None)):
        _configure_logging(args)
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)
