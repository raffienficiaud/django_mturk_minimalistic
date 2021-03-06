from django.db import models

# Create your models here.


class Image(models.Model):
  name = models.CharField(max_length = 128, unique = True)
  im   = models.ImageField(upload_to='pictures', blank = False)
  
  def __unicode__(self):
    return "%.5d - %s" % (self.id, self.name)

class Hit(models.Model):
  # an image corresponds to one hit
  image = models.ForeignKey(Image, related_name = 'hit')
  hit_id= models.CharField(max_length = 50, db_index = True, unique = True)

  def __unicode__(self):
    return "%-50s [%-50s]" % (self.hit_id, self.image.name)


class Result(models.Model):
  # the image on which this result applies
  image = models.ForeignKey(Image, related_name = 'results')

  # the content of the response
  content = models.TextField(max_length = 2048, blank = True, null = True)

  #
  # Amazon related stuff
  assignment_id = models.CharField(max_length = 50, db_index = True, unique = True)
  # the associated hit, if already processed
  hit   = models.ForeignKey(Hit, null = True)
