#! /usr/bin/env python

import jenkins
import yaml

def default_active_test(job_info):
    return True

def _count_deps(jenkins_instance, cache_dir, base_job_info, active_test, counted_deps, depth):
    if not active_test(base_job_info):
        return

    print "%s%s - Count=%i" % ("-"*depth, base_job_info['name'], len(counted_deps))
    counted_deps.add(base_job_info['name'])

    # Walk over downstream jobs
    for downstream_job in base_job_info['downstreamProjects']:
        # Only keep pursuing if we haven't seen this dep yet
        if downstream_job['name'] not in counted_deps:
            f = open("%s/job_info/%s.yaml" % (cache_dir, downstream_job['name']))
            downstream_job_info = yaml.load(f).values()[0];
            f.close()
            _count_deps(jenkins_instance, cache_dir, downstream_job_info, active_test, counted_deps, depth+1)

def count_deps(jenkins_instance, cache_dir, base_jobs, active_test=default_active_test):
    counted_deps = set()

    for base_job in base_jobs:
        if base_job not in counted_deps:
            f = open("%s/job_info/%s.yaml" % (cache_dir, base_job))
            base_job_info = yaml.load(f).values()[0];
            f.close()
            _count_deps(jenkins_instance, cache_dir, base_job_info, active_test, counted_deps, 0)
    return len(counted_deps)
