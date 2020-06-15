import asyncio
import asyncio.base_events
import asyncio.events
import asyncio.log
import heapq
import selectors
import sys
import threading

from . import JavaClass, JavaInterface

Runnable = JavaInterface("java/lang/Runnable")


class _SelectorMinusSelect(selectors.PollSelector):
    # This class removes the `select()` method from PollSelector. On Android,
    # this would be an error -- it would result in the app freezing, triggering
    # an App Not Responding pop-up from the platform, and the user killing
    # the app.
    #
    # Instead, the AndroidEventLoop cooperates with the native Android event
    # loop to be woken up to get work done as needed.
    def select(self, *args, **kwargs):
        raise NotImplementedError(
            "_SelectorMinusSelect refuses to select(); see comments."
        )


class AndroidEventLoop(asyncio.SelectorEventLoop):
    def __init__(self):
        # Tell the parent constructor to use our custom Selector.
        super().__init__(_SelectorMinusSelect())

    def _android_call_later(self, runnable, timeout_millis):
        print("Doing call_later on", self, runnable, timeout_millis)
        self._handler.postDelayed(runnable, timeout_millis)

    def _add_callback(self, handle):
        # Do the work that `SelectorEventLoop` would do, but also ask the event loop to run.
        ret = super()._add_callback(handle)
        self._run_event_loop_once_soon()
        return ret

    def _call_soon(self, callback, args, context):
        # Do the work that `SelectorEventLoop` would do, but also ask the event loop to run.
        ret = super()._call_soon(callback, args, context)
        self._run_event_loop_once_soon()
        return ret

    def _run_event_loop_once_soon(self):
        if not self._event_loop_will_run_soon:
            self._android_call_later(
                self._runnables["_run_event_loop_once_cooperatively"], 0
            )
            # Set this to True now. When the event loop runs, it'll reset to False.
            self._event_loop_will_run_soon = True

    def _run_event_loop_once_cooperatively(self):
        """Compute the next moment at which the event loop should run delayed tasks, then
        ask Android to wake us up at that time.

        I/O waiting is handled separately (currently unimplemented).

        Since this is effectively the actual event loop, it also handles stopping the loop."""
        # If we are supposed to stop, actually stop.
        if self._stopping:
            self._stopping = False
            self._thread_id = None
            asyncio.events._set_running_loop(None)
            self._set_coroutine_origin_tracking(False)
            sys.set_asyncgen_hooks(*self._old_agen_hooks)
            # Remove Android-specific object.
            self._handler = None

        # If we have actually already stopped, then do nothing.
        if self._thread_id is None:
            return

        self._event_loop_will_run_soon = False

        # Based heavily on `BaseEventLoop._run_once()` from CPython.
        _MIN_SCHEDULED_TIMER_HANDLES = 100
        _MIN_CANCELLED_TIMER_HANDLES_FRACTION = 0.5
        MAXIMUM_SELECT_TIMEOUT = 24 * 3600

        sched_count = len(self._scheduled)
        if (
            sched_count > _MIN_SCHEDULED_TIMER_HANDLES
            and self._timer_cancelled_count / sched_count
            > _MIN_CANCELLED_TIMER_HANDLES_FRACTION
        ):
            # Remove delayed calls that were cancelled if their number
            # is too high
            new_scheduled = []
            for handle in self._scheduled:
                if handle._cancelled:
                    handle._scheduled = False
                else:
                    new_scheduled.append(handle)

            heapq.heapify(new_scheduled)
            self._scheduled = new_scheduled
            self._timer_cancelled_count = 0
        else:
            # Remove delayed calls that were cancelled from head of queue.
            while self._scheduled and self._scheduled[0]._cancelled:
                self._timer_cancelled_count -= 1
                handle = heapq.heappop(self._scheduled)
                handle._scheduled = False

        timeout = None
        if self._ready or self._stopping:
            timeout = 0
        elif self._scheduled:
            # Compute the desired timeout.
            when = self._scheduled[0]._when
            timeout = min(max(0, when - self.time()), MAXIMUM_SELECT_TIMEOUT)

        if timeout is None:
            # No delayed tasks, so we can return. The loop is running, ready for others to add tasks.
            return

        # TODO: When we implement FD-based wakeup, decide if the below causes excessive wakeups.
        self._android_call_later(
            self._runnables["_run_scheduled_callbacks_then_restart_loop"],
            timeout * 1000,
        )

    def _run_scheduled_callbacks_then_restart_loop(self):
        # Based heavily on `BaseEventLoop._run_once()` from CPython -- specifically, the part
        # after blocking on `select()`.
        # Handle 'later' callbacks that are ready.
        end_time = self.time() + self._clock_resolution
        while self._scheduled:
            handle = self._scheduled[0]
            if handle._when >= end_time:
                break
            handle = heapq.heappop(self._scheduled)
            handle._scheduled = False
            self._ready.append(handle)

        # This is the only place where callbacks are actually *called*.
        # All other places just add them to ready.
        # Note: We run all currently scheduled callbacks, but not any
        # callbacks scheduled by callbacks run this time around --
        # they will be run the next time (after another I/O poll).
        # Use an idiom that is thread-safe without using locks.
        ntodo = len(self._ready)
        for i in range(ntodo):
            handle = self._ready.popleft()
            if handle._cancelled:
                continue
            if self._debug:
                try:
                    self._current_handle = handle
                    t0 = self.time()
                    handle._run()
                    dt = self.time() - t0
                    if dt >= self.slow_callback_duration:
                        asyncio.log.logger.warning(
                            "Executing %s took %.3f seconds",
                            asyncio.base_events._format_handle(handle),
                            dt,
                        )
                finally:
                    self._current_handle = None
            else:
                handle._run()
        handle = None  # Needed to break cycles when an exception occurs.

        self._android_call_later(
            self._runnables["_run_event_loop_once_cooperatively"], 0
        )

    def run_forever_cooperatively(self):
        # Based heavily on `BaseEventLoop.run_forever()` in CPython.
        if self.is_running():
            raise RuntimeError("Refusing to start since loop is already running.")
        if self._closed:
            raise RuntimeError("Event loop is closed. Create a new object.")
        self._set_coroutine_origin_tracking(self._debug)
        self._thread_id = threading.get_ident()

        self._old_agen_hooks = sys.get_asyncgen_hooks()
        sys.set_asyncgen_hooks(
            firstiter=self._asyncgen_firstiter_hook,
            finalizer=self._asyncgen_finalizer_hook,
        )
        asyncio.events._set_running_loop(self)

        # Create Android handler to run our own code on. We assume that we are running
        # in the main Android activity thread, and we therefore do not worry about thread safety.
        Handler = JavaClass("android/os/Handler")
        self._handler = Handler()  # No-arg constructor uses main Android event loop.
        # Create a Java Runnables to tick the event loop forward. We statically create
        # Runnables to avoid creating lots of temporary objects.
        python_self = self

        class RunScheduledCallbacksThenRestartLoopRunnable(Runnable):
            def run(self):
                python_self._run_scheduled_callbacks_then_restart_loop()

        class RunEventLoopOnceCooperativelyRunnable(Runnable):
            def run(self):
                python_self._run_event_loop_once_cooperatively()

        self._runnables = {
            "_run_scheduled_callbacks_then_restart_loop": RunScheduledCallbacksThenRestartLoopRunnable(),
            "_run_event_loop_once_cooperatively": RunEventLoopOnceCooperativelyRunnable(),
        }
        self._run_event_loop_once_cooperatively()
        print("Started event loop")
