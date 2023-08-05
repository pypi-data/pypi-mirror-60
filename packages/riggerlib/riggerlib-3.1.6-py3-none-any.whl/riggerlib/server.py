from __future__ import print_function

import threading
import hashlib
from six.moves.queue import Queue
import sys
import threading
import time
from collections import defaultdict
from functools import partial, wraps
from multiprocessing.pool import ThreadPool


from .task import Task
from .tools import recursive_update

import yaml
import zmq
from funcsigs import signature


class RiggerPluginInstance(object):
    def __init__(self, ident, obj, data):
        """Instance of a plugin"""
        self.ident = ident
        self.obj = obj
        self.data = data


class Rigger(object):
    """ A Rigger event framework instance.

    The Rigger object holds all configuration and instances of plugins. By default Rigger accepts
    a configuration file name to parse, though it is perfectly acceptable to pass the configuration
    into the ``self.config`` attribute.

    Args:
        config_file: A configuration file holding all of Riggers base and plugin configuration.
    """
    def __init__(self, config_file):
        self.gdl = threading.Lock()
        self.pre_callbacks = defaultdict(dict)
        self.post_callbacks = defaultdict(dict)
        self.plugins = {}
        self.config_file = config_file
        self.squash_exceptions = False
        self.initialized = False
        self._task_list = {}
        self._queue_lock = threading.Lock()
        self._global_queue = Queue()
        self._background_queue = Queue()
        self._server_shutdown = False
        self._zmq_event_handler_shutdown = False
        self._global_queue_shutdown = False
        self._background_queue_shutdown = False

        globt = threading.Thread(target=self.process_queue, name="global_queue_processor")
        globt.start()
        bgt = threading.Thread(
            target=self.process_background_queue, name="background_queue_processor")
        bgt.start()

    def process_queue(self):
        """
        The ``process_queue`` thread manages taking events on and off of the global queue.
        Both TCP and in-object fire_hooks place events onto the global_queue and these are both
        handled by the same handler called ``process_hook``. If there is an exception during
        processing, the exception is printed and execution continues.
        """
        while not self._global_queue_shutdown:
            while not self._global_queue.empty():
                with self._queue_lock:
                    tid = self._global_queue.get()
                    obj = self._task_list[tid].json_dict
                    self._task_list[tid].status = Task.RUNNING
                try:
                    loc, glo = self.process_hook(obj['hook_name'], **obj['data'])
                    combined_dict = {}
                    combined_dict.update(glo)
                    combined_dict.update(loc)
                    self._task_list[tid].output = combined_dict
                except Exception as e:
                    self.log_message(e)
                with self._queue_lock:
                    self._global_queue.task_done()
                    self._task_list[tid].status = Task.FINISHED
                if not self._task_list[tid].json_dict.get('grab_result', None):
                    del self._task_list[tid]
            time.sleep(0.1)

    def process_background_queue(self):
        """
        The ``process_background_queue`` manages the hooks which have been backgrounded. In this
        respect the tasks that are completed are not required to continue with the test and as such
        can be forgotten about. An example of this would be some that sends an email, or tars up
        files, it has all the information it needs and the main process doesn't need to wait for it
        to complete.
        """
        while not self._background_queue_shutdown:
            while not self._background_queue.empty():
                obj = self._background_queue.get()
                try:
                    local, globals_updates = self.process_callbacks(obj['cb'], obj['kwargs'])
                    with self.gdl:
                        self.global_data = recursive_update(self.global_data, globals_updates)
                except Exception as e:
                    self.log_message(e)
                self._background_queue.task_done()
            time.sleep(0.1)

    def zmq_event_handler(self, zmq_socket_address):
        """
        The ``zmq_event_handler`` thread receives (and responds to) updates from the
        zmq socket, which is normally embedded in the web server running alongside this
        riggerlib instance, in its own process.

        """
        ctx = zmq.Context()
        zmq_socket = ctx.socket(zmq.REP)
        zmq_socket.set(zmq.RCVTIMEO, 300)
        zmq_socket.bind(zmq_socket_address)

        def zmq_reply(message, **extra):
            payload = {'message': message}
            payload.update(extra)
            zmq_socket.send_json(payload)
        bad_request = partial(zmq_reply, 'BAD REQUEST')

        while not self._zmq_event_handler_shutdown:
            try:
                json_dict = zmq_socket.recv_json()
            except zmq.Again:
                continue

            try:
                event_name = json_dict['event_name']
            except KeyError:
                bad_request()

            if event_name == 'fire_hook':
                tid = self._fire_internal_hook(json_dict)
                if tid:
                    zmq_reply('OK', tid=tid)
                else:
                    bad_request()
            elif event_name == 'task_check':
                try:
                    tid = json_dict['tid']
                    extra = {
                        "tid": tid,
                        "status": self._task_list[tid].status,
                    }
                    if json_dict['grab_result']:
                        extra["output"] = self._task_list[tid].output
                    zmq_reply('OK', **extra)
                except KeyError:
                    zmq_reply('NOT FOUND')
            elif event_name == 'task_delete':
                try:
                    tid = json_dict['tid']
                    del self._task_list[tid]
                    zmq_reply('OK', tid=tid)
                except KeyError:
                    zmq_reply('OK', tid=tid)
            elif event_name == 'shutdown':
                zmq_reply('OK')
                # We gotta initiate server stop from here and stop this thread
                self._server_shutdown = True
                break
            elif event_name == 'ping':
                zmq_reply('PONG')
            else:
                bad_request()

        zmq_socket.close()

    def read_config(self, config_file):
        """
        Reads in the config file and parses the yaml data.

        Args:
            config_file: A configuration file holding all of Riggers base and plugin configuration.

        Raises:
            IOError: If the file can not be read.
            Exception: If there is any error parsing the configuration file.
        """
        try:
            with open(config_file, "r") as stream:
                data = yaml.load(stream)
        except IOError:
            print("!!! Configuration file could not be loaded...exiting")
            sys.exit(127)
        except Exception as e:
            print(e)
            print("!!! Error parsing Configuration file")
            sys.exit(127)
        self.config = data

    def parse_config(self):
        """
        Takes the configuration data from ``self.config`` and sets up the plugin instances.
        """
        self.read_config(self.config_file)
        self.setup_plugin_instances()
        self.start_server()

    def setup_plugin_instances(self):
        """
        Sets up instances into a dict called ``self.instances`` and instantiates each
        instance of the plugin. It also sets the ``self._threaded`` option to determine
        if plugins will be processed synchronously or asynchronously.
        """
        self.instances = {}
        self._threaded = self.config.get("threaded", False)
        plugins = self.config.get("plugins", {})
        for ident, config in plugins.items():
            self.setup_instance(ident, config)

    def setup_instance(self, ident, config):
        """
        Sets up a single instance into the ``self.instances`` dict. If the instance does
        not exist, a warning is printed out.

        Args:
            ident: A plugin instance identifier.
            config: Configuration dict from the yaml.
        """
        plugin_name = config.get('plugin', {})
        if plugin_name in self.plugins:
            obj = self.plugins[plugin_name]
            if obj:
                obj_instance = obj(ident, config, self)
                self.instances[ident] = RiggerPluginInstance(ident, obj_instance, config)
        else:
            msg = "Plugin [{}] was not found, "\
                  "disabling instance [{}]".format(plugin_name, ident)
            self.log_message(msg)

    def start_server(self):
        """
        Starts the ZMQ server if the ``server_enabled`` is True in the config.
        """
        self._server_hostname = self.config.get('server_address', '127.0.0.1')
        self._server_port = self.config.get('server_port', 21212)
        self._server_enable = self.config.get('server_enabled', False)
        if self._server_enable:
            zmq_socket_address = 'tcp://{}:{}'.format(self._server_hostname, self._server_port)
            # set up reciever thread for zmq event handling
            zeh = threading.Thread(
                target=self.zmq_event_handler, args=(zmq_socket_address,), name="zmq_event_handler")
            zeh.start()
            exect = threading.Thread(target=self.await_shutdown, name="executioner")
            exect.start()

    def await_shutdown(self):
        while not self._server_shutdown:
            time.sleep(0.3)
        self.stop_server()

    def stop_server(self):
        """
        Responsible for the following:
            - stopping the zmq event handler (unless already stopped through 'terminate')
            - stopping the global queue
            - stopping the background queue
        """
        self.log_message("Shutdown initiated : {}".format(self._server_hostname))
        # The order here is important
        self._zmq_event_handler_shutdown = True
        self._global_queue.join()
        self._global_queue_shutdown = True
        self._background_queue.join()
        self._background_queue_shutdown = True
        raise SystemExit

    def fire_hook(self, hook_name, **kwargs):
        """
        Parses the hook information into a dict for passing to process_hook. This is used
        to enable both the TCP and in-object fire_hook methods to use the same process_hook
        method call.

        Args:
            hook_name: The name of the hook to fire.
            kwargs: The kwargs to pass to the hooks.

        """
        json_dict = {'hook_name': hook_name, 'data': kwargs}
        self._fire_internal_hook(json_dict)

    def _fire_internal_hook(self, json_dict):
        task = Task(json_dict)
        tid = task.tid.hexdigest()
        self._task_list[tid] = task
        if self._global_queue:
            with self._queue_lock:
                self._global_queue.put(tid)
            return tid
        else:
            return None

    def process_hook(self, hook_name, **kwargs):
        """
        Takes a hook_name and a selection of kwargs and fires off the appropriate callbacks.

        This function is the guts of Rigger and is responsible for running the callback and
        hook functions. It first loads some blank dicts to collect the updates for the local
        and global namespaces. After this, it loads the pre_callback functions along with
        the kwargs into the callback collector processor.

        The return values are then classifed into local and global dicts and updates proceed.
        After this, the plugin hooks themselves are then run using the same methodology. Their
        return values are merged with the existing dicts and then the same process happens
        for the post_callbacks.

        Note: If the instance of the plugin has been marked as a background instance, and hooks
              which are called in that instance will be backgrounded. The hook will also not
              be able to return any data to the post-hook callback, although updates to globals
              will be processed as and when the backgrounded task is completed.

        Args:
            hook_name: The name of the hook to fire.
            kwargs: The kwargs to pass to the hooks.
        """
        if not self.initialized:
            return
        kwargs_updates = {}
        globals_updates = {}
        kwargs.update({'config': self.config})

        # First fire off any pre-hook callbacks
        if self.pre_callbacks.get(hook_name):
            # print "Running pre hook callback for {}".format(hook_name)
            kwargs_updates, globals_updates = self.process_callbacks(
                self.pre_callbacks[hook_name].values(), kwargs)

            # Now we can update the kwargs passed to the real hook with the updates
            with self.gdl:
                self.global_data = recursive_update(self.global_data, globals_updates)
            kwargs = recursive_update(kwargs, kwargs_updates)

        # Now fire off each plugin hook
        event_hooks = []
        for instance_name, instance in self.instances.items():
            callbacks = instance.obj.callbacks
            enabled = instance.data.get('enabled', None)
            if callbacks.get(hook_name) and enabled:
                cb = callbacks[hook_name]
                if instance.data.get('background', False):
                    self._background_queue.put({'cb': [cb], 'kwargs': kwargs})
                elif cb['bg']:
                    self._background_queue.put({'cb': [cb], 'kwargs': kwargs})
                else:
                    event_hooks.append(cb)
        kwargs_updates, globals_updates = self.process_callbacks(event_hooks, kwargs)

        # One more update for the post_hook callback
        with self.gdl:
            self.global_data = recursive_update(self.global_data, globals_updates)
        kwargs = recursive_update(kwargs, kwargs_updates)

        # Finally any post-hook callbacks
        if self.post_callbacks.get(hook_name):
            # print "Running post hook callback for {}".format(hook_name)
            kwargs_updates, globals_updates = self.process_callbacks(
                self.post_callbacks[hook_name].values(), kwargs)
            with self.gdl:
                self.global_data = recursive_update(self.global_data, globals_updates)
            kwargs = recursive_update(kwargs, kwargs_updates)
        return kwargs, self.global_data

    def process_callbacks(self, callback_collection, kwargs):
        """
        Processes a collection of callbacks or hooks for a particular event, namely pre, hook or
        post.

        The functions are passed in as an array to ``callback_collection`` and process callbacks
        first iterates each function and ensures that each one has the correct arguments available
        to it. If not, an Exception is raised. Then, depending on whether Threading is enabled or
        not, the functions are either run sequentially, or loaded into a ThreadPool and executed
        asynchronously.

        The returned local and global updates are either collected and processed sequentially, as
        in the case of the non-threaded behaviour, or collected at the end of the
        callback_collection processing and handled there.

        Note:
            It is impossible to predict the order of the functions being run. If the order is
            important, it is advised to create a second event hook that will be fired before the
            other. Rigger has no concept of hook or callback order and is unlikely to ever have.

        Args:
            callback_collection: A list of functions to call.
            kwargs: A set of kwargs to pass to the functions.

        Returns: A tuple of local and global namespace updates.
        """
        loc_collect = {}
        glo_collect = {}
        if self._threaded:
            results_list = []
            pool = ThreadPool(10)
        for cb in callback_collection:
            required_args = [sig for sig in cb['args'] if isinstance(cb['args'][sig].default, type)]
            missing = list(set(required_args).difference(set(self.global_data.keys()))
                           .difference(set(kwargs.keys())))
            if not missing:
                new_kwargs = self.build_kwargs(cb['args'], kwargs)
                if self._threaded:
                    results_list.append(pool.apply_async(cb['func'], [], new_kwargs))
                else:
                    obtain_result = self.handle_results(cb['func'], [], new_kwargs)
                    loc_collect, glo_collect = self.handle_collects(
                        obtain_result, loc_collect, glo_collect)
            else:
                raise Exception('Function {} is missing kwargs {}'
                                .format(cb['func'].__name__, missing))

        if self._threaded:
            pool.close()
            pool.join()
            for result in results_list:
                obtain_result = self.handle_results(result.get, [], {})
                loc_collect, glo_collect = self.handle_collects(
                    obtain_result, loc_collect, glo_collect)
        return loc_collect, glo_collect

    def handle_results(self, call, args, kwargs):
        """
        Handles results and depending on configuration, squashes exceptions and logs or
        returns the obtained result.

        Args:
            call: The function call.
            args: The positional arguments.
            kwargs: The keyword arguments.

        Returns: The obtained result of the callback or hook.
        """
        try:
            obtain_result = call(*args, **kwargs)
        except:
            if self.squash_exceptions:
                obtain_result = None
                self.handle_failure(sys.exc_info())
            else:
                raise

        return obtain_result

    def handle_collects(self, result, loc_collect, glo_collect):
        """
        Handles extracting the information from the hook/callback result.

        If the hook/callback returns None, then the dicts are returned unaltered, else
        they are updated with local, global namespace updates.

        Args:
            result: The result to process.
            loc_collect: The local namespace updates collection.
            glo_collect: The global namespace updates collection.
        Returns: A tuple containing the local and global updates.
        """
        if result:
            if result[0]:
                loc_collect = recursive_update(loc_collect, result[0])
            if result[1]:
                glo_collect = recursive_update(glo_collect, result[1])
        return loc_collect, glo_collect

    def build_kwargs(self, args, kwargs):
        """
        Builds a new kwargs from a list of allowed args.

        Functions only receive a single set of kwargs, and so the global and local namespaces
        have to be collapsed. In this way, the local overrides the global namespace, hence if
        a key exists in both local and global, the local value will be passed to the function
        under the the key name and the global value will be forgotten.

        The args parameter ensures that only the expected arguments are supplied.

        Args:
            args: A list of allowed argument names
            kwargs: A dict of kwargs from the local namespace.
        Returns: A consolidated global/local namespace with local overrides.
        """
        returned_args = {}
        returned_args.update({
            name: self.global_data[name] for name in args
            if name in self.global_data})
        returned_args.update({
            name: kwargs[name] for name in args
            if name in kwargs})
        return returned_args

    def register_hook_callback(self, hook_name=None, ctype="pre", callback=None, name=None):
        """
        Registers pre and post callbacks.

        Takes a callback function and assigns it to the hook_name with an optional identifier.
        The optional identifier makes it possible to hot bind functions into hooks and to
        remove them at a later date with ``unregister_hook_callback``.

        Args:
            hook_name: The name of the event hook to respond to.
            ctype: The call back type, either ``pre`` or ``post``.
            callback: The callback function.
            name: An optional name for the callback instance binding.
        """
        if hook_name and callback:
            callback_instance = self.create_callback(callback)
            if not name:
                name = hashlib.sha1(
                    str(time.time()) + hook_name + str(callback_instance['args'])).hexdigest()
            if ctype == "pre":
                self.pre_callbacks[hook_name][name] = callback_instance
            elif ctype == "post":
                self.post_callbacks[hook_name][name] = callback_instance

    def unregister_hook_callback(self, hook_name, ctype, name):
        """
        Unregisters a pre or post callback.

        If the binding has a known name, this function allows the removal of a binding.

        Args:
            hook_name: The event hook name.
            ctype: The callback type, either ``pre`` or ``post``.
            name: An optional name for the callback instance binding.
        """
        if ctype == "pre":
            del self.pre_callbacks[hook_name][name]
        elif ctype == "post":
            del self.post_callbacks[hook_name][name]

    def register_plugin(self, cls, plugin_name=None):
        """ Registers a plugin class to a name.

        Multiple instances of the same plugin can be used in Rigger, ``self.plugins``
        stores un-initialized class defintions to be used by ``setup_instances``.

        Args:
            cls: The class.
            plugin_name: The name of the plugin.
        """
        if plugin_name in self.plugins:
            print("Plugin name already taken [{}]".format(plugin_name))
        elif plugin_name is None:
            print("Plugin name cannot be None")
        else:
            # print "Registering plugin {}".format(plugin_name)
            self.plugins[plugin_name] = cls

    def get_instance_obj(self, name):
        """
        Gets the instance object for a given ident name.

        Args:
            name: The ident name of the instance.
        Returns: The object of the instance.
        """
        if name in self.instances:
            return self.instances[name].obj
        else:
            return None

    def get_instance_data(self, name):
        """
        Gets the instance data(config) for a given ident name.

        Args:
            name: The ident name of the instance.
        Returns: The data(config) of the instance.
        """
        if name in self.instances:
            return self.instances[name].data
        else:
            return None

    def configure_plugin(self, name, *args, **kwargs):
        """
        Attempts to configure an instance, passing it the args and kwargs.

        Args:
            name: The ident name of the instance.
            args: The positional args.
            kwargs: The keyword arguments.
        """
        obj = self.get_instance_obj(name)
        if obj:
            obj.configure(*args, **kwargs)

    @staticmethod
    def create_callback(callback, bg=False):
        """
        Simple function to inspect a function and return it along with it param names wrapped
        up in a nice dict. This forms a callback object.

        Args:
            callback: The callback function.
        Returns: A dict of function and param names.
        """
        params = signature(callback).parameters
        return {
            'func': callback,
            'args': params,
            'bg': bg
        }

    def handle_failure(self, exc):
        """
        Handles an exception. It is expected that this be overidden.
        """
        self.log_message(exc)

    def log_message(self, message):
        """
        "Logs" a message. It is expected that this be overidden.
        """
        print(message)
