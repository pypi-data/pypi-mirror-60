from bgparsers import readers

SAMPLE_LINES = {
    0: {},

    99999: {}
}

DATA = [
    {
        "file": "tests/data/100k_hg19.maf",
        "count": 100000,
        "lines": SAMPLE_LINES
    }, {
        "file": "tests/data/100k_hg19.maf.gz",
        "count": 100000,
        "lines": SAMPLE_LINES
    }
]


def assert_data(item):
    i = 0
    for _ in readers.variants(item["file"]):
        i += 1

    assert i == item["count"], "Count mismatch at {}".format(item["file"])
    return i


def test_readers():
    for item in DATA:
        assert_data(item)
