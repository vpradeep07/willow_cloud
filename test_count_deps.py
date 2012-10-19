#! /usr/bin/env python

import jenkins
import urllib
import yaml
import sys
import os
import time
import count_deps

from rospkg import environment


def main():
    if len(sys.argv) < 2:
        print "Usage: %s cache_dir job1 job2 job3 ..."%(sys.argv[0])
        sys.exit(0)

    cache_dir_orig = sys.argv[1]
    cache_dir = os.path.expanduser(cache_dir_orig)

    job_list = sys.argv[2:]

    # create jenkins instance
    with open(os.path.join(environment.get_ros_home(), 'catkin-debs', 'server.yaml')) as f:
        info = yaml.load(f)

    #jenkins_url = 'http://jenkins.willowgarage.com:8080/'
    jenkins_url = 'http://50.28.61.61:8080/'
    jenkins_instance = jenkins.Jenkins(jenkins_url, info['username'], info['password'])
    print "Created Jenkins instance"

    num_deps = count_deps.count_deps(jenkins_instance, cache_dir, job_list)

    print "Calculated deps for:"
    print "".join([ "%s\n" % x for x in job_list ])
    print "Found %i total deps" % num_deps

if __name__ == "__main__":
    main()