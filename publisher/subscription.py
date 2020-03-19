
class Subscription():

    PERIODIC = 'periodic'
    ON_CHANGE = 'on_change'

    def __init__(self, sid, stype, datastore, data, dest, **kwargs):
        self.sid = sid
        self.stype = stype
        self.data = data
        self.dest = dest
        self.datastore = datastore
        self.raw = None

        if stype == Subscription.PERIODIC and 'interval' in kwargs:
            self.interval = kwargs['interval']
        
        if 'raw' in kwargs:
            self.raw = kwargs['raw']

    def to_dict(self):
        _dict = {
            'sid': self.sid,
            'stype': self.stype,
            'datastore': self.datastore,
            'data': self.data,
            'dest': self.dest,
            'raw': self.raw
        }

        if self.stype == Subscription.PERIODIC:
            _dict['interval'] = self.interval

        return _dict

    def __str__(self):
        return str(self.to_dict())

    @staticmethod
    def from_dict(d):
        sub = Subscription(d['sid'], d['stype'], d['datastore'], d['data'], d['dest'])

        if 'interval' in d:
            sub.interval = d['interval']
        
        if 'raw' in d:
            sub.raw = d['raw']

        return sub
