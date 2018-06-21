junicode-restoration
===
Junicode Modified for Restoration Era Typography

## Overview
This is a fork of Peter Baker's
[Junicode](http://junicode.sourceforge.net) with
Restoration-era features.

## Docker Build
To build the image, call:

```bash
docker build -t jpsa/junicode-builder .
```

To run the container call:

```bash
docker run --rm -it -v `pwd`:/font jpsa/junicode-builder
```

## TODO
- [x] add Dockerfile for build
- [ ] convert typescript kerning to OTF in diss
- [ ] import extra swash characters
- [x] modify glyph for ſ in Roman
- [ ] make bold and italic version of ſ
- [ ] adjust ligatureless kerning in bold and italic
- [ ] update the aftko build (currently broken)
- [x] rename Junicode [roman]
- [ ] rename Junicode-Italic, Junicode-Bold when altered
- [ ] write rationale and examples
- [ ] write testing and examples
- [ ] identify other characters to import
- [ ] figure out how to build a specimen in the ttf
- [ ] none of the features make it into the FF build: debug

## File Notes

Currently, the Docker runs the pure FontForge build,
i.e. `Makefile.ff`, so some of the files in `src` are not updated or
particularly useful.  When switching to that, it's probably worth
reviewing them again.  The files specifically for the aftko build are:

- `src/GOA-*`
- `src/JunicodeNameDB`
- `src/fontinfo`
- `src/*_fontinfo`

Additionally, `src/scripts` are various maintenance and development
scripts, `util/simplegen.py` is a wrapper for FontForge,
`util/mt-Junicode.cfg` is the beginning of a microtype package for TeX
and friends, and `util/dsig.ttx` seems to be just a dummy file
regenerated each time.

## References
* [http://junicode.sourceforge.net](http://junicode.sourceforge.net)
* [http://www.adobe.com/devnet/opentype/afdko/eula.html](http://www.adobe.com/devnet/opentype/afdko/eula.html)
