from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse

from boto1.models import Image, Hit, Result
from optparse import make_option



import boto
import boto.mturk
import boto.mturk.connection

from .create_hits import get_connection


import json
import time, datetime
_time = time
from datetime import timedelta, tzinfo

STDOFFSET = timedelta(seconds = -_time.timezone)
if _time.daylight:
    DSTOFFSET = timedelta(seconds = -_time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET
ZERO = timedelta(0)

class LocalTimezone(tzinfo):

    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt.tm_isdst > 0

Local = LocalTimezone()


def from_w3c_to_datetime(str_date):
  """This is an utility function for converting the datetime returned by AMT to a proper 
  datetime in Python. The datetime in AMT contains the offset of the timezone."""
  import re
  result = re.findall("\d{2}(Z){1,5}", str_date)
  # remove all Z
  replaced = str_date.replace('Z', '')
  
  nb_z = len(result[0]) if len(result) > 0 else 0
  
  class NumberofZOffset(datetime.tzinfo):
    """Fixed offset in minutes east from UTC."""

    def __init__(self, offset, name):      
      self.__offset = datetime.timedelta(hours = offset*5)
      self.__name = name


    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO

  my_time = datetime.datetime.strptime(replaced, "%Y-%m-%dT%H:%M:%S")
  my_time.replace(tzinfo=NumberofZOffset(nb_z, 'w3c' + 'z'*nb_z))
  
  return my_time


def get_all_hits():
  """Retrieves all hits.
  """
  hits = [ i for i in get_connection().get_all_hits()]
  pn = 1
  total_pages = 1
  while pn < total_pages:
    pn = pn + 1
    print "Request hits page %i" % pn
    temp_hits = get_connection().get_all_hits(page_number=pn)
    hits.extend(temp_hits)
  return hits



def get_all_reviewable_hits():
  """Retrieves all hits that are in review state"""
  page_size = 50
  hits = get_connection().get_reviewable_hits(page_size=page_size)
  #print "Total results to fetch %s " % hits.TotalNumResults
  #print "Request hits page %i" % 1
  
  total_pages = float(hits.TotalNumResults)/page_size
  int_total= int(total_pages)
  if(total_pages-int_total>0):
    total_pages = int_total+1
  else:
    total_pages = int_total
    
  pn = 1
  while pn < total_pages:
    pn = pn + 1
    #print "Request hits page %i" % pn
    temp_hits = get_connection().get_reviewable_hits(page_size=page_size,page_number=pn)
    hits.extend(temp_hits)
  return hits


def get_all_responses(reviewable_hits, all_hits, assignments_to_skip = None):
  """Retrieves the content of the responses.
  
  :param set assignments_to_skip: a set of assignments for which the results can be skipped.
  :returns: a dictionary containing the collected responses. The dictionary is organized as 
  follow:
    - The first index of the dict is the hit id.
    - The second key of the dict is the assignment id
    - 3 entries are filled then:
      - 'response_time' is the time laps between the submission of the response and the hit creation date
      - 'worker_id' is the id of the worker which submits the current response
      - 'fields' is a dictionary containing the fields of the response, where the keys are the fields id
        and the values are the content of the responses.
  :rtype: dict
  
  """
  hit_ids = [i.HITId for i in all_hits]
  responses = {}
  
  for hit in reviewable_hits:
    assignments = get_connection().get_assignments(hit.HITId)
    
    if not assignments_to_skip is None:
      assignments = (a for a in assignments if not a.AssignmentId in assignments_to_skip)
    
    find_hit = hit_ids.index(hit.HITId)
    
    hit_creation_time = from_w3c_to_datetime(all_hits[find_hit].CreationTime)
    
    current_response = {}
    responses[hit.HITId] = current_response
    
    for assignment in assignments:
      
      current_assignment = {}
      current_response[assignment.AssignmentId] = current_assignment
      
      response_submission_time = from_w3c_to_datetime(assignment.SubmitTime)
      response_time = response_submission_time - hit_creation_time
      current_assignment['response_time'] = response_time
      current_assignment['worker_id'] = assignment.WorkerId
      
      fields = {}
      current_assignment['fields'] = fields
            
      for question_form_answer in assignment.answers[0]:
        id, value = question_form_answer.qid, question_form_answer.fields[0]
        fields[id] = value
      
  return responses



class Command(BaseCommand):
  help = 'Retrieves the results from AMT'


  def print_hit_status(self, hits):
    """Prints the status of hits
  
    :param list hits: list of hits of interest
    """
    for hit in hits:
      self.stdout.write("HIT id=%s status=%s created=%s UTC" % (hit.HITId, hit.HITStatus, from_w3c_to_datetime(hit.CreationTime)))

  def handle(self, *args, **options):
    
    nb_new_result_stored = 0
    
    self.stdout.write('Get all hits from Amazon')
    all_hits = get_all_hits()
    all_hits_set = set((h.HITId.upper().strip() for h in all_hits))
  
    self.stdout.write('Get all hits in review state')
    review_hits = get_all_reviewable_hits()
    review_set = set((h.HITId.upper().strip() for h in review_hits))
    
    # intersect with the set of hits for this application
    self.stdout.write('Intersecting with our content')
    my_application_hits = set((c.hit_id.upper().strip() for c in Hit.objects.all()))
  

    all_hits_set.intersection_update(my_application_hits)
    review_set.intersection_update(my_application_hits)
    all_hits = [a for a in all_hits if a.HITId in all_hits_set]
    review_hits = [a for a in review_hits if a.HITId in review_set]
    
    # already filled assignments
    assignments_id_already_set = set((c.assignment_id for c in Result.objects.all()))
    
    # retrieving the responses
    responses = get_all_responses(review_hits, all_hits, assignments_id_already_set)
    
    for hit_id, dic_assignment in responses.iteritems():
      current_hit = Hit.objects.get(hit_id=hit_id)
      image_object = current_hit.image
      
      for assignment_id, values in dic_assignment.iteritems():
        
        try:
          current_response = Result.objects.create(image = image_object, 
                                                     hit = current_hit,
                                                     assignment_id = assignment_id)
          
          current_response.content = values['fields']
          current_response.save()
          nb_new_result_stored += 1
        except Exception, e:
          self.stderr.write('  responses not added to the database for image %s (assignment %s)' % (image_object.name, assignment_id))
          continue   
    
    
    self.stdout.write('Successfully retrieved results')
    self.stdout.write('- New results created %d' % nb_new_result_stored)
    self.stdout.write('- Current number of results %d' % Result.objects.count())

    return

    