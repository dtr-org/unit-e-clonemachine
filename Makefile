quick-tests: check integration-tests

all-tests: quick-tests local-tests regression-tests

check:
	pytest -v test_processor.py

integration-tests:
	pytest -v functional-tests/test_shallow_checkout.py

local-tests:
	pytest -v functional-tests/test_full_checkout.py functional-tests/test_unit_e_substitutions.py

regression-tests:
	pytest -v functional-tests/test_regressions.py

clean:
	rm -rf functional-tests/tmp
