from django.core.management.base import BaseCommand, CommandError
from django.core.files import File

from boto1.models import Image
import os
from os.path import getsize, join 
from optparse import make_option

image_ext = ['.jpg', '.png', '.tiff']


class Command(BaseCommand):
  help = 'Adds the content of a folder and subfolders into the database'

  option_list = BaseCommand.option_list + (
    make_option(
      '--directory',
      dest='directory',
      default=None,
      type='string',
      help='root directory for parsing'),
    make_option(
      '--root_directory',
      dest='root_directory',
      default=None,
      type='string',
      help='''Specifies the root of all images directory, in case it is modified on the server. Images are 
           identified by their relative path name to this root.'''),
  )

  def handle(self, *args, **options):
    
    
    add_image_count = 0
    current_directory = options['directory']
      
    if options['root_directory']:
      root_dir = options['root_directory']
    else:
      root_dir = current_directory
    
    for root, dirs, files in os.walk(current_directory):
      print '- adding content from directory', root, ' --- #files %d / #MB %.2f' % \
        (len(files), sum(getsize(join(root, name)) for name in files)/(1024*1024))
    
      for name in files:
        if not os.path.splitext(name)[1].lower() in image_ext:
          self.stdout.write('  skipping file %s' % join(root, name))
          continue
        
        fullpath = join(root, name)
      
        current_im_filename = os.path.relpath(fullpath, root_dir)
        print current_im_filename
        try:
          current_im = Image.objects.create(im = File(open(fullpath)), name = current_im_filename)
        except Exception, e:
          self.stderr.write('  file %s not added' % current_im_filename)
          continue
          #raise CommandError('Error adding image %s to the database %r' % (current_im_filename, e))
  
        current_im.save()
        add_image_count += 1
  
    self.stdout.write('Successfully added directory "%s" content to the database' % current_directory)
    self.stdout.write('- New images added %d' % add_image_count)
    self.stdout.write('- Current number of images %d' % Image.objects.count())
    
