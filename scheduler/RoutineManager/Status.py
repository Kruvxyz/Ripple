class RoutineStatus:
    PENDING = "pending" # Routine initial state before running
    WAITING = "waiting" # Routine is waiting for the condition to be met
    STARTING = "starting"
    RETRYING = "retrying"
    RUNNING = "running"
    CANCELED = "canceled"
    RESTART = "restart"
    FAILED = "failed"
    ERROR = "error" # in use
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

class CommandStatus:
    pass