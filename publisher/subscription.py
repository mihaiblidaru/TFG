
class Subscription():

    PERIODIC = 'periodic'
    ON_CHANGE = 'on_change'

    def __init__(self, sid, stype, data, dest, **kwargs):
        self.sid = sid
        self.stype = stype
        self.data = data
        self.dest = dest

        if stype == Subscription.PERIODIC and 'interval' in kwargs:
            self.interval = kwargs['interval']

    def to_dict(self):
        _dict = {
            'sid': self.sid,
            'stype': self.stype,
            'data': self.data,
            'dest': self.dest
        }

        if self.stype == Subscription.PERIODIC:
            _dict['interval'] = self.interval

        return _dict

    def __str__(self):
        return str(self.to_dict())

    @staticmethod
    def from_dict(d):
        sub = Subscription(d['sid'], d['stype'], d['data'], d['dest'])
        if sub.stype == Subscription.PERIODIC:
            sub.interval = d['interval']
        return sub
