'''beds2counts - compute overlap stats between multiple bed files
=================================================================

:Tags: Genomics Intervals Comparison BED Counting

Purpose
-------

This script takes multiple bed files e.g. from multiple samples from
the same experiment. It assesses the overlap between samples and
outputs a count for each merged interval corresponding to the number
of samples that a particular interval was found in.


Example
-------

For example if the command::

    cgat bed2counts a.bed b.bed c.bed > output.tsv

is run, where a.bed-c.bed look like::

                     1         2         3         4
           012345678901234567890123456789012345678901234
    a.bed: -------          -----               -------
    b.bed:      -----        --
    c.bed:  ---

    Union: ----------       -----               -------

Then output.tsv will look like::

    contig	start	end	count
    chr1	0	7	3
    chr1	17	22	2
    chr1	37	44	1

Options
-------

The only option other than the standard cgat options is -i, --bed-file this
allows the input files to be provided as a comma seperated list to the option
rather than a space delimited set of positional arguements. It is present
purely for galaxy compatibility.

Usage
-----

    cgat beds2counts BED [BED ...] [OPTIONS]

Command line options
--------------------

'''
import tempfile
import sys

try:
    import pybedtools
except ImportError:
    pass

import cgatcore.experiment as E
import cgat.Bed as Bed
import collections
import cgatcore.iotools as iotools
import cgat.IndexedGenome as IndexedGenome


def main(argv=None):
    """script main.

    parses command line options in sys.argv, unless *argv* is given.
    """

    if not argv:
        argv = sys.argv

    # setup command line parser
    parser = E.ArgumentParser(description=__doc__)

    parser.add_argument("--version", action='version', version="1.0")

    parser.add_argument(
        "--bed-file", dest="infiles", type=str,
        metavar="bed",
        help="supply list of bed files",
        action="append")

    parser.set_defaults(infiles=[])

    # add common options (-h/--help, ...) and parse command line
    (args, unknown) = E.start(parser,
                              argv=argv,
                              unknowns=True)

    args.infiles.extend(unknown)
    if len(args.infiles) == 0:
        raise ValueError('please provide at least 1 bed file')

    E.info("concatenating bed files")
    # concatenate the list of files
    tmp = tempfile.NamedTemporaryFile(delete=False, mode="w")
    tmp_merge = tempfile.NamedTemporaryFile(delete=False, mode="w")
    infs = args.infiles
    for inf in infs:
        for bed in Bed.iterator(iotools.open_file(inf)):
            tmp.write("%s\n" % bed)
    tmp.close()

    E.info("merging bed entries")
    # merge the bed entries in the file
    name = tmp.name
    tmp_bed = pybedtools.BedTool(name)
    tmp_bed.sort().merge().saveas(tmp_merge.name)
    tmp_merge.close()

    E.info("indexing bed entries")
    # index the bed entries
    merged = IndexedGenome.Simple()
    for bed in Bed.iterator(iotools.open_file(tmp_merge.name)):
        merged.add(bed.contig, bed.start, bed.end)

    counts = collections.defaultdict(int)
    # list of samples
    samples = args.infiles

    E.info("counting no. samples overlapping each interval")
    for sample in samples:
        found = set()
        for bed in Bed.iterator(iotools.open_file(sample)):
            if merged.contains(bed.contig, bed.start, bed.end):
                key = [bed.contig] + \
                    [x for x in merged.get(bed.contig, bed.start, bed.end)]
                key = (key[0], key[1][0], key[1][1])
                if key in found:
                    continue
                found.add(key)

                # tuple of interval description as key - (contig, start, end)
                counts[key] += 1

    # open outfile
    args.stdout.write("contig\tstart\tend\tcount\n")

    E.info("outputting result")
    for interval, count in sorted(counts.items()):
        args.stdout.write(
            "\t".join(map(str, interval)) + "\t" + str(count) + "\n")

    # write footer and output benchmark information.
    E.stop()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
