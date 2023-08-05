<% from pwnlib.shellcraft import amd64 %>
<%docstring>
Execute a different process.

    >>> p = run_assembly(shellcraft.amd64.linux.sh())
    >>> p.sendline(b'echo Hello')
    >>> p.recv()
    b'Hello\n'

</%docstring>
${amd64.linux.execve('/bin///sh', ['sh'], 0)}
