"""
Infer ancestral traits based on a tree.
"""

import numpy as np
from collections import defaultdict
import os, sys
import pandas as pd
from .utils import read_metadata, write_json, get_json_name
TINY = 1e-12

def mugration_inference(tree=None, seq_meta=None, field='country', confidence=True,
                        infer_gtr=True, root_state=None, missing='?', sampling_bias_correction=None):
    """
    Infer likely ancestral states of a discrete character assuming a time reversible model.

    Parameters
    ----------
    tree : str
        name of tree file
    seq_meta : dict
        meta data associated with sequences
    field : str, optional
        meta data field to use
    confidence : bool, optional
        calculate confidence values for inferences
    infer_gtr : bool, optional
        infer a GTR model for trait transitions (otherwises uses a flat model with rate 1)
    root_state : None, optional
        force the state of the root node (currently not implemented)
    missing : str, optional
        character that is to be interpreted as missing data, default='?'

    Returns
    -------
    T : Phylo.Tree
        Biophyton tree
    gtr : treetime.GTR
        GTR model
    alphabet : dict
        mapping of character states to
    """
    from treetime import GTR
    from Bio.Align import MultipleSeqAlignment
    from Bio.SeqRecord import SeqRecord
    from Bio.Seq import Seq
    from Bio import Phylo

    T = Phylo.read(tree, 'newick')
    nodes = {n.name:n for n in T.get_terminals()}

    # Determine alphabet only counting tips in the tree
    places = set()
    for name, meta in seq_meta.items():
        if field in meta and name in nodes:
            places.add(meta[field])
    if root_state is not None:
        places.add(root_state)

    # construct GTR (flat for now). The missing DATA symbol is a '-' (ord('-')==45)
    places = sorted(places)
    nc = len(places)
    if nc>180:
        print("ERROR: geo_inference: can't have more than 180 places!", file=sys.stderr)
        return None,None,None
    elif nc==0:
        print("ERROR: geo_inference: list of places is empty!", file=sys.stderr)
        return None,None,None
    elif nc==1:
        print("WARNING: geo_inference: only one place found -- set every internal node to %s!"%places[0], file=sys.stderr)
        alphabet = {'A':places[0]}
        alphabet_values = ['A']
        gtr = None
        for node in T.find_clades():
            node.sequence=['A']
            node.marginal_profile=np.array([[1.0]])
    else:
        # set up model
        alphabet = {chr(65+i):place for i,place in enumerate(places)}
        model = GTR.custom(pi = np.ones(nc, dtype=float)/nc, W=np.ones((nc,nc)),
                          alphabet = np.array(sorted(alphabet.keys())))

        missing_char = chr(65+nc)
        alphabet[missing_char]=missing
        model.profile_map[missing_char] = np.ones(nc)
        model.ambiguous = missing_char
        alphabet_rev = {v:k for k,v in alphabet.items()}

        # construct pseudo alignment
        pseudo_seqs = []
        for name, meta in seq_meta.items():
            if name in nodes:
                s=alphabet_rev[meta[field]] if field in meta else missing_char
                pseudo_seqs.append(SeqRecord(Seq(s), name=name, id=name))
        aln = MultipleSeqAlignment(pseudo_seqs)

        # set up treetime and infer
        from treetime import TreeAnc
        tt = TreeAnc(tree=tree, aln=aln, gtr=model, convert_upper=False, verbose=0)
        tt.use_mutation_length = False
        tt.infer_ancestral_sequences(infer_gtr=infer_gtr, store_compressed=False, pc=1.0,
                                     marginal=True, normalized_rate=False)

        if sampling_bias_correction:
            tt.gtr.mu *= sampling_bias_correction
            tt.infer_ancestral_sequences(infer_gtr=False, store_compressed=False,
                                         marginal=True, normalized_rate=False)

        T = tt.tree
        gtr = tt.gtr
        alphabet_values = tt.gtr.alphabet


    # attach inferred states as e.g. node.region = 'africa'
    for node in T.find_clades():
        node.__setattr__(field, alphabet[node.sequence[0]])

    # if desired, attach entropy and confidence as e.g. node.region_entropy = 0.03
    if confidence:
        for node in T.find_clades():
            pdis = node.marginal_profile[0]
            S = -np.sum(pdis*np.log(pdis+TINY))

            marginal = [(alphabet[alphabet_values[i]], pdis[i]) for i in range(len(alphabet_values))]
            marginal.sort(key=lambda x: x[1], reverse=True) # sort on likelihoods
            marginal = [(a, b) for a, b in marginal if b > 0.001][:4] #only take stuff over .1% and the top 4 elements
            conf = {a:b for a,b in marginal}
            node.__setattr__(field + "_entropy", S)
            node.__setattr__(field + "_confidence", conf)

    return T, gtr, alphabet


