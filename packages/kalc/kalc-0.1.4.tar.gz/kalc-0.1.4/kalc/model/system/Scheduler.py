from poodle import Object, planned
from typing import Set
from kalc.misc.const import *
import kalc.model.kinds.Pod as mpod
from kalc.model.system.primitives import StatusSched
import sys


class Scheduler(Object):
    queueLength: int
    status: StatusSched
    podQueue: Set["mpod.Pod"]
    podQueue_excluded_pods_length: int
    podQueue_excluded_pods: Set["mpod.Pod"]
    # debug_var: bool
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queueLength = 0
        # self.debug_var = False
        self.status = STATUS_SCHED["Clean"]
        self.podQueue_excluded_pods_length = 0

    def __str__(self): return str(self._get_value())