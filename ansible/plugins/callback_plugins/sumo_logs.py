# adapted from:
#   https://gist.github.com/cliffano/9868180
#   https://github.com/petems/ansible-json.git
#   https://github.com/jlafon/ansible-profile
#   https://github.com/kalosoid/ansible-sumo-logs

import json
import logging
import logging.handlers
import uuid
import platform
import time
from datetime import datetime, timedelta

log = logging.getLogger("ansible")
#fh = logging.FileHandler('sample.log')
#log.addHandler(fh)


def json_log(res, uuid, play, role, task, state):
    host = platform.node()

    if type(res) == type(dict()):
        if 'verbose_override' not in res:
            res.update({"host":host})
            res.update({"uuid":uuid})
            res.update({"play":play})
            res.update({"role":role})
            res.update({"state":state})
            if task != None:
                res.update({"task":task})
                
            #        print('play: '+dumps(res))
            log.info(json.dumps(res, sort_keys=True))


class CallbackModule(object):

    start_time = datetime.now()
    uuid = None

    def __init__(self):

        self.node = platform.node()
        self.stats = {}
        self.current = None
        self.role = None
        self.task = None
        self.play = None

        self.uuid = str(uuid.uuid4())

        start_time = datetime.now()

    def days_hours_minutes_seconds(self, timedelta):
        minutes = (timedelta.seconds//60)%60
        r_seconds = timedelta.seconds - (minutes * 60)
        return timedelta.days, timedelta.seconds//3600, minutes, r_seconds

    def on_any(self, *args, **kwargs):
        self.play = self.playbook.filename

        task = getattr(self, 'task', None)
#        if task:
#            print "play = %s, role = %s, task = %s, args = %s, kwargs = %s" % (self.play, self.role, self.task,args,kwargs)

    def runner_on_failed(self, host, res, ignore_errors=False):
        json_log(res, self.uuid, self.play, self.role, self.task,'failed')

    def runner_on_ok(self, host, res):
        json_log(res, self.uuid, self.play, self.role, self.task, 'ok')

    def runner_on_error(self, host, msg, res):
        res.update({"error-msg":msg})
        json_log(res, self.uuid, self.play, self.role, self.task,'error')

    def runner_on_skipped(self, host, item=None):
        pass

    def runner_on_unreachable(self, host, res):
        json_log(res, self.uuid, self.play, self.role, self.task,'unreachable')

    def runner_on_no_hosts(self):
        pass

    def runner_on_async_poll(self, host, res, jid, clock):
        json_log(res, self.uuid, self.play, self.role, self.task,'async_poll')

    def runner_on_async_ok(self, host, res, jid):
        json_log(res, self.uuid, self.play, self.role, self.task,'async_ok')

    def runner_on_async_failed(self, host, res, jid):
        json_log(res, self.uuid, self.play, self.role, self.task,'async_failed')

    def playbook_on_start(self):
        pass

    def playbook_on_notify(self, host, handler):
        pass

    def playbook_on_no_hosts_matched(self):
        pass

    def playbook_on_no_hosts_remaining(self):
        pass

    def playbook_on_task_start(self, name, is_conditional):
        #pass

        my_list = name.split("|")

        # Check to see if we are processing a role
        if len(my_list) == 2:
            self.role = str.strip(my_list[0])
        #    self.role = self.role.strip()
            self.task = str.strip(my_list[1])
         #   self.task = self.task.strip()
            print "ROLE ROLE ROLE %s" % self.role

            # Check to see if we are procesing a new role. If so, calculate the duration of the previous role
            if self.current is not None and self.current != self.role:
                self.stats[self.current] = time.time() - self.stats[self.current]

            # Check to see if we are processing a new role. If so, start the timer
            if self.current is None or self.current != self.role:
                self.current = self.role 
                self.stats[self.current] = time.time()

        # We are now processing playbook level tasks
        else:
            self.task = str.strip(my_list[0])
            #self.task = str.strip(my_list[0])
            #self.task = self.task.strip()
            if self.current != "NULL":
                self.stats[self.current] = time.time() - self.stats[self.current]
            self.current = "NULL"

    def playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None, confirm=False, salt_size=None, salt=None, default=None):
        pass

    def playbook_on_setup(self):
        pass

    def playbook_on_import_for_host(self, host, imported_file):
        pass

    def playbook_on_not_import_for_host(self, host, missing_file):
        pass

    def playbook_on_play_start(self, name):
        pass

    def playbook_on_stats(self, stats):

        self.play = self.playbook.filename

        res = dict([(h, stats.summarize(h)) for h in stats.processed])

        end_time = datetime.now()
        timedelta = end_time - self.start_time
        duration = timedelta.total_seconds()

        res.update({"start":str(self.start_time)})
        res.update({"end":str(end_time)})
        res.update({"play_duration":duration})

        if self.current is not None and self.current != "NULL":
            # Record the timing of the very last task
            self.stats[self.current] = time.time() - self.stats[self.current]

        res.update({"role_duration":self.stats})
        
        json_log(res, self.uuid, self.play, self.role, None,'Play Completed')
