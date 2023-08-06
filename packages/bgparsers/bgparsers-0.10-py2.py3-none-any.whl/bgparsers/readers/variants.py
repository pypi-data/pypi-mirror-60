import logging
import pickle
import types
from os.path import exists, join, dirname, basename

import numpy as np

from bgparsers.readers import tsv
from bgparsers.readers.common import __open_file, __count_lines

logger = logging.getLogger("bgparsers")

EXCLUDE_PREFIX = "__exclude_"

COMMON_HEADERS = ['CHROMOSOME', 'POSITION', 'STRAND', 'REF', 'ALT', 'ALT_TYPE', 'SAMPLE', 'DONOR']
TSV_SCHEMA = [

    # Chromosome
    ({'chromosome', 'chr', 'chrom', 'chromosome_name', '#chrom'}, 'CHROMOSOME',
     lambda c: c.upper().replace('CHR', '').replace('23', 'X').replace('24', 'Y')),

    # Start position
    ({'position', 'start', 'start_position', 'pos', 'chromosome_start'}, 'POSITION', int),

    # Strand
    ({'strand', 'chromosome_strand'}, 'STRAND',
     lambda s: '-' if s in ['-', '0', '-1'] else '+' if s in ['+', '1', '+1'] else None),

    # Reference
    ({'ref', 'reference_allele', 'reference', 'reference_genome_allele'}, 'REF', str),

    # Alternate
    ({'alt', 'tumor_seq_allele2', 'variant', 'alternative', 'mutated_to_allele'}, 'ALT', str),

    # Sample ID
    ({'sample', 'tumor_sample_barcode'}, 'SAMPLE', str),

    # TCGA only: donor deduced from the sample id
    ({'tumor_sample_barcode'}, 'DONOR', lambda s: "-".join(s.split("-")[:3]) if s.startswith("TCGA") else None),

    # Donor ID
    ({'donor_id'}, 'DONOR', str)
]


def chunks_parser(data_folder, extra=None):
    chunk_count = 0
    chunk_file = join(data_folder, "c{:06d}.bgvars.xz".format(chunk_count))
    while exists(chunk_file):
        for r in pickle_parser(chunk_file, extra=extra):
            yield r
        chunk_count += 1
        chunk_file = join(data_folder, "c{:06d}.bgvars.xz".format(chunk_count))


def pickle_parser(file, extra=None):
    fd, close = __open_file(file, "rb")
    values = pickle.load(fd)
    if close:
        fd.close()

    if isinstance(values, dict):
        size = values['length']
        data = values['data']
        vectors = values['vectors']
        base = dict([(k, vectors[k]) for k in vectors.keys() if not isinstance(vectors[k], np.ndarray)])
        keys = [k for k in vectors.keys() if isinstance(vectors[k], np.ndarray)]

        if isinstance(extra, list) or extra is None:
            fields = set(COMMON_HEADERS + extra) if isinstance(extra, list) else set(COMMON_HEADERS)
            keys = [k for k in keys if k in fields]

        for i in range(size):
            r = base.copy()
            for k in keys:
                r[k] = data[k][vectors[k][i]]
            yield r

    else:
        if isinstance(extra, list) or extra is None:
            fields = COMMON_HEADERS + extra if isinstance(extra, list) else COMMON_HEADERS
            for r in values:
                yield {k: r[k] for k in fields}
        else:
            for r in values:
                yield r


def __is_pickle(file):
    return file.endswith(".bgvars.gz") or file.endswith(".bgvars.xz") or file.endswith(".bgvars")


def __parser_generator(file, extra=None, required=None):
    pickle_version = __preprocess_file(file)
    if exists(pickle_version):
        return chunks_parser(dirname(pickle_version), extra=extra)

    if __is_pickle(file):
        return pickle_parser(file, extra=extra)

    return tsv.parser(file, TSV_SCHEMA, extra=extra, required=required)


def __preprocess_file(file):
    return join(dirname(file), "bgvariants", "preprocess", basename(file), "c000000.bgvars.xz")


def variants_count(file):
    return __count_lines(file)


