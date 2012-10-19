#! /usr/bin/env python

import jenkins
import urllib
import yaml
import sys
import os
import time

from rospkg import environment

def init_jenkins_cache(jenkins_instance, cache_dir_orig):
    cache_dir = os.path.expanduser(cache_dir_orig)
    os.makedirs(cache_dir)
    job_info_dir = cache_dir + '/job_info'
    os.mkdir(job_info_dir)

    jobs = jenkins_instance.get_jobs()

    print "Found %i jobs on jenkins server" % len(jobs)

    for i,job in enumerate(jobs[:10]):
        name = job['name']
        print "%i) Fetching %s" % (i, name)
        job_info = jenkins_instance.get_job_info(urllib.pathname2url(name))

        f = open("%s/%s.yaml" % (job_info_dir, name), 'w')
        yaml.dump(job_info, f)
        f.close()

        time.sleep(0.25)


def main():
    if len(sys.argv) < 2:
        print "Usage: %s cache_dir"%(sys.argv[0])
        sys.exit(0)

    cache_dir = sys.argv[1]

    # create jenkins instance
    with open(os.path.join(environment.get_ros_home(), 'catkin-debs', 'server.yaml')) as f:
        info = yaml.load(f)

    #jenkins_url = 'http://jenkins.willowgarage.com:8080/'
    jenkins_url = 'http://50.28.61.61:8080/'
    jenkins_instance = jenkins.Jenkins(jenkins_url, info['username'], info['password'])
    print "Created Jenkins instance"

    # run job
    init_jenkins_cache(jenkins_instance, cache_dir)

if __name__ == "__main__":
    main()
