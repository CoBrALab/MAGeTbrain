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

    for stage_name, count in {'image.prep'            : 2,  # autocrop and nuc
                              'subject.to.modelspace' : 1,
                              'subject.to.modelspace' : 1, 
                              'pairwise.reg'          : 1, 
                              'model.subject.xfm'     : 2,  # nl and nl-only xfms
                              'model.subject.gridavg' : 1 , 
                              'model.subject.displace': 1}.iteritems():

      stage = tasklist.stages[stage_name]
      self.assertTrue(stage, msg=stage_name + ' - ' + repr(stage))
      self.assertEquals(len(stage), count, 
          msg="Stage {} has {} commands, but only {} expected: {}".format(
            stage_name, len(stage), count, "\n".join(map(str,stage))))

if __name__ == '__main__':
  unittest.main()

