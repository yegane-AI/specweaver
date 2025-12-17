# SpecWeaver (AXI-Lite <-> Wishbone edition)

## In Progress & Next Up (actively building)

I’m extending SpecWeaver beyond the current AXI-Lite <-> Wishbone write path.

### Short-term (good first issues)
- [ ] **Add read support**: AXI-Lite `AR/R` -> Wishbone read cycle (mirror of write FSM, no bursts).
- [ ] **Split-write option**: Implement `allow_split_writes: true` in codegen (two WB cycles if AXI write crosses a word boundary) and update the checker’s message.
- [ ] **cocotb smoke test**: Simple memory model + bridge stimulus for a few `(addr_low2, WSTRB)` cases (pass/fail expectations).
- [ ] **CI setup**: GitHub Actions to run `pytest` and a formatting check on PRs.
- [ ] **Doc→DSL extractor (md/pdf)**: Rule-based headings/keywords to fill `data_width`, `addressing`, `byte_enable_width`; write to YAML.
- [ ] **Z3 mini-backend**: Optional path that produces a concrete counterexample trace (addr, mask) for cross-boundary writes.

### Medium-term
- [ ] **Wishbone pipelined variant**: Add `max_outstanding>1` policy and checker warnings; codegen a 1-deep buffer option.
- [ ] **APB profile**: DSL + checker hooks and codegen for AXI-Lite -> APB (single-beat).
- [ ] **Streamlit demo**: Upload YAMLs, run check, and download generated SV/SVA with a small diagram of the data path.
- [ ] **Graphviz diagrams**: Render the bridge FSM and byte-lane mapping directly from the policy.

### Nice-to-have
- [ ] **UVM agent templates** generated from the DSL (smoke-level sequences + SVA bind).
- [ ] **LLM-assist**: Optional prompt to refine YAML extraction and suggest missing fields, gated behind an env var.
- [ ] **Spec diff**: Human-readable diff between two DSLs highlighting semantic changes (widths, addressing, invariants).

**How to collaborate**
1. Comment on an item above or open an issue titled `[task] <name>`.
2. Fork, create a feature branch, and send a PR with a short demo (logs or screenshot).
3. I’ll review quickly—small, focused PRs are ideal.




## An AI Agent for Protocol Compatibility

Docs -> DSL -> checks -> code. Reads mini-specs, loads YAML DSLs, checks compatibility (Z3-free heuristics here),
and generates a small AXI-Lite → Wishbone bridge skeleton + SVA.

## Install
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Try it
```bash
python -m specweaver.cli check examples/dsl/axi_lite.yaml examples/dsl/wishbone.yaml --policy examples/chains/axi_lite_to_wishbone.yaml
python -m specweaver.cli synthesize --src examples/dsl/axi_lite.yaml --dst examples/dsl/wishbone.yaml --out out/axi2wb
```

Outputs a report and emits `axi_lite_to_wishbone_bridge.sv` + `axi_lite_to_wishbone_bridge_sva.sv`.

In progress: Making the model even more autonomous.  
