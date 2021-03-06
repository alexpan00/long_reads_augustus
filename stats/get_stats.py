'''
Script to read the stats produce by cuffcompare for different files in the
same directory and generate a file with all the stats
'''

import argparse
import os
import statistics
import subprocess


def parse_stats(f_in: str)-> str:
    '''
    Function to read the stats file and collapse the important stats in one 
    line. This stats are the sensitivity and precision at Nt, exon and gene
    level.

    Inputs:
        f_in (str): path to the stats file produce by cuffcompare

    Outputs:
        stats_str (str): string with the important stats produce by cuffcompare
    '''
    # Create a lsit to save the important stats produce by sufcompare
    stats = [0]*6
    with open(f_in, "r") as stats_file:
        for line in stats_file:
            # The stats are in the lines that don't satart with #
            if not line.startswith("#") and len(line) > 1:
                ll = line.split()
                # the first fild of the line indicated the level
                # The second the Sn and the third the Pr
                if ll[0] == "Base":
                    stats[0] = ll[2]
                    stats[1] = ll[3]
                if ll[0] == "Exon":
                    stats[2] = ll[2]
                    stats[3] = ll[3]
                if ll[0] == "Transcript":
                    stats[4] = ll[2]
                    stats[5] = ll[3]
                    break
    # Convert the list to a str separated by \t
    stats_str = "\t".join(stats)
    return stats_str


def parse_identity(f_in:str)-> str:
    '''
    Function to read the file with the aligment info and get the number of
    perfect hits, the mean and the median identity

    Inputs:
        f_in (str): path to the file with the alignmnet info
    
    Outputs:
        identity_stats (str): get the summary stats from the aligment info
    '''
    # Create a list to save the identity of all the aligments
    identity_list = list()
    with open(f_in, "r") as identity_file:
        for line in identity_file:
            identity_list.append(float(line.split()[2]))
    
    # Count the number of perfect hits (100 identity %)
    perfect_hits = str(identity_list.count(100.0))
    identity_median = str(statistics.median(identity_list))
    identity_mean = str(statistics.mean(identity_list))

    # Create a str with the results
    identity_stats = identity_mean + "\t" + identity_median + "\t" + perfect_hits

    return identity_stats


def get_FP(base_name: str)-> str:
    '''
    Function to obtain the number of false positives, this is the number of 
    genes that could't be related to any gene in the reference.

    This is done by comparing the number of lines in the tracking file produce
    by cuffcompare and the number of lines in the file that contains the
    aligments info.

    Inputs:
        base_name (str): name of the files wo/ the extension

    Outputs:
        false_positives (str): the total number of false positives
    '''
    # Count lines in the tracking file (total number of genes)
    tracking_file = subprocess.run(["wc", "-l", base_name + ".tracking"], 
                        stdout=subprocess.PIPE, 
                        universal_newlines=True)
    total_genes = int(tracking_file.stdout.split()[0])

    # Count the number of lines in the identity file 
    # (genes matched to reference)
    identity_file = subprocess.run(["wc", "-l", base_name + ".identity"],
                        stdout=subprocess.PIPE, 
                        universal_newlines=True)
    mached_genes = int(identity_file.stdout.split()[0])

    # The difference between the two is the number of FP
    false_positives = total_genes - mached_genes
    return str(false_positives)


def getTP(base_name: str)-> int:
    '''
    Function to obtain the number of True positives and patial TP, this is the 
    number of predicted genes  that could be related to a gene in the reference

    This is done by counting the number of unique reference genes in the
    identity file (TP and partial TP)

    Inputs:
        base_name (str): name of the files wo/ the extension

    Outputs:
        true_positives (str): the total number of true_positives
    '''
    true_positives_id = set()
    with open(base_name + ".identity", "r") as f_in:
        for line in f_in:
            true_positives_id.add(line.split()[0])
    true_positives = len(true_positives_id)
    return true_positives


