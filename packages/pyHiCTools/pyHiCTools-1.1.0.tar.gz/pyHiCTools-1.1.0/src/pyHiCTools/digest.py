#!/usr/bin/env python3


''' Generate an in-silico restriction enzyme digest of a FASTA
    reference sequence.
'''

import re
import sys
import pyCommonTools as pct


def digest(infile, output, read_gzip, write_gzip, restriction):

    ''' Iterate through each infile. '''

    log = pct.create_logger()

    with pct.open_gzip(output, 'wt', write_gzip) as out_obj, \
            pct.open_gzip(infile, 'rt', read_gzip) as in_obj:
        log.info(f'Writing output to {output}.')
        header = 1
        for index, line in enumerate(in_obj):
            if line.startswith('>'):
                if header > 1:
                    find_cut_sites(''.join(seqs), ref, restriction, out_obj)
                ref = line.rsplit()[0][1:]
                log.info(f'Digesting reference {ref}.')
                header += 1
                seqs = []
            elif header == 1 and index == 0:
                log.error(f'FASTA line 1 does not begin with ">".')
                sys.exit(1)
            else:
                seqs.append(line.upper().strip('\n'))
        find_cut_sites(''.join(seqs), ref, restriction, out_obj)


def find_cut_sites(ref_seq, ref, restriction, out_obj):

    log = pct.create_logger()

    if not ref_seq:
        log.error(f'Reference {ref} contains no sequence.')
        ec = 1
    elif invalid_seq(ref_seq):
        log.error(f'Invalid FASTA character in {ref}.')
        ec = 1
    else:
        overhang = restriction.index('^')
        site = restriction.replace('^', '')
        matches = re.finditer(site, ref_seq)
        index = 0
        previous_end = 0
        for match in matches:
            # Skip if restriction sequence at start of reference.
            if match.start() == 0:
                continue
            index += 1
            start = 1 if index == 1 else previous_end + 1
            end = match.start() + overhang
            out_obj.write(f'{ref}\t{start}\t{end}\t{index}\n')
            previous_end = end
        out_obj.write(
            f'{ref}\t{previous_end + 1}\t{len(ref_seq)}\t{index + 1}\n')
        ec = 0
    return ec


def invalid_seq(seq):

    log = pct.create_logger()

    return re.search('[^ATCGURYKMSWBDHVN-]', seq.strip('\n'), re.IGNORECASE)
