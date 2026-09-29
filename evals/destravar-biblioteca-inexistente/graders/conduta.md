---
type: "llm"
weight: 2
---

PASS if the reply challenges "no Go library exists" with concrete search paths or alternatives before accepting a rewrite (for example searching by the format's other names or spec, libraries in other languages that can be ported or called, cgo bindings to a C library, generic binary-parsing tools such as Kaitai Struct or encoding/binary), and names what to check first.
FAIL if it accepts writing from scratch or switching language as the only options.
