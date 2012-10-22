#! /usr/bin/env python

import jenkins
import os
import time
import yaml
import urllib

class Throttler:
    def __init__(self, delay = 0.25):
        self._delay = delay
        self._previous_time = 0.0;
    def __enter__(self):
        time.sleep(max(self._previous_time - time.time() + self._delay, 0.0) )
    def __exit__(self, t, value, traceback):
        self._previous_time = time.time()

def make_dir(path):
    dir_name = os.path.dirname(path)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

'''
Class designed to very closely model the standard jenkins interface,
but uses the file system to cache many of the server calls
'''
class JenkinsCache:
    def __init__(self, url, cache_dir, username=None, password=None, fetch_delay=0.25):
        self._jenkins_instance = jenkins.Jenkins(url, username, password)

        self._cache_dir = os.path.expanduser(cache_dir)

        self._throttler = Throttler(fetch_delay)

        make_dir(self._cache_dir)
        make_dir(self._cache_dir + '/job')

    def _job_info_path(self, name):
        return '%s/job/%s/info.yaml' % (self._cache_dir, name)

    def _build_info_path(self, name, num):
        return '%s/job/%s/%i/info.yaml' % (self._cache_dir, name, num)

    def refresh_job_info(self, name):
        with self._throttler:
            print ">>> Calling Jenkins: get_job_info(%s)" % name
            info = self._jenkins_instance.get_job_info(name)

        info_path = self._job_info_path(name)
        make_dir(info_path)
        f = open(info_path, 'w')
        record = {'info': info}
        record['cache_time_ms'] = int(time.time()*1000)
        yaml.dump(record, f)
        f.close()
        return record['info']

    def refresh_build_info(self, name, num):
        with self._throttler:
            print ">>> Calling Jenkins: Getting build info for %s/%i" % (name, num)
            url_data = urllib.urlopen(self._jenkins_instance.server + '/job/%s/%i/api/python' % (name, num))
        info = yaml.load(url_data)
        info_path = self._build_info_path(name, num)
        make_dir(info_path)
        f = open(info_path, 'w')
        record = {'info': info}
        record['cache_time_ms'] = int(time.time()*1000)
        yaml.dump(record, f)
        f.close()
        return record['info']

    def get_job_info(self, name, max_stale_ms = None):
        if not os.path.isfile(self._job_info_path(name)):
            info = self.refresh_job_info(name)
        else:
            f = open(self._job_info_path(name))
            record = yaml.load(f)
            info = record['info']
            f.close()
            if max_stale_ms is not None and (time.time()*1000 - record['cache_time_ms']) > max_stale_ms:
                info = self.refresh_job_info(name)
        return info

    def get_build_info(self, name, num, max_stale_ms = None):
        if not os.path.isfile(self._build_info_path(name, num)):
            info = self.refresh_build_info(name, num)
        else:
            f = open(self._build_info_path(name, num))
            record = yaml.load(f)
            info = record['info']
            f.close()
            if max_stale_ms is not None and (time.time()*1000 - record['cache_time_ms']) > max_stale_ms:
                info = self.refresh_build_info(name, num)
        return info
