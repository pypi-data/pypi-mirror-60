import json
import logging

from django_swappable_tasks import handlers

logger = logging.getLogger(__name__)


def get_fully_qualified_task_name(obj):
    """
    :param obj: a valid python object
    :return: fully qualified dotted name
    For example from betarcade.apps.bets.tasks import update_fixtures_from_remote
    will return betarcade.apps.bets.tasks.update_fixtures_from_remote
    """
    return ".".join([obj.__module__, obj.__name__])


def import_method_from_name(function_string):
    import importlib
    mod_name, func_name = function_string.rsplit('.', 1)
    mod = importlib.import_module(mod_name)
    return getattr(mod, func_name)


def split_comma_separated_args(comma_separated_args):
    if comma_separated_args is None:
        return []
    return [int(i) if i.isdigit() else str(i) for i in comma_separated_args.split(',')]


def dump_args_into_comma_separated_list(task_args):
    if not isinstance(task_args, list):
        task_args_list = list()
        task_args_list.append(task_args)
        task_args = task_args_list
    comma_separated_args = ','.join(str(arg) for arg in task_args)
    return comma_separated_args


def run_task(task_path, args_json, kwargs_json):
    args, kwargs = [], {}
    if args_json is not None:
        args = split_comma_separated_args(args_json)
    if kwargs_json is not None:
        kwargs = json.loads(kwargs_json)
    try:
        if task_path is not None:
            task = import_method_from_name(task_path)
            logger.debug("Running {}".format(task_path))
            result = task(*args, **kwargs)
            logger.debug("Completed {}. Result : {}.".format(task_path, str(result)))
            return True, str(result)
        else:
            return False, "Task not provided."
    except Exception as e:
        logger.error(e)
        return False, "Error : {}".format(str(e))


def process_task_asynchronously(task, queue, task_args=[], task_kwargs={}, *args, **kwargs):
    from django.conf import settings
    if settings.DEFAULT_ASYNC_TASKS_HANDLER == "CELERY":
        return handlers.CeleryHandler.add_task_to_queue(task, task_args, task_kwargs, queue)
    elif settings.DEFAULT_ASYNC_TASKS_HANDLER == "GOOGLE_CLOUD_TASKS":
        return handlers.GoogleCloudTasksHandler.add_task_to_queue(task, task_args, task_kwargs, queue)
    else:
        raise ValueError("Unknown tasks handler {}.".format(settings.DEFAULT_ASYNC_TASKS_HANDLER))
