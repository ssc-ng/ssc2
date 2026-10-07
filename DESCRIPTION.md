Stata package to install Stata packages from **date-based snapshots** of the SSC archive,
mirrored at <https://github.com/ssc-ng/archive>.
Backward compatible with `ssc`.

## Description

`ssc2` is a drop-in replacement for the system-provided `ssc` command.
The key addition to the options is:

- **`date()`** — install/describe/type/copy a package *as of a given date*
  (`YYYY-MM-DD`), or `date(latest)` for the most recent mirrored state.


Snapshots are date-stamped git tags in the mirror repository. Daily
snapshots exist from **2021-12-21** onward (with occasional gaps, see the
mirror's [ERRATA](https://github.com/ssc-ng/archive/blob/main/ERRATA.md)).
