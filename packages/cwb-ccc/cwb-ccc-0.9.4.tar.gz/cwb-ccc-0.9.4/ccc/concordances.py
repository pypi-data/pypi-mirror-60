#! /usr/bin/env python
# -*- coding: utf-8 -*-

from random import sample
# part of module
from .cwb import anchor_query_to_anchors
# requirements
from pandas import DataFrame


class Concordance(object):

    def __init__(self,
                 engine,
                 context=20,
                 s_break='text',
                 order='random',
                 p_show=[],
                 cut_off=100):

        self.engine = engine

        self.settings = {
            'context': context,
            's_break': s_break,
            'p_show': p_show,
            'order': order,
            'cut_off': cut_off
        }

    def query(self, query, anchored=None):

        if anchored is None:
            anchored = len(anchor_query_to_anchors(query)) > 0

        if not anchored:
            df_node = self.engine.df_node_from_query(
                query,
                self.settings['s_break']
            )
        else:
            df_node = self.engine.df_anchor_from_query(
                query,
                self.settings['s_break']
            )

        if len(df_node) == 0:
            return {}

        concordance = df_node_to_concordance(
            engine=self.engine,
            df_node=df_node,
            context=self.settings['context'],
            order=self.settings['order'],
            cut_off=self.settings['cut_off'],
            p_show=self.settings['p_show'],
            anchored=anchored
        )

        return concordance


# node to concordance (needs engine) ###########################################
def df_node_to_concordance(engine,
                           df_node,
                           context=20,
                           order='random',
                           cut_off=100,
                           p_show=[],
                           anchored=None,
                           role='match'):
    """ formats concordance lines for a df_node """

    # avoid trying to get more concordance lines than there are
    topic_matches = set(df_node['match_start'])
    if not cut_off or len(topic_matches) < cut_off:
        cut_off = len(topic_matches)

    # take appropriate sub-set
    if order == 'random':
        topic_matches_cut = sample(topic_matches, cut_off)
    elif order == 'first':
        topic_matches_cut = sorted(list(topic_matches))[:cut_off]
    elif order == 'last':
        topic_matches_cut = sorted(list(topic_matches))[-cut_off:]
    else:
        raise NotImplementedError("concordance order not implemented")

    # check if there's anchors
    anchor_keys = set(df_node.columns) - {'region_start', 'region_end', 's_id',
                                          'match_end', 'match_start'}

    # automatically determine by default
    if anchored is None:
        anchored = len(anchor_keys) > 0

    # fill concordance dictionary
    concordance = dict()
    for match_start in topic_matches_cut:

        # take values from row
        row = df_node.loc[df_node['match_start'] == match_start]
        # int(row.pop('match_start'))
        match_end = int(row.pop('match_end'))
        # s_id = row.pop('s_id')
        s_start = int(row.pop('region_start'))
        s_end = int(row.pop('region_end'))

        # handle optional anchors
        if anchored:
            anchors = dict()
            for anchor in anchor_keys:
                anchors[anchor] = int(row[anchor])

        # init concordance line variables
        roles = list()
        offset = list()
        cpos = list()

        # fill cpos, role, offset
        for position in range(
                max([s_start, match_start-context]),
                min([match_end+context, s_end])+1
        ):
            cpos.append(position)
            roles.append(position >= match_start and position <= match_end)
            if position < match_start:
                offset.append(position - match_start)
            elif position > match_end:
                offset.append(position - match_end)
            else:
                offset.append(0)

        # lexicalize positions
        word = engine.lexicalize_positions(cpos)

        # transform concordance line to dataframe
        concordance_line = DataFrame(
            index=cpos,
            data={
                'word': word,
                role: roles,
                'offset': offset
            }
        )
        concordance_line.index.name = 'cpos'

        # handle optional anchors
        if anchored:
            concordance_line['anchor'] = None
            for anchor in anchors.keys():
                if anchors[anchor] != -1:
                    concordance_line.at[anchors[anchor], 'anchor'] = anchor

        # handle additional p-attributes
        for p_att in p_show:
            p_show_tokens = engine.lexicalize_positions(cpos, p_att)
            concordance_line[p_att] = p_show_tokens

        # save concordance line
        concordance[match_start] = concordance_line

    return concordance
