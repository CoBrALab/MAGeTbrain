#/usr/bin/env python2.7
# vim: set ts=2 sw=2:
import MAGeT
from MAGeT.morpho import *
from MAGeT.mbpipe import *
import unittest

class TestMorphobits(unittest.TestCase):
  def setUp(self):
    self.morpho = morpho = Morphobits()
    morpho.config('output_dir','output')
    morpho.config('reg_dir',   'registrations')

    model     = image('input/atlas1.mnc')
    atlases   = [model]
    subjects  = [image('input/subject1.mnc')]
    templates = subjects
    self.model_only_1_subject = [atlases,subjects,templates,model]

  def test_model_only_single_subject_sanity_checks(self):
    tasklist  = self.morpho.build_pipeline(*self.model_only_1_subject)

    for stage_name in [ 'subject.nuc', 'subject.to.modelspace',
        'subject.to.modelspace', 'pairwise.reg', 'model.subject.xfm',
        'model.subject.gridavg', 'model.subject.displace']:

      stage = tasklist.stages[stage_name]
      self.assertTrue(stage, msg=stage_name + ' - ' + repr(stage))
      self.assertEquals(len(stage), 1, msg=stage_name + ' - ' + repr(stage))

if __name__ == '__main__':
  unittest.main()

