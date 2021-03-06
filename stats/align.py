'''
Script que permite leer el archivo tracker producido como salida de cuffcompare
y generar alienamientos entre las secuencias de proteínas para obtenr el % 
de identidad

This scripts reads a tracker file produce using cuffcompare and generates the
aligments bewteen the related sequences in that file to obtein the identity %
'''

import argparse
from Bio import SeqIO
from Bio import Align
from Bio.Align import substitution_matrices

def track_parser(track: str, query_dict:dict, ref_dict: dict)-> list:
    '''
    Reading of the tracking file and generating alingments

    Inputs:
        track (str): path to the tracker file from cuffcompare
        query_dict (dict): multifasta from the query proteins sequences
            parsed using biopython
        ref_dict (dict): multifasta from the reference proteins sequences
            parsed using biopython
    Outputs:
        An aligment list with the query and reference ids and the identuty %
        between the 2 proteins 
    '''
    # To align proteins the relation between transcripts must be in the 
    # accepted list, if not will be considered a FP.
    accepted_relations = ["=", "c", "j"]
    # List to store th aligments identity %
    aligment_list = list()
    # Read the tracker files that relates queries and references
    with open(track, "r") as f_in:
        for linea in f_in:
            ll = linea.split()
            # Parse the line
            # If it is not a FP
            if ll[3] in accepted_relations:
                # Get ref and query id
                ref_id = ll[2].split("|")[1]
                query_id = ll[4].split("|")[1]
                # Get ref and query sequences
                ref_seq = ref_dict[ref_id]
                query_seq = query_dict[query_id]
                # Align the two sequences
                aligment_list.append(alingment(ref_seq, query_seq))
    return aligment_list


def alingment(seq1, seq2)-> list:
    '''
    Inputs:
        seq1 and seq2 (SeqRecords): sequences to bealign as SeqRecord obbjects
    Output (list):
        A list with the sequences ids and the identity %
    '''
    # Create the aligment object with the BLOSUM62 matrix
    aligner = Align.PairwiseAligner()
    aligner.open_gap_score = -10
    aligner.extend_gap_score = -0.5
    matrix = substitution_matrices.load("BLOSUM62")
    aligner.substitution_matrix = matrix
    
    # Align the two sequences using Biopython built in method
    alignments = aligner.align(seq1.seq, seq2.seq)

    # Pick the substitution matrix from the alignment with the highest score
    m = alignments[0].substitutions
    
    # Get the number of identical positions between the two sequences
    identidad = 0
    for i in range(len(m)):
        identidad += m[i, i]
    # Get the sequences with the maximal lenght
    seq_len = max(len(seq1.seq), len(seq2.seq))

    # Get the identity %
    identity_percentage = str((identidad/seq_len)*100)
    return [seq1.id, seq2.id, identity_percentage]
    

def main():
    parser = argparse.ArgumentParser(description="Script to evaluate the identity %")
    parser.add_argument("track",
                        help="path to the tracker file from cuffcompare")
    parser.add_argument("query",
                        help="path to the query multifasta")
    parser.add_argument("ref",
                        help="path to the reference multifasta")
    parser.add_argument("out",
                        help="output name")
    args = parser.parse_args()
    # Reading fasta file into dictionary
    print("Query lenght:")
    query_dict = SeqIO.to_dict(SeqIO.parse(args.query, "fasta"))
    print(len(query_dict))
    print("Reference lenght:")
    ref_dict = SeqIO.to_dict(SeqIO.parse(args.ref, "fasta"))
    print(len(ref_dict))

    # Reading cuffcompare tracking file and alignment
    alignment_list = track_parser(args.track, query_dict, ref_dict)
    
    # write the results to output file
    f_out = open(args.out, "w")
    for alignment in alignment_list:
        f_out.write("\t".join(alignment) + "\n")
    f_out.close()
    
if __name__=="__main__":
    main()