def getFN(base_name: str)-> str:
    '''
    Function to obtain the number of false negatives, this is the number of 
    genes of the reference that could't be related to any predicted gene.

    This is done by comparing the number of unique reference genes in the
    identity file (TP and partial TP) with the total number of genes in the
    reference

    Inputs:
        base_name (str): name of the files wo/ the extension

    Outputs:
        false_negatives (str): the total number of false negatives
    '''
    true_positives = getTP(base_name)
    with open(base_name + ".stats", "r") as f_in:
        for line in f_in:
            if line.startswith("# Reference mRNAs"):
                total_genes = int(line.split()[4])
                break
    false_negatives = total_genes - true_positives
    return str(false_negatives)


def get_BUSCO_stats(f_in: str)-> dict:
    '''
    Fuction to get the number of BUSCO complete genes in single and multiple
    copies.

    Inputs:
        f_in (str): BUSCO short_summary file
    
    Outputs:
        stats_BUSCO (dict): number of single copy and duplicated BUSCOS
    '''
    stats_BUSCO = dict()
    with open(f_in, "r") as short_summary:
        for line in short_summary:
            if "(S)" in line:
                stats_BUSCO["S"] = int(line.split()[0])
            if "(D)" in line:
                stats_BUSCO["D"] = int(line.split()[0])
                break

    return stats_BUSCO


def compare_BUSCOS(d_ref: dict, f_in: str)-> dict:
    '''
    Function to compare the found BUSCOS in the reference proteom against the
    predicted proteins

    Inputs:
        d_ref (dict): reference proteom stats
        f_in (str): path to the BUSCO results

    Outputs:
        relative_completness (dict): % of single copy and duplicated BUSCOS
    '''
    relative_completness = dict()
    # Get the stats of the predicted genes
    d_test = get_BUSCO_stats(f_in + "/run_eutheria_odb10/short_summary.txt")

    # Get the copletness in realtion to the reference
    relative_completness["S"] = d_test["S"]/d_ref["S"]
    relative_completness["D"] = d_test["D"]/d_ref["D"]

    return relative_completness


def main():
    parser = argparse.ArgumentParser(description=("Get the stats produce by"
                                                   " cuffcompare and the"
                                                   " aligment"))
    parser.add_argument("wd", help="path with the necessary files")
    parser.add_argument("pd", help="path with the BUSCO outputs")
    parser.add_argument("ref_BUSCO", help="path to ref proteom BUSCO stats")
    args = parser.parse_args()

    # Get reference BUSCO stats
    ref_BUSCO_stats = get_BUSCO_stats(args.ref_BUSCO)

    # get a list of the necessary files
    files = os.listdir(args.wd)

    # Get a name for the output file
    # Get the name of a random file without the extennsion
    name = files[0].split(".")[0]
    # Split the name
    l_name = name.split("_")
    # The last fild contains the length of the flanking region and the
    # previous one should contain the technology used
    output_name = l_name[-1] + "_" + l_name[-2] + ".tsv"
    # Open the output file
    f_out = open(args.wd + "/" + output_name, "w")
    f_out.write("N_genes\tnt_sn\tnt_sp\texon_sn\texon_sp\tgene_sn\tgene_sp\tmean_identity\tmedian_identity\tPH\tFP\tFN\tSC\tDU\n")
    for file in files:
        # Get the stats output from cuffcompare
        if file.endswith(".stats"):
            # Get file basename
            base_name = file.split(".")[0]
            # Get number of genes
            n_genes = file.split("_")[1]
            # Get Sn and Pr
            stats = parse_stats(args.wd + "/" + file)
            # Get identity
            identity_stats = parse_identity(args.wd + "/" + base_name + ".identity")
            # Get FP
            false_positives = get_FP(args.wd + "/" + base_name)
            # Get FN
            false_negatives = getFN(args.wd + "/" + base_name)
            # Get BUSCO stats
            completness = compare_BUSCOS(ref_BUSCO_stats, args.pd + "/" + base_name)
            complete_info = n_genes + "\t" + stats + "\t" + identity_stats + \
                            "\t" + false_positives + "\t" + false_negatives + \
                            "\t" + str(completness["S"]) + "\t" + str(completness["D"])
            f_out.write(complete_info + "\n")
    f_out.close()

if __name__ =="__main__":
    main()