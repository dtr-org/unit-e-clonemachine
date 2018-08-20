# UnitE clone machine

This python script applies basic transformations to the bitcoin-core codebase:

- replaces `bitcoin` with `unite`
- replaces names of units like `COIN → UNIT` and `CENT → EEES`
- renames files
- changes the name of the client from `Satoshi` to `Feuerland`
- fixes tests accordingly
- etc.

## purpose

The idea is to apply this script every time we rebase against/merge with
the bitcoincore repository. This way we can have things renamed nicely and
save ourselves a lot of merge headaches.

## workflow

We work on our fork of bitcoin. Whenever we want to merge with bitcoin upstream
we fork the bitcoin branch we want to merge with _again_ and apply the clonemachine
one it. Then we merge with that adjusted fork.

```
# do not blindly copy n paste, this outlines the procedure
git remote add bitcoin git@github.com:bitcoin/bitcoin.git
git fetch bitcoin
git checkout -b bitcoin-integration bitcoin/master
<path>/<to>/<clonemachine>/clonemachine.py
git merge master
```

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
exactly like bitcoin but is named unite. It helps, but it does not do
everything (and it is not intended to).
