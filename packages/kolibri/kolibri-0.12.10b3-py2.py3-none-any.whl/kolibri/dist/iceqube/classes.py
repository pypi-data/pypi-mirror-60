import copy
import logging
from functools import partial

from iceqube.utils import import_stringified_func, stringify_func

logger = logging.getLogger(__name__)


class State(object):
    """
    the State object enumerates a Job's possible valid states.

    SCHEDULED means the Job has been accepted by the client, but has not been
    sent to the workers for running.

    QUEUED means the Job has been sent to the workers for running, but has not
    been run yet (to our knowledge).

    RUNNING means that one of the workers has started running the job, but is not
    complete yet. If the job has been set to track progress, then the job's progress
    and total_progress fields should be continuously updated.

    FAILED means that the job's function has raised an exception during runtime.
    The job's exception and traceback fields should be set.

    CANCELING means that the system has received the user's request to cancel, and will
    cancel the job once an opportunity arises.

    CANCELED means that the job has been canceled from running.

    COMPLETED means that the function has run to completion. The job's result field
    should be set with the function's return value.
    """

    SCHEDULED = "SCHEDULED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    CANCELING = "CANCELING"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"


class Job(object):
    """
    Job represents a function whose execution has been deferred through the Client's schedule function.

    Jobs are stored on the storage backend for persistence through restarts, and are scheduled for running
    to the workers.
    """

    def __init__(self, func, *args, **kwargs):
        """
        Create a new Job that will run func given the arguments passed to Job(). If the track_progress keyword parameter
        is given, the worker will pass an update_progress function to update interested parties about the function's
        progress. See Client.__doc__ for update_progress's function parameters.

        :param func: func can be a callable object, in which case it is turned into an importable string,
        or it can be an importable string already.
        """
        self.job_id = kwargs.pop('job_id', None)
        self.state = kwargs.pop('state', State.QUEUED)
        self.traceback = ""
        self.exception = None
        self.track_progress = kwargs.pop('track_progress', False)
        self.cancellable = kwargs.pop('cancellable', False)
        self.extra_metadata = kwargs.pop('extra_metadata', {})
        self.progress = 0
        self.total_progress = 0
        self.args = args
        self.kwargs = kwargs

        if callable(func):
            funcstring = stringify_func(func)
        elif isinstance(func, str):
            funcstring = func
        else:
            raise Exception(
                "Error in creating job. We do not know how to "
                "handle a function of type {}".format(type(func)))

        self.func = funcstring

    def get_lambda_to_execute(self):
        """
        return a function that executes the function assigned to this job.

        If job.track_progress is None (the default), the returned function accepts no argument
        and simply needs to be called. If job.track_progress is True, an update_progress function
        is passed in that can be used by the function to provide feedback progress back to the
        job scheduling system.

        :return: a function that executes the original function assigned to this job.
        """
        def y(update_progress_func, cancel_job_func):
            """
            Call the function stored in self.func, and passing in update_progress_func
            or cancel_job_func depending if self.track_progress or self.cancellable is defined,
            respectively.
            :param update_progress_func: The callback for when the job updates its progress.
            :param cancel_job_func: The function that the function has to call occasionally to see
            if the user wants to cancel the currently running job.
            :return: Any
            """

            func = import_stringified_func(self.func)
            extrafunckwargs = {}

            args, kwargs = copy.copy(self.args), copy.copy(self.kwargs)

            if self.track_progress:
                extrafunckwargs["update_progress"] = partial(update_progress_func, self.job_id)

            if self.cancellable:
                extrafunckwargs["check_for_cancel"] = partial(cancel_job_func, self.job_id)

            kwargs.update(extrafunckwargs)

            return func(*args, **kwargs)

        return y

    @property
    def percentage_progress(self):
        """
        Returns a float between 0 and 1, representing the current job's progress in its task.
        If total_progress is not given or 0, just return self.progress.

        :return: float corresponding to the total percentage progress of the job.
        """

        if self.total_progress != 0:
            return float(self.progress) / self.total_progress
        else:
            return self.progress

    def __repr__(self):
        return "<Job id: {id} state: {state} progress: {p}/{total} func: {func}>".format(
            id=self.job_id,
            state=self.state,
            func=self.func,
            p=self.progress,
            total=self.total_progress
        )
