#!/usr/bin/env python2.7
# vim: set ts=2 sw=2:
import logging
from itertools import chain
import datetime
import subprocess
import os, os.path
import glob
import sys
import errno
from collections import defaultdict
from os.path import join, exists, basename, dirname

STAGE_NONE      = 'NONE'         # not a stage

## Logging
class SpecialFormatter(logging.Formatter):
  FORMATS = {logging.DEBUG :"DBG: MOD %(module)s: LINE %(lineno)d: %(message)s",
             logging.ERROR : "ERROR: %(message)s",
             logging.INFO : "%(message)s",
             'DEFAULT' : "%(levelname)s: %(message)s"}

  def format(self, record):
    self._fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
    return logging.Formatter.format(self, record)

hdlr = logging.StreamHandler(sys.stderr)
hdlr.setFormatter(SpecialFormatter())
logging.root.addHandler(hdlr)
logging.root.setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

### Pipeline construction
class CommandQueue(object):
  def __init__(self):
    self.commands = {}  # stage -> [command, ...]
    self.dry_run = False

  def set_dry_run(self, state):
    self.dry_run = state

  def append_commands(self, stage, commands):
    command_list = self.commands.get(stage, [])
    command_list.extend(commands)
    self.commands[stage] = command_list

  def run(self, stages = []):
    """Runs the given stages, in order, or all if none are supplied"""
    if not stages:
      stages = self.commands.keys()

    for stage in [s for s in stages if s in self.commands.keys()]:
      for command in self.commands[stage]:
        self.execute(command)

  def __str__(self):
    __str = 'Pipeline:\n'
    for stage, commands in self.commands.items():
      __str += 'STAGE: {0}\n'.format(stage)
      __str += '  '+'\n  '.join(commands)
    return __str

  def execute(self, command, input = ""):
    """Spins off a subprocess to run the cgiven command"""
    if input:
      logger.debug("exec: {0}\n\t{1}".format(command, input.replace('\n','\n\t')))
    else:
      logger.debug("exec: " + command)

    if self.dry_run:
      return
    proc = subprocess.Popen(command.split(),
             stdin = subprocess.PIPE, stdout = 2, stderr = 2)
    proc.communicate(input)
    if proc.returncode != 0:
      raise Exception("Returns %i :: %s" %( proc.returncode, command ))

class ParallelCommandQueue(CommandQueue):
  def __init__(self, processors = 8):
    CommandQueue.__init__(self)
    self.processors = processors

  def run(self, stages):
    if not stages:
      stages = self.commands.keys()

    previous_stage = STAGE_NONE
    for stage in [s for s in stages if s in self.commands.keys()]:
      if self.commands[stage]:
        self.parallel(self.commands[stage])
        previous_stage = stage

  def parallel(self, commands):
    "Runs the list of commands through parallel"
    command = 'parallel -j%i' % self.processors
    self.execute(command, input='\n'.join(commands))

class ScriptCommandQueue(CommandQueue):
  def __init__(self, scriptname, processes=8):
    CommandQueue.__init__(self)
    self.scriptname = scriptname
    self.processes  = processes
  def run(self, stages=None):
    if not stages:
      stages = self.commands.keys()





class QBatchCommandQueue(CommandQueue):
  def __init__(self, processors = 8, batch='pbs'):
    assert batch in ['pbs','sge']
    CommandQueue.__init__(self)
    self.processors = processors
    self.batch = batch

  def run(self, stages):
    if not stages:
      stages = self.commands.keys()

    previous_stage = STAGE_NONE
    for stage in [s for s in stages if s in self.commands.keys()]:
      if self.commands[stage]:
        unique_stage = "{0}_{1}".format(stage,
            ''.join([random.choice(string.letters) for i in xrange(4)]))
        walltime   = stage_queue_hints[stage]['walltime']
        processors = stage_queue_hints[stage]['procs']
        self.qbatch(self.commands[stage], batch_name=unique_stage, afterok=previous_stage+"*",
            walltime=walltime, processors = processors)
        previous_stage = unique_stage

  def qbatch(self, commands, batch_name = None, afterok=None, walltime="10:00:00", processors = None):
    logger.info('running {0} commands after stage {1}'.format(len(commands), afterok))

    opt_name    = batch_name and '-N {0}'.format(batch_name) or ''
    opt_afterok = afterok and '--afterok_pattern {0}'.format(afterok) or ''
    batchsize   = min(self.processors, processors)
    self.execute('qbatch --batch_system {0} {1} {2} - {3} {4}'.format(
        self.batch, opt_name, opt_afterok, batchsize, walltime),
        input='\n'.join(commands))

