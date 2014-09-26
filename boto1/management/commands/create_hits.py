from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse

from boto1.models import Image, Hit
from optparse import make_option


import boto
import boto.mturk
import boto.mturk.connection

_mturk_connexion = None

def get_connection():
  global _mturk_connexion
  
  if _mturk_connexion is None:
    _mturk_connexion = boto.mturk.connection.MTurkConnection(
       aws_access_key_id="my_secret", 
       aws_secret_access_key='my_secret_key', 
       debug=True, 
       host='mechanicalturk.sandbox.amazonaws.com')
  
  return _mturk_connexion

def create_external_question_hit(title, url):
  question = boto.mturk.question.ExternalQuestion(url, 500)
  new_hit = get_connection().create_hit(
                question=question, 
                title=title, 
                description="http django csrf disabled demo", 
                reward=0.02, 
                keywords="image,processing,segmentation")
  
  return new_hit


class Command(BaseCommand):
  help = 'Synchronise the content not sent yet to Amazon'

  option_list = BaseCommand.option_list + (
    make_option(
      '--careful',
      dest='careful',
      default=None,
      type='string',
      help='checks for collisions, takes more time to complete'),
  )

  def handle(self, *args, **options):
    
    nb_hit_created = 0
    
    for image_object in Image.objects.filter(hit__isnull=False).distinct():
      self.stdout.write(' * %-50s %s' % (image_object.name, ' '.join(i.hit_id for i in image_object.hit.all())))
    
    images_to_sync = Image.objects.filter(hit__isnull=True).distinct()
    for image_object in images_to_sync:
  
      new_hit = create_external_question_hit(
                  'botox', 
                  reverse('image_annotation_form', args=[image_object.id]))
      
      try:
        current_hit = Hit.objects.create(image = image_object, hit_id = new_hit[0].HITId)
      except Exception, e:
        self.stderr.write('  hit not added to the database but added to Amazon for image %s %r' % (image_object.name, new_hit))
        continue

      self.stdout.write(' + %-50s %s' % (image_object.name, current_hit.hit_id))
      
      nb_hit_created += 1
    
    self.stdout.write('Successfully created the hits')
    self.stdout.write('- New hits created %d' % nb_hit_created)
    self.stdout.write('- Current number of images %d' % Image.objects.count())
