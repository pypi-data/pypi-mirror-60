#! /usr/bin/env python
# -*- coding: utf-8 -*-

from collections import Counter
# requirements
from pandas import DataFrame
from association_measures import measures, frequencies


class Collocates(object):

    def __init__(self, engine, max_window_size=20, s_break='text',
                 order='O11', p_query='lemma', cut_off=100,
                 ams=['z_score', 't_score', 'dice', 'log_likelihood',
                      'mutual_information']):

        self.engine = engine

        self.settings = {
            'max_window_size': max_window_size,
            's_break': s_break,
            'p_query': p_query,
            'order': order,
            'cut_off': cut_off,
            'ams': ams
        }

    def query(self, query, window=5):

        if window > self.settings['max_window_size']:
            print("WARNING: desired window outside maximum window size")
            return DataFrame()

        df_node = self.engine.df_node_from_query(
            query, self.settings['s_break'], context=self.settings['max_window_size']
        )
        df_cooc, match_pos = df_node_to_cooc(
            df_node, self.settings['max_window_size']
        )
        collocates = self.calculate_collocates(
            df_cooc, len(match_pos), window
        )
        return collocates

    def df_cooc_to_counts(self,
                          df_cooc,
                          window,
                          drop_hapaxes=True):

        # slice relevant window
        relevant = df_cooc.loc[abs(df_cooc['offset']) <= window]
        relevant = relevant.drop_duplicates('cpos')

        # number of possible occurence positions within window
        f1_inflated = len(relevant)

        # lexicalize positions
        lex_items = self.engine.lexicalize_positions(
            relevant['cpos'],
            self.settings['p_query']
        )

        # the co-occurrence counts in the window
        counts = Counter(lex_items)
        counts = DataFrame.from_dict(counts, orient='index')
        counts.columns = ["O11"]

        # drop hapax legomena for improved performance
        if drop_hapaxes:
            counts = counts.loc[~(counts['O11'] <= 1)]

        return counts, f1_inflated

    def calculate_collocates(self, df_cooc, f1, window):

        counts, f1_inflated = self.df_cooc_to_counts(
            df_cooc,
            window
        )
        f2 = self.engine.get_marginals(counts.index, self.settings['p_query'])
        contingencies = counts_to_contingencies(
            counts, f1, f1_inflated, f2, self.engine.corpus_size
        )
        collocates = add_ams(
            contingencies, self.settings['ams']
        )
        collocates.sort_values(
            by=self.settings['order'], ascending=False, inplace=True
        )

        return collocates


# utilities ####################################################################
def df_node_to_cooc(df_node, context):
    """ converts df_node to df_cooc """

    # match-positions for book-keeping
    match_pos_set = set()

    # fill cooc lists
    match_list = list()
    cpos_list = list()
    offset_list = list()

    for row in df_node.iterrows():

        # take values from row
        match = row[1]['match_start']
        matchend = row[1]['match_end']
        s_start = row[1]['region_start']
        s_end = row[1]['region_end']

        # fill variables
        for position in range(
                max([s_start, match-context]),
                min([matchend+context, s_end])+1
        ):
            if position < match:
                match_list.append(match)
                cpos_list.append(position)
                offset_list.append(position - match)
            elif position > matchend:
                match_list.append(match)
                cpos_list.append(position)
                offset_list.append(position - matchend)
            else:
                match_pos_set.add(position)

    # concatenate to dataframe
    df_cooc = DataFrame({
        'match': match_list,
        'cpos': cpos_list,
        'offset': offset_list
    })

    # drop node positions
    df_cooc = df_cooc[~df_cooc['cpos'].isin(match_pos_set)]

    return df_cooc, match_pos_set


def counts_to_contingencies(counts, f1, f1_inflated, f2, N):
    """ window counts + marginals to contingency table"""

    # create contingency table
    N_deflated = N - f1
    contingencies = counts
    contingencies = contingencies.join(f2)
    contingencies['N'] = N_deflated
    contingencies['f1'] = f1_inflated
    return contingencies


def add_ams(contingencies, am_names):
    """ annotates a contingency table with AMs """

    # select relevant association measures
    ams_all = {
        'z_score': measures.z_score,
        't_score': measures.t_score,
        'dice': measures.dice,
        'log_likelihood': measures.log_likelihood,
        'mutual_information': measures.mutual_information
    }
    ams = [ams_all[k] for k in am_names if k in ams_all.keys()]

    # rename for convenience
    df = contingencies

    # create the contigency table with the observed frequencies
    df['O11'], df['O12'], df['O21'], df['O22'] = frequencies.observed_frequencies(df)
    # create the indifference table with the expected frequencies
    df['E11'], df['E12'], df['E21'], df['E22'] = frequencies.expected_frequencies(df)

    # calculate all association measures
    measures.calculate_measures(df, measures=ams)
    df.index.name = 'item'

    return df
