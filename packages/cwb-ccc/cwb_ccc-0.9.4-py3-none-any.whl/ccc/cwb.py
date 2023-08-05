#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
from glob import glob
from collections import Counter
# part of module
from .cqp_interface import CQP
from .utils import Cache, create_identifier
# requirements
from pandas import DataFrame, read_csv, to_numeric
from CWB.CL import Corpus
from io import StringIO


# some utilities that don't need the engine
def anchor_query_to_anchors(anchor_query, strict=False):
    """ get anchors present in query """

    anchors = dict()
    p = re.compile(r"@\d")

    for m in p.finditer(anchor_query):
        if strict:
            if m.group() in anchors.keys():
                raise KeyError('duplicate keys provided')
        anchors[m.group()] = [m.start(), m.end()]

    keys = [int(a[1]) for a in anchors.keys()]

    return keys


def dump_to_df_node(dump, nr_columns=4):
    """ convert cqp output to pandas dataframe """
    if nr_columns == 4:
        df = read_csv(StringIO(dump),
                      sep="\t", header=None, index_col=[0, 1],
                      names=["match_start", "match_end", "target", "keyword"],
                      dtype=int)
    elif nr_columns == 2:
        df = read_csv(StringIO(dump),
                      sep="\t", header=None,
                      names=["target", "keyword"],
                      dtype=int)
    return df


