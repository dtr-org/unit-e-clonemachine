quick-tests: check integration-tests

all-tests: quick-tests local-tests regression-tests

check:
	python3 -m unittest -v test_fork.py

integration-tests:
	python3 -m unittest -v functional-tests/test_clonemachine.py

local-tests:
	python3 -m unittest -v functional-tests/test_appropriation.py
	python3 functional-tests/test_unit_e_substitutions.py -v

regression-tests:
	python3 functional-tests/test_regressions.py -v

clean:
	rm -rf functional-tests/tmp
