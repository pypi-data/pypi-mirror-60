import logging

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from django_swappable_tasks import utils

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TasksHandlerView(View):
    def post(self, request, *args, **kwargs):
        task = request.GET.get('task', None)
        args_json = request.GET.get('args', None)
        kwargs_json = request.GET.get('kwargs', None)
        return self.process_task_request(task, args_json, kwargs_json)

    def get(self, request, *args, **kwargs):
        task = request.GET.get('task', None)
        args_json = request.GET.get('args', None)
        kwargs_json = request.GET.get('kwargs', None)
        return self.process_task_request(task, args_json, kwargs_json)

    def process_task_request(self, task, args_json, kwargs_json):
        success, result = utils.run_task(task_path=task, args_json=args_json, kwargs_json=kwargs_json)
        if success:
            status = 200
        else:
            status = 400
        return HttpResponse("Status {} Result : {}".format(success, result), status=status)
