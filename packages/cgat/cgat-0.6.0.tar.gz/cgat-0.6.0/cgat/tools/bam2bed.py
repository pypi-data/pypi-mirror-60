"""bam2bed.py - convert bam formatted file to bed formatted file
================================================================

:Tags: Genomics NGS Intervals BAM BED Conversion

Purpose
-------

This tool converts BAM files into BED files supplying the intervals
for each read in the BAM file.  BAM files must have a corresponding
index file ie. example.bam and example.bam.bai

For example::

   samtools view example.bam

   READ1    163    1      13040   15     76M    =      13183   219     ...
   READ1    83     1      13183   7      76M    =      13040   -219    ...
   READ2    147    1      13207   0      76M    =      13120   -163    ...

   python bam2bed.py example.bam

   1       13039   13115   READ1     15      +
   1       13119   13195   READ2     0       +
   1       13182   13258   READ1     7       -
   1       13206   13282   READ2     0       -

By default, bam2bed outputs each read as a separate interval.  With
the option ``--merge-pairs`` paired-end reads are merged and output as
a single interval. The strand is set according to the first read in a
pair.

Usage
-----

::

   cgat bam2bed BAMFILE [--merge-pairs] [options]

operates on the file BAMFILE::

   cgat bam2bed [--merge-pairs] [options]

operates on the stdin as does::

   cgat bam2bed -I BAMFILE [--merge-pairs] [options]


To merge paired-end reads and output fragment interval ie. leftmost
mapped base to rightmost mapped base::

   cat example.bam | cgat bam2bed --merge-pairs

   1       13119   13282   READ2     0       +
   1       13039   13258   READ1     7       +

To use merge pairs on only a region of the genome use samtools view::

   samtools view -ub example.bam 1:13000:13100 | cgat bam2bed --merge-pairs

Note that this will select fragments were the first read-in-pair is in
the region.

Options
-------

-m, --merge-pairs
    Output one region per fragment rather than one region per read,
    thus a single region is create stretching from the start of the
    frist read in pair to the end of the second.

    Read pairs that meet the following criteria are removed:

    * Reads where one of the pair is unmapped
    * Reads that are not paired
    * Reads where the pairs are mapped to different chromosomes
    * Reads where the the insert size is not between the max and
      min (see below)

.. warning::

    Merged fragements are always returned on the +ve strand.
    Fragement end point is estimated as the alignment start position
    of the second-in-pair read + the length of the first-in-pair
    read. This may lead to inaccuracy if you have an intron-aware
    aligner.

--max-insert-size, --min-insert-size
    The maximum and minimum size of the insert that is allowed when
    using the --merge-pairs option. Read pairs closer to gether or futher
    apart than the min and max repsectively are skipped.

-b, --bed-format
    What format to output the results in. The first n columns of the bed
    file will be output.



Type::

   python bam2bed.py --help

for command line help.

Command line options
--------------------

"""

import sys
import pysam
import cgatcore.experiment as E
from cgat.BamTools.bamtools import merge_pairs


def main(argv=None):
    """script main.

    parses command line options in sys.argv, unless *argv* is given.
    """

    if not argv:
        argv = sys.argv

    # setup command line parser
    parser = E.ArgumentParser(description=__doc__)

    parser.add_argument("--version", action='version', version="1.0")

    parser.add_argument("-m", "--merge-pairs", dest="merge_pairs",
                        action="store_true",
                        help="merge paired-ended reads and output interval "
                        "for entire fragment. ")

    parser.add_argument("--max-insert-size", dest="max_insert_size", type=int,
                        help="only merge paired-end reads if they are less than "
                        "# bases apart. "
                        " 0 turns off this filter. ")

    parser.add_argument("--min-insert-size", dest="min_insert_size", type=int,
                        help="only merge paired-end reads if they are at "
                        "least # bases apart. "
                        " 0 turns off this filter. ")

    parser.add_argument("--bed-format", dest="bed_format", type=str,
                        choices=('3', '4', '5', '6'),
                        help="bed format to output. ")

    parser.set_defaults(
        region=None,
        call_peaks=None,
        merge_pairs=None,
        min_insert_size=0,
        max_insert_size=0,
        bed_format='6',
    )

    (args, unknown) = E.start(parser, argv=argv, unknowns=True)

    if len(unknown) == 0:
        unknown.append("-")

    samfile = pysam.AlignmentFile(unknown[0], "rb")

    args.bed_format = int(args.bed_format)

    if args.merge_pairs is not None:
        counter = merge_pairs(samfile,
                              args.stdout,
                              min_insert_size=args.min_insert_size,
                              max_insert_size=args.max_insert_size,
                              bed_format=args.bed_format)

        E.info("category\tcounts\n%s\n" % counter.asTable())

    else:
        # use until_eof. Files from stdin have no index
        it = samfile.fetch(until_eof=True)

        # more comfortable cigar parsing will
        # come with the next pysam release
        BAM_CMATCH = 0
        BAM_CDEL = 2
        BAM_CREF_SKIP = 3
        take = (BAM_CMATCH, BAM_CDEL, BAM_CREF_SKIP)
        outfile = args.stdout

        for read in it:
            if read.is_unmapped:
                continue

            t = 0
            for op, l in read.cigar:
                if op in take:
                    t += l

            if read.is_reverse:
                strand = "-"
            else:
                strand = "+"
            outfile.write("%s\t%d\t%d\t%s\t%d\t%c\n" %
                          (read.reference_name,
                           read.pos,
                           read.pos + t,
                           read.qname,
                           read.mapq,
                           strand))

    E.stop()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
