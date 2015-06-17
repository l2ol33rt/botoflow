import time

from awsflow import *
from awsflow.core.exceptions import CancellationError, CancelledError

class MySpecialCancelledError(CancelledError):

    def __init__(self, extra_data):
        self.extra_data = extra_data


@activities(schedule_to_start_timeout=60,
            start_to_close_timeout=60)
class BunchOfActivities(object):
    @activity(version='1.1')
    def sum(self, x, y):
        return x + y

    @activity(version='1.4',
              schedule_to_close_timeout=60*2)
    def mul(self, x, y):
        return x * y

    @activity('1.1')
    def throw(self):
        raise ValueError("Hello-Error")

    @activity('1.0')
    def heartbeating_activity(self, repeat_num):
        for i in range(repeat_num):
            time.sleep(0.2)
            get_context().heartbeat(str(i))

    @activity('1.0', task_list='FAKE')
    def wrong_tasklist_activity(self, sleep_secs):
        return

    @activity('1.0')
    def heartbeating_custom_error_activity(self, repeat_num):
        for i in range(repeat_num):
            time.sleep(0.2)
            try:
                get_context().heartbeat(str(i))
            except CancellationError:
                raise MySpecialCancelledError("spam")


@activities(schedule_to_start_timeout=60,
            start_to_close_timeout=60)
class ManualActivities(object):
    @manual_activity(version='1.0')
    def perform_task(self, **kwargs):
        activity_context = context.get_context()
        task_token = activity_context.task.token

        with open('task_token.txt', 'w') as shared_file:
            shared_file.write(task_token)
