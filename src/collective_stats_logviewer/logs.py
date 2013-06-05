import datetime
import re
import time
import requests
from collective_stats_logviewer.model import Log
from json import dumps
from model import db

def parse_file(filename):
    with open(filename, 'rb') as fp:
        for line in fp.readlines():
            result = do_it(line)
            if result:
                yield result
            else:
                continue

def send_json(results):
    requests.post('http://127.0.0.1:5000/receive_json/', data=results)

def do_it(line):
    first_request_time = None
    last_request_time = None
    total_rendering_time = 0
    total_rss_change = 0
 
    if line.count('INFO collective.stats'):
        pattern = re.compile("^(?P<access_time>\d+-\d+-\w+:\d+:\d+) INFO collective\.stats \| (?P<publisher_time>\d+\.\d+) (?P<traverse_time>\d+\.\d+) (?P<commit_time>\d+\.\d+) (?P<transform_time>\d+\.\d+) (?P<setstate_time>\d+\.\d+) (?P<total_object_loads>\d+) (?P<object_loads_from_cache>\d+) (?P<objects_modified>\d+) \| (?P<action>\w+:)(?P<url>.*) \| .* \| RSS\: (?P<start_RSS>\d+) - (?P<end_RSS>\d+).*")
        match_result = pattern.match(line)
        if match_result:
            result =  match_result.groupdict()
            if not first_request_time:
                request_time = datetime.datetime.strptime(result['access_time'], 
                                    "%Y-%m-%dT%H:%M:%S")
            else:
                request_time = datetime.datetime.strptime(result['access_time'], 
                                    "%Y-%m-%dT%H:%M:%S")             
            l = {'id': result['url'], 
                 'request_time': time.mktime(request_time.timetuple()),
                 'publisher_time': result['publisher_time'],
                 'traverse_time': result['traverse_time'],
                 'commit_time': result['commit_time'],
                 'tranform_time': result['transform_time'],
                 'setstate_time': result['setstate_time'],
                 'total_object_loads': result['total_object_loads'],
                 'object_loads_from_cache': result['object_loads_from_cache'],
                 'objects_modified': result['objects_modified'],
                 'action': result['action'],
                 'url': result['url'],
                 'start_RSS': result['start_RSS'],
                 'end_RSS': result['end_RSS']}
            return l

if __name__ == '__main__':
    results = {'result': list(parse_file('/home/jafaraf/Desktop/collective_stats_logviewer/instance1.log'))}
    send_json(results)

#def do_it(line):
#    first_request_time = None
#    pattern = re.compile("^(?P<access_time>\d+-\d+-\w+:\d+:\d+) INFO collective\.stats \| (?P<publisher_time>\d+\.\d+) (?P<traverse_time>\d+\.\d+) (?P<commit_time>\d+\.\d+) (?P<transform_time>\d+\.\d+) (?P<setstate_time>\d+\.\d+) (?P<total_object_loads>\d+) (?P<object_loads_from_cache>\d+) (?P<objects_modified>\d+) \| (?P<action>\w+:)(?P<url>.*) \| .* \| RSS\: (?P<start_RSS>\d+) - (?P<end_RSS>\d+)")
#    match_result = re.match(pattern, line)
#    if match_result:
#        result =  match_result.groupdict()
#
#        if not first_request_time:
#            request_time = datetime.datetime.strptime(result['access_time'], 
#                                                      "%Y-%m-%dT%H:%M:%S")
#        else:
#            request_time = datetime.datetime.strptime(result['access_time'], 
#                                                      "%Y-%m-%dT%H:%M:%S")             
#        l = Log(request_time, result['publisher_time'], result['traverse_time'], result['commit_time'], result['transform_time'],
#                result['setstate_time'], result['total_object_loads'], result['object_loads_from_cache'], result['objects_modified'],
#                result['action'], result['url'], result['start_RSS'], result['end_RSS'])
#        db.session.add(l)
#        db.session.commit()
#        db.session.refresh(l)
#        return l.id
#    return None
