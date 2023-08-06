from colorama import Fore
import time
import sys
from . import ExpEval, ExpEvalProcedure
from .ulib import Signal
from .ulib.detector import Detector

if __name__ == '__main__':
    ex = ExpEval()
    detector = Detector(level=2 if sys.argv[1] == str(88005553535) else 0)
    while True:
        query = input(Fore.CYAN + "> " + Fore.RESET)
        try:
            time_start = time.time()
            result = ExpEvalProcedure(ex, query)()
            time_ready = time.time()
            print(f"{Fore.YELLOW}%s{Fore.RESET}={Fore.GREEN}%s{Fore.RESET}" % (query, result))
            print("It took %d seconds to execute" % (time_ready - time_start))
        except Exception as err:
            if isinstance(err, Signal):
                err: Signal
                if err.name == "exit":
                    break
            else:
                print(Fore.RED, end="")
                print("Oh no! %s!" % err.__class__.__name__)
                print(err)
                print(Fore.RESET, end="")
else:
    print("Ты паровозик?")
