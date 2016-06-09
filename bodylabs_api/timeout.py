import signal
from contextlib import contextmanager


class TimeoutError(Exception):
    pass

def raise_on_timeout(msg):
    raise TimeoutError(msg)

@contextmanager
def Timeout(seconds=None, minutes=None, hours=None, message=None):
    '''
    Context manager that raises TimeoutError if not exitted in time.
    '''
    if seconds or minutes or hours:
        default_message = ['Timeout reached after']
        accumulated_seconds = int(0)
        if hours is not None:
            hours = int(hours)
            accumulated_seconds += hours * 3600
            default_message.append('{} hour(s)'.format(hours))
        if minutes is not None:
            minutes = int(minutes)
            accumulated_seconds += minutes * 60
            default_message.append('{} minute(s)'.format(minutes))
        if seconds is not None:
            seconds = int(seconds)
            accumulated_seconds += seconds
            default_message.append('{} second(s)'.format(seconds))
        if message is None:
            timeout_message = ' '.join(default_message)
        else:
            timeout_message = message.format(
                seconds=seconds, minutes=minutes,
                hours=hours, total_seconds=accumulated_seconds
            )

        signal_handler = lambda x, y: raise_on_timeout(timeout_message)
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(accumulated_seconds)
        try:
            yield
        finally:
            signal.alarm(0)
    else:
        yield
