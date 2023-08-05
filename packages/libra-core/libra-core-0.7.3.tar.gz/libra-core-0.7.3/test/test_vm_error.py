from libra.vm_error import *
from libra.transaction import *
import libra
from canoser import Uint64
import pytest

def test_status_code():
	assert StatusCode.INVALID_SIGNATURE == 1
	assert StatusCode.UNKNOWN_STATUS == Uint64.max_value
	assert StatusCode.get_name(1) == "INVALID_SIGNATURE"

