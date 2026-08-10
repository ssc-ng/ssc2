---
layout: default
title: Reference
nav_order: 3
---

# Reference

Install and uninstall packages from SSC, including from date-based snapshots of an SSC mirror. Web rendering of the Stata help file (`help ssc2`).
{: .manhead}

## Syntax
{: #syntax}

Describe a specified package at SSC mirror
{: .hang}

`ssc2` `describe` \{ *pkgname* \| *letter* \} \[`,` `saving(`*`filename`*\[`, replace`\]`)` `date(datespec)` `from(url)`\]
{: .syn}

Install a specified package from SSC mirror
{: .hang}

`ssc2` `install` *pkgname* \[`,` `all` `replace` `update` `replaceall` `date(datespec)` `from(url)`\]
{: .syn}

Type a specific file stored at SSC mirror
{: .hang}

`ssc2` `type` *`filename`* \[`, asis` `date(datespec)` `from(url)`\]
{: .syn}

Copy a specific file from SSC mirror to your computer
{: .hang}

`ssc2` `copy` *`filename`* \[`,` `plus` `personal` `replace` `public` `binary` `date(datespec)` `from(url)`\]
{: .syn}

where *letter* in `ssc2 describe` is `a`-`z` or `_`, and *datespec* is a date in **YYYY-MM-DD** format or the word **latest**.
{: .syn}

## Command overview
{: #overview}

Subcommands that accept `date()` and `from()`, and therefore can act on a snapshot:

`ssc2 install` *pkgname* installs the specified package, from a dated snapshot when `date()` is given. See [Options for selecting a snapshot](#options_snapshot) and [Options for use with ssc2 install](#options_ssc2_install).
{: .hang}

`ssc2 describe` *pkgname* describes, but does not install, the specified package as it stood in the selected snapshot. Give a single letter, `a`-`z` or `_`, instead of a package name to list all packages starting with that letter in that snapshot.
{: .hang}

`ssc2 type` *`filename`* and `ssc2 copy` *filename* display and copy an individual file from the selected snapshot. `ssc2 cat` and `ssc2 cp` are synonyms.
{: .hang}

Subcommands specific to `ssc2`:

`ssc2 snapshots` reports the snapshot coverage of the mirror and how to point `ssc2` at a different one.
{: .hang}

`ssc2 versions` *pkgname* is not yet implemented. It will list the versions of a package available across snapshots.
{: .hang}

Subcommands passed through to `ssc` unchanged: `ssc2 new` (`whatsnew`), `ssc2 hot` (`whatshot`), and `ssc2 uninstall`. Their options are documented in `ssc`.

## Options for selecting a snapshot (describe, install, type, copy)
{: #options_snapshot}

`date(datespec)` selects the snapshot of the SSC archive as of the specified date. *datespec* is either a date in **YYYY-MM-DD** format (for example, `date(2022-01-07)`) or **latest**, which uses the most recently mirrored state of the archive. If no snapshot exists for the specified date, an error message points to the [list of available snapshot dates](https://github.com/labordynamicsinstitute/ssc-mirror/tags).
{: .hang}

`from(url)` specifies the base URL of the snapshot mirror. If `from()` is not specified, the URL is taken from the Stata global `SSC2_MIRROR` if that is set; otherwise from the environment variable `SSC2_MIRROR` if that is set; otherwise the built-in default `https://raw.githubusercontent.com/labordynamicsinstitute/ssc-mirror` is used. The overrides exist because the mirror may move to a different host; they also let you point at your own clone, which must use the same layout (*url*`/`*ref*`/fmwww.bc.edu/repec/bocode/`). The analogous `SSC2_MIRROR_API` global or environment variable overrides the API endpoint used only for diagnosing failed snapshot lookups.
{: .hang}

## Options for use with ssc2 install
{: #options_ssc2_install}

When a snapshot is requested with `date()` or `from()`, `ssc2 install` compares the requested snapshot with any installed copy of the same package, using the snapshot date recorded in the installed copy's source; a copy installed from SSC directly carries no snapshot date and cannot be compared. Because repeated dated installs would otherwise accumulate multiple entries in the ado directory (each snapshot is a distinct source URL, and `ado uninstall` would then report that more than one package matches), each of the three options below removes the superseded copies before installing.

`replace` reinstalls the *same* snapshot. If an installed copy is from a different snapshot, or has no snapshot date, the install is refused and the message points to `update` and `replaceall`. Without `date()` or `from()`, `replace` has its usual `ssc` meaning (see [below](#options_inherited)), except that a snapshot-installed copy of the package is retired first so the package remains singly tracked.
{: .hang}

`update` (only with `date()` or `from()`) installs the requested snapshot only if it is newer than every installed copy of the package. If the installed copy is the same age or newer, nothing is done.
{: .hang}

`replaceall` (only with `date()` or `from()`) replaces any installed version of the package without comparing versions; this is the option to use for downgrading, and the only applicable one with `date(latest)`.
{: .hang}

If none of the three is specified and any file of the package already exists, nothing is downloaded or installed, exactly as with `ssc`.

## Options inherited from ssc
{: #options_inherited}

The following options behave exactly as they do in `ssc`, and are documented in `ssc`: `all` with `ssc2 install`; `replace` with `ssc2 install` when no snapshot is requested (see [above](#options_ssc2_install) for the snapshot case); `saving()` with `ssc2 describe` and `ssc2 new`; `type` with `ssc2 new`; `n()` and `author()` with `ssc2 hot`; `asis` with `ssc2 type`; and `plus`, `personal`, `replace`, `public`, and `binary` with `ssc2 copy`.

## Keeping packages up to date
{: #adoupdate}

`ado update` checks each installed package against the source it was installed from and updates those that have changed. Packages installed by `ssc2` from a dated snapshot record that snapshot's URL as their source, and a snapshot never changes, so `ado update` leaves them as they are: a pinned package stays pinned. Packages installed without `date()` come from SSC itself and are updated normally.

To move a pinned package to a different snapshot, install it again with the new `date()` and `update` (to move forward only) or `replaceall` (to move in either direction). To return a package to ordinary SSC tracking, install it without `date()`, using `replace`.

Use `ssc2 uninstall` (a synonym for `ado uninstall`) to remove a package, however it was installed.

## Examples
{: #examples}

Describe the package `oaxaca`

`. ssc2 describe oaxaca`
{: .syn}

This passes through the request to `ssc`, describing the package on SSC.
{: .hang}

Describe the package `oaxaca` as of a specific date

`. ssc2 describe oaxaca, date(2022-01-07)`
{: .syn}

Install package `oaxaca` as of a specific date

`. ssc2 install oaxaca, date(2022-01-07)`
{: .syn}

Uninstall previously installed package `oaxaca`

`. ssc2 uninstall oaxaca`
{: .syn}

This uninstalls the installed copy of `oaxaca`, regardless of how it was installed.
{: .hang}


Generated automatically from `sthlp/ssc2.sthlp` on 2026-08-10. The in-Stata
help file is the authoritative version.
{: .gennote}
