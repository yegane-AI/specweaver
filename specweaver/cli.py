import typer, yaml
from .dsl import load_protocol
from .checks import check_compat_axi_to_wb
from .codegen import write_bridge
from . import __version__
from .utils import console
import time as time ## I have some ideas about timing

app = typer.Typer(add_completion=False, help=f"SpecWeaver v{__version__} — AXI-Lite ↔ Wishbone")

@app.command()
def check(src: str, dst: str, policy: str = typer.Option(None, help="YAML policy path")):
    axi = load_protocol(src)
    wb  = load_protocol(dst)
    pol = yaml.safe_load(open(policy, "r")) if policy else {"contiguous_wstrb": True, "allow_split_writes": False, "buffer_depth": 0}
    rep = check_compat_axi_to_wb(axi, wb, pol)
    console.print(f"[note] Source: {axi.protocol} → Dest: {wb.protocol}")
    for s in rep["summary"]: console.print("[good] " + s)
    for d in rep["details"]: console.print("[bad] " + d)
    if rep["counterexamples"]:
        console.print(f"[note] Counterexamples (addr_low2, WSTRB): {rep['counterexamples'][:10]}")
    if rep["recommendations"]:
        console.print("[note] " + " ".join(rep["recommendations"]))
    console.print(f"[note] Overall: {'OK' if rep['ok'] else 'NOT OK'}")

@app.command()
def synthesize(src: str, dst: str, out: str = typer.Option("out/axi2wb")):
    write_bridge(out)
    console.print(f"[good] Wrote SystemVerilog bridge + SVA to {out}")

if __name__ == "__main__":
    app()
