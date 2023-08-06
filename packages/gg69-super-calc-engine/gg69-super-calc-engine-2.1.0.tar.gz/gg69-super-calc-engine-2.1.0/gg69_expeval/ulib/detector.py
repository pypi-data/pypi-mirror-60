from typing import Tuple, List
import re


class Detector:
    def __init__(self, level=1):
        self.targets = ["57", "69", "179", "228"]
        self.pattern = "[(%s)]" % (")(".join(self.targets))
        self.level = level

    def analyse(self, calc_res, level=None) -> List[Tuple[int, int]]:
        if level is None:
            level = self.level
        string = str(calc_res)
        if level == 0:
            return []
        elif level == 1:
            if string in self.targets:
                return [(0, len(string))]
        elif level == 2:
            detection_res = []
            p = 0
            while p < len(string):
                search_res = re.search(self.pattern, string)
                if search_res is None:
                    break
                detection_res.append(search_res.span())
                p = search_res.end() + 1

            else:
                raise Exception("Invalid cool numbers detection level")
