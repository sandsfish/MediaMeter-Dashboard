import datetime
import re

def solr_query(media, start, end):
    '''Convert a media query, start and end date into a solr query string.'''
    startdate = datetime.datetime.strptime(start, '%Y-%m-%d').date()
    enddate = datetime.datetime.strptime(end, '%Y-%m-%d').date()
    query = '+publish_date:[%sT00:00:00Z TO %sT23:59:59Z] AND %s' % (
        startdate.strftime('%Y-%m-%d')
        , enddate.strftime('%Y-%m-%d')
        , media
    )
    return query

def solr_date_queries(media, start, end):
    '''Return a list of solr queries, one for each day between start and end
    (inclusive).'''
    startdate = datetime.datetime.strptime(start, '%Y-%m-%d').date()
    enddate = datetime.datetime.strptime(end, '%Y-%m-%d').date()
    num_days = (enddate - startdate).days + 1
    dates = [startdate + datetime.timedelta(x) for x in range(num_days)]
    dates = [date.strftime('%Y-%m-%d') for date in dates]
    query_format = "+publish_date:[%sT00:00:00Z TO %sT23:59:59Z] AND %s"
    queries = [(date, query_format % (date, date, media)) for date in dates]
    return queries

def media_to_solr(media):
    d = { 'sets':[], 'sources':[] }
    for m in media.split(','):
        match = re.search(r'(.*):\[(.*)\]', m)
        d[match.group(1)] = match.group(2).split(',')
    solr = ['media_id:%d' % int(i) for i in d['sources'] if len(i)]
    solr += ['media_sets_id:%d' % int(i) for i in d['sets'] if len(i)]
    return ' AND '.join(solr)
    