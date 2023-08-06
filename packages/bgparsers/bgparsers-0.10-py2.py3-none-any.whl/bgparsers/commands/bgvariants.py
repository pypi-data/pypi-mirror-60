import functools
import logging
import os
import sys
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from os.path import isdir, join, basename, dirname, exists

import click
from tqdm import tqdm

from bgparsers import selector
from bgparsers.commands.tasks.cat import run as task_cat
from bgparsers.commands.tasks.count import run as task_count
from bgparsers.commands.tasks.preprocess import run as task_preprocess
from bgparsers.commands.tasks.script import run as task_script
from bgparsers.utils import dequote

logger = logging.getLogger("bgparsers")


def __preprocess_chunk(file, chunk):
    return join(dirname(file), "bgvariants", "preprocess", basename(file), "c{:06d}.bgvars.xz".format(chunk))


def __input_to_selection(input):
    if len(input) == 0:
        input = (os.getcwd(),)

    selection = []
    for i in input:
        selection += (list(selector.find(i)) if isdir(i) else [(i, None)])

    # TODO Implement this at selector
    selection_chunks = []
    for file, ann in selection:
        chunk = 0
        chunk_file = __preprocess_chunk(file, chunk)
        if exists(chunk_file):
            while exists(chunk_file):
                selection_chunks.append((chunk_file, ann))
                chunk += 1
                chunk_file = __preprocess_chunk(file, chunk)
        else:
            selection_chunks.append((file, ann))

    return selection_chunks


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option('--debug', help='Show debug messages.', is_flag=True)
@click.version_option()
def cli(debug):
    # Configure the logging
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S')
    logging.getLogger("bgparsers").setLevel(logging.DEBUG if debug else logging.INFO)
    logger.debug(sys.argv)


@click.command(short_help='Create a preprocessed version of the input file/folder.')
@click.argument('input', type=click.Path(exists=True), nargs=-1)
@click.option('--force', help='Overwrite files if exists.', is_flag=True)
@click.option('--cores', help='Maximum processes to run in parallel.', type=click.INT, default=os.cpu_count())
def preprocess(input, force, cores):
    selection = __input_to_selection(input)
    pool_method = Pool if len(selection) > 1 and cores > 1 else ThreadPool

    with pool_method(cores) as pool:
        task = functools.partial(task_preprocess, force=force, exist_ok=True)
        for output_file in tqdm(pool.imap_unordered(task, selection), total=len(selection),
                                desc="Parsing input files".rjust(40)):
            logger.debug(output_file)


def __parse_where(where):
    where_dict = {}
    for w in where:
        if "==" in w:
            field, value = w.split("==")
            where_dict[field.strip()] = dequote(value.strip())
            continue

        logger.error("Unknown where syntax '%s'", w)
        sys.exit(-1)
    return where_dict


@click.command(short_help='Concatenate files to standard input')
@click.argument('input', type=click.Path(exists=True), nargs=-1)
@click.option('--columns', '-c', multiple=True, type=click.STRING, help="Extra columns to add")
@click.option('--where', '-w', multiple=True, type=click.STRING, help="Filter expression. ie: CHROMOSOME==\"4\"")
def cat(input, columns, where):
    task_cat(
        __input_to_selection(input),
        columns=columns,
        where=__parse_where(where)
    )


@click.command(short_help='Count number of variants')
@click.argument('input', type=click.Path(exists=True), nargs=-1)
@click.option('--where', '-w', multiple=True, type=click.STRING)
@click.option('--groupby', '-g', type=click.STRING)
@click.option('--cores', help='Maximum processes to run in parallel.', type=click.INT, default=os.cpu_count())
@click.option('--quite', '-q', help="Don't show the progress, only the total count.", is_flag=True)
def count(input, where, groupby, cores, quite):
    selection = __input_to_selection(input)
    with Pool(cores) as pool:
        task = functools.partial(task_count, where=__parse_where(where), groupby=groupby)
        map_method = pool.imap_unordered if len(selection) > 1 else map

        total = 0
        groups = {}
        for c, g in tqdm(
            map_method(task, selection),
            total=len(selection),
            desc="Counting variants".rjust(40),
            disable=(len(selection) < 2 or quite)
        ):
            # Update groups
            if g is not None:
                for k, v in g.items():
                    val = groups.get(k, 0)
                    groups[k] = val + v

            total += c

    if len(groups) > 0:
        for k, v in sorted(groups.items(), key=lambda v: v[1]):
            print("{}\t{}".format(k, v))

    print("TOTAL\t{}".format(total))


@click.command(short_help='Groupby and run script')
@click.argument('input', type=click.Path(exists=True), nargs=1)
@click.option('--script', '-s', type=click.STRING)
@click.option('--where', '-w', multiple=True, type=click.STRING)
@click.option('--groupby', '-g', type=click.STRING)
@click.option('--cores', help='Maximum processes to run in parallel.', type=click.INT, default=os.cpu_count())
@click.option('--quite', '-q', help="Don't show the progress, only the total count.", is_flag=True)
def groupby(input, script, where, groupby, cores, quite):

    where_parsed = __parse_where(where)
    selection = list(selector.groupby(input, by=groupby, where=where_parsed))

    with Pool(cores) as pool:
        task = functools.partial(task_script, script=script, where=where_parsed)
        map_method = pool.imap_unordered if len(selection) > 1 else map

        for group_key, group_result in tqdm(
            map_method(task, selection),
            total=len(selection),
            desc="Computing groups".rjust(40),
            disable=(len(selection) < 2 or quite)
        ):
            for r in group_result:
                print("{}\t{}".format(group_key, r))


cli.add_command(preprocess)
cli.add_command(cat)
cli.add_command(count)
cli.add_command(groupby)

if __name__ == "__main__":
    cli()
