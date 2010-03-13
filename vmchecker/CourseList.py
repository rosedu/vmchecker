#!/usr/bin/env python

"""A module to interact with the course list"""


DEFAULT_CONFIG_FILE_LIST = '/etc/vmchecker/config.list'

class CourseList():
    """A class to interact with the course list"""
    def __init__(self, config_file_list=DEFAULT_CONFIG_FILE_LIST):
        """Create a CourseList object.
        config_file_list - the path to the file containign the courses.
        Defaults to DEFAULT_CONFIG_FILE_LIST
        """
        course_list = {}
        with open(config_file_list) as handle:
            lines = handle.readlines()
            for line in lines:
                fields = line.split(':')
                if len(fields) == 2:
                    course_list[fields[0].strip()] = fields[1].strip()
        self.course_list = course_list

    def course_names(self):
        """Returns a list with the names of all courses"""
        return self.course_list.keys()

    def course_configs(self):
        """Returns a list with the paths of all the config files for
        all courses"""
        return self.course_list.values()

    def course_config(self, course_id):
        """Returns the config file for the specified course"""
        return self.course_list[course_id]

def _test():
    """Run a small test on CourseList"""
    c_list = CourseList()
    print c_list.course_names()
    print c_list.course_configs()
    if len(c_list.course_names()) > 0:
        print c_list.course_config(c_list.course_names()[0])
    else:
        print "no courses :("


if __name__ == "__main__":
    _test()
