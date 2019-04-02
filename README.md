# Unit-e clonemachine

This python script applies basic transformations to the Bitcoin Core codebase:

- replaces `bitcoin` with `unit-e` (in various variations)
- replaces names of units like `COIN → UNIT` and `CENT → EEES`
- renames files
- changes the name of the client from `Satoshi` to `Feuerland`
- fixes tests accordingly
- etc.

## purpose

The idea is to apply this script every time we rebase against/merge with the
[Bitcoin Core repository](https://github.com/bitcoin/bitcoin). This way we can
have things renamed nicely and save ourselves a lot of merge headaches.

## workflow

We work on our fork of bitcoin. Whenever we want to merge with bitcoin upstream
we fork the bitcoin branch we want to merge with _again_ and apply the clonemachine
one it. Then we merge with that adjusted fork.

```
# do not blindly copy n paste, this outlines the procedure
git remote add bitcoin git@github.com:bitcoin/bitcoin.git
git fetch bitcoin
git checkout -b bitcoin-integration bitcoin/master
<path>/<to>/<clonemachine>/clonemachine.py fork --unit-e-branch=master
git merge master
```

Clonemachine has a list of appropriated files, i.e. files which have changed so
much in unit-e that it doesn't make sense to try to merge them. They are replaced
by the version from the unit-e repository. You need to pass the branch where the
unit-e code is with the `--unit-e-branch` option.

You can see the changes of all appropriated files since the last merge by
running `clonemachine.py show-upstream-diff`. You need to specify the
`--bitcoin-branch` option (in the scenario from above it would be
`--bitcoin-branch=bitcoin/master`).

## mechanics

The transformations are carried out in a safe way, i.e. certain replacements
must not happen (so there is a blacklist to prevent that), as for example
the mac build downloads dependencies from `bitcoincore.org` (the blacklist
item would be exactly that `bitcoincore.org`, i.e. the script does not replace
some occurences if they occur in a certain context).

Also some replacements only happen if they are not preceeded or followed by
a certain regular expression (artifical example: to replace `unt` safely but
not `grunt`).

## what it does not do

It does not apply certain patches which alter the behavior of the coin.
All you get from applying this script is a generic altcoin which works
exactly like bitcoin but is named unit-e. It helps, but it does not do
everything (and it is not intended to).

## requirements

Clonemachine requires Python 3.6 or later.

## setup

In order to run clonemachine and its tests you need to install its dependencies.
You can do so by running `pip3 install -r requirements.txt` in the root dir of
the repository.

## tests

Clonemachine comes with a couple of unit, integration, and regression tests.
They can be run through `make`. See the [`Makefile`](Makefile) for some more
details.

All but the unit tests work on checkouts of `unit-e` and `bitcoin` in a so it
might take a little bit to set up the initial clones. Once they are there, the
tests reuse the existing checkouts. Use `make clean` to delete them and get a
clean slate again. The temporary data is stored in a directory `tmp` in the
[`functional-tests`](functional-tests) directory.

There is a regression test which compares the changes clonemachine creates with
a known good reference. This reference is stored as a diff file in
[`functional--tests/test_data`](functional-tests/test_data). To create or
update the reference data there is the script
[`create_reference_data.py`](functional-tests/create_reference_data.py).

If the regression fails, it writes a file `diff.diff` in the `tmp` directory.
There you can see what changes are different from what is expected. It's a diff
of diffs so brace yourself with some abstraction when reading it ;-).

## changes of how substitutions are done

If substitutions are changed in clonemachine so that it substitutes differently
than at previous runs, there will be merge conflicts, if the code in the
`unit-e` code base is not adapted accordingly. Clonemachine can be used for that
as well. See the `--substitute-unit-e-naming` option for an example how to do it
and `test_unit_e_substitutions.py` for how to test it.

When changing the rules of how clonemachine does substitutions you can use the
following scheme to adapt the unit-e codebase and clonemachine in sync so that
they yield the same results:

* Implement a `--substitute-unit-e-*` option to do the substitutions in the
  unit-e code base. Use the existing ones as an example.
* Check that you get the desired substitutions by comparing the diff on unit-e
* Adapt the test in `test_unit_e_substitutions.py` to take the last diff as a
  base and compare with a newly created one after applying `clonemachine.py
  --substitute-unit-e-*`.
* Create a new reference diff by running `./create_reference_data.py` in the
  `functional-tests` directrory.
* Implement the corresponding changes in clonemachine in `fork.py`.
* Run `pytest test_unit_e_substitutions.py` to check that the changes have the
  same result. If they don't you can find the diff in
  `functional-tests/tmp/diff.diff`. Iterate until the diff is empty and the test
  passes.
* Submit pull request for `unit-e` after applying `clonemachine.py
  --substitute-unit-e-*` and for clonemachine commit the changes there.
