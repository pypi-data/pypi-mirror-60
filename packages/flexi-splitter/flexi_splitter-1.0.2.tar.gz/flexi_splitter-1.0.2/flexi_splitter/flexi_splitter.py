#!/usr/bin/env python3
# -*-coding:Utf-8 -*
"""
This module provides all the function to split fastq files according to the
adaptator information provided in a .yaml configuration file
"""

import os
from contextlib import ExitStack
import sys
import getopt
from gzip import open as gzopen
import yaml  # pip install pyyaml
from . import suffix_tree
import time


class Reads:
    """
    Class to manage Reads manipulation
    """

    def __init__(self, fin=None):
        self.header = str()
        self.seq = str()
        self.qual_str = str()
        self.qual = list()
        if fin is not None:
            self.read(fin=fin)

    def __del__(self):
        del self.header
        del self.seq
        del self.qual

    def read(self, fin):
        """
        read a read from an open buffer
        """
        try:
            self.header = str(fin.readline())[1:-1]
            self.seq = str(fin.readline())[:-1]
            fin.readline()
            self.qual_str = str(fin.readline())[:-1]
            self.str2qual(self.qual_str)
        except IOError as err:
            print("error: Reads::read() ")
            fin.close()
            raise err

    def str2qual(self, qual):
        """
        convert phred score to integer
        """
        del self.qual
        self.qual = list()
        for base_qual in qual:
            self.qual.append(ord(base_qual)-64)

    def qual2str(self):
        """
        convert interger to phred score
        """
        return self.qual_str

    def write(self, fout):
        """
        write a read in an open buffer
        """
        try:
            fout.write("@" + self.header + "\n")
            fout.write(self.seq + "\n")
            fout.write("+\n")
            fout.write(self.qual2str() + "\n")
        except IOError as err:
            print("error: Reads::write() ")
            fout.close()
            raise err

    def __str__(self):
        """
        write a read as an str
        """
        reads = "@" + self.header + "\n"
        reads += self.seq + "\n"
        reads += "+\n"
        reads += self.qual2str() + "\n"
        return reads


