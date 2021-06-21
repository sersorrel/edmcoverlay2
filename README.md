# edmcoverlay2

[EDMC Overlay][] for Linux.

## Installation

- Clone the repo into your EDMC plugins directory
  - NB: you *should not* name the directory `edmcoverlay2`. Typically,
    you should name it `edmcoverlay`, for compatibility with as many
    plugins as possible. For some plugins, you may need to rename it to
    `EDMCOverlay` instead. You cannot currently use both names at once.
- Install the dependencies (mostly X11 development headers; on Ubuntu,
  the `xorg-dev` package may be sufficient)
- Run `make`
- In the EDMC settings, configure the size and position of the overlay

## Usage

edmcoverlay2 aims to be 100% compatible with EDMC Overlay. Both the
Python library and the local server (running on port 5010) are present,
although for new plugins I highly recommend using the Python library
where possible.

Some features are not yet implemented, and there are likely to be bugs.

## Contributing

Contributions are welcome!

In particular, I'd like to move away from direct use of the X APIs where
possible – the use of `XDrawString` means that there are very few
available fonts, and the fonts that do exist have extremely limited
glyph coverage. Probably something like Pango (presumably in conjunction
with cairo) is the best option. Help in doing this would be greatly
appreciated.

Everyone interacting with this project is expected to abide by the terms
of the Contributor Covenant Code of Conduct. Violations should be
reported to coc-enforcement-edmcoverlay2@sorrel.sh.

## Copyright

Copyright © 2020 Ash Holland. Licensed under the GPL (version 3 only).

edmcoverlay2 is heavily based on [X11 overlay][] by @ericek111 (GPLv3).

Additionally, parts of edmcoverlay2 are copied from other projects:

- [gason][] (MIT)
- [lib_netsockets][] (Apache 2.0)

edmcoverlay2 would not exist without them.

Copyright notices can be found in the relevant source files.

[EDMC Overlay]: https://github.com/inorton/EDMCOverlay
[gason]: https://github.com/vivkin/gason
[lib_netsockets]: https://github.com/pedro-vicente/lib_netsockets
[X11 overlay]: https://gist.github.com/ericek111/774a1661be69387de846f5f5a5977a46
