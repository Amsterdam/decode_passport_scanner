import ctypes
# from ctypes import CDLL, c_size_t

_zenroom = ctypes.CDLL('./_zenroom.so')

script = "print('Hello world! How is your day today?')"
conf = None
keys = None
data = None
verbosity = 1

stdout_buf = ctypes.create_string_buffer("x" * 1024)
stdout_len = ctypes.c_size_t(1024)

stderr_buf = ctypes.create_string_buffer("x" * 1024)
stderr_len = ctypes.c_size_t(1024)

_zenroom.zenroom_exec_tobuf(
      script, conf, keys, data, verbosity,
      stdout_buf, stdout_len, stderr_buf, stderr_len)


print(stdout_buf.value)
