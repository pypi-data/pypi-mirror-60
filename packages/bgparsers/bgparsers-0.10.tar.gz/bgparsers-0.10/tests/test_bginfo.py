import json
from bgparsers import selector
from bgparsers import readers


def test_bginfo():
    rows = []
    headers = ["SAMPLE", "DONOR", "CHROMOSOME", "POSITION", "REF", "ALT", "STRAND", "ALT_TYPE", "SAMPLE2", "DATASET", "GENOMEREF"]
    for input_file, input_annotations in selector.find("tests/data"):
        for r in readers.variants(input_file, annotations=input_annotations):
            rows.append([r.get(h, None) for h in headers])

    with open('tests/data/bginfo_output.json', 'r', encoding='utf-8') as f:
        valid_rows = json.load(f)

    assert len(rows) == len(valid_rows)
    for i, row in enumerate(rows):
        assert row == valid_rows[i]
