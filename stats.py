#! /usr/bin/python
import datetime
import re


def do_it(file='instance1.log'):
    first_request_time = None
    last_request_time = None
    total_rendering_time = 0
    total_rss_change = 0
    num_requests = 0
    drawer = {}
    with open(file, 'rb') as logfile:
        for line in logfile.readlines():
            num_requests += 1
            if line.count('INFO collective.stats'):
                pattern = re.compile("^(?P<access_time>\d+-\d+-\w+:\d+:\d+) INFO collective\.stats \| (?P<publisher_time>\d+\.\d+) (?P<traverse_time>\d+\.\d+) (?P<commit_time>\d+\.\d+) (?P<transform_time>\d+\.\d+) (?P<setstate_time>\d+\.\d+) (?P<total_object_loads>\d+) (?P<object_loads_from_cache>\d+) (?P<objects_modified>\d+) \| (?P<action>\w+:)(?P<url>.*) \| .* \| RSS\: (?P<start_RSS>\d+) - (?P<end_RSS>\d+)")
                match_result = re.match(pattern, line)
                if match_result:
                    result =  match_result.groupdict()
                    if not first_request_time:
                        first_request_time = datetime.datetime.strptime(result['access_time'], 
                                            "%Y-%m-%dT%H:%M:%S")
                    last_request_time = datetime.datetime.strptime(result['access_time'], 
                                            "%Y-%m-%dT%H:%M:%S")             
                    id = result['url']
                    if id not in drawer:
                        drawer[id] = {
                            'rss_diff': 0,
                            'details': [],
                            'actual_url': id, 
                            'object_cache_misses': 0,
                            'url_hits': 0,
                            'avg_rss': 0.0,
                            'total_rss': 0.0,
                            'time_rendering': 0.0,
                            'avg_req_time': 0.0,
                        }
                    item = drawer[id]
                    item['details'].append(result)
                    item['url_hits'] += 1
                    rss_diff = int(result['end_RSS']) - int(result['start_RSS'])
                    item['rss_diff'] += rss_diff
                    total_rss_change += rss_diff
                    item['avg_rss'] = rss_diff and rss_diff/item['url_hits'] or 0.0
                    item['total_rss'] += rss_diff
                    item['time_rendering'] += float(result['publisher_time'])
                    total_rendering_time += float(result['publisher_time'])
                    item['avg_req_time'] = item['time_rendering']/item['url_hits']
        total_time = last_request_time - first_request_time
        reqs_sec = num_requests/total_time.total_seconds()

        print '=' * 80
        print 'SUMMARY'
        print '=' * 80
        print "This instance is receiving %s requests per second." % (reqs_sec)
        time_per_request = total_rendering_time/num_requests
        print "The average rendering time is %s seconds." % (time_per_request)
        optimal_capacity = total_time.total_seconds() * (1/time_per_request)
        optimal_requests = optimal_capacity/total_time.total_seconds()
        print "It should be able to handle %.2f requests/sec (per thread)" % (optimal_requests)
        print "It is at %.2f%% capacity" % ((reqs_sec/optimal_requests) * 100)

        
        num_offenders = 20
        fucked_threshold = 2  # pages longer than 2 seconds, should really be 1....
        print "The following URLs are likely screwing you on rendering time: \n"
        significatly_fucked = dict((k, v) for k, v in drawer.iteritems() if v['avg_req_time'] >= fucked_threshold)
        sorted_drawer = sorted(significatly_fucked.items(),  key=lambda x: x[1]['time_rendering'], reverse=True)[:num_offenders]
        print_section('SLOW REQUESTS', sorted_drawer, total_rendering_time)

        sorted_drawer = sorted(drawer.items(),  key=lambda x: x[1]['time_rendering'], reverse=True)[:num_offenders]
        print_section('INSTANCE CHOKERS', sorted_drawer, total_rendering_time)

        print "The following items are consuming too much memory: \n\n"
        sorted_drawer = sorted(drawer.items(),  key=lambda x: x[1]['rss_diff'], reverse=True)[:num_offenders]
        print_section('MEMORY HOGS', sorted_drawer, total_rendering_time, total_rss_change)
       
        
        return drawer

def print_section(section_name, sorted_drawer, total_rendering_time, total_rss_change=None):
    print '\n\n', '=' * 80
    print section_name
    print '=' * 80
    for num, (id, fucker) in enumerate(sorted_drawer):
        print "%s. %s" %(num, get_normalized_url(id))
        print '-' *80
        print "Total time server spent rendering this page: %.2f seconds" % fucker['time_rendering']
        print "Average time to render: %s" % fucker['avg_req_time']
        print "Number of renders for this instance: %s " % fucker['url_hits']
        if total_rss_change:
            print "%% of memory used: %.2f" % ((fucker['total_rss']/total_rss_change) * 100)
        time_saved_render_once = fucker['time_rendering'] - fucker['avg_req_time']
        print "If you cached this page as a middle man, you would save %.4f%% of server load" % ((time_saved_render_once/total_rendering_time) * 100)
        print 
        print


def get_normalized_url(id):
    return id.replace("/VirtualHostBase/http/", "http://").replace("VirtualHostRoot/", "").replace(":80/engin", "")

if __name__ == '__main__':
    do_it()
