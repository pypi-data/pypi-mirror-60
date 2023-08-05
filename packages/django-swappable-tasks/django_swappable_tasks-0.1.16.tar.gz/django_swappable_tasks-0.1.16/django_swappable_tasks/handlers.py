import datetime
import json
import logging

from django.conf import settings
from django.urls import reverse

from django_swappable_tasks import utils

logger = logging.getLogger(__name__)


class TasksHandlerBase(object):
    @classmethod
    def add_task_to_queue(cls, task, task_args, task_kwargs, queue, *args, **kwargs):
        raise NotImplementedError


class CeleryHandler(TasksHandlerBase):
    @classmethod
    def add_task_to_queue(cls, task, task_args, task_kwargs, queue, *args, **kwargs):
        return task.delay(*task_args, **task_kwargs)


class GoogleCloudTasksHandler(TasksHandlerBase):
    @classmethod
    def add_task_to_queue(cls, task, task_args, task_kwargs, queue, *args, **kwargs):
        """Create a task for a given queue with an arbitrary payload."""
        from google.cloud import tasks_v2
        from google.protobuf import timestamp_pb2

        # Create a client.
        client = tasks_v2.CloudTasksClient()

        project, location = kwargs.get('project', None), kwargs.get('location', None)

        if project is None:
            project = settings.GOOGLE_CLOUD_PROJECT_ID
        if location is None:
            location = settings.GOOGLE_CLOUD_TASKS_LOCATION_NAME

        fully_qualified_task_name = utils.get_fully_qualified_task_name(task)

        payload = dict(task=fully_qualified_task_name)
        if len(task_args) > 0:
            payload.update({'args': utils.dump_args_into_comma_separated_list(task_args)})
        if len(task_kwargs.keys()) > 0:
            payload.update({'kwargs': json.dumps(task_kwargs)})

        # Construct the fully qualified queue name.
        parent = client.queue_path(project, location, queue)
        import urllib
        query_string = urllib.parse.urlencode(payload)
        relative_uri = "{}?{}".format(reverse('django_swappable_tasks:tasks'), query_string)

        # Construct the request body.
        task = {
            'app_engine_http_request': {  # Specify the type of request.
                'http_method': 'POST',
                'relative_uri': relative_uri
            }
        }
        if payload is not None:
            # The API expects a payload of type bytes.
            converted_payload = str(payload).encode()

            # Add the payload to the request.
            task['app_engine_http_request']['body'] = converted_payload

        in_seconds = kwargs.get('in_seconds', None)
        if in_seconds is not None:
            # Convert "seconds from now" into an rfc3339 datetime string.
            d = datetime.datetime.utcnow() + datetime.timedelta(seconds=in_seconds)

            # Create Timestamp protobuf.
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(d)

            # Add the timestamp to the tasks.
            task['schedule_time'] = timestamp

        # Use the client to build and send the task.
        response = client.create_task(parent, task)

        logger.debug('Created task {}'.format(response.name))
        return response

