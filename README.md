# UnitE clone machine

This python script applies basic transformations to the bitcoin-core codebase:

- replaces `bitcoin` with `unite`
- replaces names of units like `COIN → UNIT` and `CENT → EEES`
- renames files
- fixes tests accordingly
- etc.

## purpose

The idea is to apply this script every time we rebase against/merge with
the bitcoincore repository. This way we can have things renamed nicely and
safe ourselves a lot of merge headaches.

## mechanics

The transformations are carried out in a safe way, i.e. certain replacements
must not happen (so there is a blacklist to prevent that), as for example
the mac build downloads dependencies from `bitcoincore.org` (the blacklist
item would be exactly that `bitcoincore.org`, i.e. the script does not replace
some occurences if they occur in a certain context).

Also some replacements only happen if they are not preceeded or followed by
a certain regular expression (artifical example: to replace `unt` safely but
not `grunt`).


