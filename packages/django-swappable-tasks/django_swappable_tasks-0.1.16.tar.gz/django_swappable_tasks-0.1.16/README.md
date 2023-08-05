# Django swappable tasks

## Introduction

> Considering you have a django project running on different servers each with its own asynchronous tasks handler this project helps you have one way to process the tasks while converting to the respective handler in the background. Currently Google Cloud Tasks and Celery are supported.

## Code Samples

> To set up you will need to add the following to your settings.py file
```DEFAULT_ASYNC_TASKS_HANDLER = env('DEFAULT_ASYNC_TASKS_HANDLER')```
This can either be ```CELERY``` or ```GOOGLE_CLOUD_TASKS```.

If you are using celery remember to set up other settings such as ```CELERY_BROKER_URL```, ```CELERY_RESULT_BACKEND```, ```CELERY_ACCEPT_CONTENT```, ```CELERY_TASK_SERIALIZER```, ```CELERY_RESULT_SERIALIZER```, ```CELERY_TIMEZONE```

For google cloud tasks remember to set up the following settings ```GOOGLE_CLOUD_PROJECT_ID```, ```GOOGLE_CLOUD_TASKS_LOCATION_NAME```, ```GOOGLE_APPLICATION_CREDENTIALS```

Add the view to your projects urls.py file as below

````
from django.urls import path, include
urlpatterns = [
          ...
          path('tasks/', include('django_swappable_tasks.urls')),    
          ...    
]
````



Assume you have a task as below
````
from myproject.celery_app import app

@app.task
def my_blocking_task(name, age):
      import time
      import random
      sleep_seconds = random.randint(20, 45)
      time.sleep(sleep_seconds)
      print("Hello {}, your age is {}".format(name, age)
````
To process a task asynchronously do it as below
````
from django_swappable_tasks.utils import process_task_asynchronously
from my project.tasks import my_blocking_task
task_kwargs = {"name": "John Doe", "age" : 18}
process_task_asynchronously(my_blocking_task, "google_default_queue", task_args=[], task_kwargs= task_kwargs)
````

## Installation

> To install the package do 
```pip install django_swappable_tasks```
You can also directly install from [The GitHub Repository](https://github.com/jerryshikanga/django_swappable_tasks.git)
