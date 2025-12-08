from textwrap import dedent
from pathlib import Path
##adding timing soon

def axi_lite_to_wishbone_sv(module_name="axi_lite_to_wishbone_bridge"):
    return dedent(f"""
    // {module_name}.sv              Verilog will be supported too. 
    // Minimal AXI-Lite (32) -> Wishbone Classic (32) single-beat write bridge.

    module {module_name} (
      input  logic         clk,
      input  logic         rst_n,
      // AXI-Lite W
      input  logic [31:0]  AWADDR,
      input  logic         AWVALID,
      output logic         AWREADY,
      input  logic [31:0]  WDATA,
      input  logic [3:0]   WSTRB,
      input  logic         WVALID,
      output logic         WREADY,
      output logic [1:0]   BRESP,
      output logic         BVALID,
      input  logic         BREADY,
      // Wishbone
      output logic [31:0]  WB_ADR,
      output logic [31:0]  WB_DAT_MOSI,
      input  logic [31:0]  WB_DAT_MISO,
      output logic [3:0]   WB_SEL,
      output logic         WB_WE,
      output logic         WB_CYC,
      output logic         WB_STB,
      input  logic         WB_ACK
    );

      typedef enum logic [1:0] {IDLE, LATCH, WB_CYCLE, RESP} state_e;
      state_e state, nstate;
      logic [31:0] awaddr_q, wdata_q;
      logic [3:0]  wstrb_q;

      wire both = AWVALID && WVALID;
      assign AWREADY = (state==IDLE);
      assign WREADY  = (state==IDLE);

      always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
          state<=IDLE; awaddr_q<='0; wdata_q<='0; wstrb_q<='0;
        end else begin
          state <= nstate;
          if (state==IDLE && both) begin
            awaddr_q <= AWADDR; wdata_q <= WDATA; wstrb_q <= WSTRB;
          end
        end
      end

      always_comb begin
        nstate = state;
        WB_CYC=0; WB_STB=0; WB_WE=0; BVALID=0; BRESP=2'b00;
        WB_ADR = awaddr_q[31:2];
        WB_DAT_MOSI = wdata_q;
        WB_SEL = wstrb_q;
        unique case (state)
          IDLE:   if (both) nstate=LATCH;
          LATCH:  begin WB_CYC=1; WB_STB=1; WB_WE=1; nstate = WB_ACK ? RESP : WB_CYCLE; end
          WB_CYCLE: begin WB_CYC=1; WB_STB=1; WB_WE=1; if (WB_ACK) nstate=RESP; end
          RESP:   begin BVALID=1; if (BREADY) nstate=IDLE; end
        endcase
      end
    endmodule
    """)

def sva_for_axi2wb(module_name="axi_lite_to_wishbone_bridge"):
    return dedent(f"""
    // {module_name}_sva.sv
    property p_cyc_stb_together; @(posedge clk) disable iff (!rst_n) WB_CYC |-> WB_STB; endproperty
    assert property(p_cyc_stb_together);
    property p_addr_stable; @(posedge clk) disable iff (!rst_n) (state!=IDLE) |-> (WB_ADR == awaddr_q[31:2]); endproperty
    assert property(p_addr_stable);
    property p_sel_mirror; @(posedge clk) disable iff (!rst_n) (state!=IDLE) |-> (WB_SEL == wstrb_q); endproperty
    assert property(p_sel_mirror);
    """)

def write_bridge(out_dir: str):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    Path(out_dir, "axi_lite_to_wishbone_bridge.sv").write_text(axi_lite_to_wishbone_sv(), encoding="utf-8")
    Path(out_dir, "axi_lite_to_wishbone_bridge_sva.sv").write_text(sva_for_axi2wb(), encoding="utf-8")
    return out_dir
