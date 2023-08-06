v_str_raw = """  output [17:0]  io_M_AXI_0_AWID, // @[:@77016.4]
  output [17:0]  io_M_AXI_0_AWUSER, // @[:@77016.4]
  output [25:0]  io_M_AXI_0_AWADDR, // @[:@77016.4]
  output [7:0]   io_M_AXI_0_AWLEN, // @[:@77016.4]
  output [2:0]   io_M_AXI_0_AWSIZE, // @[:@77016.4]
  output [1:0]   io_M_AXI_0_AWBURST, // @[:@77016.4]
  output         io_M_AXI_0_AWLOCK, // @[:@77016.4]
  output [3:0]   io_M_AXI_0_AWCACHE, // @[:@77016.4]
  output [2:0]   io_M_AXI_0_AWPROT, // @[:@77016.4]
  output [3:0]   io_M_AXI_0_AWQOS, // @[:@77016.4]
  output         io_M_AXI_0_AWVALID, // @[:@77016.4]
  input          io_M_AXI_0_AWREADY, // @[:@77016.4]
  output [17:0]  io_M_AXI_0_ARID, // @[:@77016.4]
  output [17:0]  io_M_AXI_0_ARUSER, // @[:@77016.4]
  output [25:0]  io_M_AXI_0_ARADDR, // @[:@77016.4]
  output [7:0]   io_M_AXI_0_ARLEN, // @[:@77016.4]
  output [2:0]   io_M_AXI_0_ARSIZE, // @[:@77016.4]
  output [1:0]   io_M_AXI_0_ARBURST, // @[:@77016.4]
  output         io_M_AXI_0_ARLOCK, // @[:@77016.4]
  output [3:0]   io_M_AXI_0_ARCACHE, // @[:@77016.4]
  output [2:0]   io_M_AXI_0_ARPROT, // @[:@77016.4]
  output [3:0]   io_M_AXI_0_ARQOS, // @[:@77016.4]
  output         io_M_AXI_0_ARVALID, // @[:@77016.4]
  input          io_M_AXI_0_ARREADY, // @[:@77016.4]
  output [511:0] io_M_AXI_0_WDATA, // @[:@77016.4]
  output [63:0]  io_M_AXI_0_WSTRB, // @[:@77016.4]
  output         io_M_AXI_0_WLAST, // @[:@77016.4]
  output         io_M_AXI_0_WVALID, // @[:@77016.4]
  input          io_M_AXI_0_WREADY, // @[:@77016.4]
  input  [17:0]  io_M_AXI_0_RID, // @[:@77016.4]
  input  [25:0]  io_M_AXI_0_RUSER, // @[:@77016.4]
  input  [511:0] io_M_AXI_0_RDATA, // @[:@77016.4]
  input  [1:0]   io_M_AXI_0_RRESP, // @[:@77016.4]
  input          io_M_AXI_0_RLAST, // @[:@77016.4]
  input          io_M_AXI_0_RVALID, // @[:@77016.4]
  output         io_M_AXI_0_RREADY, // @[:@77016.4]
  input  [17:0]  io_M_AXI_0_BID, // @[:@77016.4]
  input  [17:0]  io_M_AXI_0_BUSER, // @[:@77016.4]
  input  [1:0]   io_M_AXI_0_BRESP, // @[:@77016.4]
  input          io_M_AXI_0_BVALID, // @[:@77016.4]
  output         io_M_AXI_0_BREADY, // @[:@77016.4]"""


def parseLine(raw_string):
    # Remove chisel comments
    toks = raw_string.split(",")[0].split()
    l = len(toks)

    def get_io_str(io):
        return "Input" if io == "input" else "Output"

    def get_sig_type(wire):
        return wire.split("_")[-1].lower()

    def get_wire_len(wire_r):
        return str(int(wire_r.split(':')[0][1:]) + 1)

    if l == 2:
        io, name = toks
        print("add_interface_port io_M_AXI_0 " + name + " " + get_sig_type(name) + " " + get_io_str(io) + " " + "1")
    else:
        io = toks[0]
        bit_range = toks[1]
        name = toks[2]
        print("add_interface_port io_M_AXI_0 " + name + " " + get_sig_type(name)
              + " " + get_io_str(io)
              + " " + get_wire_len(bit_range)
              )


if __name__ == "__main__":
    v_str = v_str_raw.split("\n")
    for line in v_str:
        parseLine(line)

