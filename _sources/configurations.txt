.. _configurations-label: 

Configurations
==============

::

    def set_server(
            host='127.0.0.1',
            port=2043,
            server_name='default',
            app=None,
            workers=1,
            process=1,
            input_buffer_size=1000,
            output_buffer_size=1000,
            keep_alive=True,
            keep_alive_timeout=10,
            use_ssl=False,
            crt_file="",
            key_file="",
            debug=False,
            use_http2=True):
            # ...

**host, server, port, app**:
  Same as that of WSGIref.

**workers**:
  specifies # of greenlets handling connections.

**process**:
  specifies # of processes to run the server.

**input_buffer_size, output_buffer_size**:
  specifies # of bytes to use for input/output buffer.

**keep_alive, keep_alive_timeout**:
  specifies whether or not to use the keep-alive feature, and TCP timeout as seconds.

**use_ssl, crt_file, key_file**:
  specifies whether or not to use the SSL, and certificate file and key file.

**debug**:
  specifies the server to print debug message or not.

**use_http2**:
  specifies whether the server use HTTP/2 or not.

