#Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import KFS.log
import logging
import traceback
from main import main


KFS.log.setup_logging("", logging.INFO)
try:
    main()
except:
    logging.critical(traceback.format_exc())
    
    print("\n\nPress enter to close program.", flush=True)
    input() #pause
else:
    print("\n", end="", flush=True)