def load_yaml(path):
    """
    Load yaml configuration file.

    params: path
    """
    with open(path, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            for adaptator in config:
                if not adaptator == 'conditions':
                    config[adaptator]['coords']['start'] = int(
                        config[adaptator]['coords']['start'] - 1
                    )
                    config[adaptator]['coords']['stop'] = int(
                        config[adaptator]['coords']['stop'] - 1
                    )
                    config[adaptator]['coords']['reads'] = int(
                        config[adaptator]['coords']['reads'] - 1
                    )
            config['conditions']['unassigned'] = None
            config = update_config(config)
            return config
        except yaml.YAMLError as err:
            raise err


def update_config(config):

    """
    Add possition where to remove adaptator requencially
    """
    for adaptator in config:
        if not adaptator == 'conditions':
            config[adaptator]['coords']['start_update'] = \
                config[adaptator]['coords']['start']
            config[adaptator]['coords']['stop_update'] = \
                config[adaptator]['coords']['stop']
            config = update_positions(
                config=config,
                adaptator=adaptator,
                ntuple=config[adaptator]['coords']['reads']
            )
    return config


def test_adaptator(config, adaptator, ntuple, verbose=False):
    """
    Run tests on the adaptator

    params: config
    params: adaptator
    """
    try:
        if adaptator not in config.keys():
            if verbose:
                print("error: extract_barcode(), config doesn't contain " +
                      str(adaptator) +
                      " adaptator.")
            raise KeyError

        if 'coords' not in config[adaptator].keys():
            if verbose:
                print("error: extract_barcode(), " +
                      str(adaptator) +
                      " has no coords")
            raise KeyError

        if 'reads' not in config[adaptator]['coords'].keys():
            if verbose:
                print("error: extract_barcode(), " +
                      str(adaptator) +
                      " has no reads")
            raise KeyError

        if 'start' not in config[adaptator]['coords'].keys():
            if verbose:
                print("error: extract_barcode(), " +
                      str(adaptator) +
                      " has no start")
            raise KeyError

        if 'stop' not in config[adaptator]['coords'].keys():
            if verbose:
                print("error: extract_barcode(), " +
                      str(adaptator) +
                      " has no stop")
            raise KeyError

        if not ntuple == config[adaptator]['coords']['reads']:
            if verbose:
                print("error: extract_barcode(), " +
                      str(adaptator) +
                      " not present for reads " +
                      str(ntuple))
            raise ValueError

    except KeyError:
        if verbose:
            print("error: test_adaptator() ")
        raise KeyError
    except ValueError:
        if verbose:
            print("error: test_adaptator() ")
        raise ValueError


def extract_pos(config, adaptator, verbose=False):
    """
    Extract adaptator position from load_config() output.

    params: config
    params: adaptator
    """
    try:
        return config[adaptator]['coords']
    except KeyError:
        if verbose:
            print("error: extract_pos() ")
        raise KeyError


def extract_barcode_pos(reads, start, stop, header):
    """
    Extract sequence of adaptator from pos.

    params: seq
    params: start
    params: stop
    params: header
    """
    stop = stop + 1
    if header:
        if start == 0:
            seq = reads.header[-stop:]
            return {'seq': seq, 'qual': [40 for x in range(len(seq))]}
        seq = reads.header[-stop:-start]
        return {'seq': seq, 'qual': [40 for x in range(len(seq))]}
    if start == 0:
        return {
            'seq': reads.seq[:stop],
            'qual': reads.qual[:stop]
        }
    stop = stop - 1
    return {
        'seq': reads.seq[start:stop],
        'qual': reads.qual[start:stop]
    }


def extract_barcode(reads, config, adaptator, ntuple, verbose=False):
    """
    Extract barcode from config from adaptator.

    params: seq
    params: config
    params: adaptator
    """
    if verbose:
        test_adaptator(config=config,
                       adaptator=adaptator,
                       ntuple=ntuple,
                       verbose=verbose)
    coords = config[adaptator]['coords']
    return extract_barcode_pos(
        reads=reads,
        start=coords['start'],
        stop=coords['stop'],
        header=coords['header'])


def write_umi_in_header(reads, umi):
    """
    Copy the UMI in the header separated by an _ to use later with UMI_tools.

    params: seq
    params: config
    params: adaptator
    """
    header = reads.header.split(" ")
    header[0] += "_" + str(umi['seq'])
    reads.header = " ".join(header)
    return reads


def list_adaptator_barcode(config, adaptator, ntuple, verbose=False):
    """
    Create a list of concatened barecode seq and a list of concatened barcode
    names from the config.

    params: config
    params: adaptator
    """
    barcode_list = dict()
    if (adaptator not in ["UMI", "conditions"] and
            config[adaptator]['coords']['reads'] == ntuple):
        for sample in config[adaptator]['samples']:
            barcode_list[sample['name']] = sample['seq']
        return barcode_list
    if verbose:
        print("error: list_adaptator_barcode() cannot list barcode for " +
              str(adaptator) + " with reads " + str(ntuple))
    raise KeyError


def list_reads_number(config):
    """
    return the number of different reads from config

    :params config
    :return:
    """
    read_number = 0
    for adaptator in config:
        if not adaptator == 'conditions':
            if int(config[adaptator]['coords']['reads']) > read_number:
                read_number = int(config[adaptator]['coords']['reads'])
    return read_number + 1


def create_barcode_dictionaries(config, mismatch=None):
    """
    Build list of suffixtree from config.

    :params (dict) a config dictionnaly
    :return:
    """
    adaptators_dict = suffix_tree.Forest(mismatch=mismatch)
    for adaptator in config:
        if adaptator not in ['UMI', 'conditions']:
            for barcode in config[adaptator]['samples']:
                adaptators_dict.add_sequence(
                    adaptator=adaptator,
                    sequence=barcode['seq'],
                    barcode=barcode['name']
                )
    return adaptators_dict


def match_barcode(reads, config, adaptator, barcode_dictionary, ntuple,
                  verbose=False):
    """
    Search barcode suffixtree.

    params: seq
    params: config
    params: adaptator
    params: barcode_dictionary
    """
    try:
        read = extract_barcode(
            reads=reads,
            config=config,
            adaptator=adaptator,
            ntuple=ntuple,
            verbose=verbose
        )
        return barcode_dictionary.search_reads(
            adaptator=adaptator,
            seq=read['seq'],
            qual=read['qual'],
            cache=True,
            verbose=verbose
        )
    except KeyError:
        if verbose:
            print("error: match_barcode() \"" +
                  str(reads.seq) +
                  "\" not found in \"" +
                  str(adaptator) +
                  "\" for reads " +
                  str(ntuple))
    except IndexError:
        if verbose:
            print("error: match_barcode() \"" +
                  str(reads.seq) +
                  "\" not found in \"" +
                  str(adaptator) +
                  "\" for reads " +
                  str(ntuple))


def match_barcodes(reads, config, barcode_dictionary, ntuple, verbose=False):
    """
    Search all barcodes

    params: seq
    params: config
    params: adaptator_dictionary
    """
    barode_names = list()
    for adaptator in config:
        if adaptator not in ['UMI', 'conditions']:
            if config[adaptator]['coords']['reads'] == ntuple:
                barode_names.append(
                    match_barcode(
                        reads=reads,
                        config=config,
                        adaptator=adaptator,
                        barcode_dictionary=barcode_dictionary,
                        ntuple=ntuple,
                        verbose=verbose
                    )
                )
    return barode_names


def barcode_to_sample(barcodes, config, bcd_dic_found, verbose=False):
    """
    find sample name from a list of barcode

    params: barcodes list() of barcode name
    params: config
    """
    try:
        return list(config['conditions'].keys())[
            list(config['conditions'].values()).index(barcodes)]
    except ValueError:
        if verbose:
            print("error: barcode_to_sample() \"" +
                  str(barcodes) +
                  "\" is not in the sample list, assigning to \"unassigned\"")
        if str(barcodes) in bcd_dic_found:
            bcd_dic_found[str(barcodes)] += 1
        else:
            bcd_dic_found[str(barcodes)] = 1
        return "unassigned"


def assign_reads(reads_list, config, barcode_dictionary, bcd_dic_found, verbose=False):
    """
    find sample of a list of paired sequences

    params: seqs list() for fastq sequences
    params: config
    params: adaptator_dictionary
    """
    barcode_names = list()
    ntuple = 0
    for reads in reads_list:
        barcode_names += match_barcodes(
            reads=reads,
            config=config,
            barcode_dictionary=barcode_dictionary,
            ntuple=ntuple,
            verbose=verbose
        )
        ntuple += 1
    return barcode_to_sample(barcodes=barcode_names,
                             config=config,
                             verbose=verbose,
                             bcd_dic_found=bcd_dic_found)


def remove_barcode_pos(reads, start, stop, header):
    """
    Remove sequence of adaptator from pos.

    params: seq
    params: start
    params: stop
    params: header
    """
    stop = stop + 1
    if header:
        size = len(reads.header)
        if start == 0:
            reads.header = reads.header[:(size-stop)]
        else:
            reads.header = reads.header[:(size-stop)] + \
                reads.header[(size-start):]
    else:
        if start == 0:
            reads.seq = reads.seq[stop:]
            reads.qual = reads.qual[stop:]
            reads.qual_str = reads.qual_str[stop:]
        else:
            stop = stop - 1
            reads.seq = reads.seq[0:start] + reads.seq[stop:]
            reads.qual = reads.qual[0:start] + reads.qual[stop:]
            reads.qual_str = reads.qual_str[0:start] + reads.qual_str[stop:]
    return reads


def remove_barcode(reads, config, adaptator, ntuple, verbose=False):
    """
    Remove barcode from sequence (i.e trim read).

    params: seq
    params: config
    params: adaptator
    """
    if verbose:
        test_adaptator(config=config, adaptator=adaptator, ntuple=ntuple,
                       verbose=verbose)
    coords = config[adaptator]['coords']

    return remove_barcode_pos(
        reads=reads,
        start=coords['start_update'],
        stop=coords['stop_update'],
        header=coords['header']
    )


def update_position(config, adaptator, adapt, adaptator_length, ntuple):
    """
    Update barcode position in config file when a barcode is removed

    params: config
    params: adaptator
    params: adapt
    params: adaptator_length
    """
    if (not adapt == 'conditions' and
            not adapt == adaptator and
            config[adapt]['coords']['header'] ==
            config[adaptator]['coords']['header'] and
            config[adapt]['coords']['reads'] == ntuple):
        if (config[adapt]['coords']['start'] >
                config[adaptator]['coords']['start']):
            config[adapt]['coords']['start_update'] = (
                config[adapt]['coords']['start'] - adaptator_length
            )
            config[adapt]['coords']['stop_update'] = (
                config[adapt]['coords']['stop'] - adaptator_length)
    return config


def update_positions(config, adaptator, ntuple):
    """
    Update barcode position in config file when a barcode is removed

    params: config
    params: barcode
    """
    adaptator_length = (
        config[adaptator]['coords']['stop'] -
        config[adaptator]['coords']['start']
    ) + 1
    update_next = False
    for adapt in config:
        if update_next:
            config = update_position(config=config,
                                     adaptator=adaptator,
                                     adapt=adapt,
                                     adaptator_length=adaptator_length,
                                     ntuple=ntuple)
        if adapt == adaptator:
            update_next = True
    return config


def remove_barcodes(reads, config, ntuple, verbose=False):
    """
    Remove barcodes from sequence (i.e trim read).
    can be call once by read, otherwise adaptator coords doesn't macht anymore

    params: seq
    params: config
    params: reads int()
    return: seq
    """
    if not isinstance(reads, Reads):
        if verbose:
            print("error: remove_barcode(), reads is not of type Reads")
        raise ValueError
    for adaptator in config:
        if (not adaptator == 'conditions' and
                ntuple == config[adaptator]['coords']['reads']):
            reads = remove_barcode(
                reads=reads,
                config=config,
                adaptator=adaptator,
                ntuple=ntuple,
                verbose=verbose
            )
    return reads


def write_seq(reads, fout, config, ntuple, verbose=False):
    """
    write sequence without adaptor in the correct file

    params: seq
    params: fout
    params: config
    params: reads int()
    """
    try:
        remove_barcodes(reads=reads,
                        config=config,
                        ntuple=ntuple,
                        verbose=verbose).write(fout=fout)
    except IOError as err:
        print("error: write_seq() ")
        raise err


def write_seqs(reads_list, fouts, config, sample, umi_bol, verbose=False):
    """
    write pair of sequences without adaptor in the correct files

    params: seq
    params: fouts
    params: config
    params: sample
    """
    ntuple = 0
    if umi_bol:
        umi = extract_barcode(reads_list[(config['UMI']['coords']['reads'])],
                              config,
                              'UMI',
                              config['UMI']['coords']['reads'],
                              verbose)

    for reads in reads_list:
        reads = write_umi_in_header(reads=reads,
                                    umi=umi)
        write_seq(reads=reads,
                  fout=fouts[sample][ntuple],
                  config=config,
                  ntuple=ntuple,
                  verbose=verbose)
        ntuple += 1


def read_reads(fins, reads_list, ntuple, line_number):
    """
    read a read from handle

    params: fin file handle
    return: read str()
    """
    if line_number == 0:
        for reads in ntuple:
            reads_list[reads].header = fins[reads][1:-1]
    if line_number == 1:
        for reads in ntuple:
            reads_list[reads].seq = fins[reads][:-1]
    if line_number == 3:
        for reads in ntuple:
            reads_list[reads].qual_str = fins[reads][:-1]
            reads_list[reads].str2qual(reads_list[reads].qual_str)
    return reads_list


def parse_ntuples_fastq(ffastqs,
                        fouts,
                        config,
                        ntuple,
                        umi_bol,
                        mismatch=None,
                        verbose=False):
    """
    process a fastq files

    params: ffastq a buffer of a fastq file
    params: config
    """
    barcode_dictionary = create_barcode_dictionaries(config=config,
                                                     mismatch=mismatch)
    sequences_number = 0
    line_number = 0
    reads_list = list()
    Samples = {}
    Bcd_dic_found = {}

    for read in ntuple:
        reads_list.append(Reads())
    for list_ffastqs in zip(*ffastqs):
        reads_list = read_reads(
            fins=list_ffastqs,
            ntuple=ntuple,
            reads_list=reads_list,
            line_number=line_number,
        )
        if line_number == 3:
            sample = assign_reads(reads_list=reads_list,
                                  config=config,
                                  barcode_dictionary=barcode_dictionary,
                                  verbose=verbose,
                                  bcd_dic_found=Bcd_dic_found)
            write_seqs(reads_list=reads_list,
                       fouts=fouts,
                       config=config,
                       sample=sample,
                       umi_bol=umi_bol,
                       verbose=verbose)

            if sample in Samples:
                Samples[sample] += 1
            else:
                Samples[sample] = 1

            line_number = 0
        else:
            line_number += 1
        sequences_number += 1

    print("\n** Ending splitting at",\
    time.strftime("%A %d %B %Y %H:%M:%S"),"**")
    print("\nnumber of processed sequences: " +
          str(int(sequences_number/4)) +
          " x " +
          str(len(ntuple)) +
          " files : ")
    for elmts in Samples:
        print(elmts, "\t", Samples[elmts], "reads")
    print("\nunassigned barcodes found : ")
    for elmts in Bcd_dic_found:
        print(elmts, "\t", Bcd_dic_found[elmts], "reads")


def out_files(fastqs, condition, results_path):
    """
    generate list of output file for a given condition

    params: fastqs a list() of fastq files path
    params: condition
    params: results_path
    """
    try:
        fastqs_out = list()
        for fastq in fastqs:
            fastq = os.path.split(fastq)[1]
            fastqs_out.append(results_path + '/' + condition + '/' + fastq)
            if os.path.isfile(fastqs_out[-1]):
                error_msg = ("error: the file " +
                             fastqs_out[-1] +
                             " exists, and flexi_splitter is not going to" +
                             " erase it for you")
                print("error: the file " +
                      fastqs_out[-1] +
                      " exists, and flexi_splitter is not going to erase it" +
                      " for you")
                raise IOError(error_msg)
        return fastqs_out
    except Exception as err:
        print("error: out_files() ")
        raise err


def open_output(fastqs, config, stack, results_path, gzed):
    """
    open output files

    params: fastqs a list() of fastq files path
    params: config
    params: stack
    params: results_path
    """
    try:
        fouts = dict()
        for condition in config['conditions']:
            condition_path = results_path + '/' + condition
            if not os.path.isdir(condition_path):
                os.makedirs(condition_path)
            fastqs_out = out_files(fastqs=fastqs,
                                   condition=condition,
                                   results_path=results_path)

            if gzed:
                fouts[condition] = [
                    stack.enter_context(gzopen(fastq, 'wt')) for fastq in fastqs_out
                ]
            else:
                fouts[condition] = [
                    stack.enter_context(open(fastq, 'w')) for fastq in fastqs_out
                ]
        return fouts
    except IOError as err:
        print("error: open_output()")
        raise err
    except Exception as err:
        print("error: open_output() ")
        raise err


def close_output(fouts, config):
    """
    close output files

    params: fastqs a list() of fastq files path
    params: config
    params: stack
    params: results_path
    """
    try:
        for condition in config['conditions']:
            for fout in fouts[condition]:
                fout.close()
    except Exception as err:
        print("error: close_output() ")
        raise err


def parse_ntuples_fastqs(fastqs,
                         config,
                         results_path,
                         umi_bol,
                         verbose=False,
                         mismatch=None,
                         ntuple_param=None,
                         gzed=False):
    """
    process a list of fastq files

    params: fastqs a list() of fastq files path
    params: config
    """
    try:
        with ExitStack() as stack:
            if gzed:
                ffastqs = [
                    stack.enter_context(
                        gzopen(fastq, 'rt')) for fastq in fastqs
                ]
            else:
                ffastqs = [
                    stack.enter_context(
                        open(fastq, 'r')) for fastq in fastqs
                ]

            fouts = open_output(fastqs=fastqs,
                                config=config,
                                stack=stack,
                                results_path=results_path,
                                gzed=gzed)
            parse_ntuples_fastq(ffastqs=ffastqs,
                                fouts=fouts,
                                config=config,
                                verbose=verbose,
                                mismatch=mismatch,
                                ntuple=range(0, ntuple_param),
                                umi_bol=umi_bol)
            close_output(fouts=fouts,
                         config=config)
    except IOError as err:
        print("error: parse_ntuples_fastqs()")
        print(err)


def usage():
    """
    Print command line help
    """
    print('usage : flexi_splitter -f <inputfile1[,inputfile2...,inputfileN]> \
-o <outputfolder> -c <configfile> [OPTIONS]\n')
    print("mandatory parameters : \n\
        -f, --fastqs   list of fastq files separated by a comma without \
whitespace \n\
        -o, --ofolder  path to the output folder. Need to be empty or if not\n\
                       exists, flexi_splitter creates it\n\
        -c, --config   path to the config file in yaml format\n\noptions : \n\
        -h, --help     print this message\n\
        -v, --verbose  only usefull for debugging\n\
        -m, --mismatch mismatches allowed per adaptor. By default, n-1 \n\
                       mismatches are allowed (n = adaptor length) \n\
        -n, --ntuple   number of matched files. If not set, flexi_splitter try\n\
                       to guess it from the config file\n\
        --version      print flexi_splitter version ")



def check_options(argv):
    """
    Check optagrs options
    """
    version = "1.0.2"

    parameters = dict()
    parameters['verbose'] = False
    parameters['ntuple'] = None

    try:
        opts, args = getopt.getopt(argv, "hvn:f:o:c:m:", ["help",
                                                          "version",
                                                          "fastqs=",
                                                          "ofolder=",
                                                          "config=",
                                                          "verbose",
                                                          "mismatch=",
                                                          "ofolder=",
                                                          "ntuple="])

    except getopt.GetoptError:
        print('error: check_options() invalid option')
        usage()
        raise getopt.GetoptError

    for elmts in opts:
        if elmts[0] in ('-f', '--fastqs'):
            parameters['inputfiles'] = elmts[1].split(',')
        elif elmts[0] in ('-o', '--ofolder'):
            parameters['outputfolder'] = elmts[1]
        elif elmts[0] in ('-c', '--config'):
            parameters['config'] = elmts[1]
        elif elmts[0] in ('-v', '--verbose'):
            parameters['verbose'] = True
        elif elmts[0] in ('-m', '--mismatch'):
            parameters['mismatch'] = elmts[1]
            print("mismatch allowed : " + parameters['mismatch'])
        elif elmts[0] in ('-n', '--ntuple'):
            parameters['ntuple'] = int(elmts[1])
        elif elmts[0] in ('--version'):
            print("flexi_splitter", version)
            exit(0)
        elif elmts[0] in ('-h', '--help'):
            usage()
            exit(0)

    if (parameters['inputfiles'][0].split('.')[-1] == 'gz' and
            parameters['inputfiles'][0].split('.')[-2] == 'fastq'):
        parameters['gzed'] = True
    elif parameters['inputfiles'][0].split('.')[-1] == 'fastq':
        parameters['gzed'] = False
    else:
        print("Error : unknow file format : " +
              parameters['inputfiles'][0].split('.')[-1])
        usage()

    return parameters


def check_files(outputfolder, inputfile, configfile):
    """
    Check validity of input files
    """
    print("\n** Checking input and output files **")
    for elmts in inputfile:
        if not os.path.exists(elmts):
            print("error: check_files() " +
                  elmts +
                  " file doesn't exist"
                  )
            usage()
            raise IOError

    if not os.path.exists(outputfolder):
        print(outputfolder + " does not exist : Creating it ")
        os.makedirs(outputfolder)

    if not os.path.exists(configfile):
        print("error: check_files() config file doesn't exist")
        usage()
        raise IOError

    print('\nInput file: ', inputfile)
    print('Output folder: ', outputfolder)
    print('Config file: ', configfile)


def check_configfile(config, umi_bol):
    """
    Check existence of config file
    """
    print("\n** Checking config file **")
    try:
        config['conditions']
    except KeyError:
        print("error: check_configfile() no conditions section " +
              "in the config file")
        raise KeyError

    print("found ", len(config)-1, "adatators: ")

    for adpt in config:
        if (adpt not in ['UMI', 'conditions']):
            print("\t" + adpt + " :", len(config[adpt]["samples"]), "barcodes")
        elif adpt == 'UMI':
            print("\t" + 'UMI')

    print("\nfound ", len(config['conditions'])-1, "samples")
    print("\nusing UMI : ", umi_bol)


def main(argv=None):
    """
    Main function for command line usage
    """

    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        usage()
        exit(0)

    """
    check and grep optionscreate_barcode_dict
    """
    parameters = check_options(argv)

    """
    check_files
    """
    check_files(outputfolder=parameters['outputfolder'],
                inputfile=parameters['inputfiles'],
                configfile=parameters['config'])

    """
    load the config file
    """
    config = load_yaml(parameters['config'])

    if parameters['ntuple'] is None:
        parameters['ntuple'] = list_reads_number(config)

    umi_bol = False
    for adpt in config:
        if adpt == 'UMI':
            umi_bol = True

    """
    test if config file is OK
    """
    check_configfile(config=config,
                     umi_bol=umi_bol)

    """
    main function
    """

    if 'mismatch' not in parameters:
        parameters['mismatch'] = None
    else:
        parameters['mismatch'] = int(parameters['mismatch'])
    print("\n** Starting splitting file  at",\
    time.strftime("%A %d %B %Y %H:%M:%S"),"**")
    parse_ntuples_fastqs(fastqs=parameters['inputfiles'],
                         config=config,
                         results_path=parameters['outputfolder'],
                         verbose=parameters['verbose'],
                         mismatch=parameters['mismatch'],
                         ntuple_param=parameters['ntuple'],
                         gzed=parameters['gzed'],
                         umi_bol=umi_bol)


if __name__ == "__main__":
    main()
