import asyncio
import asyncio.base_events
import asyncio.events
import asyncio.log
import heapq
import selectors
import sys
import threading

from . import JavaClass, JavaInterface

Handler = JavaClass("android/os/Handler")
Runnable = JavaInterface("java/lang/Runnable")


class AndroidEventLoop(asyncio.SelectorEventLoop):
    # `AndroidEventLoop` exists to support starting the Python event loop cooperatively with
    # the built-in Android event loop. Since it's cooperative, it has a `run_forever_cooperatively()`
    # method which returns immediately. This is is different from the parent class's `run_forever()`,
    # which blocks.
    #
    # In some cases, for simplicity of implementation, this class reaches into the internals of the
    # parent and grandparent classes.
    #
    # A Python event loop needs to handle two things:
    #
    # - Waking the event loop when delayed tasks are ready to run.
    #
    # - Waking the event loop when I/O is possible on a set of file descriptors.
    #
    # `SelectorEventLoop` uses an approach we **cannot** use: it calls the `select()` method
    # to block waiting for specific file descriptors to be come ready for I/O, or a timeout
    # corresponding to the soonest delayed task, whichever occurs sooner.
    #
    # To handle delayed tasks, `AndroidEventLoop` asks the Android event loop to wake it up when
    # its soonest delayed task is ready. To accomplish this, it relies on a `SelectorEventLoop`
    # implementation detail: `_scheduled` is a collection of tasks sorted by soonest wakeup time.
    #
    # To handle waking up when it's possible to do I/O, `AndroidEventLoop` will register file descriptors
    # with the Android event loop so the platform can wake it up accordingly. It does not do this yet.
    def __init__(self):
        # Tell the parent constructor to use our custom Selector.
        super().__init__(_SelectorMinusSelect())
        # Create placeholders for lazily-created objects.
        self.android_interop = AndroidInterop()

    # Override parent `_call_soon()` to ensure Android wakes us up to do the delayed task.
    def _call_soon(self, callback, args, context):
        ret = super()._call_soon(callback, args, context)
        self.enqueue_android_wakeup_for_delayed_tasks()
        return ret

    # Override parent `_add_callback()` to ensure Android wakes us up to do the delayed task.
    def _add_callback(self, handle):
        ret = super()._add_callback(handle)
        self.enqueue_android_wakeup_for_delayed_tasks()
        return ret

    def run_forever_cooperatively(self):
        """Configure the event loop so it is started, doing as little work as possible to
        ensure that. Most Android interop objects are created lazily so that the cost of
        event loop interop is not paid by apps that don't use the event loop."""
        # Based on `BaseEventLoop.run_forever()` in CPython.
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

    def enqueue_android_wakeup_for_delayed_tasks(self):
        """Ask Android to wake us up when delayed tasks are ready to be handled.

        Since this is effectively the actual event loop, it also handles stopping the loop."""
        # If we are supposed to stop, actually stop.
        if self._stopping:
            self._stopping = False
            self._thread_id = None
            asyncio.events._set_running_loop(None)
            self._set_coroutine_origin_tracking(False)
            sys.set_asyncgen_hooks(*self._old_agen_hooks)
            # Remove Android event loop interop objects.
            self.android_interop = None
            return

        # If we have actually already stopped, then do nothing.
        if self._thread_id is None:
            return

        timeout = self._get_next_delayed_task_wakeup()
        if timeout is None:
            # No delayed tasks.
            return

        # Ask Android to wake us up to run delayed tasks. Running delayed tasks also
        # checks for other tasks that require wakeup by calling this method. The fact that
        # running delayed tasks can trigger the next wakeup is what makes this event loop a "loop."
        self.android_interop.call_later(
            "run_delayed_tasks", self.run_delayed_tasks, timeout * 1000,
        )

    def _get_next_delayed_task_wakeup(self):
        """Compute the time to sleep before we should be woken up to handle delayed tasks."""
        # This is based heavily on the CPython's implementation of `BaseEventLoop._run_once()`
        # before it blocks on `select()`.
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

        return timeout

    def run_delayed_tasks(self):
        """Android-specific: Run any delayed tasks that have become ready. Additionally, check if
        there are more delayed tasks to execute in the future; if so, schedule the next wakeup."""
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

        # End code borrowed from CPython, within this method.
        self.enqueue_android_wakeup_for_delayed_tasks()


