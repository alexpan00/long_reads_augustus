'''
Script to reads the stats produce by cuffcompare for different files in the
same directory and generate a file ith all the stats
'''

import argparse
import os
import statistics
    

def parse_stats(f_in: str)-> str:
    '''
    Read the stats file and collapse the important stats in one line
    '''
    stats = [0]*6
    with open(f_in, "r") as stats_file:
        for line in stats_file:
            if not line.startswith("#"):
                ll = line.split()
                if ll[0] == "Base":
                    stats[0] = ll[2]
                    stats[1] = ll[3]
                if ll[0] == "Exon":
                    stats[2] = ll[2]
                    stats[3] = ll[3]
                if ll[0] == "Transcript":
                    stats[4] = ll[2]
                    stats[5] = ll[3]
    stats_str = "\t".join(stats)
    return stats_str


def parse_identity(f_in:str)-> str:
    '''
    Read the file with the aligment info and get the number of perfect hits
    the mean and the median identity
    '''
    identity_list = list()
    with open(f_in, "r") as identity_file:
        for line in identity_file:
            identity_list.append(float(line.split()[2]))
    perfect_hits = str(identity_list.count(100.0))
    identity_median = str(statistics.median(identity_list))
    identity_mean = str(statistics.mean(identity_list))
    identity_stats = identity_mean + "\t" + identity_median + "\t" + perfect_hits

    return identity_stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("wd")
    args = parser.parse_args()

    files = os.listdir(args.wd)
    f_out = open(args.wd + "/summary.tsv", "w")
    f_out.write("N_genes\tnt_sn\tnt_sp\texon_sn\texon_sp\tgene_sn\tgene_sp\tmean_identity\tmedian_identity\tPH\n")
    for file in files:
        if file.endswith(".stats"):
            # Get file basename
            base_name = file.split(".")[0]
            # Get number of genes
            n_genes = file.split("_")[1]
            # Get Sn and Pr
            stats = parse_stats(file)
            # Get identity
            identity_stats = parse_identity(args.wd + "/" + base_name + ".identity")
            complete_info = n_genes + "\t" + stats + "\t" + identity_stats
            f_out.write(complete_info + "\n")
    f_out.close()

if __name__ =="__main__":
    main()