import subprocess
import time
from dataclasses import dataclass

from py4j.java_gateway import JavaGateway


class GraphScope:
    def __init__(
            self,
            app_name: str,
            server_args: str = "--synth --fpga=vcs",
            python_binder_dir: str = "../",
            default_reconnect_time: float = 0.5,
    ):
        self._server_process = subprocess.Popen(
            'cd {} && sbt "runMain eager.PythonBinder {}"'.format(
                python_binder_dir, server_args
            ),
            shell=True,
        )
        self._gateway = JavaGateway()
        self._binder = None
        while not self._binder:
            try:
                self._binder = self._gateway.entry_point.getServerBinder()
            except:
                time.sleep(default_reconnect_time)
        self._binder.setAppName(app_name)
        print("service at pid {}".format(self._server_process.pid))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def pid(self):
        return self._server_process.pid

    def add_args(self, n_args: int):
        self._binder.addArgs(n_args)

    def construct(self):
        try:
            self._binder.construct()
        except:
            pass
        self._server_process.wait()

    def arg_in(self, sign: bool, n_int_bits: int, n_frac_bits: int, dtype: str):
        return self._binder.getHostArgIn(sign, n_int_bits, n_frac_bits, dtype)

    def arg_out(self, sign: bool, n_int_bits: int, n_frac_bits: int, dtype: str):
        return self._binder.getHostArgOut(sign, n_int_bits, n_frac_bits, dtype)

    # TODO: Annotate these with types...
    def set_host_arg(self, reg, data):
        return self._binder.setHostArg(reg, data)

    def get_sram1(
        self, sign: bool, n_int_bits: int, n_frac_bits: int, d_type, dim0: int
    ):
        return self._binder.getSRAM1(sign, n_int_bits, n_frac_bits, d_type, dim0)

    def dense1_dram2sram(self, d, s, d_start, d_end, d_step, d_par, s_len):
        self._binder.dense1DRAM2SRAM(d, s, d_start, d_end, d_step, d_par, s_len)

    def dense1_sram2dram(self, d, s, d_start, d_end, d_step, d_par, s_len):
        self._binder.dense1SRAM2DRAM(d, s, d_start, d_end, d_step, d_par, s_len)

    def read_sram1_at(self, r, idx):
        return self._binder.readSRAM1At(r, idx)

    def write_sram1_at(self, r, idx, data):
        self._binder.writeSRAM1At(r, idx, data)

    def get_dram1(
        self, sign: bool, n_int_bits: int, n_frac_bits: int, d_type: str, dim0: int
    ):
        return self._binder.getDRAM1Instance(
            sign, n_int_bits, n_frac_bits, d_type, dim0
        )

    def get_dram2(
        self,
        sign: bool,
        n_int_bits: int,
        n_frac_bits: int,
        inst_type: str,
        dim0: int,
        dim1: int,
    ):
        return self._binder.getDRAM2Instance(
            sign, n_int_bits, n_frac_bits, inst_type, dim0, dim1
        )

    def get_host_arg(self, reg):
        return self._binder.getHostArg(reg)

    def get_accel_reg_inst(
        self, sign: bool, n_int_bits: int, n_frac_bits: int, dtype: str, inst_type: str
    ):
        return self._binder.getAccelRegInst(
            sign, n_int_bits, n_frac_bits, dtype, inst_type
        )

    def write_reg(self, src_reg, data):
        return self._binder.writeReg()

    def read_accel_host_reg(self, src_reg):
        return self._binder.readAccelHostReg(src_reg)

    def read_accel_reg(self, src_reg_ptr):
        return self._binder.readAccelReg(src_reg_ptr)

    def fix_add(self, a, b):
        return self._binder.fixAdd(a, b)

    def write_accel_host_reg(self, dst_reg, data_ptr):
        self._binder.writeAccelHostReg(dst_reg, data_ptr)

    def run_accel(self, is_streaming=False):
        self._binder.runAccel(is_streaming)

    def loop_scope_entrance(self):
        return self._binder.loopScopeEntrance()

    def loop_scope_exit(
        self, start, end, step, par, loop_type, scope_ptr, is_sequential
    ):
        self._binder.loopScopeExit(
            start, end, step, par, loop_type, scope_ptr, is_sequential
        )


class Loop:
    _s: GraphScope
    _is_sequential: bool

    def __init__(
            self, s: GraphScope, start, end, step, par, is_sequential=False
    ):
        self._s = s
        # TODO: These could all be pointer types...
        self._start = start
        self._end = end
        self._step = step
        self._par = par
        self._is_sequential = is_sequential

    def __enter__(self):
        print("enter loop")
        self._loop_index_ptr = self._s.loop_scope_entrance()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("exiting loop")
        print(self._start, self._end, self._step, self._par, self._loop_index_ptr)
        self._s.loop_scope_exit(
            self._start,
            self._end,
            self._step,
            self._par,
            "Foreach",
            self._loop_index_ptr,
            self._is_sequential,
        )

    @property
    def loop_index(self):
        return self._loop_index_ptr


@dataclass
class Accel:
    s: GraphScope
    is_streaming: bool = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exiting Accel")
        self.s.run_accel(self.is_streaming)
