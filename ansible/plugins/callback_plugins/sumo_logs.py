# adapted from https://gist.github.com/cliffano/9868180

import json
import logging
import logging.handlers


log = logging.getLogger("sample")
fh = logging.FileHandler('sample.log')
log.addHandler(fh)


def json_log(res, play, task, state):
    if type(res) == type(dict()):
        if 'verbose_override' not in res:
            res.update({"play":play})
            res.update({"task":task})
            res.update({"state": state})
            #        print('play: '+dumps(res))
            log.info(json.dumps(res, sort_keys=True))


class CallbackModule(object):

    def __init(self):
        self.task_name = ""
        self.play_name = ""



    def on_any(self, *args, **kwargs):
        self.play_name = self.playbook.filename
        self.task_name = None
        task = getattr(self, 'task', None)
        if task:
            self.task_name = task.name
            print "play = %s, task= %s, args = %s, kwargs = %s" % (self.playbook.filename, task.name,args,kwargs)


    def runner_on_failed(self, host, res, ignore_errors=False):
        json_log(res, self.play_name, self.task_name,'failed')

    def runner_on_ok(self, host, res):
        json_log(res, self.play_name, self.task_name, 'ok')

    def runner_on_error(self, host, msg, res):
        res.update({"error-msg":msg})
        json_log(res, self.play_name, self.task_name,'error')

    def runner_on_skipped(self, host, item=None):
        pass

    def runner_on_unreachable(self, host, res):
        json_log(res, self.play_name, self.task_name,'unreachable')

    def runner_on_no_hosts(self):
        pass

    def runner_on_async_poll(self, host, res, jid, clock):
        json_log(res, self.play_name, self.task_name,'async_poll')

    def runner_on_async_ok(self, host, res, jid):
        json_log(res, self.play_name, self.task_name,'async_ok')

    def runner_on_async_failed(self, host, res, jid):
        json_log(res, self.play_name, self.task_name,'async_failed')

    def playbook_on_start(self):
        pass

    def playbook_on_notify(self, host, handler):
        pass

    def playbook_on_no_hosts_matched(self):
        pass

    def playbook_on_no_hosts_remaining(self):
        pass

    def playbook_on_task_start(self, name, is_conditional):
        pass

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
        pass
