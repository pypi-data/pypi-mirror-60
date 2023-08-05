#define __NR_exit 1
#define __NR_fork 2
#define __NR_read 3
#define __NR_write 4
#define __NR_open 5
#define __NR_close 6
#define __NR_creat 8
#define __NR_link 9
#define __NR_unlink 10
#define __NR_execve 11
#define __NR_chdir 12
#define __NR_time 13
#define __NR_mknod 14
#define __NR_chmod 15
#define __NR_lchown 16
#define __NR_lseek 19
#define __NR_getpid 20
#define __NR_mount 21
#define __NR_umount 22
#define __NR_setuid 23
#define __NR_getuid 24
#define __NR_stime 25
#define __NR_ptrace 26
#define __NR_alarm 27
#define __NR_pause 29
#define __NR_utime 30
#define __NR_access 33
#define __NR_nice 34
#define __NR_sync 36
#define __NR_kill 37
#define __NR_rename 38
#define __NR_mkdir 39
#define __NR_rmdir 40
#define __NR_dup 41
#define __NR_pipe 42
#define __NR_times 43
#define __NR_brk 45
#define __NR_setgid 46
#define __NR_getgid 47
#define __NR_signal 48
#define __NR_geteuid 49
#define __NR_getegid 50
#define __NR_acct 51
#define __NR_umount2 52
#define __NR_ioctl 54
#define __NR_fcntl 55
#define __NR_setpgid 57
#define __NR_umask 60
#define __NR_chroot 61
#define __NR_ustat 62
#define __NR_dup2 63
#define __NR_getppid 64
#define __NR_getpgrp 65
#define __NR_setsid 66
#define __NR_sigaction 67
#define __NR_setreuid 70
#define __NR_setregid 71
#define __NR_sigsuspend 72
#define __NR_sigpending 73
#define __NR_sethostname 74
#define __NR_setrlimit 75
#define __NR_getrlimit 76
#define __NR_getrusage 77
#define __NR_gettimeofday 78
#define __NR_settimeofday 79
#define __NR_getgroups 80
#define __NR_setgroups 81
#define __NR_symlink 83
#define __NR_readlink 85
#define __NR_uselib 86
#define __NR_swapon 87
#define __NR_reboot 88
#define __NR_readdir 89
#define __NR_mmap 90
#define __NR_munmap 91
#define __NR_truncate 92
#define __NR_ftruncate 93
#define __NR_fchmod 94
#define __NR_fchown 95
#define __NR_getpriority 96
#define __NR_setpriority 97
#define __NR_statfs 99
#define __NR_fstatfs 100
#define __NR_ioperm 101
#define __NR_socketcall 102
#define __NR_syslog 103
#define __NR_setitimer 104
#define __NR_getitimer 105
#define __NR_stat 106
#define __NR_lstat 107
#define __NR_fstat 108
#define __NR_lookup_dcookie 110
#define __NR_vhangup 111
#define __NR_idle 112
#define __NR_wait4 114
#define __NR_swapoff 115
#define __NR_sysinfo 116
#define __NR_ipc 117
#define __NR_fsync 118
#define __NR_sigreturn 119
#define __NR_clone 120
#define __NR_setdomainname 121
#define __NR_uname 122
#define __NR_adjtimex 124
#define __NR_mprotect 125
#define __NR_sigprocmask 126
#define __NR_create_module 127
#define __NR_init_module 128
#define __NR_delete_module 129
#define __NR_get_kernel_syms 130
#define __NR_quotactl 131
#define __NR_getpgid 132
#define __NR_fchdir 133
#define __NR_bdflush 134
#define __NR_sysfs 135
#define __NR_personality 136
#define __NR_afs_syscall 137
#define __NR_setfsuid 138
#define __NR_setfsgid 139
#define __NR__llseek 140
#define __NR_getdents 141
#define __NR__newselect 142
#define __NR_flock 143
#define __NR_msync 144
#define __NR_readv 145
#define __NR_writev 146
#define __NR_getsid 147
#define __NR_fdatasync 148
#define __NR__sysctl 149
#define __NR_mlock 150
#define __NR_munlock 151
#define __NR_mlockall 152
#define __NR_munlockall 153
#define __NR_sched_setparam 154
#define __NR_sched_getparam 155
#define __NR_sched_setscheduler 156
#define __NR_sched_getscheduler 157
#define __NR_sched_yield 158
#define __NR_sched_get_priority_max 159
#define __NR_sched_get_priority_min 160
#define __NR_sched_rr_get_interval 161
#define __NR_nanosleep 162
#define __NR_mremap 163
#define __NR_setresuid 164
#define __NR_getresuid 165
#define __NR_query_module 167
#define __NR_poll 168
#define __NR_nfsservctl 169
#define __NR_setresgid 170
#define __NR_getresgid 171
#define __NR_prctl 172
#define __NR_rt_sigreturn 173
#define __NR_rt_sigaction 174
#define __NR_rt_sigprocmask 175
#define __NR_rt_sigpending 176
#define __NR_rt_sigtimedwait 177
#define __NR_rt_sigqueueinfo 178
#define __NR_rt_sigsuspend 179
#define __NR_pread 180
#define __NR_pwrite 181
#define __NR_chown 182
#define __NR_getcwd 183
#define __NR_capget 184
#define __NR_capset 185
#define __NR_sigaltstack 186
#define __NR_sendfile 187
#define __NR_getpmsg 188
#define __NR_putpmsg 189
#define __NR_vfork 190
#define __NR_ugetrlimit 191
#define __NR_mmap2 192
#define __NR_truncate64 193
#define __NR_ftruncate64 194
#define __NR_stat64 195
#define __NR_lstat64 196
#define __NR_fstat64 197
#define __NR_lchown32 198
#define __NR_getuid32 199
#define __NR_getgid32 200
#define __NR_geteuid32 201
#define __NR_getegid32 202
#define __NR_setreuid32 203
#define __NR_setregid32 204
#define __NR_getgroups32 205
#define __NR_setgroups32 206
#define __NR_fchown32 207
#define __NR_setresuid32 208
#define __NR_getresuid32 209
#define __NR_setresgid32 210
#define __NR_getresgid32 211
#define __NR_chown32 212
#define __NR_setuid32 213
#define __NR_setgid32 214
#define __NR_setfsuid32 215
#define __NR_setfsgid32 216
#define __NR_pivot_root 217
#define __NR_mincore 218
#define __NR_madvise 219
#define __NR_getdents64 220
#define __NR_fcntl64 221
#define __NR_readahead 222
#define __NR_sendfile64 223
#define __NR_setxattr 224
#define __NR_lsetxattr 225
#define __NR_fsetxattr 226
#define __NR_getxattr 227
#define __NR_lgetxattr 228
#define __NR_fgetxattr 229
#define __NR_listxattr 230
#define __NR_llistxattr 231
#define __NR_flistxattr 232
#define __NR_removexattr 233
#define __NR_lremovexattr 234
#define __NR_fremovexattr 235
#define __NR_gettid 236
#define __NR_tkill 237
#define __NR_futex 238
#define __NR_sched_setaffinity 239
#define __NR_sched_getaffinity 240
#define __NR_tgkill 241
#define __NR_io_setup 243
#define __NR_io_destroy 244
#define __NR_io_getevents 245
#define __NR_io_submit 246
#define __NR_io_cancel 247
#define __NR_exit_group 248
#define __NR_epoll_create 249
#define __NR_epoll_ctl 250
#define __NR_epoll_wait 251
#define __NR_set_tid_address 252
#define __NR_fadvise64 253
#define __NR_timer_create 254
#define __NR_timer_settime (254+1)
#define __NR_timer_gettime (254+2)
#define __NR_timer_getoverrun (254+3)
#define __NR_timer_delete (254+4)
#define __NR_clock_settime (254+5)
#define __NR_clock_gettime (254+6)
#define __NR_clock_getres (254+7)
#define __NR_clock_nanosleep (254+8)
#define __NR_fadvise64_64 264
#define __NR_statfs64 265
#define __NR_fstatfs64 266
#define __NR_remap_file_pages 267
#define __NR_mq_open 271
#define __NR_mq_unlink 272
#define __NR_mq_timedsend 273
#define __NR_mq_timedreceive 274
#define __NR_mq_notify 275
#define __NR_mq_getsetattr 276
#define __NR_kexec_load 277
#define __NR_add_key 278
#define __NR_request_key 279
#define __NR_keyctl 280
#define __NR_waitid 281
#define __NR_ioprio_set 282
#define __NR_ioprio_get 283
#define __NR_inotify_init 284
#define __NR_inotify_add_watch 285
#define __NR_inotify_rm_watch 286
#define __NR_openat 288
#define __NR_mkdirat 289
#define __NR_mknodat 290
#define __NR_fchownat 291
#define __NR_futimesat 292
#define __NR_unlinkat 294
#define __NR_renameat 295
#define __NR_linkat 296
#define __NR_symlinkat 297
#define __NR_readlinkat 298
#define __NR_fchmodat 299
#define __NR_faccessat 300
#define __NR_pselect6 301
#define __NR_ppoll 302
#define __NR_unshare 303
#define __NR_set_robust_list 304
#define __NR_get_robust_list 305
#define __NR_splice 306
#define __NR_sync_file_range 307
#define __NR_tee 308
#define __NR_vmsplice 309
#define __NR_getcpu 311
#define __NR_epoll_pwait 312
#define __NR_utimes 313
#define __NR_fallocate 314
#define __NR_utimensat 315
#define __NR_signalfd 316
#define __NR_timerfd 317
#define __NR_eventfd 318
#define __NR_timerfd_create 319
#define __NR_timerfd_settime 320
#define __NR_timerfd_gettime 321
#define MAP_32BIT 0x40
#define INADDR_ANY 0
#define INADDR_BROADCAST 0xffffffff
#define INADDR_NONE 0xffffffff
#define INADDR_LOOPBACK 0x7f000001
#define EPERM 1
#define ENOENT 2
#define ESRCH 3
#define EINTR 4
#define EIO 5
#define ENXIO 6
#define E2BIG 7
#define ENOEXEC 8
#define EBADF 9
#define ECHILD 10
#define EAGAIN 11
#define ENOMEM 12
#define EACCES 13
#define EFAULT 14
#define ENOTBLK 15
#define EBUSY 16
#define EEXIST 17
#define EXDEV 18
#define ENODEV 19
#define ENOTDIR 20
#define EISDIR 21
#define EINVAL 22
#define ENFILE 23
#define EMFILE 24
#define ENOTTY 25
#define ETXTBSY 26
#define EFBIG 27
#define ENOSPC 28
#define ESPIPE 29
#define EROFS 30
#define EMLINK 31
#define EPIPE 32
#define EDOM 33
#define ERANGE 34
#define EDEADLK 35
#define ENAMETOOLONG 36
#define ENOLCK 37
#define ENOSYS 38
#define ENOTEMPTY 39
#define ELOOP 40
#define EWOULDBLOCK 11
#define ENOMSG 42
#define EIDRM 43
#define ECHRNG 44
#define EL2NSYNC 45
#define EL3HLT 46
#define EL3RST 47
#define ELNRNG 48
#define EUNATCH 49
#define ENOCSI 50
#define EL2HLT 51
#define EBADE 52
#define EBADR 53
#define EXFULL 54
#define ENOANO 55
#define EBADRQC 56
#define EBADSLT 57
#define EDEADLOCK 35
#define EBFONT 59
#define ENOSTR 60
#define ENODATA 61
#define ETIME 62
#define ENOSR 63
#define ENONET 64
#define ENOPKG 65
#define EREMOTE 66
#define ENOLINK 67
#define EADV 68
#define ESRMNT 69
#define ECOMM 70
#define EPROTO 71
#define EMULTIHOP 72
#define EDOTDOT 73
#define EBADMSG 74
#define EOVERFLOW 75
#define ENOTUNIQ 76
#define EBADFD 77
#define EREMCHG 78
#define ELIBACC 79
#define ELIBBAD 80
#define ELIBSCN 81
#define ELIBMAX 82
#define ELIBEXEC 83
#define EILSEQ 84
#define ERESTART 85
#define ESTRPIPE 86
#define EUSERS 87
#define ENOTSOCK 88
#define EDESTADDRREQ 89
#define EMSGSIZE 90
#define EPROTOTYPE 91
#define ENOPROTOOPT 92
#define EPROTONOSUPPORT 93
#define ESOCKTNOSUPPORT 94
#define EOPNOTSUPP 95
#define ENOTSUP 95
#define EPFNOSUPPORT 96
#define EAFNOSUPPORT 97
#define EADDRINUSE 98
#define EADDRNOTAVAIL 99
#define ENETDOWN 100
#define ENETUNREACH 101
#define ENETRESET 102
#define ECONNABORTED 103
#define ECONNRESET 104
#define ENOBUFS 105
#define EISCONN 106
#define ENOTCONN 107
#define ESHUTDOWN 108
#define ETOOMANYREFS 109
#define ETIMEDOUT 110
#define ECONNREFUSED 111
#define EHOSTDOWN 112
#define EHOSTUNREACH 113
#define EALREADY 114
#define EINPROGRESS 115
#define ESTALE 116
#define EUCLEAN 117
#define ENOTNAM 118
#define ENAVAIL 119
#define EISNAM 120
#define EREMOTEIO 121
#define EDQUOT 122
#define ENOMEDIUM 123
#define EMEDIUMTYPE 124
#define ECANCELED 125
#define ENOKEY 126
#define EKEYEXPIRED 127
#define EKEYREVOKED 128
#define EKEYREJECTED 129
#define __SYS_NERR ((129) + 1)
#define __LITTLE_ENDIAN 1234
#define __BIG_ENDIAN 4321
#define __BYTE_ORDER 4321
#define __FLOAT_WORD_ORDER 4321
#define LITTLE_ENDIAN 1234
#define BIG_ENDIAN 4321
#define BYTE_ORDER 4321
#define __WORDSIZE 32
#define __FSUID_H 1
#define NSIG 32
#define _NSIG 64
#define SIGHUP 1
#define SIGINT 2
#define SIGQUIT 3
#define SIGILL 4
#define SIGTRAP 5
#define SIGABRT 6
#define SIGIOT 6
#define SIGFPE 8
#define SIGKILL 9
#define SIGSEGV 11
#define SIGPIPE 13
#define SIGALRM 14
#define SIGTERM 15
#define SIGUNUSED 31
#define SIGBUS 7
#define SIGUSR1 10
#define SIGUSR2 12
#define SIGSTKFLT 16
#define SIGCHLD 17
#define SIGCONT 18
#define SIGSTOP 19
#define SIGTSTP 20
#define SIGTTIN 21
#define SIGTTOU 22
#define SIGURG 23
#define SIGXCPU 24
#define SIGXFSZ 25
#define SIGVTALRM 26
#define SIGPROF 27
#define SIGWINCH 28
#define SIGIO 29
#define SIGPWR 30
#define SIGSYS 31
#define SIGCLD 17
#define SIGPOLL 29
#define SIGLOST 30
#define SIGRTMIN 32
#define SIGRTMAX (64-1)
#define SA_NOCLDSTOP 0x00000001
#define SA_NOCLDWAIT 0x00000002
#define SA_SIGINFO 0x00000004
#define SA_RESTORER 0x04000000
#define SA_ONSTACK 0x08000000
#define SA_RESTART 0x10000000
#define SA_INTERRUPT 0x20000000
#define SA_NODEFER 0x40000000
#define SA_RESETHAND 0x80000000
#define SA_NOMASK 0x40000000
#define SA_ONESHOT 0x80000000
#define SS_ONSTACK 1
#define SS_DISABLE 2
#define MINSIGSTKSZ 2048
#define SIGSTKSZ 8192
#define SIG_BLOCK 0
#define SIG_UNBLOCK 1
#define SIG_SETMASK 2
#define SI_MAX_SIZE 128
#define SIGEV_SIGNAL 0
#define SIGEV_NONE 1
#define SIGEV_THREAD 2
#define SIGEV_THREAD_ID 4
#define SIGEV_MAX_SIZE 64
#define _SYS_TIME_H 1
#define ITIMER_REAL 0
#define ITIMER_VIRTUAL 1
#define ITIMER_PROF 2
#define __NUM_GPRS 16
#define __NUM_FPRS 16
#define __NUM_ACRS 16
#define _SIGCONTEXT_NSIG 64
#define _SIGCONTEXT_NSIG_BPW 64
#define __SIGNAL_FRAMESIZE 160
#define _SIGCONTEXT_NSIG_WORDS (64 / 64)
#define FD_SETSIZE 1024
#define R_OK 4
#define W_OK 2
#define X_OK 1
#define F_OK 0
#define SEEK_SET 0
#define SEEK_CUR 1
#define SEEK_END 2
#define STDIN_FILENO 0
#define STDOUT_FILENO 1
#define STDERR_FILENO 2
#define _CS_PATH 1
#define _SC_CLK_TCK 1
#define _SC_ARG_MAX 2
#define _SC_NGROUPS_MAX 3
#define _SC_OPEN_MAX 4
#define _SC_PAGESIZE 5
#define _SC_NPROCESSORS_ONLN 6
#define _SC_NPROCESSORS_CONF 6
#define _SC_PHYS_PAGES 7
#define _PC_PATH_MAX 1
#define _PC_VDISABLE 2
#define L_cuserid 17
#define _POSIX_VERSION 199506
#define F_ULOCK 0
#define F_LOCK 1
#define F_TLOCK 2
#define F_TEST 3
#define STAT64_HAS_BROKEN_ST_INO 1
#define S_IFMT 0xf000
#define S_IFSOCK 0xc000
#define S_IFLNK 0xa000
#define S_IFREG 0x8000
#define S_IFBLK 0x6000
#define S_IFDIR 0x4000
#define S_IFCHR 0x2000
#define S_IFIFO 0x1000
#define S_ISUID 0x800
#define S_ISGID 0x400
#define S_ISVTX 0x200
#define S_IRWXU 0x1c0
#define S_IRUSR 0x100
#define S_IWUSR 0x80
#define S_IXUSR 0x40
#define S_IRWXG 0x38
#define S_IRGRP 0x20
#define S_IWGRP 0x10
#define S_IXGRP 0x8
#define S_IRWXO 0x7
#define S_IROTH 0x4
#define S_IWOTH 0x2
#define S_IXOTH 0x1
#define S_IREAD 0x100
#define S_IWRITE 0x80
#define S_IEXEC 0x40
#define F_LINUX_SPECIFIC_BASE 1024
#define O_ACCMODE 0x3
#define O_RDONLY 0x0
#define O_WRONLY 0x1
#define O_RDWR 0x2
#define O_CREAT 0x40
#define O_EXCL 0x80
#define O_NOCTTY 0x100
#define O_TRUNC 0x200
#define O_APPEND 0x400
#define O_NONBLOCK 0x800
#define O_NDELAY 0x800
#define O_SYNC 0x1000
#define FASYNC 0x2000
#define O_DIRECT 0x4000
#define O_LARGEFILE 0x8000
#define O_DIRECTORY 0x10000
#define O_NOFOLLOW 0x20000
#define O_NOATIME 0x40000
#define F_DUPFD 0
#define F_GETFD 1
#define F_SETFD 2
#define F_GETFL 3
#define F_SETFL 4
#define F_GETLK 5
#define F_SETLK 6
#define F_SETLKW 7
#define F_SETOWN 8
#define F_GETOWN 9
#define F_SETSIG 10
#define F_GETSIG 11
#define F_GETLK64 12
#define F_SETLK64 13
#define F_SETLKW64 14
#define FD_CLOEXEC 1
#define F_RDLCK 0
#define F_WRLCK 1
#define F_UNLCK 2
#define F_EXLCK 4
#define F_SHLCK 8
#define F_INPROGRESS 16
#define LOCK_SH 1
#define LOCK_EX 2
#define LOCK_NB 4
#define LOCK_UN 8
#define LOCK_MAND 32
#define LOCK_READ 64
#define LOCK_WRITE 128
#define LOCK_RW 192
#define O_ASYNC 0x2000
#define MREMAP_MAYMOVE 1
#define MREMAP_FIXED 2
#define PROT_READ 0x1
#define PROT_WRITE 0x2
#define PROT_EXEC 0x4
#define PROT_NONE 0x0
#define MAP_SHARED 0x01
#define MAP_PRIVATE 0x02
#define MAP_FIXED 0x10
#define MAP_ANONYMOUS 0x20
#define MAP_GROWSDOWN 0x0100
#define MAP_DENYWRITE 0x0800
#define MAP_EXECUTABLE 0x1000
#define MAP_LOCKED 0x2000
#define MAP_NORESERVE 0x4000
#define MAP_POPULATE 0x8000
#define MS_ASYNC 1
#define MS_INVALIDATE 2
#define MS_SYNC 4
#define MCL_CURRENT 1
#define MCL_FUTURE 2
#define MADV_NORMAL 0x0
#define MADV_RANDOM 0x1
#define MADV_SEQUENTIAL 0x2
#define MADV_WILLNEED 0x3
#define MADV_DONTNEED 0x4
#define MAP_ANON 0x20
#define MAP_FILE 0
#define SOL_SOCKET 1
#define SO_DEBUG 1
#define SO_REUSEADDR 2
#define SO_TYPE 3
#define SO_ERROR 4
#define SO_DONTROUTE 5
#define SO_BROADCAST 6
#define SO_SNDBUF 7
#define SO_RCVBUF 8
#define SO_KEEPALIVE 9
#define SO_OOBINLINE 10
#define SO_NO_CHECK 11
#define SO_PRIORITY 12
#define SO_LINGER 13
#define SO_BSDCOMPAT 14
#define SO_PASSCRED 16
#define SO_PEERCRED 17
#define SO_RCVLOWAT 18
#define SO_SNDLOWAT 19
#define SO_RCVTIMEO 20
#define SO_SNDTIMEO 21
#define SO_ACCEPTCONN 30
#define SO_SNDBUFFORCE 32
#define SO_RCVBUFFORCE 33
#define SO_SECURITY_AUTHENTICATION 22
#define SO_SECURITY_ENCRYPTION_TRANSPORT 23
#define SO_SECURITY_ENCRYPTION_NETWORK 24
#define SO_BINDTODEVICE 25
#define SO_ATTACH_FILTER 26
#define SO_DETACH_FILTER 27
#define SO_PEERNAME 28
#define SO_TIMESTAMP 29
#define SCM_TIMESTAMP 29
#define SOCK_STREAM 1
#define SOCK_DGRAM 2
#define SOCK_RAW 3
#define SOCK_RDM 4
#define SOCK_SEQPACKET 5
#define SOCK_PACKET 10
#define UIO_FASTIOV 8
#define UIO_MAXIOV 1024
#define SCM_RIGHTS 0x01
#define SCM_CREDENTIALS 0x02
#define SCM_CONNECT 0x03
#define AF_UNSPEC 0
#define AF_UNIX 1
#define AF_LOCAL 1
#define AF_INET 2
#define AF_AX25 3
#define AF_IPX 4
#define AF_APPLETALK 5
#define AF_NETROM 6
#define AF_BRIDGE 7
#define AF_ATMPVC 8
#define AF_X25 9
#define AF_INET6 10
#define AF_ROSE 11
#define AF_DECnet 12
#define AF_NETBEUI 13
#define AF_SECURITY 14
#define AF_KEY 15
#define AF_NETLINK 16
#define AF_ROUTE 16
#define AF_PACKET 17
#define AF_ASH 18
#define AF_ECONET 19
#define AF_ATMSVC 20
#define AF_SNA 22
#define AF_IRDA 23
#define AF_PPPOX 24
#define AF_WANPIPE 25
#define AF_MAX 32
#define PF_UNSPEC 0
#define PF_UNIX 1
#define PF_LOCAL 1
#define PF_INET 2
#define PF_AX25 3
#define PF_IPX 4
#define PF_APPLETALK 5
#define PF_NETROM 6
#define PF_BRIDGE 7
#define PF_ATMPVC 8
#define PF_X25 9
#define PF_INET6 10
#define PF_ROSE 11
#define PF_DECnet 12
#define PF_NETBEUI 13
#define PF_SECURITY 14
#define PF_KEY 15
#define PF_NETLINK 16
#define PF_ROUTE 16
#define PF_PACKET 17
#define PF_ASH 18
#define PF_ECONET 19
#define PF_ATMSVC 20
#define PF_SNA 22
#define PF_IRDA 23
#define PF_PPPOX 24
#define PF_WANPIPE 25
#define PF_MAX 32
#define SOMAXCONN 128
#define MSG_OOB 1
#define MSG_PEEK 2
#define MSG_DONTROUTE 4
#define MSG_TRYHARD 4
#define MSG_CTRUNC 8
#define MSG_PROBE 0x10
#define MSG_TRUNC 0x20
#define MSG_DONTWAIT 0x40
#define MSG_EOR 0x80
#define MSG_WAITALL 0x100
#define MSG_FIN 0x200
#define MSG_EOF 0x200
#define MSG_SYN 0x400
#define MSG_CONFIRM 0x800
#define MSG_RST 0x1000
#define MSG_ERRQUEUE 0x2000
#define MSG_NOSIGNAL 0x4000
#define MSG_MORE 0x8000
#define SOL_IP 0
#define SOL_TCP 6
#define SOL_UDP 17
#define SOL_IPV6 41
#define SOL_ICMPV6 58
#define SOL_RAW 255
#define SOL_IPX 256
#define SOL_AX25 257
#define SOL_ATALK 258
#define SOL_NETROM 259
#define SOL_ROSE 260
#define SOL_DECNET 261
#define SOL_X25 262
#define SOL_PACKET 263
#define SOL_ATM 264
#define SOL_AAL 265
#define SOL_IRDA 266
#define IPX_TYPE 1
#define SHUT_RD 0
#define SHUT_WR 1
#define SHUT_RDWR 2
#define NI_NOFQDN 1
#define NI_NUMERICHOST 2
#define NI_NAMEREQD 4
#define NI_NUMERICSERV 8
#define NI_DGRAM 16
#define EAI_FAMILY -1
#define EAI_SOCKTYPE -2
#define EAI_BADFLAGS -3
#define EAI_NONAME -4
#define EAI_SERVICE -5
#define EAI_ADDRFAMILY -6
#define EAI_NODATA -7
#define EAI_MEMORY -8
#define EAI_FAIL -9
#define EAI_AGAIN -10
#define EAI_SYSTEM -11
#define AI_NUMERICHOST 1
#define AI_CANONNAME 2
#define AI_PASSIVE 4
#define SIOCADDRT 0x890B
#define SIOCDELRT 0x890C
#define SIOCRTMSG 0x890D
#define SIOCGIFNAME 0x8910
#define SIOCSIFLINK 0x8911
#define SIOCGIFCONF 0x8912
#define SIOCGIFFLAGS 0x8913
#define SIOCSIFFLAGS 0x8914
#define SIOCGIFADDR 0x8915
#define SIOCSIFADDR 0x8916
#define SIOCGIFDSTADDR 0x8917
#define SIOCSIFDSTADDR 0x8918
#define SIOCGIFBRDADDR 0x8919
#define SIOCSIFBRDADDR 0x891a
#define SIOCGIFNETMASK 0x891b
#define SIOCSIFNETMASK 0x891c
#define SIOCGIFMETRIC 0x891d
#define SIOCSIFMETRIC 0x891e
#define SIOCGIFMEM 0x891f
#define SIOCSIFMEM 0x8920
#define SIOCGIFMTU 0x8921
#define SIOCSIFMTU 0x8922
#define SIOCSIFNAME 0x8923
#define SIOCSIFHWADDR 0x8924
#define SIOCGIFENCAP 0x8925
#define SIOCSIFENCAP 0x8926
#define SIOCGIFHWADDR 0x8927
#define SIOCGIFSLAVE 0x8929
#define SIOCSIFSLAVE 0x8930
#define SIOCADDMULTI 0x8931
#define SIOCDELMULTI 0x8932
#define SIOCGIFINDEX 0x8933
#define SIOGIFINDEX 0x8933
#define SIOCSIFPFLAGS 0x8934
#define SIOCGIFPFLAGS 0x8935
#define SIOCDIFADDR 0x8936
#define SIOCSIFHWBROADCAST 0x8937
#define SIOCGIFCOUNT 0x8938
#define SIOCGIFBR 0x8940
#define SIOCSIFBR 0x8941
#define SIOCGIFTXQLEN 0x8942
#define SIOCSIFTXQLEN 0x8943
#define SIOCGIFDIVERT 0x8944
#define SIOCSIFDIVERT 0x8945
#define SIOCETHTOOL 0x8946
#define SIOCDARP 0x8953
#define SIOCGARP 0x8954
#define SIOCSARP 0x8955
#define SIOCDRARP 0x8960
#define SIOCGRARP 0x8961
#define SIOCSRARP 0x8962
#define SIOCGIFMAP 0x8970
#define SIOCSIFMAP 0x8971
#define SIOCADDDLCI 0x8980
#define SIOCDELDLCI 0x8981
#define SIOCDEVPRIVATE 0x89F0
#define PTRACE_TRACEME 0
#define PTRACE_PEEKTEXT 1
#define PTRACE_PEEKDATA 2
#define PTRACE_PEEKUSR 3
#define PTRACE_PEEKUSER 3
#define PTRACE_POKETEXT 4
#define PTRACE_POKEDATA 5
#define PTRACE_POKEUSR 6
#define PTRACE_POKEUSER 6
#define PTRACE_CONT 7
#define PTRACE_KILL 8
#define PTRACE_SINGLESTEP 9
#define PTRACE_ATTACH 0x10
#define PTRACE_DETACH 0x11
#define PTRACE_SYSCALL 24
#define PTRACE_GETEVENTMSG 0x4201
#define PTRACE_GETSIGINFO 0x4202
#define PTRACE_SETSIGINFO 0x4203
#define PTRACE_O_TRACESYSGOOD 0x00000001
#define PTRACE_O_TRACEFORK 0x00000002
#define PTRACE_O_TRACEVFORK 0x00000004
#define PTRACE_O_TRACECLONE 0x00000008
#define PTRACE_O_TRACEEXEC 0x00000010
#define PTRACE_O_TRACEVFORKDONE 0x00000020
#define PTRACE_O_TRACEEXIT 0x00000040
#define PTRACE_O_MASK 0x0000007f
#define PTRACE_EVENT_FORK 1
#define PTRACE_EVENT_VFORK 2
#define PTRACE_EVENT_CLONE 3
#define PTRACE_EVENT_EXEC 4
#define PTRACE_EVENT_VFORK_DONE 5
#define PTRACE_EVENT_EXIT 6
#define PT_TRACE_ME 0
#define PT_READ_I 1
#define PT_READ_D 2
#define PT_READ_U 3
#define PT_WRITE_I 4
#define PT_WRITE_D 5
#define PT_WRITE_U 6
#define PT_CONTINUE 7
#define PT_KILL 8
#define PT_STEP 9
#define PT_ATTACH 0x10
#define PT_DETACH 0x11
#define PT_PSWMASK 0x00
#define PT_PSWADDR 0x04
#define PT_GPR0 0x08
#define PT_GPR1 0x0C
#define PT_GPR2 0x10
#define PT_GPR3 0x14
#define PT_GPR4 0x18
#define PT_GPR5 0x1C
#define PT_GPR6 0x20
#define PT_GPR7 0x24
#define PT_GPR8 0x28
#define PT_GPR9 0x2C
#define PT_GPR10 0x30
#define PT_GPR11 0x34
#define PT_GPR12 0x38
#define PT_GPR13 0x3C
#define PT_GPR14 0x40
#define PT_GPR15 0x44
#define PT_ACR0 0x48
#define PT_ACR1 0x4C
#define PT_ACR2 0x50
#define PT_ACR3 0x54
#define PT_ACR4 0x58
#define PT_ACR5 0x5C
#define PT_ACR6 0x60
#define PT_ACR7 0x64
#define PT_ACR8 0x68
#define PT_ACR9 0x6C
#define PT_ACR10 0x70
#define PT_ACR11 0x74
#define PT_ACR12 0x78
#define PT_ACR13 0x7C
#define PT_ACR14 0x80
#define PT_ACR15 0x84
#define PT_ORIGGPR2 0x88
#define PT_FPC 0x90
#define PT_FPR0_HI 0x98
#define PT_FPR0_LO 0x9C
#define PT_FPR1_HI 0xA0
#define PT_FPR1_LO 0xA4
#define PT_FPR2_HI 0xA8
#define PT_FPR2_LO 0xAC
#define PT_FPR3_HI 0xB0
#define PT_FPR3_LO 0xB4
#define PT_FPR4_HI 0xB8
#define PT_FPR4_LO 0xBC
#define PT_FPR5_HI 0xC0
#define PT_FPR5_LO 0xC4
#define PT_FPR6_HI 0xC8
#define PT_FPR6_LO 0xCC
#define PT_FPR7_HI 0xD0
#define PT_FPR7_LO 0xD4
#define PT_FPR8_HI 0xD8
#define PT_FPR8_LO 0XDC
#define PT_FPR9_HI 0xE0
#define PT_FPR9_LO 0xE4
#define PT_FPR10_HI 0xE8
#define PT_FPR10_LO 0xEC
#define PT_FPR11_HI 0xF0
#define PT_FPR11_LO 0xF4
#define PT_FPR12_HI 0xF8
#define PT_FPR12_LO 0xFC
#define PT_FPR13_HI 0x100
#define PT_FPR13_LO 0x104
#define PT_FPR14_HI 0x108
#define PT_FPR14_LO 0x10C
#define PT_FPR15_HI 0x110
#define PT_FPR15_LO 0x114
#define PT_CR_9 0x118
#define PT_CR_10 0x11C
#define PT_CR_11 0x120
#define PT_IEEE_IP 0x13C
#define PT_LASTOFF 0x13C
#define PT_ENDREGS 0x140-1
#define NUM_GPRS 16
#define NUM_FPRS 16
#define NUM_CRS 16
#define NUM_ACRS 16
#define GPR_SIZE 4
#define FPR_SIZE 8
#define FPC_SIZE 4
#define FPC_PAD_SIZE 4
#define CR_SIZE 4
#define ACR_SIZE 4
#define STACK_FRAME_OVERHEAD 96
#define FPC_EXCEPTION_MASK 0xF8000000
#define FPC_FLAGS_MASK 0x00F80000
#define FPC_DXC_MASK 0x0000FF00
#define FPC_RM_MASK 0x00000003
#define FPC_VALID_MASK 0xF8F8FF03
#define PER_EM_MASK 0xE8000000
#define PTRACE_PEEKUSR_AREA 0x5000
#define PTRACE_POKEUSR_AREA 0x5001
#define PTRACE_PEEKTEXT_AREA 0x5002
#define PTRACE_PEEKDATA_AREA 0x5003
#define PTRACE_POKETEXT_AREA 0x5004
#define PTRACE_POKEDATA_AREA 0x5005
#define PTRACE_PROT 21
#define S390_SYSCALL_SIZE 2
#define SYS_access 33
#define SYS_acct 51
#define SYS_add_key 278
#define SYS_adjtimex 124
#define SYS_afs_syscall 137
#define SYS_alarm 27
#define SYS_bdflush 134
#define SYS_brk 45
#define SYS_capget 184
#define SYS_capset 185
#define SYS_chdir 12
#define SYS_chmod 15
#define SYS_chown 182
#define SYS_chown32 212
#define SYS_chroot 61
#define SYS_clock_getres (254+7)
#define SYS_clock_gettime (254+6)
#define SYS_clock_nanosleep (254+8)
#define SYS_clock_settime (254+5)
#define SYS_clone 120
#define SYS_close 6
#define SYS_creat 8
#define SYS_create_module 127
#define SYS_delete_module 129
#define SYS_dup 41
#define SYS_dup2 63
#define SYS_epoll_create 249
#define SYS_epoll_ctl 250
#define SYS_epoll_pwait 312
#define SYS_epoll_wait 251
#define SYS_eventfd 318
#define SYS_execve 11
#define SYS_exit 1
#define SYS_exit_group 248
#define SYS_faccessat 300
#define SYS_fadvise64 253
#define SYS_fadvise64_64 264
#define SYS_fallocate 314
#define SYS_fchdir 133
#define SYS_fchmod 94
#define SYS_fchmodat 299
#define SYS_fchown 95
#define SYS_fchown32 207
#define SYS_fchownat 291
#define SYS_fcntl 55
#define SYS_fcntl64 221
#define SYS_fdatasync 148
#define SYS_fgetxattr 229
#define SYS_flistxattr 232
#define SYS_flock 143
#define SYS_fork 2
#define SYS_fremovexattr 235
#define SYS_fsetxattr 226
#define SYS_fstat 108
#define SYS_fstat64 197
#define SYS_fstatfs 100
#define SYS_fstatfs64 266
#define SYS_fsync 118
#define SYS_ftruncate 93
#define SYS_ftruncate64 194
#define SYS_futex 238
#define SYS_futimesat 292
#define SYS_getcpu 311
#define SYS_getcwd 183
#define SYS_getdents 141
#define SYS_getdents64 220
#define SYS_getegid 50
#define SYS_getegid32 202
#define SYS_geteuid 49
#define SYS_geteuid32 201
#define SYS_getgid 47
#define SYS_getgid32 200
#define SYS_getgroups 80
#define SYS_getgroups32 205
#define SYS_getitimer 105
#define SYS_get_kernel_syms 130
#define SYS_getpgid 132
#define SYS_getpgrp 65
#define SYS_getpid 20
#define SYS_getpmsg 188
#define SYS_getppid 64
#define SYS_getpriority 96
#define SYS_getresgid 171
#define SYS_getresgid32 211
#define SYS_getresuid 165
#define SYS_getresuid32 209
#define SYS_getrlimit 76
#define SYS_get_robust_list 305
#define SYS_getrusage 77
#define SYS_getsid 147
#define SYS_gettid 236
#define SYS_gettimeofday 78
#define SYS_getuid 24
#define SYS_getuid32 199
#define SYS_getxattr 227
#define SYS_idle 112
#define SYS_init_module 128
#define SYS_inotify_add_watch 285
#define SYS_inotify_init 284
#define SYS_inotify_rm_watch 286
#define SYS_io_cancel 247
#define SYS_ioctl 54
#define SYS_io_destroy 244
#define SYS_io_getevents 245
#define SYS_ioperm 101
#define SYS_ioprio_get 283
#define SYS_ioprio_set 282
#define SYS_io_setup 243
#define SYS_io_submit 246
#define SYS_ipc 117
#define SYS_kexec_load 277
#define SYS_keyctl 280
#define SYS_kill 37
#define SYS_lchown 16
#define SYS_lchown32 198
#define SYS_lgetxattr 228
#define SYS_link 9
#define SYS_linkat 296
#define SYS_listxattr 230
#define SYS_llistxattr 231
#define SYS__llseek 140
#define SYS_lookup_dcookie 110
#define SYS_lremovexattr 234
#define SYS_lseek 19
#define SYS_lsetxattr 225
#define SYS_lstat 107
#define SYS_lstat64 196
#define SYS_madvise 219
#define SYS_mincore 218
#define SYS_mkdir 39
#define SYS_mkdirat 289
#define SYS_mknod 14
#define SYS_mknodat 290
#define SYS_mlock 150
#define SYS_mlockall 152
#define SYS_mmap 90
#define SYS_mmap2 192
#define SYS_mount 21
#define SYS_mprotect 125
#define SYS_mq_getsetattr 276
#define SYS_mq_notify 275
#define SYS_mq_open 271
#define SYS_mq_timedreceive 274
#define SYS_mq_timedsend 273
#define SYS_mq_unlink 272
#define SYS_mremap 163
#define SYS_msync 144
#define SYS_munlock 151
#define SYS_munlockall 153
#define SYS_munmap 91
#define SYS_nanosleep 162
#define SYS__newselect 142
#define SYS_nfsservctl 169
#define SYS_nice 34
#define SYS_open 5
#define SYS_openat 288
#define SYS_pause 29
#define SYS_personality 136
#define SYS_pipe 42
#define SYS_pivot_root 217
#define SYS_poll 168
#define SYS_ppoll 302
#define SYS_prctl 172
#define SYS_pread 180
#define SYS_pselect6 301
#define SYS_ptrace 26
#define SYS_putpmsg 189
#define SYS_pwrite 181
#define SYS_query_module 167
#define SYS_quotactl 131
#define SYS_read 3
#define SYS_readahead 222
#define SYS_readdir 89
#define SYS_readlink 85
#define SYS_readlinkat 298
#define SYS_readv 145
#define SYS_reboot 88
#define SYS_remap_file_pages 267
#define SYS_removexattr 233
#define SYS_rename 38
#define SYS_renameat 295
#define SYS_request_key 279
#define SYS_rmdir 40
#define SYS_rt_sigaction 174
#define SYS_rt_sigpending 176
#define SYS_rt_sigprocmask 175
#define SYS_rt_sigqueueinfo 178
#define SYS_rt_sigreturn 173
#define SYS_rt_sigsuspend 179
#define SYS_rt_sigtimedwait 177
#define SYS_sched_getaffinity 240
#define SYS_sched_getparam 155
#define SYS_sched_get_priority_max 159
#define SYS_sched_get_priority_min 160
#define SYS_sched_getscheduler 157
#define SYS_sched_rr_get_interval 161
#define SYS_sched_setaffinity 239
#define SYS_sched_setparam 154
#define SYS_sched_setscheduler 156
#define SYS_sched_yield 158
#define SYS_sendfile 187
#define SYS_sendfile64 223
#define SYS_setdomainname 121
#define SYS_setfsgid 139
#define SYS_setfsgid32 216
#define SYS_setfsuid 138
#define SYS_setfsuid32 215
#define SYS_setgid 46
#define SYS_setgid32 214
#define SYS_setgroups 81
#define SYS_setgroups32 206
#define SYS_sethostname 74
#define SYS_setitimer 104
#define SYS_setpgid 57
#define SYS_setpriority 97
#define SYS_setregid 71
#define SYS_setregid32 204
#define SYS_setresgid 170
#define SYS_setresgid32 210
#define SYS_setresuid 164
#define SYS_setresuid32 208
#define SYS_setreuid 70
#define SYS_setreuid32 203
#define SYS_setrlimit 75
#define SYS_set_robust_list 304
#define SYS_setsid 66
#define SYS_set_tid_address 252
#define SYS_settimeofday 79
#define SYS_setuid 23
#define SYS_setuid32 213
#define SYS_setxattr 224
#define SYS_sigaction 67
#define SYS_sigaltstack 186
#define SYS_signal 48
#define SYS_signalfd 316
#define SYS_sigpending 73
#define SYS_sigprocmask 126
#define SYS_sigreturn 119
#define SYS_sigsuspend 72
#define SYS_socketcall 102
#define SYS_splice 306
#define SYS_stat 106
#define SYS_stat64 195
#define SYS_statfs 99
#define SYS_statfs64 265
#define SYS_stime 25
#define SYS_swapoff 115
#define SYS_swapon 87
#define SYS_symlink 83
#define SYS_symlinkat 297
#define SYS_sync 36
#define SYS_sync_file_range 307
#define SYS__sysctl 149
#define SYS_sysfs 135
#define SYS_sysinfo 116
#define SYS_syslog 103
#define SYS_tee 308
#define SYS_tgkill 241
#define SYS_time 13
#define SYS_timer_create 254
#define SYS_timer_delete (254+4)
#define SYS_timerfd 317
#define SYS_timerfd_create 319
#define SYS_timerfd_gettime 321
#define SYS_timerfd_settime 320
#define SYS_timer_getoverrun (254+3)
#define SYS_timer_gettime (254+2)
#define SYS_timer_settime (254+1)
#define SYS_times 43
#define SYS_tkill 237
#define SYS_truncate 92
#define SYS_truncate64 193
#define SYS_ugetrlimit 191
#define SYS_umask 60
#define SYS_umount 22
#define SYS_umount2 52
#define SYS_uname 122
#define SYS_unlink 10
#define SYS_unlinkat 294
#define SYS_unshare 303
#define SYS_uselib 86
#define SYS_ustat 62
#define SYS_utime 30
#define SYS_utimensat 315
#define SYS_utimes 313
#define SYS_vfork 190
#define SYS_vhangup 111
#define SYS_vmsplice 309
#define SYS_wait4 114
#define SYS_waitid 281
#define SYS_write 4
#define SYS_writev 146