#### Guts
class Template:
  """Represents an MR image with labels, optionally"""
  def __init__(self, image, labels = None):
    image_path      = os.path.realpath(image)
    self.stem       = os.path.basename(os.path.splitext(image_path)[0])
    self.image      = image
    self.labels     = labels

    expected_labels = os.path.join(dirname(dirname(image_path)), 'labels', self.stem + "_labels.mnc")
    if not labels and os.path.exists(expected_labels):
      self.labels = expected_labels

  @classmethod
  def get_templates(cls, path):
    """return a list of MR image Templates from the given path.  Expect to find
    a child folder named brains/ containing MR images, and labels/ containing
    corresponding labels."""
    return [Template(i) for i in glob.glob(join(path, 'brains', "*.mnc"))]


# new style?
class datafile:
  def __init__(self, path):
    self.path = path
    self.abspath = os.path.abspath(path)
    self.basename = os.path.basename(path)
    self.dirname = os.path.dirname(path)
    self.realpath = os.path.realpath(path)
    self.stem = os.path.splitext(self.basename)[0]
  def exists(self):
    return os.path.isfile(self.realpath)
  def __str__(self):
    return self.abspath
  def __repr__(self):
    return self.realpath
  def __eq__(self, other):
    if isinstance(other,self.__class__):
      return os.path.realpath(self.abspath) == os.path.realpath(other.abspath)
    else:
      return false
  def __ne__(self,other):
    return not self.__eq__(other)
  def __hash__(self):
    return hash(os.path.realpath(self.abspath))

class out(datafile):
  pass

class image(datafile):
  def objects(self):
    return map(datafile, glob.glob('{0.dirname}/../objects/*.obj'.format(self)))
  def labels(self):
    return map(datafile,
        glob.glob('{0.dirname}/../labels/{0.stem}_labels.mnc'.format(self)))

class command:
  def __init__(self, fmt_string, *args, **kwargs):
    cmdstr = fmt_string.format(*args,**kwargs)
    self.__init__(shlex.split(cmdstr))  # split it up into parts
    #
    #todo: we could augment the usual string formatting syntax to include
    #      the ability to indicate types (e.g. that an argument is an 'out'put
    #      file.
    #
    #      Ideas:
    #         # 1. use <Type>@<string> to mean
    #         #   call Type(string), as in:
    #         nuc_correct {0} out@{output_dir}/nuc/{0.stem}
    #
    #         # Q: what if there are @ characters in the string?
    #         # A: too bad. :-)  But honestly, we could just check for strings
    #         that match $\w+@ so that the only strings that may get confused
    #         are those that happen to start with out@ and are NOT mean to be
    #         interpreted as types.
    #
    #         # 2. use the conversion option for output files: o
    #         bestlinreg {from} {to} {xfm!o} {resampled!o}

  def __init__(self, *args):
    #todo: sanity checks
    self.cmd = args

