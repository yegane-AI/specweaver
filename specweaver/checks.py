from .schema import ProtocolDSL
# other libraries might be needed.
def _contiguous(mask: int) -> bool:
    if mask == 0: return False
    while (mask & 1) == 0:
        mask >>= 1
    while (mask & 1) == 1:
        mask >>= 1
    return mask == 0

def _crosses_word_boundary(addr_low2: int, wstrb: int) -> bool:
    start = addr_low2 % 4
    bytes_sel = [i for i in range(4) if (wstrb >> i) & 1]
    if not bytes_sel: return False
    low = min(bytes_sel); high = max(bytes_sel)
    return (start + high) >= 4 and low == 0

def check_compat_axi_to_wb(axi: ProtocolDSL, wb: ProtocolDSL, policy: dict) -> dict:
    report = {"summary": [], "details": [], "counterexamples": [], "recommendations": [], "ok": False}

    if not axi.protocol.lower().startswith("axi"):
        report["details"].append("Source protocol must be AXI/AXI-Lite")
    if not wb.protocol.lower().startswith("wishbone"):
        report["details"].append("Destination protocol must be Wishbone")

    if axi.data_width != wb.data_width:
        report["details"].append(f"Data width mismatch {axi.data_width} vs {wb.data_width}")
    else:
        report["summary"].append(f"Data width compatible: {axi.data_width} bits")

    if axi.addressing != "byte" or wb.addressing != "word":
        report["details"].append(f"Addressing expected AXI[byte]→WB[word], got {axi.addressing}→{wb.addressing}")
    else:
        report["summary"].append("Addressing compatible: byte→word (ADR := AWADDR>>2)")

    if axi.max_outstanding > 1 or wb.max_outstanding > 1:
        report["details"].append("Only 1 outstanding supported in this model")

    contiguous_required = bool(policy.get("contiguous_wstrb", True))
    allow_split = bool(policy.get("allow_split_writes", False))
    buffer_depth = int(policy.get("buffer_depth", 0))

    if contiguous_required:
        bad = [5,6,9,10]  # non-contiguous samples
        if any(_contiguous(m) for m in bad):
            report["details"].append("Contiguity check inconsistent (internal error)")
        else:
            report["summary"].append("Contiguous WSTRB required")
    else:
        report["summary"].append("Non-contiguous WSTRB allowed")

    offenders = []
    for a in [0,1,2,3]:
        for m in range(1,16):
            if _crosses_word_boundary(a,m):
                offenders.append((a,m))
    if offenders and not allow_split:
        report["details"].append("AXI writes that cross 32-bit word boundary cannot map to single WB cycle")
        report["counterexamples"] = offenders[:12]
        report["recommendations"].append("Enable split writes or forbid cross-boundary WSTRB via constraints")
    else:
        report["summary"].append("Cross-boundary writes handled (split)")

    if buffer_depth == 0:
        report["summary"].append("No internal buffering; back-pressure propagates to AXI (OK for AXI-Lite)")
    else:
        report["summary"].append(f"Bridge buffering enabled (depth={buffer_depth})")

    report["ok"] = (len([d for d in report["details"] if "mismatch" in d or "cannot" in d or "expected" in d]) == 0)
    return report
