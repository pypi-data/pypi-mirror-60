from datetime import datetime;
from os.path import isfile as isFile;

class Logger:

    def __init__(self, log_filename_postfix = "log", log_filename_extension = "log", path_to_log = "."):

        self.log_filename_postfix = log_filename_postfix;
        self.log_filename_extension = log_filename_extension;
        self.path_to_log = path_to_log;
        self.initLogFile();

        return None;

    def initLogFile(self, log_filename_postfix = None, \
                                 log_filename_extension = None, \
                                 path_to_log = None):
        """ PRIVATE """

        if not log_filename_postfix:
            log_filename_postfix = self.log_filename_postfix;

        if not log_filename_extension:
            log_filename_extension = self.log_filename_extension;

        if not path_to_log:
            path_to_log = self.path_to_log;

        self.the_day = self.timeStamp()[:10];
        self.log_file_name = "{}/{}_{}.{}".\
        format(
                    path_to_log,
                    self.the_day,
                    log_filename_postfix,
                    log_filename_extension
                  );
        if not isFile(self.log_file_name):
            self.writeDown("The log file created. \n ----------------------------------------------- \n\n");

    def timeStamp(self, digits_after_dot = 2):
        """ PRIVATE """
        full_string_of_time_stamp = str(datetime.now());

        if digits_after_dot >= 6:
            string_of_time_stamp = full_string_of_time_stamp;
        else:
            if digits_after_dot <=0:
                cut_mark = -7;
            else:
                cut_mark = digits_after_dot - 6;
            string_of_time_stamp = full_string_of_time_stamp[:cut_mark];

        return string_of_time_stamp;

    def writeDown(self, message_string):

        the_timestamp = self.timeStamp();
        the_day = the_timestamp[:10];
        if the_day != self.the_day:
            self.initLogFile();
            
        log_string = "{}: {} \n".\
        format(
                    self.timeStamp(),
                    message_string
                  );

        print(log_string);
        with open(self.log_file_name, "a") as log_file:
            log_file.write(log_string);

        return None;