class taskset:
  def __init__(self):
    self.stages = defaultdict(list)
    self.stage_order = []
  def stage(self,stage_name):
    """syntactic sugar"""
    t = self
    class _stage():
      def command(self, *args):
        t.command(stage_name,args)
    return _stage()
  def command(self,stage,cmd):
    self.stages[stage].append(cmd)
    if stage not in self.stage_order: self.stage_order.append(stage)
  def set_stage_order(self, order):
    assert set(order).issubset(set(self.stages.keys)), "some stages given are not part of this taskset"
    self.stage_order = order
  def __str__(self):
    __str=""
    for stage in self.stage_order:
      __str += '{0}:\n'.format(stage)
      for command in self.stages[stage]:
        __str += '\t{0}\n'.format(' '.join(map(str,command)))
    return __str
  def populate_queue(self, commandqueue):
    for stage in self.stages:
      unfinished, outputs = self._filter_unfinished(self.stages[stage])
      if not unfinished:
        continue

      # make output dirs directories
      map(mkdirp, set(map(lambda x: x.dirname, chain(*outputs))))

      cmds = map(lambda command: " ".join(map(str,command)), unfinished)
      commandqueue.append_commands(stage, set(cmds))

  def runqueue(self, commandqueue, populate=True):
    if populate:
        self.populate_queue(commandqueue)
    commandqueue.run(self.stage_order)

  def _filter_unfinished(self,commands):
    """returns tuple of each unfinished command, and a list of its output files"""
    details = [(c,filter(lambda x: isinstance(x,out),c)) for c in commands]
    filtered = [(c,o) for (c,o) in details if not all(map(lambda x: os.path.isfile(str(x)),o))]
    if filtered:
        unfinished, outputs = zip(*filtered)
    else:
        unfinished, outputs = (), ()
    return (unfinished, outputs)

  def write_to_script(self,scriptname,processes=8):
    script = open(scriptname,'w')
    script.write('#!/bin/bash\n')
    script.write(
        'echo "This script was generated by MAGeT morph on {0!s}"\n'.format(
          datetime.datetime.now()))

    for stage in self.stage_order:
      details = [(c,filter(lambda x: isinstance(x,out),c)) for c in self.stages[stage]]
      runnable, outputs = zip(*details)

      script.write('\necho "STAGE {0} -- creating directories"\n'.format(stage))
      dirs_to_make = set(map(lambda x: x.dirname, chain(*outputs)))
      script.write(''.join(map(lambda x: 'mkdir -p "{0}"\n'.format(x),
        dirs_to_make))+'\n')

      script.write('\necho "STAGE {0} -- commands"\n'.format(stage))
      commands = map(lambda command: " ".join(map(str,command)), runnable)
      if processes == 0:
        script.write('\n'.join(commands) + '\n')
      else:
        for i in range(0,len(commands),processes):
          batch = commands[i:i+processes]
          script.write(' &\n'.join(batch) + ' &\n')
          script.write('wait;\n')

    script.write('\necho "DONE!!!!"\n')
    script.close()


def run_command(command):
  cmdstr = " ".join(map(str,command))
  print >> sys.stderr, 'COMMAND:', cmdstr
  return call(cmdstr,shell=True)

class multiprocqueue:
  def run(self,tasks,processes=None,stage_order=None):
    """Runs the commands from the given stages in the task list.

       If stages isn't provided, then all stages are run. """
    stage_order = stage_order or tasks.stage_order
    for stage in stage_order:
      print '## stage:', stage,'##'

      #
      unfinished, outputs = self._filter_unfinished(tasks.stages[stage])
      if not unfinished:
        continue

      # make output dirs directories
      map(mkdirp, set(map(lambda x: x.dirname, chain(*outputs))))

      # actually run the stages
      results = self._run(unfinished, stage, processes)

      print 'results ---',results
      #TODO: assert that there were no errors
      if not all(map(lambda x: x==0,results)):
        print "Error in stage {0}. Exiting...".format(stage)
        return -1

  def _run(self,commands,stage, processes=None):
    return Pool(processes).map(run_command, commands)

  def _filter_unfinished(self,commands):
    """returns tuple of each unfinished command, and a list of its output files"""
    details = [(c,filter(lambda x: isinstance(x,out),c)) for c in commands]
    filtered = [(c,o) for (c,o) in details if not all(map(lambda x: os.path.isfile(str(x)),o))]
    if filtered:
        unfinished, outputs = zip(*filtered)
    else:
        unfinished, outputs = (), ()
    return (unfinished, outputs)

class scriptqueue(multiprocqueue):
  def __init__(self):
    self.stage = 1

  def _run(self,commands,stage,processes=None):
    open('{0}_{1}.sh'.format(self.stage,stage),'w').write(
        "\n".join(map(lambda x: " ".join(map(str,x)),commands))+'\n')
    self.stage += 1
    return [0]

class batcharrayqueue(multiprocqueue):
  def __init__(self):
    self.stage = 1

  def _run(self,commands,stage,processes=None):
    task_list='{0}_{1}.sh'.format(self.stage,stage)
    open(task_list,'w').write(
        "\n".join(map(lambda x: " ".join(map(str,x)),commands))+'\n')
    execute('echo qarray {task_list}'.format(**vars()))
    self.stage += 1
    return [0]




### utility functions
def mkdirp(*p):
  """Like mkdir -p"""
  path = join(*p)
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno == errno.EEXIST:
      pass
    else: raise
  return path

def execute(command, input = ""):
  """Spins off a subprocess to run the cgiven command"""
  proc = subprocess.Popen(command.split(),
           stdin = subprocess.PIPE, stdout = 2, stderr = 2)
  proc.communicate(input)
  if proc.returncode != 0:
    raise Exception("Returns %i :: %s" %( proc.returncode, command ))

def parallel(commands, processors=8):
  "Runs the list of commands through parallel"
  command = 'parallel -j%i' % processors
  execute(command, input='\n'.join(commands))
