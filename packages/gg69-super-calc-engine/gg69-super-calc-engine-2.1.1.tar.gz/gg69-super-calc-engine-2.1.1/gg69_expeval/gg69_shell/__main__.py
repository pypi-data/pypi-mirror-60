from colorama import Fore, Style
import time
import sys
from gg69_expeval import ExpEval, ExpEvalProcedure
from gg69_expeval.ulib import Signal
from gg69_expeval.gg69_shell.detector import Detector

if __name__ == '__main__':
    ex = ExpEval()
    if len(sys.argv) >= 2 and sys.argv[1] == str(88005553535):
        print("Try me soon...")
        sys.exit()
        # detection_level = 2
    else:
        detection_level = 0
    detector = Detector(detection_level)
    while True:
        query = input(Fore.CYAN + "> " + Fore.RESET)
        try:
            time_start = time.time()
            result = ExpEvalProcedure(ex, query)()
            time_ready = time.time()
            print(Fore.YELLOW + query + Fore.WHITE + "=" + Fore.GREEN + detector.color_marked(str(result), Fore.GREEN) + Style.RESET_ALL)
            print("It took %d seconds to execute" % (time_ready - time_start))
        except Exception as err:
            if isinstance(err, Signal):
                err: Signal
                if err.name == "exit":
                    break
            else:
                print(Fore.RED, end="")
                print(err.__class__.__name__)
                print(err)
                print(Fore.RESET, end="")
else:
    print("Ты паровозик?")
