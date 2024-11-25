class RoutineStatus:
    WAITING = "waiting" # Routine is waiting for the condition to be met
    PENDING = "pending" # Routine is pending to run
    DONE = "done" # Routine is done
    RETRY = "retry"
    RUNNING = "running"
    CANCELED = "canceled"
    FAIL = "fail"
    ERROR = "error" 
    COMPLETE = "complete"
    UNKNOWN = "unknown"

class TaskStatus:
    PENDING = "pending" # Indicate no task has been set
    READY = "ready" # Indicate task has been set and ready to run
    RUNNING = "running"
    # COMPLETED = "completed"
    DONE = "done"
    # FAILED = "failed"
    ERROR = "error"
    # UNKNOWN = "unknown"

class TaskInstanceStatus:
    PENDING = "pending" # Indicate no task has been set
    RUNNING = "running"
    # COMPLETED = "completed"
    DONE = "done"
    # FAILED = "failed"
    ERROR = "error"
    UNKNOWN = "unknown"
