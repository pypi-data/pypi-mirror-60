from nose.tools import assert_not_equal as neq_
from nose.tools import timed

from easyprocess import EasyProcess

# if run with coverage:
#        Fatal Python error: deallocating None


@timed(1000)
def test_timeout():  # pragma: no cover
    for x in range(1000):
        print("index=", x)
        neq_(EasyProcess("sleep 5").call(timeout=0.05).return_code, 0)
