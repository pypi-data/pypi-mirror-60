#!/usr/bin/env python
#
# processing.py - Cleaning and processing parsing and functions.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains functionality for parsing the ``Process`` column of
the processing table, and the ``Clean`` column of the variable
table. Definitions of the available (pre-)processing functions are in the
:mod:`cleaning_functions` and :mod:`.processing_functions` modules.


The :func:`processData` function is also defined here - it executes the
processes defined in the processing table.


Special processing functions can be applied to a variable's data by adding
them to the ``Clean`` and ``Process`` columns of the variable or processing
table respectively.  Processing is specified as a comma-separated list of
process functions - for example::


    process1, process2(), process3('arg1', arg2=1234)


The :func:`parseProcesses` function parses such a line, and returns a list of
:class:`Process` objects which can be used to query the process name and
arguments, and to run each process.
"""


import functools as ft
import itertools as it
import os.path   as op
import              os
import              glob
import              logging
import              tempfile
import              collections

import pyparsing as pp
import pandas    as pd

from . import util
from . import custom


log = logging.getLogger(__name__)


def processData(dtable):
    """Applies all processing specified in the processing table to the data.

    :arg dtable: The :class:`DataTable` instance.
    """

    ptable = dtable.proctable

    for i in ptable.index:

        # refresh the list of all variables
        # in the data on each iteration, as
        # a previously executed process may
        # add/remove variables to/from the
        # data.
        all_vids = dtable.variables
        all_vids = [v for v in all_vids if v != 0]

        # For each process, the processing table
        # contains a "process variable type",
        # a list of vids, and the process itself.
        # The pvtype is one of:
        #   - vids:                   apply the process to the specified vids
        #   - independent:            apply the process independently to the
        #                             specified vids
        #   - all:                    apply the process to all vids
        #   - all_independent:        apply the process independently to all
        #                             vids
        #   - all_except:             apply the process to all vids except the
        #                             specified ones
        #   - all_independent_except: apply the process independently to all
        #                             vids except the specified ones
        pvtype, vids = ptable.loc[i, 'Variable']
        procs        = ptable.loc[i, 'Process']

        # Build a list of lists of vids, with
        # each vid list a group of variables
        # that is to be processed together.

        # apply independently to every variable
        if pvtype in ('all_independent', 'all_independent_except'):
            if pvtype.endswith('except'): exclude = vids
            else:                         exclude = []
            vids = [[v] for v in all_vids if v not in exclude]

        # apply simultaneously to every variable
        elif pvtype in ('all', 'all_except'):
            if pvtype.endswith('except'): exclude = vids
            else:                         exclude = []
            vids = [[v for v in all_vids if v not in exclude]]

        # apply independently to specified variables
        elif pvtype == 'independent':
            vids = [[v] for v in vids if dtable.present(v)]

        # apply simultaneously to specified variables
        else:  # 'vids'
            vids = [[v for v in vids if dtable.present(v)]]

        vids = [vg for vg in vids if len(vg) > 0]

        if len(vids) == 0:
            continue

        # Run each process sequentially -
        # each process may be parallelised
        # by the runProcess function
        for proc in procs.values():
            runProcess(proc, dtable, vids)


def runProcess(proc, dtable, vids):
    """Called by :func:`processData`. Runs the given process, and updates
    the :class:`.DataTable` as needed.

    :arg proc:   :class:`.Process` to run.
    :arg dtable: :class:`.DataTable` containing the data.
    :arg vids:   List of lists, groups of variable IDs to run the process on.
    """

    # We assume that processes which work on more
    # than one variable will manage their own
    # concurrency. Processes which work on just
    # one variable are executed in parallel here.
    runparallel = [vg for vg in vids if len(vg) == 1]
    runserial   = [vg for vg in vids if len(vg)  > 1]
    allvids     = list(it.chain(*vids))
    results     = []

    if len(runparallel) + len(runserial) == 0:
        return

    log.debug('Running process %s on %u variables %s ...',
              proc.name, len(allvids), allvids[:5])

    fmt = '[{} {} ...] completed in %s (%+iMB)'.format(proc.name, allvids[:5])
    with util.timed(proc.name, log, logging.DEBUG, fmt=fmt), \
         tempfile.TemporaryDirectory() as workDir:

        # Execute single-variable
        # processes in parallel
        if len(runparallel) > 0:
            with dtable.pool() as pool:

                subtables  = [dtable.subtable(dtable.columns(vg[0]))
                              for vg in runparallel]
                workDirs   = [op.join(workDir, str(i))
                              for i in range(len(runparallel))]
                func       = ft.partial(runParallelProcess, proc)
                parresults = pool.starmap(func, zip(subtables,
                                                    runparallel,
                                                    workDirs))

                subtables, parresults = zip(*parresults)

                results.extend(parresults)

                # Merge results back in - this
                # includes in-place modifications
                # to columns, and column flags/
                # metadata. Added/removed columns
                # are handled below.
                for subtable in subtables:
                    dtable.merge(subtable)

        # Processes which act on more
        # than one column can take care
        # of their own parallelism
        for vg in runserial:
            results.append(proc.run(dtable, vg))

        remove  = []
        add     = []
        addvids = []
        addmeta = []

        for r in results:
            results = unpackResults(proc, r)
            remove .extend(results[0])
            add    .extend(results[1])
            addvids.extend(results[2])
            addmeta.extend(results[3])

        # Parallelised processes save new
        # series to disk - load them back in.
        if log.getEffectiveLevel() >= logging.DEBUG:
            savedSeries = list(glob.glob(
                op.join(workDir, '**', '*.pkl'), recursive=True))
            if len(savedSeries) > 0:
                log.debug('[%s]: Reading %u new column from %s %s ...',
                          proc.name, len(savedSeries), workDir, vids[:5])

        for i in range(len(add)):
            if isinstance(add[i], str):
                add[i] = pd.read_pickle(add[i])

        # remove columns first, in case
        # there is a name clash between
        # the old and new columns.
        if len(remove) > 0: dtable.removeColumns(remove)
        if len(add)    > 0: dtable.addColumns(add, addvids, addmeta)


def runParallelProcess(proc, dtable, vids, workDir):
    """Used by :func:`runProcess`. Calls ``proc.run``, and returns its
    result and the (possibly modified) ``dtable``.

    :arg proc:   :class:`Process` to run
    :arg dtable: :class:`DataTable` instance (probably a subtable)
    :arg vids:   List of varisable IDs
    :returns:    A tuple containing:
                  - A reference to ``dtable``
                  - the result of ``proc.run()``
    """
    os.mkdir(workDir)
    result = proc.run(dtable, vids)
    remove, add, addvids, addmeta = unpackResults(proc, result)

    # New columns are saved to disk,
    # rather than being copied back
    # to the parent process. We only
    # do this if running in a
    # multiprocessing context
    if not util.inMainProcess() and len(add) > 0:
        log.debug('[%s]: Saving %u new columns to %s %s...',
                  proc.name, len(add), workDir, vids[:5])
        for i, series in enumerate(add):
            fname  = op.join(workDir, '{}.pkl'.format(i))
            add[i] = fname
            series.to_pickle(fname)

    return dtable, (remove, add, addvids, addmeta)


def unpackResults(proc, result):
    """Parses the results returned by a :class:`.Process`. See the
    :mod:`.processing_functions` module for details on what can be returned
    by a processing function.

    :arg proc:   The :class:`.Process`
    :arg result: The value returned by :meth:`.Process.run`.
    :returns:    A tuple containing:
                  - List of columns to remove
                  - List of new series to add
                  - List of variable IDs for new series
                  - List of metadata for new series
    """

    remove  = []
    add     = []
    addvids = []
    addmeta = []

    if result is None:
        return remove, add, addvids, addmeta

    error = ValueError('Invalid return value from '
                       'process {}'.format(proc.name))

    def expand(res, length):
        if res is None: return [None] * length
        else:           return res

    # columns to remove
    if isinstance(result, list):
        remove.extend(result)

    elif isinstance(result, tuple):

        # series/vids to add
        if len(result) == 2:
            add    .extend(result[0])
            addvids.extend(expand(result[1], len(result[0])))
            addmeta.extend(expand(None,      len(result[0])))

        # columns to remove, and
        # series/vids to add
        elif len(result) in (3, 4):

            if len(result) == 3:
                result = list(result) + [None]

            remove .extend(result[0])
            add    .extend(result[1])
            addvids.extend(expand(result[2], len(result[1])))
            addmeta.extend(expand(result[3], len(result[1])))
        else:
            raise error
    else:
        raise error

    return remove, add, addvids, addmeta


class NoSuchProcessError(Exception):
    """Exception raised by the :class:`Process` class when an unknown
    process name is specified.
    """


class Process:
    """Simple class which represents a single processing step. The :meth:`run`
    method can be used to run the process on the data for a specific variable.
    """


    def __init__(self, ptype, name, args, kwargs):
        """Create a ``Process``.

        :arg ptype: Process type - either ``cleaner`` or ``processor``
                    (see the :mod:`.custom` module).
        :arg name:  Process name
        :arg args:  Positional arguments to pass to the process function.
        :arg args:  Keyword arguments to pass to the process function.
        """

        # cleaner functions are not
        # defined in processing_functions,
        # so in this case func will be None.
        self.__ptype    = ptype
        self.__name     = name
        self.__args     = args
        self.__kwargs   = kwargs
        self.__metaproc = kwargs.pop('metaproc', None)


    def __repr__(self):
        """Return a string representation of this ``Process``."""
        args    = ','.join([str(v) for v in self.__args])
        kwargs  = ','.join(['{}={}'.format(k, v) for k, v in
                           self.__kwargs.items()])

        allargs = [args, kwargs]
        allargs = [a for a in allargs if a != '']
        allargs = ', '.join(allargs)
        return '{}[{}]({})'.format(self.__name, self.__ptype, allargs)


    @property
    def name(self):
        """Returns the name of this ``Process``. """
        return self.__name


    @property
    def args(self):
        """Returns the positional arguments for this ``Process``. """
        return self.__args


    @property
    def kwargs(self):
        """Returns the keyword arguments for this ``Process``. """
        return self.__kwargs


    def run(self, *args):
        """Run the process on the data, passing it the given arguments,
        and any arguments that were passed to :meth:`__init__`.
        """
        result = custom.run(self.__ptype,
                            self.__name,
                            *args,
                            *self.__args,
                            **self.__kwargs)

        if self.__metaproc is not None and \
           isinstance(result, tuple)   and \
           len(result) == 4:

            # The first argument to a process
            # should be the data table
            dtable = args[0]

            # The 3rd/4th args returned from a
            # process hould be a list of vids,
            # and a list of metadata for each of
            # them
            vids    = result[2]
            meta    = result[3]
            mproc   = self.__metaproc
            newmeta = []

            for vid, vmeta in zip(vids, meta):
                try:
                    newval = custom.runMetaproc(mproc, dtable, vid, vmeta)
                    newmeta.append(newval)

                except Exception as e:
                    log.warning('Metadata processing function '
                                'failed (vid %u): %s', vid, e)
                    newmeta.append(vmeta)

            result = tuple(list(result[:3]) + [newmeta])

        return result


def parseProcesses(procs, ptype):
    """Parses the given string containing one or more comma-separated process
    calls, as defined in the processing table. Returns a list of
    :class:`Process` objects.

    :arg procs: String containing one or more comma-separated (pre-)processing
                steps.

    :arg ptype: either ``cleaner`` or ``processor``

    :returns:   A list of :class:`Process` objects.

    """

    def makeProcess(toks):
        name = toks[0]

        args   = ()
        kwargs = {}

        if len(toks) == 2:
            if isinstance(toks[1], tuple):
                args   = toks[1]
            elif isinstance(toks[1], dict):
                kwargs = toks[1]
        elif len(toks) == 3:
            args, kwargs = toks[1:]

        if not custom.exists(ptype, name):
            raise NoSuchProcessError(name)

        return Process(ptype, name, args, kwargs)

    parser = pp.delimitedList(makeParser().setParseAction(makeProcess))

    try:
        parsed = parser.parseString(procs, parseAll=True)
    except Exception as e:
        log.error('Error parsing process list "{}": {}'.format(procs, e))
        raise e

    return list(parsed)


@ft.lru_cache()
def makeParser():
    """Generate a ``pyparsing`` parser which can be used to parse a single
    process call in the processing table.
    """

    lparen   = pp.Literal('(').suppress()
    rparen   = pp.Literal(')').suppress()

    def convertBoolean(tok):
        tok = tok[0]
        if   tok == 'True':  return True
        elif tok == 'False': return False
        else:                return tok

    def parseArgs(toks):
        return [tuple(toks)]

    def parseKwargs(toks):
        kwargs = collections.OrderedDict()
        for i in range(0, len(toks), 2):
            kwargs[toks[i]] = toks[i + 1]
        return kwargs

    funcName = pp.pyparsing_common.identifier
    argval   = (pp.QuotedString('"')                                       ^
                pp.QuotedString("'")                                       ^
                pp.pyparsing_common.number                                 ^
                pp.oneOf(['True', 'False']).setParseAction(convertBoolean) ^
                pp.Literal('None').setParseAction(pp.replaceWith(None)))
    kwargs   = (pp.pyparsing_common.identifier +
                pp.Literal('=').suppress() +
                argval)
    posargs  = pp.delimitedList(argval).setParseAction(parseArgs)
    kwargs   = pp.delimitedList(kwargs).setParseAction(parseKwargs)
    allargs  = pp.delimitedList(pp.Optional(posargs) + pp.Optional(kwargs))
    allargs  = lparen   + pp.Optional(allargs) + rparen
    function = funcName + pp.Optional(allargs)

    return function
