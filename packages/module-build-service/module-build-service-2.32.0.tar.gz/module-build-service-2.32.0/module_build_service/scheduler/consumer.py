# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
""" The FedmsgConsumer class that acts as a consumer entry point for fedmsg-hub.
This class reads and processes messages from the message bus it is configured
to use.
"""

import inspect
import itertools

try:
    # python3
    import queue
except ImportError:
    # python2
    import Queue as queue

import koji
import fedmsg.consumers
import moksha.hub
import six
import sqlalchemy.exc

import module_build_service.messaging
import module_build_service.scheduler.handlers.repos
import module_build_service.scheduler.handlers.components
import module_build_service.scheduler.handlers.modules
import module_build_service.scheduler.handlers.tags
import module_build_service.scheduler.handlers.greenwave
import module_build_service.monitor as monitor

from module_build_service import models, log, conf
from module_build_service.db_session import db_session
from module_build_service.scheduler.handlers import greenwave
from module_build_service.utils import module_build_state_from_msg


class MBSConsumer(fedmsg.consumers.FedmsgConsumer):
    """ This is triggered by running fedmsg-hub. This class is responsible for
    ingesting and processing messages from the message bus.
    """

    config_key = "mbsconsumer"

    # It is set to the id of currently handled module build. It is used to
    # group all the log messages associated with single module build to
    # per module build log file.
    current_module_build_id = None

    def __init__(self, hub):
        # Topic setting needs to be done *before* the call to `super`.

        backends = module_build_service.messaging._messaging_backends
        prefixes = conf.messaging_topic_prefix  # This is a list.
        services = backends[conf.messaging]["services"]
        suffix = backends[conf.messaging]["topic_suffix"]
        self.topic = [
            "{}.{}{}".format(prefix.rstrip("."), category, suffix)
            for prefix, category in itertools.product(prefixes, services)
        ]
        if not self.topic:
            self.topic = "*"
        log.debug("Setting topics: {}".format(", ".join(self.topic)))

        # The call to `super` takes action based on the setting of topics above
        super(MBSConsumer, self).__init__(hub)

        # Our call to `super` above should have initialized an `incoming` queue
        # for us.. but in certain test situations, it does not.  So here,
        # establish a fake `incoming` queue.
        if not hasattr(self, "incoming"):
            self.incoming = queue.Queue()

        # These two values are typically provided either by the unit tests or
        # by the local build command.  They are empty in the production environ
        self.stop_condition = hub.config.get("mbsconsumer.stop_condition")
        initial_messages = hub.config.get("mbsconsumer.initial_messages", [])
        for msg in initial_messages:
            self.incoming.put(msg)

        # Furthermore, extend our initial messages with any that were queued up
        # in the test environment before our hub was initialized.
        while module_build_service.messaging._initial_messages:
            msg = module_build_service.messaging._initial_messages.pop(0)
            self.incoming.put(msg)

        # These are our main lookup tables for figuring out what to run in
        # response to what messaging events.
        self.NO_OP = NO_OP = lambda config, msg: True
        self.on_build_change = {
            koji.BUILD_STATES["BUILDING"]: NO_OP,
            koji.BUILD_STATES[
                "COMPLETE"
            ]: module_build_service.scheduler.handlers.components.complete,
            koji.BUILD_STATES["FAILED"]: module_build_service.scheduler.handlers.components.failed,
            koji.BUILD_STATES[
                "CANCELED"
            ]: module_build_service.scheduler.handlers.components.canceled,
            koji.BUILD_STATES["DELETED"]: NO_OP,
        }
        self.on_module_change = {
            models.BUILD_STATES["init"]: module_build_service.scheduler.handlers.modules.init,
            models.BUILD_STATES["wait"]: module_build_service.scheduler.handlers.modules.wait,
            models.BUILD_STATES["build"]: NO_OP,
            models.BUILD_STATES["failed"]: module_build_service.scheduler.handlers.modules.failed,
            models.BUILD_STATES["done"]: module_build_service.scheduler.handlers.modules.done,
            # XXX: DIRECT TRANSITION TO READY
            models.BUILD_STATES["ready"]: NO_OP,
            models.BUILD_STATES["garbage"]: NO_OP,
        }
        # Only one kind of repo change event, though...
        self.on_repo_change = module_build_service.scheduler.handlers.repos.done
        self.on_tag_change = module_build_service.scheduler.handlers.tags.tagged
        self.on_decision_update = module_build_service.scheduler.handlers.greenwave.decision_update
        self.sanity_check()

    def shutdown(self):
        log.info("Scheduling shutdown.")
        from moksha.hub.reactor import reactor

        reactor.callFromThread(self.hub.stop)
        reactor.callFromThread(reactor.stop)

    def validate(self, message):
        if conf.messaging == "fedmsg":
            # If this is a faked internal message, don't bother.
            if isinstance(message, module_build_service.messaging.BaseMessage):
                log.info("Skipping crypto validation for %r" % message)
                return
            # Otherwise, if it is a real message from the network, pass it
            # through crypto validation.
            super(MBSConsumer, self).validate(message)

    def consume(self, message):
        monitor.messaging_rx_counter.inc()

        # Sometimes, the messages put into our queue are artificially put there
        # by other parts of our own codebase.  If they are already abstracted
        # messages, then just use them as-is.  If they are not already
        # instances of our message abstraction base class, then first transform
        # them before proceeding.
        if isinstance(message, module_build_service.messaging.BaseMessage):
            msg = message
        else:
            msg = self.get_abstracted_msg(message)

        # Primary work is done here.
        try:
            self.process_message(msg)
            monitor.messaging_rx_processed_ok_counter.inc()
        except sqlalchemy.exc.OperationalError as error:
            monitor.messaging_rx_failed_counter.inc()
            if "could not translate host name" in str(error):
                log.exception(
                    "SQLAlchemy can't resolve DNS records. Scheduling fedmsg-hub to shutdown.")
                self.shutdown()
            else:
                raise
        except Exception:
            monitor.messaging_rx_failed_counter.inc()
        finally:
            db_session.remove()

        if self.stop_condition and self.stop_condition(message):
            self.shutdown()

    def get_abstracted_msg(self, message):
        parser = module_build_service.messaging._messaging_backends[conf.messaging].get("parser")
        if parser:
            try:
                return parser.parse(message)
            except module_build_service.messaging.IgnoreMessage:
                pass
        else:
            raise ValueError("{0} backend does not define a message parser".format(conf.messaging))

    def sanity_check(self):
        """ On startup, make sure our implementation is sane. """
        # Ensure we have every state covered
        for state in models.BUILD_STATES:
            if models.BUILD_STATES[state] not in self.on_module_change:
                raise KeyError("Module build states %r not handled." % state)
        for state in koji.BUILD_STATES:
            if koji.BUILD_STATES[state] not in self.on_build_change:
                raise KeyError("Koji build states %r not handled." % state)

        all_fns = list(self.on_build_change.items()) + list(self.on_module_change.items())
        for key, callback in all_fns:
            expected = ["config", "msg"]
            if six.PY2:
                argspec = inspect.getargspec(callback)[0]
            else:
                argspec = inspect.getfullargspec(callback)[0]
            if argspec != expected:
                raise ValueError(
                    "Callback %r, state %r has argspec %r!=%r" % (callback, key, argspec, expected))

    def _map_message(self, db_session, msg):
        """Map message to its corresponding event handler and module build"""

        if isinstance(msg, module_build_service.messaging.KojiBuildChange):
            handler = self.on_build_change[msg.build_new_state]
            build = models.ComponentBuild.from_component_event(db_session, msg)
            if build:
                build = build.module_build
            return handler, build

        if isinstance(msg, module_build_service.messaging.KojiRepoChange):
            return (
                self.on_repo_change,
                models.ModuleBuild.from_repo_done_event(db_session, msg)
            )

        if isinstance(msg, module_build_service.messaging.KojiTagChange):
            return (
                self.on_tag_change,
                models.ModuleBuild.from_tag_change_event(db_session, msg)
            )

        if isinstance(msg, module_build_service.messaging.MBSModule):
            return (
                self.on_module_change[module_build_state_from_msg(msg)],
                models.ModuleBuild.from_module_event(db_session, msg)
            )

        if isinstance(msg, module_build_service.messaging.GreenwaveDecisionUpdate):
            return (
                self.on_decision_update,
                greenwave.get_corresponding_module_build(msg.subject_identifier)
            )

        return None, None

    def process_message(self, msg):
        # Choose a handler for this message
        handler, build = self._map_message(db_session, msg)

        if handler is None:
            log.debug("No event handler associated with msg %s", msg.msg_id)
            return

        idx = "%s: %s, %s" % (handler.__name__, type(msg).__name__, msg.msg_id)

        if handler is self.NO_OP:
            log.debug("Handler is NO_OP: %s", idx)
            return

        if not build:
            log.debug("No module associated with msg %s", msg.msg_id)
            return

        MBSConsumer.current_module_build_id = build.id

        log.info("Calling %s", idx)

        try:
            further_work = handler(conf, msg) or []
        except Exception as e:
            log.exception("Could not process message handler.")
            db_session.rollback()
            db_session.refresh(build)
            build.transition(
                db_session,
                conf,
                state=models.BUILD_STATES["failed"],
                state_reason=str(e),
                failure_type="infra",
            )
            db_session.commit()

            # Allow caller to do something when error is occurred.
            raise
        else:
            # Handlers can *optionally* return a list of fake messages that
            # should be re-inserted back into the main work queue. We can use
            # this (for instance) when we submit a new component build but (for
            # some reason) it has already been built, then it can fake its own
            # completion back to the scheduler so that work resumes as if it
            # was submitted for real and koji announced its completion.
            for event in further_work:
                log.info("  Scheduling faked event %r", event)
                self.incoming.put(event)
        finally:
            MBSConsumer.current_module_build_id = None
            log.debug("Done with %s", idx)


def get_global_consumer():
    """ Return a handle to the active consumer object, if it exists. """
    hub = moksha.hub._hub
    if not hub:
        raise ValueError("No global moksha-hub obj found.")

    for consumer in hub.consumers:
        if isinstance(consumer, MBSConsumer):
            return consumer

    raise ValueError("No MBSConsumer found among %r." % len(hub.consumers))


def work_queue_put(msg):
    """ Artificially put a message into the work queue of the consumer. """
    consumer = get_global_consumer()
    consumer.incoming.put(msg)


def fake_repo_done_message(tag_name):
    msg = module_build_service.messaging.KojiRepoChange(
        msg_id="a faked internal message", repo_tag=tag_name + "-build")
    work_queue_put(msg)
