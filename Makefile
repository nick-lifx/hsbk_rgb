# Copyright (c) 2020 Nick Downing
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

all: c_fixed c_float monitor prepare protocol python

.PHONY: c_fixed
c_fixed: prepare
	${MAKE} -C $@

.PHONY: c_float
c_float: prepare
	${MAKE} -C $@

.PHONY: monitor
monitor:
	${MAKE} -C $@

.PHONY: prepare
prepare: monitor
	${MAKE} -C $@

.PHONY: protocol
protocol:
	${MAKE} -C $@

.PHONY: python
python: prepare
	${MAKE} -C $@

clean:
	${MAKE} -C c_fixed clean
	${MAKE} -C c_float clean
	${MAKE} -C monitor clean
	${MAKE} -C prepare clean
	${MAKE} -C protocol clean
	${MAKE} -C python clean
