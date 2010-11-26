from __future__ import absolute_import
from flask import g
import gc

class Dozer(object):
    def __init__(self, app):
        self.app = app
        self.app.config.setdefault('SQLITE3_DATABASE', ':memory:')

        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)
        self.app.add_url_rule('/_dozer', self.index)
    
    def log_event(self, name, msg, start, end):
        pass
        
    
    def index(self):
        pass
        
    def before_request(self):
        g.sqlite3_db = self.connect()

    def after_request(self, response):
        g.sqlite3_db.close()
        return response
    
    def tick(self):
        gc.collect()
        
        typecounts = {}
        for obj in gc.get_objects():
            objtype = type(obj)
            if objtype in typecounts:
                typecounts[objtype] += 1
            else:
                typecounts[objtype] = 1
        
        for objtype, count in typecounts.iteritems():
            typename = objtype.__module__ + "." + objtype.__name__
            if typename not in self.history:
                self.history[typename] = [0] * self.samples
            self.history[typename].append(count)
        
        samples = self.samples + 1
        
        # Add dummy entries for any types which no longer exist
        for typename, hist in self.history.iteritems():
            diff = samples - len(hist)
            if diff > 0:
                hist.extend([0] * diff)
        
        # Truncate history to self.maxhistory
        if samples > self.maxhistory:
            for typename, hist in self.history.iteritems():
                hist.pop(0)
        else:
            self.samples = samples