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

class TaskInstanceStatus:
    PENDING = "pending" # Indicate no task has been set
    READY = "ready" # Indicate task has been set and ready to run
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"

class TriggerInstanceStatus:
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"

