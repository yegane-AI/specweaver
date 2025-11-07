# SpecWeaver (AXI-Lite <-> Wishbone edition)

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
