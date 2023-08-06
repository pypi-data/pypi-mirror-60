'''
vcfstats_sqlite.py - reformat output of vcf-stats for database loading
======================================================================

:Tags: Python

Purpose
-------

create a csv separated file for loading into a database from 
output of vcf-stats utility in vcf-tools package.

Usage
-----

Example::

   python vcfstats_sqlite.py [files] > [outfile]

Type::

   python vcfstats_sqlite.py --help

for command line help.


Command line options
--------------------

'''
import os
import sys
import cgatcore.experiment as E
import cgatcore.iotools as iotools


def main(argv=None):
    """script main.

    parses command line options in sys.argv, unless *argv* is given.
    """

    if argv is None:
        argv = sys.argv

    parser = E.ArgumentParser(description=__doc__)

    parser.add_argument("--version", action='version', version="1.0")

    (args, unknown) = E.start(parser,
                              unknowns=True)

    args.filenames = unknown

    if len(args.filenames) < 1:
        args.stdout.write("# Error: no vcf-stats files specified/found.")
        sys.exit(1)

    E.info("Parsing %i file(s)" % len(args.filenames))

    # set up output files
    vcf_file = iotools.open_file('vcfstats.txt', 'w')
    indel_file = iotools.open_file('indelstats.txt', 'w')
    snp_file = iotools.open_file('snpstats.txt', 'w')
    shared_file = iotools.open_file('sharedstats.txt', 'w')

    for fileno, filename in enumerate(args.filenames):

        prefix = os.path.basename(filename)
        trackname = prefix.replace(".vcfstats", "")

        if os.path.exists(filename):
            lines = [x for x in iotools.open_file(filename, "r").readlines()]
        else:
            lines = []

        if len(lines) == 0:
            args.stdout.write(
                "# Error: empty vcf-stats file found: $(filename)s")
            sys.exit(1)
        else:
            E.info("File %i contains %i lines" % (fileno, len(lines)))
            vcf_stats = dict(track=trackname)
            snp_stats = dict(track=trackname)
            indel_stats = dict()
            shared_stats = dict()
            all_vars = False
            indels = False
            snps = False
            shared = False
            for i, line in enumerate(lines):
                line = line.strip()
                if line.find("'all'") > -1:
                    all_vars = True
                    E.info("Found 'all'")
                    continue

                if all_vars:
                    if line.find("=>") > -1:
                        fields = line.split("=>")
                        key = fields[0].strip().replace(
                            "'", "").replace(">", "_")
                        val = fields[1].strip().replace(",", "")
                    else:
                        key = "NA"
                        val = "NA"
                    if key == "indel" and val == "{":
                        indels = True
                        E.info("Found 'indels'")
                        continue
                    elif key == "snp" and val == "{":
                        snps = True
                        E.info("Found 'SNPs'")
                        continue
                    elif key == "shared" and val == "{":
                        shared = True
                        E.info("Found 'Shared'")
                        continue

                    if indels:
                        if line.find("}") > -1:
                            indels = False
                            E.info("Processed 'indels'")
                            continue
                        else:
                            indel_stats[key] = val
                    elif snps:
                        if line.find("}") > -1:
                            snps = False
                            E.info("Processed 'SNPs'")
                            continue
                        else:
                            snp_stats[key] = val
                    elif shared:
                        if line.find("}") > -1:
                            shared = False
                            E.info("Processed 'Shared'")
                            continue
                        else:
                            shared_stats[key] = val
                    elif key != "NA":
                        vcf_stats[key] = val

            # Ensure all keys are present
            allkeys = ["nalt_1", "nalt_2", "nalt_3", "nalt_4",
                       "nalt_5", "track", "count", "snp_count", "indel_count"]
            for k in allkeys:
                if k in vcf_stats:
                    continue
                else:
                    vcf_stats[k] = "0"

            # Write header (for first file only)
            if filename == args.filenames[0]:

                # Ensure keys are sorted
                srt = list(vcf_stats.keys())
                srt.sort()
                sep = ""
                for k in srt:
                    vcf_file.write("%s%s" % (sep, k))
                    sep = "\t"
                vcf_file.write("\n")

                indel_file.write("track\tindel_length\tindel_count\n")
                shared_file.write("track\tno_samples\tvar_count\n")

                sep = ""
                for k in snp_stats.keys():
                    snp_file.write("%s%s" % (sep, k))
                    sep = "\t"
                snp_file.write("\n")

            # Write data
            sep = ""
            srt = list(vcf_stats.keys())
            srt.sort()
            for k in srt:
                vcf_file.write("%s%s" % (sep, vcf_stats[k]))
                sep = "\t"
            vcf_file.write("\n")

            # Check all indel lengths are covered
            r = list(range(-20, 20, 1))
            for i in r:
                if str(i) in indel_stats:
                    continue
                else:
                    indel_stats[i] = "0"
            for k in indel_stats.keys():
                indel_file.write("%s\t%s\t%s\n" %
                                 (trackname, k, indel_stats[k]))

            for k in shared_stats.keys():
                shared_file.write("%s\t%s\t%s\n" %
                                  (trackname, k, shared_stats[k]))

            sep = ""
            for k in snp_stats.keys():
                snp_file.write("%s%s" % (sep, snp_stats[k]))
                sep = "\t"
            snp_file.write("\n")

    # close files
    vcf_file.close()
    indel_file.close()
    snp_file.close()

    E.stop()
    sys.exit(0)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
