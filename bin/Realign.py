from alignment import Fasta
from adapters.TRFDriver import TRFDriver, Repeat
from adapters.HMMDriver import HMMDriver
from alignment.AlignmentIterator import AlignmentPositionGenerator
from tools import perf
import os   
import sys
from alignment.Alignment import Alignment
from tools.file_wrapper import Open
from alignment.AlignmentCanvas import AlignmentCanvas
import json
from tools.ArgumentParser import parse_arguments

def brainwash(className):
    dct = dict();
    for key, value in className.__dict__.iteritems():
        if hasattr(value, '__call__'):
            dct[key] = lambda *_, **__: None
        else: 
            dct[key] = None
    return type('Brainwashed' + className.__name__, (object,), dct)

def compute_annotations(args, alignment_filename, model):
    annotations = dict()
    if 'trf' in args.tracks:
        trf = None
        for trf_executable in args.trf:
            if os.path.exists(trf_executable):
                trf = TRFDriver(trf_executable, mathType=args.mathType)
                #break
        if trf:
            repeats = trf.run(alignment_filename)
            annotations['trf'] = repeats
                        
    if 'original_repeats' in args.tracks:
        repeats = json.load(Open(alignment_filename + '.repeats',
                                 'r'))
        for k, v in repeats.iteritems():
            repeats[k] = [Repeat(_v[0], _v[1], _v[2], _v[3], _v[4]) 
                          for _v in v]
        
        annotations['original_repeats'] = repeats

    if 'trf_cons' in args.tracks:
        trf = None
        for trf_executable in args.trf:
            if os.path.exists(trf_executable):
                trf = TRFDriver(trf_executable, mathType=args.mathType)
                #break
        if trf:
            repeats = trf.run(alignment_filename)
        #    repeats = json.load(Open(alignment_filename + '.repeats',
        #                         'r'))
        #    for k, v in repeats.iteritems():
        #        repeats[k] = [Repeat(_v[0], _v[1], _v[2], _v[3], _v[4]) 
        #                      for _v in v]
            annotations['trf_cons'] = {}
            for seq_name in repeats:
                cons = set([repeat.consensus for repeat in repeats[seq_name]])
                annotations['trf_cons'][seq_name] = cons
    
    if 'hmm' in args.tracks:
        paths = None;
        if args.trf != None and len(args.trf) > 0:
            paths = args.trf
        driver = HMMDriver(paths, args.mathType, model)
        if driver:
            repeats = driver.run(alignment_filename)
            annotations['hmm'] = repeats
            
    perf.msg("Hints computed in {time} seconds.")
    perf.replace()
    return annotations

def realign_file(args, model, output_filename, alignment_filename):
    # begin of HACK
    if args.expand_model:
        old_tracks = args.tracks
        args.tracks.add('trf_cons')
    m = model
    if args.annotation_model:
        m = args.annotation_model
    annotations = compute_annotations(args, alignment_filename, m)
    if args.expand_model:
        consensuses = annotations['trf_cons']
        args.tracks = old_tracks
        if 'trf_cons' not in old_tracks:
            del args.tracks['trf_cons']
    # end of HACK
    with Open(output_filename, 'w') as output_file_object:
        for aln in Fasta.load(
            alignment_filename, 
            args.alignment_regexp, 
            Alignment, 
            sequence_selectors=args.sequence_regexp):
            if len(aln.sequences) < 2:
                sys.stderr.write("ERROR: not enough sequences in file\n")
                return 1
            if len(args.draw) == 0:
                drawer = brainwash(AlignmentCanvas)()
            else:
                drawer = AlignmentCanvas()
                drawer.add_original_alignment(aln)
            aln, unmask_repeats = args.mask_repeats(aln, annotations)
            seq1, seq2 = tuple(map(Fasta.alnToSeq, aln.sequences[:2]))
            perf.msg("Data loaded in {time} seconds.")
            perf.replace()
            if args.expand_model:
                # Potrebujem zistit konsenzy
                A = consensuses[aln.names[0]]
                B = consensuses[aln.names[1]]
                cons = list(A.union(B))
                real_model = model.expandModel({'consensus': cons})
            else: 
                real_model = model
            realigner = args.algorithm()
            realigner.setDrawer(drawer)
            realigner.prepareData(seq1, aln.names[0], seq2, aln.names[1], aln, 
                                  real_model, annotations, args)
                                                              
            aln = realigner.realign(0, len(seq1), 0, len(seq2))
            aln = unmask_repeats(aln)
            perf.msg("Sequence was realigned in {time} seconds.")
            perf.replace()
            if len(args.draw) > 0:
                drawer.add_sequence('X', seq1)
                drawer.add_sequence('Y', seq2)
                drawer.add_alignment_line(101, (255, 0, 255, 255), 2, 
                                          AlignmentPositionGenerator(
                                              Alignment([aln[0], aln[2]])))
                drawer.draw(args.draw, 2000, 2000)
                perf.msg("Image was drawn in {time} seconds.")
            # Save output_file
            Fasta.saveAlignmentPiece(aln, output_file_object)


#TODO: if sampling, the alignment is not necessary
@perf.runningTimeDecorator
def worker(transformation):
    # ====== Parse parameters ==================================================
    args = parse_arguments()
    if args is None:
        return 1
        
    alignment_filename_template = args.alignment
    output_filename_template = args.output_file
    
    # ====== Check SGE parameters ==============================================
    task_ids = [None]
    if os.environ.has_key('SGE_TASK_ID'):
        if os.environ['SGE_TASK_ID'] != 'undefined':
            sge_task_id = int(os.environ['SGE_TASK_ID'])
            if not os.environ.has_key('SGE_STEP_SIZE'):
                sge_step_size = 1
            else:
                sge_step_size = int(os.environ['SGE_STEP_SIZE'])
            sge_task_last = int(os.environ['SGE_TASK_LAST'])
            task_ids = range(
                sge_task_id,
                min(sge_task_id + sge_step_size, sge_task_last + 1)
            )

    # ====== Realign all sequences =============================================
    ret = 0
    for task_id in task_ids:
        if task_id == None:
            output_filename = output_filename_template
            alignment_filename = alignment_filename_template
        else:
            output_filename = output_filename_template.format(id=task_id - 1)
            alignment_filename = \
                alignment_filename_template.format(id=task_id - 1)
         
        ret = max(ret,transformation(args, args.model, output_filename,
                                     alignment_filename))
    return ret


    
if __name__ == "__main__":
    ret = worker(realign_file)
    perf.printAll()
    exit(ret)
