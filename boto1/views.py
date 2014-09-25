from django.shortcuts import render

from boto1.models import Image, Hit, Result
from boto1.forms import FormAMT
from django.views.generic.detail import DetailView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt

from django.utils.decorators import method_decorator
from django.conf import settings

def index(request):
  images_list = Image.objects.order_by('name')
  return render(
          request, 
          'boto1/index.html', 
          {'images_list': images_list})
  

class ImageAnnotation(DetailView):
  """This one shows the form on the user side"""

  model = Image
  template_name = 'boto1/image_task.html'

  @method_decorator(xframe_options_exempt)
  def dispatch(self, *args, **kwargs):
    return super(ImageAnnotation, self).dispatch(*args, **kwargs)


  def get_context_data(self, **kwargs):
    context = super(ImageAnnotation, self).get_context_data(**kwargs)
    current_image = self.object # done in super
    
    context['assignmentid'] = self.request.GET.get('assignmentId', '')
    if(context['assignmentid'] == '' or context['assignmentid'] == 'ASSIGNMENT_ID_NOT_AVAILABLE'):
      context['is_demo'] = True
    else:
      context['is_demo'] = False

    context['amazon_url'] = self.request.GET.get('turkSubmitTo________', settings.MTURK_SUBMIT_URL)
    context['form'] = FormAMT(initial = {'assignmentId' : context['assignmentid'] })
    #context['context'] = '%r' % context
    
    return context
  
