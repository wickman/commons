from twitter.common.quantity import Amount, Time
from twitter.common.testing.clock import ThreadedClock

from twitter.pingpong import PingPongServer


class TestPingPongServer(PingPongServer):
  def __init__(self, *args, **kw):
    self._calls = []
    super(TestPingPongServer, self).__init__(*args, **kw)
    
  def send_request(self, endpoint, message, ttl):
    self._calls.append((endpoint, message, ttl))
  
  def expect_calls(self, *calls):
    for expected_call in calls:
      try:
        call = self._calls.pop(0)
        assert expected_call == call, (
            'Expected endpoint=%s message=%s ttl=%s, ' % expected_call, 
            'got endpoint=%s message=%s ttl=%s.' % call)
      except IndexError:
        assert False, 'Expected endpoint=%s message=%s ttl=%s, got nothing' % expected_call


def test_defer_expectation():
  clock = ThreadedClock()
  pps = TestPingPongServer('foo', 31337, clock=clock)
  
  pps.ping('hello world', ttl=1)
  clock.tick(TestPingPongServer.PING_DELAY.as_(Time.SECONDS))
  pps.expect_calls()
  
  pps.ping('hello world', ttl=2)
  clock.tick(TestPingPongServer.PING_DELAY.as_(Time.SECONDS))
  pps.expect_calls(('pong', 'hello world', 1))