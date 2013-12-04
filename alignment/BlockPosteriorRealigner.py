'''
Created on Jan 17, 2013

@author: mic
'''
from tools import perf
from alignment.PosteriorRealigner import PosteriorRealigner

class BlockPosteriorRealigner(PosteriorRealigner):

    @perf.runningTimeDecorator
    def computeBacktrackTable(self, x, dx, y, positionGenerator, ignore):
        return self._computeBacktrackTable(
            x,
            dx,
            y,
            positionGenerator,
            ignore,
            lambda _sdx, _sdy: self.mathType(_sdx + _sdy),
        )