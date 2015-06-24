import logging
import time

from system import *
from statistics import *

class Simulation:

    logger = logging.getLogger("sim")

    def __init__(self, mission_time, iterations, raid_type, raid_num, disk_capacity, 
            disk_fail_parms, disk_repair_parms, disk_lse_parms, disk_scrubbing_parms):
        self.mission_time = mission_time
        self.iterations = iterations
        self.raid_type = raid_type
        self.raid_num = raid_num
        self.disk_capacity = disk_capacity
        self.disk_fail_parms = disk_fail_parms
        self.disk_repair_parms = disk_repair_parms
        self.disk_lse_parms = disk_lse_parms
        self.disk_scrubbing_parms = disk_scrubbing_parms

        self.logger.debug("Simulation: iterations = %d" % iterations)

        self.system = None

    def simulate(self):
        sample_list = []
        raid_failure_count = 0
        sector_error_count = 0

        self.system = System(self.mission_time, self.raid_type, self.raid_num, self.disk_capacity, self.disk_fail_parms,
            self.disk_repair_parms, self.disk_lse_parms, self.disk_scrubbing_parms)

        for i in range(self.iterations):

            if (i+1) % 100000 == 0:
                self.logger.warning("complete %d iterations" % i)

            self.system.reset()
        
            result = self.system.run()

            if result[0] == System.RESULT_NOTHING_LOST:
                #sample_list.append(0)
                self.logger.debug("%dth iteration: nothing lost")
            elif result[0] == System.RESULT_RAID_FAILURE:
                self.logger.debug("%dth iteration: %s, %d bytes lost" % (i, "RAID Failure", result[1]))
                sample_list.append(result[1])
                raid_failure_count += 1
            elif result[0] == System.RESULT_SECTORS_LOST:
                self.logger.debug("%dth iterations: %s, %d bytes lost" % (i, "Sectors Lost", sum(result[1:])))
                sample_list.append(sum(result[1:]))
                sector_error_count += len(result) - 1
            else:
                sys.exit(2)

        prob_result = None
        byte_result = None

        samples = Samples()
        localtime = time.asctime(time.localtime(time.time()))
        self.logger.warning("%s : all iterations finish: calculating results" % localtime)
        samples.calcResults("0.90", sample_list, self.iterations)

        # finished, return results
        # the format of result:
        return (samples, raid_failure_count, sector_error_count)
