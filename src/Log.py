import dataclasses
import datetime as dt
import gzip
import inspect
import logging
import os
import re


LOG_FILENAME_PATTERN: str=r"^((?P<date_year>[0-9]{1,})-(?P<date_month>[0-1][0-9])-(?P<date_day>[0-3][0-9])-[0-9]{1,}\.log\.gz)$"


@dataclasses.dataclass
class Log:
    """
    Represents 1 log.
    """

    date: dt.date   #date the logtimes refer to, from filename
    filename: str   #filename
    content: str    #content

    def __init__(self, filepath: str, date: None|dt.date=None) -> None:
        """
        Constructs log object from filepath to log file. Expects no date given, expects filename to match LOG_FILENAME_PATTERN.

        Arguments:
        - self
        - filepath: the filepath to the log file

        Raises:
        - TypeError: date is neither None nor a datetime.date.
        - ValueError: date is not given and the given filename does not match LOG_FILENAME_PATTERN.
        """

        zipped: bool


        logging.debug(f"Constructing Log from filepath=\"{filepath}\" and date=\"{date}\"...")
        
        self.filename=os.path.basename(filepath)    #extract filename
        logging.debug(f"self.filename: {self.filename}")


        if date==None:
            re_match=re.search(LOG_FILENAME_PATTERN, self.filename)                                                                                     #look if filename is in expected format, otherwise cannot parse date
            if re_match==None:
                raise ValueError(f"Error in {self.__init__.__name__}{inspect.signature(self.__init__)}: Given filename \"{self.filename}\" does not match the log filename pattern.")
            self.date=dt.date(int(re_match.groupdict()["date_year"]), int(re_match.groupdict()["date_month"]), int(re_match.groupdict()["date_day"]))   #construct date from parsed information
        elif type(date)==dt.date:
            self.date=date
        else:
            raise TypeError(f"Error in {self.__init__.__name__}{inspect.signature(self.__init__)}: date is neither None nor a datetime.date, but of type \"{type(date)}\".")
        logging.debug(f"self.date: {self.date.strftime('%Y-%m-%d')}")


        zipped=os.path.splitext(self.filename)[1]==".gz"    #if log file extension is .gz: file is zipped
        if zipped==True:                                    #if file zipped: decompress first to read content
            with gzip.open(filepath, "rt") as log_file:
                self.content=log_file.read()
        elif zipped==False:                                 #if file not zipped: read content normally
            with open(filepath, "rt") as log_file:
                self.content=log_file.read()
        else:
            raise RuntimeError(f"Error in {self.__init__.__name__}{inspect.signature(self.__init__)}: zipped is neither True nor False, but \"{zipped}\".")
        logging.debug(f"self.content: {self.content}")
        

        logging.debug(f"\rConstructed Log from filepath=\"{filepath}\" and date=\"{date}\".")
        return