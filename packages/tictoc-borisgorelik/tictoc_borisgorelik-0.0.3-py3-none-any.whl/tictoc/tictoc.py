"""TicToc provides a simple mechanism to measure the wall time (a stopwatch) with a reasonable accuracy."""

import time


class TicToc:
    """
    TicToc provides a simple mechanism to measure the wall time (a stopwatch) with a reasonable accuracy.

    Crete an object. Run `tic()` to start the timer, `toc()` to stop it. Repeated tic-toc's will accumulate the time.
    The tic-toc pair is useful in interactive environments such as the shell or a notebook. Whenever `toc` is called,
    a useful message is automatically printed to stdout. For non-interactive purposes, use `start` and `stop`, as
    they are less verbose.
    Following is an example of how to use TicToc:

    ```
        def leibniz_pi(n):
        ret = 0
        for i in range(n * 1000000):
            ret += ((4.0 * (-1) ** i) / (2 * i + 1))
        return ret

    # usage examples
    tt_overall = TicToc('overall')  # started  by default
    tt_cumulative = TicToc('cumulative', start=False)
    for iteration in range(1, 4):
        tt_cumulative.start()
        tt_current = TicToc('current')
        pi = leibniz_pi(iteration)
        tt_current.stop()
        tt_cumulative.stop()
        time.sleep(0.01)  # this inteval will not be accounted for by `tt_cumulative`
        print(
            f'Iteration {iteration}: pi={pi:.9}. '
            f'The computation took {tt_current.running_time():.2f} seconds. '
            f'Running time is {tt_overall.running_time():.2} seconds'
        )
    tt_overall.stop()
    print(tt_overall)
    print(tt_cumulative)
    ```

    """

    def __init__(self, name=None, start=True, verbose=False, report_invocations=True):
        """
        Create a new stopwatch.

        Parameters
        ----------
        name : str
            Every stopwatch can have an optional name.
        start : bool
            If True (default), creating the object will also start the stopwatch
        verbose : bool
            Verbosity control
        report_invocations  : bool
            Should `__str__` contain information on the how many times the stopwatch was invoked
        """
        if name is None:
            name = 'Running time'
        self.name = name
        self.delta_time = 0.0
        self.times = 0
        self._t_start = None
        self.state = 'off'
        self.verbose = verbose
        self.report_invocations = report_invocations
        if start is True:
            self.start()

    def __add__(self, other):
        """
        Adding one TicToc to another will combine their cumulative running times and the number of invocations.

        The adding result inherits all the information such as state, verbosity etc from `self`

        Parameters
        ----------
        other : TicToc
            Another TicToc object
        Returns
        -------
        TicToc
            the new object.
        """
        assert not self.is_running()
        assert not other.is_running()
        ret = self.__class__(self.name, False, self.verbose, self.report_invocations)
        ret.delta_time = self.delta_time + other.delta_time
        ret.times = self.times + other.times
        return ret

    def tic(self):
        """Start the stopwatch. Alias to self.start()."""
        return self.start()

    def start(self):
        """Start the stopwatch."""
        self._t_start = time.time()
        if self.state != 'on':
            self.times += 1
        self.state = 'on'
        return self

    def toc(self):
        """Like `stop` but prints and returns the string representation of this object."""
        self.stop()
        ret = self.__str__()
        if self.verbose:
            print(ret)
        return ret

    def stop(self):
        """Stop the stopwatch."""
        t_stop = time.time()
        self.state = 'off'
        delta_time = t_stop - self._t_start
        self.delta_time += delta_time
        self._t_start = None
        return self

    def restart(self):
        """Reset everything and start again."""
        self.reset()
        return self.tic()

    def reset(self):
        """Reset the inner state. Set the status to 'off'."""
        if self.is_running():
            self.stop()
        self.delta_time = 0.0
        self.times = 0

    def running_time(self):
        """Return the running time in seconds without altering the current stopwatch state."""
        if self.state == 'on':
            t_curr = time.time()
            delta_time = t_curr - self._t_start
            delta_time += self.delta_time
        else:
            delta_time = self.delta_time
        return delta_time

    def is_running(self):
        """Is the stopwatch running."""
        return self.state == 'on'

    def str_running_time(self):
        """Return nicely formatted string representation of the running time."""
        seconds_per_minute = 60.
        seconds_per_hour = 60. * seconds_per_minute
        delta_time = self.running_time()
        int_hours = int(delta_time / seconds_per_hour)
        minutes = (delta_time - int_hours * seconds_per_hour) / seconds_per_minute
        int_minutes = int(minutes)
        seconds = delta_time - int_hours * seconds_per_hour - int_minutes * seconds_per_minute
        if int_hours:
            ret = '%02d:%02d:%04.1f' % (int_hours, int_minutes, seconds)
        else:
            ret = '%02d:%04.1f' % (int_minutes, seconds)
        return ret

    def __str__(self):
        """Return the string representation of self."""
        ret = self.str_running_time()
        if bool(self.name):
            ret = f'{self.name}: {ret}'
        if self.report_invocations or self.verbose:
            ret += f' ({self.times:,d} invocations)'
        return ret

    def __repr__(self):
        """Return the string representation of the running time."""
        return self.str_running_time()
