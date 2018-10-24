import os
import csv
import argparse
from shutil import copyfile

recommendations = {}

# argument input
desc_str = """
        Program to parse topmed fail metrics.
    """
parser = argparse.ArgumentParser(description=desc_str)
parser.add_argument("-f", type=str, help='input topmed <>build38.fail.tsv file')
args = parser.parse_args()


if not os.path.exists(args.f):
    print(args.f + " does not exist")
    exit()


def selfrg(sample, directory, type):

    if type == 'Freemix_Alpha':
        out_header = ['RG', 'FREEMIX']
        outfile = sample + '.FREEMIX.selfRG'

    if type == 'GENOTYPING_CHIPMIX':
        out_header = ['RG', 'CHIPMIX']
        outfile = sample + '.CHIPMIX.selfRG'

    if os.path.exists(directory + '/GT_verify_bam_id.selfRG'):
        out = {}
        line_count = 0
        zero_count = 0
        with open(directory + '/GT_verify_bam_id.selfRG', 'r') as infilecsv, open(outfile, 'w') as outfilecsv:
            file_reader = csv.DictReader(infilecsv, delimiter='\t')
            file_writer = csv.DictWriter(outfilecsv, fieldnames=out_header, delimiter='\t', extrasaction='ignore')
            file_writer.writeheader()
            for line in file_reader:
                if type == 'Freemix_Alpha':
                    checkline = line['FREEMIX']
                if type == 'GENOTYPING_CHIPMIX':
                    checkline = line['CHIPMIX']

                line_count += 1
                if float(checkline) == 0.00000:
                    zero_count += 1
                file_writer.writerow(line)

            recommendation = 'Abandon library do not use again. For the samples with the high contamination ' \
                             'rate, fail the samples and select new ones from the same cohort if possible to ' \
                             'replace them, instead of attempting the existing samples again.'
            if float(zero_count/line_count) > 0.25:
                recommendation = "User examine contamination file"

    return recommendation


if os.path.exists(args.f):
    with open(args.f, 'r') as infiletsv:
        file_reader = csv.DictReader(infiletsv, delimiter="\t")

        for line in file_reader:

            if 'Freemix_Alpha' in line['QC Failed Metrics']:
                if float(line['Freemix_Alpha']) >= 0.10:
                    print('F1')
                    recommendations['Recommendations'] = selfrg(line['DNA'], line['WorkingDirectory'], 'Freemix_Alpha')
                if float(line['Freemix_Alpha']) >= 0.01 and float(line['Freemix_Alpha']) < 0.10:
                    print('F2')
                    recommendations['Recommendations'] = 'Abandon sample and select a new one from the list of extras ' \
                                                         'provided by the collaborator.'
                print(recommendations)

            elif 'GENOTYPING_CHIPMIX' in line['QC Failed Metrics']:
                if float(line['GENOTYPING_CHIPMIX']) >= 0.10 and float(line['GENOTYPING_CHIPMIX']) < 0.90:
                    print('HERE!')
                    recommendations['Recommendations'] = selfrg(line['DNA'], line['WorkingDirectory'],
                                                                'GENOTYPING_CHIPMIX')
                if float(line['GENOTYPING_CHIPMIX']) >= 0.01 and float(line['GENOTYPING_CHIPMIX']) < 0.10:
                    print('HERE2')
                    recommendations['Recommendations'] = 'User examine contamination file'

                if float(line['GENOTYPING_CHIPMIX']) >= 0.90:
                    print('HERE3')
                    recommendations['Recommendations'] = 'possible mismatched identity sample swap has occurred, ' \
                                                         'examine CHIPMIX scores for each RG'

                    if os.path.exists(line['WorkingDirectory'] + '/GT_verify_bam_id.selfRG'):
                        cwd = os.getcwd()
                        selfRG_source = os.path.join(line['WorkingDirectory'], 'GT_verify_bam_id.selfRG')
                        selfRG_dest = os.path.join(cwd, line['DNA'] + '.genotyping_chipmix/GT_verify_bam_id.selfRG')
                        if not os.path.exists(selfRG_dest):
                            os.mkdir(line['DNA'] + '.genotyping_chipmix')
                            copyfile(selfRG_source, selfRG_dest)
                print(recommendations)

