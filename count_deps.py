#! /usr/bin/env python

import jenkins_cache
import yaml

def default_active_test(job_info):
    return True

def _count_deps(cache, base_job_info, active_test, counted_deps, depth):
    if not active_test(base_job_info):
        return

    print "%s%s - Count=%i" % ("-"*depth, base_job_info['name'], len(counted_deps))

    name = base_job_info['name']
    # Store the current depth if it's bigger
    counted_deps[name] = max( counted_deps.get(name, depth), depth)

    # Walk over downstream jobs
    for downstream_job in base_job_info['downstreamProjects']:
        # Only keep pursuing if we haven't seen this dep yet
        if downstream_job['name'] not in counted_deps:
            downstream_job_info = cache.get_job_info(downstream_job['name'])
            _count_deps(cache, downstream_job_info, active_test, counted_deps, depth+1)

def count_deps(cache, base_jobs, active_test=default_active_test):
    counted_deps = dict()

    for base_job in base_jobs:
        if base_job not in counted_deps:
            base_job_info = cache.get_job_info(base_job)
            _count_deps(cache, base_job_info, active_test, counted_deps, 0)
    return len(counted_deps), counted_deps