class _SelectorMinusSelect(selectors.PollSelector):
    # This class removes the `select()` method from PollSelector, purely as
    # a safety mechanism. On Android, this would be an error -- it would result
    # in the app freezing, triggering an App Not Responding pop-up from the
    # platform, and the user killing the app.
    #
    # Instead, the AndroidEventLoop cooperates with the native Android event
    # loop to be woken up to get work done as needed.
    def select(self, *args, **kwargs):
        raise NotImplementedError(
            "_SelectorMinusSelect refuses to select(); see comments."
        )


class AndroidInterop:
    """Encapsulate details of Android event loop cooperation."""

    def __init__(self):
        self._runnable_by_key = {}
        self._calling_soon = set()
        self._handler = None

    @property
    def handler(self):
        if self._handler is None:
            # We use `android.os.Handler.postDelayed()` to ask for wakeup. This requires an instance
            # of `Handler`, which we cache. We use the default constructor which assumes we are on
            # the Android UI thread.
            self._handler = Handler()
        return self._handler

    def get_or_create_runnable(self, key, fn):
        if key in self._runnable_by_key:
            return self._runnable_by_key[key]
        android_interop_self = self

        class PythonRunnable(Runnable):
            def run(self):
                if key in android_interop_self._calling_soon:
                    android_interop_self._calling_soon.remove(key)
                fn()

        self._runnable_by_key[key] = PythonRunnable()
        return self._runnable_by_key[key]

    def call_soon_dedup(self, key, fn):
        """Enqueue a Python callable `fn` to be run soon. Use `key` to identify avoid duplication:
        if `call_soon_dedup()` is called twice with the same `key`, we only ask Android for one
        wake-up."""
        if key in self._calling_soon:
            return
        self.handler.postDelayed(self.get_or_create_runnable(key, fn), 0)

    def call_later(self, key, fn, timeout_millis):
        """Enqueue a Python callable `fn` to be run after `timeout_millis` milliseconds. Since this
        relies on a `java.lang.Runnable`, and we want create as few Java objects as possible, use
        `key` as a cache key to avoid creating the same `Runnable` repeatedly."""
        # Coerce timeout_millis to an integer since postDelayed() takes an integer (jlong).
        self.handler.postDelayed(
            self.get_or_create_runnable(key, fn), int(timeout_millis)
        )


# Some methods in this file are based on CPython's implementation.
# Per https://github.com/python/cpython/blob/master/LICENSE , re-use is permitted
# via the Python Software Foundation License Version 2, which includes inclusion
# into this project under its BSD license terms so long as we retain this copyright notice:
# Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
# 2014, 2015, 2016, 2017, 2018, 2019, 2020 Python Software Foundation; All Rights Reserved.
# and the Python Software Foundation License Version 2 itself.
#
# # PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------

# 1. This LICENSE AGREEMENT is between the Python Software Foundation
# ("PSF"), and the Individual or Organization ("Licensee") accessing and
# otherwise using this software ("Python") in source or binary form and
# its associated documentation.

# 2. Subject to the terms and conditions of this License Agreement, PSF hereby
# grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce,
# analyze, test, perform and/or display publicly, prepare derivative works,
# distribute, and otherwise use Python alone or in any derivative version,
# provided, however, that PSF's License Agreement and PSF's notice of copyright,
# i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
# 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020 Python Software Foundation;
# All Rights Reserved" are retained in Python alone or in any derivative version
# prepared by Licensee.

# 3. In the event Licensee prepares a derivative work that is based on
# or incorporates Python or any part thereof, and wants to make
# the derivative work available to others as provided herein, then
# Licensee hereby agrees to include in any such work a brief summary of
# the changes made to Python.

# 4. PSF is making Python available to Licensee on an "AS IS"
# basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
# IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND
# DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
# FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT
# INFRINGE ANY THIRD PARTY RIGHTS.

# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
# FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
# A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON,
# OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.

# 6. This License Agreement will automatically terminate upon a material
# breach of its terms and conditions.

# 7. Nothing in this License Agreement shall be deemed to create any
# relationship of agency, partnership, or joint venture between PSF and
# Licensee.  This License Agreement does not grant permission to use PSF
# trademarks or trade name in a trademark sense to endorse or promote
# products or services of Licensee, or any third party.

# 8. By copying, installing or otherwise using Python, Licensee
# agrees to be bound by the terms and conditions of this License
# Agreement.
