#!/usr/bin/env python

DEFAULT_CONFIG_FILE_LIST = '/etc/vmchecker/config.list'

class CourseList():
    def __init__(self, config_file_list=DEFAULT_CONFIG_FILE_LIST):
        course_list = {}
        with open(config_file_list) as f:
            lines = f.readlines()
            for line in lines:
                fields = line.split(':')
                if len(fields) == 2:
                    course_list[fields[0].strip()] = fields[1].strip()
        self.course_list = course_list

    def courseNames(self):
        return self.course_list.keys()

    def courseConfigs(self):
        return self.course_list.values()

    def courseConfig(self, courseId):
        return self.course_list[courseId]

if __name__ == "__main__":
    c = CourseList()
    print c.courseNames()
    print c.courseConfigs()
    if len(c.courseNames()) > 0:
        print c.courseConfig(c.courseNames()[0])
    else:
        print "no courses :("

            
            
            
    