def variants(file, annotations=None, extra=None, required=None):
    try:
        if isinstance(file, types.GeneratorType) or isinstance(file, list):
            # Allow to concatenate a reader and a selector. Ex: readers.variants( selector.find( ...
            for f, a in file:
                for row in variants(f, annotations=a, extra=extra, required=required):
                    yield row
        else:

            preprocess = exists(__preprocess_file(file)) or __is_pickle(file)
            if annotations is not None and preprocess:
                annotations = {k: v for k, v in annotations.items() if
                               isinstance(v, tuple) and v[0] not in ['mapping', 'internal']}

            if annotations is not None:
                internal_annotations = []
                for k, v in annotations.items():
                    if isinstance(v, tuple) and v[0] == 'internal':
                        if isinstance(v[1], tuple):
                            internal_annotations += v[1][1]
                        else:
                            internal_annotations.append(v[1])

                if len(internal_annotations) > 0 and extra is not True:
                    if isinstance(extra, list):
                        extra += [h for h in internal_annotations if h not in extra]
                    else:
                        extra = internal_annotations

            parser = __parser_generator(file, extra=extra, required=required)
            if annotations is None or len(annotations) == 0:
                for row in parser:

                    # Add postprocessing annotations
                    if not preprocess:
                        row = __postprocess_row(row)

                    if row is None:
                        continue

                    yield row
            else:
                for row in parser:

                    # Add row annotations and filter non-valid rows
                    row, excludes = __annotate_row(row, annotations)
                    if row is None:
                        continue

                    # Add postprocessing annotations
                    if not preprocess:
                        row = __postprocess_row(row)

                    row = __exclude_row(row, excludes)
                    if row is None:
                        continue

                    yield row

    except NotImplementedError as e:
        logger.error("{}. {}".format(file, e))
        raise e


def prefix_length(ref, alt):
    i = 0
    while i < len(ref) and i < len(alt) and ref[i] == alt[i]:
        i += 1
    return i


def suffix_length(ref, alt):
    i = len(ref) - 1
    j = len(alt) - 1
    while i >= 0 and j >= 0 and ref[i] == alt[j]:
        i -= 1
        j -= 1
    return len(ref) - i - 1


def indel_postprocess(start, ref, alt):
    """
    Removes the bases that are repeated in both ref and alt and are therefore NOT variants
    :param start:
    :param ref:
    :param alt:
    :return:
    """
    prefix_len = prefix_length(ref, alt)
    ins_correction = 1 if len(ref) < len(alt) else 0
    start += max(0, prefix_len - ins_correction)
    alt = alt[prefix_len:]
    ref = ref[prefix_len:]

    suffix_len = suffix_length(ref, alt)
    if suffix_len > 0:
        alt = alt[:-suffix_len]
        ref = ref[:-suffix_len]

    ref = '-' if ref == '' else ref
    alt = '-' if alt == '' else alt

    return start, ref, alt


def __postprocess_row(row):
    if "ALT_TYPE" not in row and 'REF' in row:  # ALT is assumed to be always present
        l_ref = len(row['REF'])
        l_alt = len(row['ALT'])

        if l_alt != l_ref:
            alteration_type = "indel"
        else:
            if l_alt > 1:
                alteration_type = "mnp"
            else:
                if '-' in row['REF'] or '-' in row['ALT']:
                    alteration_type = "indel"
                else:
                    alteration_type = "snp"
        row['ALT_TYPE'] = alteration_type

    if "STRAND" not in row:
        row['STRAND'] = "+"

    # Use VEP like insertions and deletions formatting
    if row.get('ALT_TYPE', '') == "indel":
        row['POSITION'], row['REF'], row['ALT'] = indel_postprocess(row['POSITION'], row['REF'], row['ALT'])

    return row


def __annotate_row(row, annotations):
    excludes = {}

    def sort_key(i):
        return 1 if not isinstance(i[1], tuple) else {'internal': 2, 'mapping': 3}.get(i[1][0], 4)

    sorted_annotations = list(sorted(annotations.items(), key=sort_key))

    for k, v in sorted_annotations:

        # Skip exclusion
        if k.startswith(EXCLUDE_PREFIX):
            excludes[k.replace(EXCLUDE_PREFIX, "")] = v
            continue

        if isinstance(v, tuple):

            if v[0] == 'mapping':
                row[k] = __annotate_value(row, v)
            elif v[0] == 'filtering':
                row[k] = __annotate_value(row, v)
                if row[k] is None:
                    return None
            elif v[0] == 'not':
                v_not = v[1]
                if isinstance(v_not, tuple):
                    if v_not[0] == 'mapping':
                        v_not = __annotate_value(row, v_not)
                if v_not is not None:
                    return None
            elif v[0] == 'internal':
                if isinstance(v[1], tuple):
                    try:
                        row[k] = v[1][0].format(**row)
                    except Exception:
                        row[k] = None
                else:
                    row[k] = row.get(v[1], None)
                continue
            else:
                # Filter non annotated rows
                if row[v[0]] not in v[2]:
                    return None
                row[k] = v[1]
        else:
            row[k] = v

    return row, excludes


def __exclude_row(row, excludes):

    # Process exclusions after the row has been annotated
    for k, v in excludes.items():
        if len(v) > 1:
            if row[k] in v:
                return None
        elif len(v) == 1:
            v = list(v)[0]

            # Negative exclusion
            if v is not None and v.startswith("!"):
                v = v.replace("!", "")
                if row[k] != v:
                    return None
            else:
                if row[k] == v:
                    return None

    return row


def __annotate_value(row, annotation):
    map_key = row[annotation[1]]
    map_value = annotation[2].get(map_key, None)
    return map_value
