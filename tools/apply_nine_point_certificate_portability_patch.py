#!/usr/bin/env python3
from pathlib import Path

verifier = Path("tools/verify_kneser_nine_point_link_k5.py")
text = verifier.read_text()
constant = 'EXPECTED_GZIP_CERTIFICATE_SHA256 = "f63cad91fd91a94f6fba484de031e6d480c0236f54709fd0ecd7ab5063c3f40b"\n'
assert text.count(constant) == 1
text = text.replace(constant, "")
assert_line = "    assert hashlib.sha256(compressed).hexdigest() == EXPECTED_GZIP_CERTIFICATE_SHA256\n"
assert text.count(assert_line) == 2
text = text.replace(assert_line, "")
assert "EXPECTED_GZIP_CERTIFICATE_SHA256" not in text
verifier.write_text(text)

note = Path(
    "problems/math-0003-kneser-ramsey-lower-bound/proof/"
    "nine-point-link-k5.md"
)
note_text = note.read_text()
old = '''The deterministic proof payload has hashes

```text
raw JSON:  30a35dcd239712ee87e4f65ddb5ab71a0965facf63d5595fd237ad95e9c6223d
gzip:      f63cad91fd91a94f6fba484de031e6d480c0236f54709fd0ecd7ab5063c3f40b
```
'''
new = '''The canonical uncompressed proof payload has SHA-256

```text
30a35dcd239712ee87e4f65ddb5ab71a0965facf63d5595fd237ad95e9c6223d
```

The gzip file is only a transport representation. Its compressed bytes may
vary across Python and zlib builds; verification always decompresses it and
checks the canonical raw payload hash above.
'''
assert note_text.count(old) == 1
note.write_text(note_text.replace(old, new))