def register_arguments(parser):
    """Add subcommand specific arguments

    Parameters
    ----------
    parser : argparse
        subcommand argument parser
    """
    parser.add_argument('--tree', '-t', required=True, help="tree to perform trait reconstruction on")
    parser.add_argument('--metadata', required=True, help="tsv/csv table with meta data")
    parser.add_argument('--columns', required=True, nargs='+',
                        help='metadata fields to perform discrete reconstruction on')
    parser.add_argument('--confidence',action="store_true",
                        help='record the distribution of subleading mugration states')
    parser.add_argument('--sampling-bias-correction', type=float,
                        help='a rough estimate of how many more events would have been observed'
                             ' if sequences represented an even sample. This should be'
                             ' roughly the (1-sum_i p_i^2)/(1-sum_i t_i^2), where p_i'
                             ' are the equilibrium frequencies and t_i are apparent ones.'
                             '(or rather the time spent in a particular state on the tree)')
    parser.add_argument('--output-node-data', type=str, help='name of JSON file to save trait inferences to')
    parser.add_argument('--output', '-o', type=str, help='DEPRECATED. Same as --output-node-data')
    parser.epilog = "Note that missing data must be represented by a `?` character. Missing data will currently be inferred."

def run(args):
    """run mugration inference

    Parameters
    ----------
    args : namespace
        command line arguments are parsed by argparse
    """
    tree_fname = args.tree
    traits, columns = read_metadata(args.metadata)

    from Bio import Phylo
    T = Phylo.read(tree_fname, 'newick')
    missing_internal_node_names = [n.name is None for n in T.get_nonterminals()]
    if np.all(missing_internal_node_names):
        print("\n*** WARNING: Tree has no internal node names!")
        print("*** Without internal node names, ancestral traits can't be linked up to the correct node later.")
        print("*** If you want to use 'augur export' later, re-run this command with the output of 'augur refine'.")
        print("*** If you haven't run 'augur refine', you can add node names to your tree by running:")
        print("*** augur refine --tree %s --output-tree <filename>.nwk"%(tree_fname) )
        print("*** And use <filename>.nwk as the tree when running 'ancestral', 'translate', and 'traits'")

    mugration_states = defaultdict(dict)
    models = defaultdict(dict)
    out_prefix = '.'.join(args.tree.split('.')[:-1])
    for column in args.columns:
        T, gtr, alphabet = mugration_inference(tree=tree_fname, seq_meta=traits,
                                               field=column, confidence=args.confidence, sampling_bias_correction=args.sampling_bias_correction)
        if T is None: # something went wrong
            continue

        for node in T.find_clades():
            mugration_states[node.name][column] = node.__getattribute__(column)
            if args.confidence:
                mugration_states[node.name][column+'_confidence'] = node.__getattribute__(column+'_confidence')
                mugration_states[node.name][column+'_entropy'] = node.__getattribute__(column+'_entropy')

        if gtr:
            # add gtr models to json structure for export
            models[column]['rate'] = gtr.mu
            models[column]['alphabet'] = [alphabet[k] for k in sorted(alphabet.keys())]
            models[column]['equilibrium_probabilities'] = list(gtr.Pi)
            models[column]['transition_matrix'] = [list(x) for x in gtr.W]

        if gtr:
            with open(out_prefix+'%s.mugration_model.txt'%column, 'w') as ofile:
                ofile.write('Map from character to field name\n')
                for k,v in alphabet.items():
                    ofile.write(k+':\t'+str(v)+'\n')
                ofile.write('\n\n')

                ofile.write(str(gtr))

    out_name = get_json_name(args, out_prefix+'_traits.json')
    write_json({"models":models, "nodes":mugration_states},out_name)

    print("\nInferred ancestral states of discrete character using TreeTime:"
          "\n\tSagulenko et al. TreeTime: Maximum-likelihood phylodynamic analysis"
          "\n\tVirus Evolution, vol 4, https://academic.oup.com/ve/article/4/1/vex042/4794731\n", file=sys.stdout)

    print("results written to", out_name, file=sys.stdout)