class CWBEngine(object):
    """ interface to CWB, convenience wrapper """

    def __init__(self,
                 corpus_name,
                 registry_path="/usr/local/share/cwb/registry/",
                 lib_path=None,
                 cqp_bin="cqp",
                 cache_path="/tmp/ccc-cache"):
        """Establishes connection to indexed corpus. Raises KeyError if corpus
        not in registry.
        """

        # set cache
        self.cache = Cache(cache_path)

        # registry path
        self.registry_path = registry_path

        # obligatory corpus settings
        self.corpus_name = corpus_name

        # set interface
        self.corpus = Corpus(
            self.corpus_name,
            registry_dir=self.registry_path
        )
        self.cqp = CQP(
            bin=cqp_bin,
            options='-c -r ' + self.registry_path
        )

        # activate corpus
        self.cqp.Exec(self.corpus_name)

        # get corpus attributes
        df = read_csv(StringIO(self.cqp.Exec("show cd;")), sep="\t",
                      names=['att', 'value', 'annotation'])
        self.corpus_attributes = df

        # get corpus size
        self.corpus_size = len(self.corpus.attribute('word', 'p'))

        # load macros and wordlists
        self.lib_path = lib_path
        if self.lib_path:
            self.read_lib(self.lib_path)

    def read_lib(self, path_lib):
        """reads macros and worldists"""

        # wordlists
        wordlists = glob(os.path.join(path_lib, "wordlists", "*"))
        for wordlist in wordlists:
            name = wordlist.split("/")[-1].split(".")[0]
            abs_path = os.path.abspath(wordlist)
            cqp_exec = 'define $%s < "%s";' % (
                name, abs_path
            )
            self.cqp.Exec(cqp_exec)

        # macros
        macros = glob(os.path.join(path_lib, "macros", "*"))
        for macro in macros:
            abs_path = os.path.abspath(macro)
            cqp_exec = 'define macro < "%s";' % abs_path
            self.cqp.Exec(cqp_exec)

    def _df_node_from_query(self, query, s_break, context=50,
                            match_strategy='standard'):
        """see df_node_from_query, which is a cached version of this method"""
        # matching strategy
        self.cqp.Exec('set MatchingStrategy "%s";' % match_strategy)

        # run query
        query += " within %s;" % s_break
        self.cqp.Query(query)
        cqp_result = self.cqp.Dump()

        # return empty dataframe if query has no results
        if cqp_result == [['']]:
            return DataFrame()

        # transform to dataframe
        df = DataFrame(cqp_result)
        df.columns = ['match_start', 'match_end', 'keyword', 'target']
        df = df.astype(int)

        # confine regions
        df_node = self.confine_df_node(df, s_break, context)

        return df_node

    def df_node_from_query(self, query, s_break, context=50,
                           match_strategy='standard'):
        """executes query within s_break to get df_node

        :param str query: valid CQP query (without 'within' clause)
        :param str s_break: s-attribute to confine regions
        :param int context: maximum context around node (symmetric)

        :return: df_node with 5 columns (match_start, match_end,
        region_start, region_end, s_id)
        :rtype: pd.DataFrame
        """

        # cache
        idx = create_identifier(self.corpus_name, self.lib_path, 'df_node_from_query',
                                query, s_break, context, match_strategy)
        cached_data = self.cache.get(idx)

        # create result
        if cached_data is None:
            df_node = self._df_node_from_query(query, s_break, context=50,
                                               match_strategy='standard')
            self.cache.set(idx, df_node)
        else:
            df_node = cached_data
        return df_node

    def _df_anchor_from_query(self, anchor_query, s_break, context=50,
                              match_strategy="standard"):
        """see df_anchor_from_query, which is a cached version of this method"""

        # check which anchors there are
        anchors = anchor_query_to_anchors(anchor_query)

        # matching strategy
        self.cqp.Exec('set MatchingStrategy "%s";' % match_strategy)

        # first run: 0 and 1
        self.cqp.Exec("set AnchorNumberTarget 0; set AnchorNumberKeyword 1;")
        self.cqp.Exec("Result = " + anchor_query + " within " + s_break + ";")

        dump = self.cqp.Exec("dump Result;")

        # convert to df_anchor
        df_anchor = dump_to_df_node(dump)
        df_anchor.columns = [0, 1]

        # if there's nothing to return ...
        if df_anchor.empty:
            return DataFrame()

        # join all the other ones
        for pair in [(2, 3), (4, 5), (6, 7), (8, 9)]:
            if pair[0] in anchors or pair[1] in anchors:
                # load matches
                self.cqp.Exec("Result;")
                # set appropriate anchors
                self.cqp.Exec(
                    "set AnchorNumberTarget %d; set AnchorNumberKeyword %d;" % pair
                )
                self.cqp.Exec('Temp = <match> ( %s );' % anchor_query)
                dump = self.cqp.Exec("dump Temp;")
                df = dump_to_df_node(dump)
                df.columns = [pair[0], pair[1]]
                df_anchor = df_anchor.join(df)

        # re-set CQP
        self.cqp.Exec(self.corpus_name)
        self.cqp.Exec("set ant 0; ank 1;")

        # NA handling
        df_anchor.dropna(axis=1, how='all', inplace=True)
        df_anchor = df_anchor.apply(to_numeric, downcast='integer')
        df_anchor.fillna(-1, inplace=True)

        # drop constant columns (contain only -1)
        df_anchor = df_anchor.loc[:, (df_anchor != df_anchor.iloc[0]).any()]

        # move index to columns
        df_anchor = df_anchor.reset_index()

        # confine regions
        df_anchor = self.confine_df_node(df_anchor, s_break, context)

        return df_anchor

    def df_anchor_from_query(self, anchor_query, s_break="text",
                             context=50, match_strategy="standard"):
        """executes anchored query within s_break to get df_anchor

        :param str anchor_query: anchored CQP query (without 'within' clause)
        :param str s_break: s-attribute to confine regions
        :param int context: maximum context around match (symmetric)

        :return: df_anchor with 5 base columns (match_start, match_end,
        region_start, region_end, s_id) and additional columns for each anchor
        :rtype: pd.DataFrame
        """

        # cache
        idx = create_identifier(self.corpus_name, self.lib_path, 'df_anchor_from_query',
                                anchor_query, s_break, context, match_strategy)
        cached_data = self.cache.get(idx)

        # create result
        if cached_data is None:
            df_anchor = self._df_anchor_from_query(anchor_query, s_break, context=50,
                                                   match_strategy='standard')
            self.cache.set(idx, df_anchor)
        else:
            df_anchor = cached_data

        return df_anchor

    def confine_df_node(self, df, s_break, context):

        # get s_break info
        s_regions = self.corpus.attribute(s_break, "s")
        s_region = DataFrame(
            df.match_start.apply(lambda x: s_regions.find_pos(x)).tolist()
        )
        df['s_start'] = s_region[0]
        df['s_end'] = s_region[1]
        df['s_id'] = df.match_start.apply(lambda x: s_regions.cpos2struc(x))

        # confine regions by s_break
        df['region_start'] = df.match_start - context
        df['region_end'] = df.match_end + context
        df.region_start = df[['region_start', 's_start']].max(axis=1)
        df.region_end = df[['region_end', 's_end']].min(axis=1)
        df = df.drop(['s_start', 's_end'], axis=1)

        # downcast values
        df = df.apply(to_numeric, downcast='integer')

        return df

    def count_matches(self, df_dump, p_att="lemma", split=True):
        """counts strings or tokens in df_dump[['match_start', 'match_end']]"""

        # undump the dump
        df_dump = df_dump.astype(str)
        dump = df_dump[['match_start', 'match_end']].values.tolist()
        self.cqp.Undump('Last', table=dump)

        # retrieve context strings
        context_strings = self.cqp.Exec(
            "tabulate Last match .. matchend %s;" % p_att
        ).split("\n")

        # optionally split strings into tokens
        if split:
            tokens = list()
            for t in context_strings:
                tokens += t.split(" ")
        else:
            tokens = context_strings

        # count
        counts = Counter(tokens)
        counts = DataFrame.from_dict(counts, orient='index')
        counts.columns = ['freq']
        counts = counts.sort_values('freq', ascending=False)
        return(counts)

    def lexicalize_positions(self, positions, p_att='word', ignore_missing=True):
        """Fills corpus positions. Raises IndexError if out-of-bounds.

        :param list positions: corpus positions to fill
        :param str p_att: p-attribute to fill positions with

        :return: lexicalizations of the positions
        :rtype: list

        """
        tokens_all = self.corpus.attribute(p_att, 'p')
        tokens_requested = list()
        if ignore_missing:
            positions = [p for p in positions if p != -1]
        for position in positions:
            tokens_requested.append(
                tokens_all[position]
            )
        return tokens_requested

    def get_marginals(self, items, p_att='word', regex=False, flags=1):
        """Extracts marginal frequencies for given items (0 if not in corpus).

        :param list items: items to get marginals for
        :param str p_att: p-attribute to get counts for
        :param int flags: 1 = %c, 2 = %d, 3 = %cd

        :return: counts for each item (indexed by items, column "f2")
        :rtype: DataFrame

        """
        tokens_all = self.corpus.attribute(p_att, 'p')
        counts = list()
        for item in items:
            if not regex:
                try:
                    counts.append(tokens_all.frequency(item))
                except KeyError:
                    counts.append(0)
            else:
                cpos = tokens_all.find_pattern(item, flags=flags)
                counts.append(len(cpos))
        f2 = DataFrame(index=items)
        f2['f2'] = counts
        return f2
