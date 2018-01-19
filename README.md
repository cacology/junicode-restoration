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
- [ ] convert typescript kerning to OTF
- [ ] import extra swash characters
- [ ] modify glyph for ſ

## References
* [http://junicode.sourceforge.net](http://junicode.sourceforge.net)
* [http://www.adobe.com/devnet/opentype/afdko/eula.html](http://www.adobe.com/devnet/opentype/afdko/eula.html)
