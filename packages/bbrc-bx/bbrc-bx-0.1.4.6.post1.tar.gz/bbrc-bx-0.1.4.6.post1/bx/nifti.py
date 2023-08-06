import logging as log
import os.path as op
import os
from bx.command import Command

class NiftiCommand(Command):
    '''Download NIfTI images from a given sequence (`SeriesDesc`).

    Usage: bx nifti <resource_id>
    User is then asked for sequence name (ex: T1, T2, DWI). Has to match with
    the one in XNAT.'''

    nargs = 1

    def __init__(self, *args, **kwargs):
        super(NiftiCommand, self).__init__(*args, **kwargs)


    def parse(self):
        id = self.args[0]
        self.sequence_name = 'T1_ALFA1 '
        if not os.environ.get('CI_TEST', None):
            s = input('Enter Sequence Name (i.e. Series Description):')
            self.sequence_name = s
        log.info(self.sequence_name)
        self.run_id(id, download_sequence,
            sequence_name=self.sequence_name, destdir=self.destdir)


def download_sequence(x, experiments, sequence_name, destdir):

    import shutil
    from glob import glob
    import tempfile
    from tqdm import tqdm

    for e in tqdm(experiments):
        log.debug('Experiment %s:'%e['ID'])

        scans = x.select.experiment(e['ID']).scans()
        seq_scans = [s for s in scans if not s.label().startswith('0-') and\
            sequence_name == s.attrs.get('type')]
        log.debug('Found following scans: %s'%seq_scans)

        for s in seq_scans:
            r = s.resource('NIFTI')
            if not r.exists():
                log.error('%s has no NIFTI'%e)
                continue
            wd = tempfile.mkdtemp()

            r.get(dest_dir=wd, extract=True)
            fp = glob(op.join(wd, 'NIFTI', '*.nii.gz'))
            if len(fp) != 1:
                log.error('Multiple files found in archive. Skipping %s (%s) folder: %s'\
                    %(e['ID'], s.label(), op.join(wd, 'NIFTI')))
                continue
            fp = fp[0]
            fn = '%s_%s_%s_%s.nii.gz'%(e['subject_label'], e['label'],
                s.label(), e['ID'])
            log.debug('Saving %s...'%fn)
            shutil.move(fp, op.join(destdir, fn))
            shutil.rmtree(wd)
