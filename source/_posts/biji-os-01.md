---
title: "趣谈Linux操作系统笔记01（对应03-06）"
date: 2019-04-06 22:00:30
tags:
  - "os"
---

### 1 操作系统简介

#### 1.1 什么是操作系统

![](/images/biji_os_01/WX20190406-221620@2x.png)  
在谈论什么是操作系统前我们可以回忆一下十几年前买电脑的过程，引用文章的栗子就是”那时候买电脑，经常是这样一个情景：三五个哥们儿一起来到电脑城，呼啦呼啦采购了一大堆硬件，有密密麻麻都是针脚的**CPU**；有铺满各种复杂电路的一块板子，也就是**主板**；还需要买块**显卡**，用来连接显示器；还需要买个**网卡**，里面可以插网线；还要买块**硬盘**，将来用来存放文件；然后还需要一大堆**线**，将这些设备和主板连接起来；最终再来一个**鼠标**，一个**键盘**，还有一个**显示器**。设备差不多啦，准备开整！”,那么此时如何将这些硬件连接起来并使用户能够在不知道硬件的情况下进行操作呢（比如总不能让用户手动操作强行写入显示器所在内存使显示器显示字符），**没错这层硬件细节与用户使用普通软件的抽象就是操作系统**，

#### 1.2 为什么需要操作系统

其实回答这个问题只需要看一看没有操作系统的时候，实际上，最早的计算机没有操作系统（这里我们假设最早的计算机是ENIAC,实际上这个定义一直有争议这里只是举例）; 他们是一次负责一个程序的大型机器。出于这个原因，他们并不真正需要操作系统。事实上，最早的计算机要求用户物理连接和断开插头板上的电线以检索计算。但是如果你没有操作系统，你可以让你的电脑做任何事吗？（那时候说的程序员都还是指拔插连接线用以实现运算的女性呢～）

是。但是你还有很多工作要做。如果没有操作系统使用和执行标准的系统方法来运行计算机，那么您就会处于编写必须告诉计算机确切操作的代码（或程序）的位置。因此，如果要在文字处理程序中键入文档，则必须从头创建代码，告诉计算机响应键盘上按下的每个字符。然后，您必须编写一个代码，告诉计算机这些响应必须如何转换为屏幕。您必须告诉您的计算机如何绘制您想要的角色！想想你的文字处理程序有的每一个选项或可能性。您必须直接在硬盘上为每一个代码编写代码。

文中说**操作系统其实就像一个软件外包公司，其内核就相当于这家外包公司的老板。所以接下来的整个课程中，请你将自己的角色切换成这家软件外包公司的老板，设身处地地去理解操作系统是如何协调各种资源，帮客户做成事情的。**，那么其实这个类比隐含了默认场景，完整的类比应该是，客户尽是一些不具备软件开发能力的公司，此时客户看到了某款爆款软件”拼西西”的成功，心急如焚的想要构建一个高并发、高可用的”拼东东”东东，那么问题来了，公司内部没有现成的基础设施（消息队列、缓存等），更重要的是连个懂业务开发的技术人员都没有，我作为客户好急啊～从0-1完成传统企业转型臣妾做不到啊，然而我转念一想我其实不需要会开发我只需要一个中间层懂开发就行了，我输入业务输出的是计算机相应的程序就行，好了这不隔壁老张开了家软件外包公司帮我屏蔽了软件开发的抽象（对应到os就是输入输出设备，进程，存储等抽象），那么我就能安心的进行业务拓展了呢。（可以说广大应用软件正是站在巨人（操作系统）的肩膀上）

*脑洞一下，如果说图灵机是没有os的计算机（其实是一种计算模型，当然也可以称为计算机），那么我们来思考一下图灵机适合现代使用吗？*

小王想要看漫画，请问您从图灵机抽象能给我显示一个小姐姐图片吗，这当然不行，虽然图灵机的实现可以支持各种逻辑运算结构但是图灵机并没有规定如何将纸带连接到显示屏（缺少了硬件驱动管理等），实际上之前说的早期的计算机确实是图灵机的一种实现，现在他有了一个响当当的名号**冯诺伊曼体系结构**，但是这种体系结构只是为os打好了硬件基础，在这个体系结构之上的抽象才是操作系统。那么现在我们知道图灵机距离适合现在使用差了两个层次，第一层是现代的体系结构作为图灵机的实现，第二层是操作系统的介入屏蔽硬件体系结构并提供一些好用的基础工具（比如进程抽象)

*继续脑洞等价于图灵机的理论模型最知名的应该属于图灵师父在图灵机理论发表之前发布的lambda calculus，这是一种纯数学的模型（理解起来需要花费一点时间但是很有意思，推荐可以去看看计算语义学方面的书），上面我的脑洞在这里可以翻译为我能用数学函数运算看动漫吗？*

这次我觉得这次应该没人质疑了吧，当然你可能会想到，从看动漫降维抽象到计算理论这一层（对应到体系结构的实现）那么好像看起来我看动漫的基础就是lambda calculus呢（当然实际上并不是的，这里我指的是计算能力上的等价，ladmda calculus的计算能力是等价于图灵机的所以这里看动漫的基础归结到体系结构的抽象可以是图灵机并等价于lambda calculus）

#### 1.3 “双击 QQ”这个过程，都需要用到哪些硬件？

用户开始对着屏幕上的 QQ 图标双击鼠标了。

1. 鼠标就会通过鼠标线给电脑发消息，告知电脑，鼠标向某个方向移动了多少距离
2. 屏幕，也就是显示器，是计算机的输出设备，将计算机处理用户请求展示给用户看
3. 显卡，由显卡控制在显示器的哪个坐标上再绘制一个鼠标箭头
4. RAM, 坐标值经过鼠标输入中断写入ram对应的屏幕内存对应区域

#### 1.4 从点击 QQ 图标，看操作系统全貌

- 硬盘是个物理设备，要按照规定格式化成为文件系统，才能存放这些程序。文件系统需要一个系统进行统一管理，称为文件管理子系统（File Management Subsystem）。
- 当操作系统拿到 QQ 的二进制执行文件的时候，就可以运行这个文件了。QQ 的二进制文件是静态的，称为程序（Program），而运行起来的 QQ，是不断进行的，称为进程（Process）。
- 在操作系统中，也有同样的问题，例如多个进程都要往打印机上打印文件，如果随便乱打印进程，就会出现同样一张纸，第一行是 A 进程输出的文字，第二行是 B 进程输出的文字，全乱套了。所以，打印机的直接操作是放在操作系统内核里面的，进程不能随便操作。但是操作系统也提供一个办事大厅，也就是系统调用（System Call）。
- 在操作系统中，进程的执行也需要分配 CPU 进行执行，也就是按照程序里面的二进制代码一行一行地执行。于是，为了管理进程，我们还需要一个进程管理子系统（Process Management Subsystem）。如果运行的进程很多，则一个 CPU 会并发运行多个进程，也就需要 CPU 的调度能力了。
- 在操作系统中，不同的进程有不同的内存空间，但是整个电脑内存就这么点儿，所以需要统一的管理和分配，这就需要内存管理子系统（Memory Management Subsystem）。

也可以使用软件外包公司的组织架构模拟以上的os组成模块  
![](/images/biji_os_01/WX20190406-234401@2x.png)

#### 1.5 os组成总览

![](/images/biji_os_01/WX20190406-234419@2x.png)

#### 1.6 课堂练习

系统调用 kernel/  
进程管理 kernel/, arch//kernel  
内存管理 mm/, arch//mm  
文件 fs/  
设备 drivers/char, drivers/block  
网络 net/

**arch**代表某种架构

### 2 常用的Linux命令

#### 2.1 常用Linux命令图示

![](/images/biji_os_01/4.jpg)

#### 2.2 部分命令在centos体系和ubnutu体系下的差别

**安装软件命令(以安装jdk为例)**  
centos体系：  
rpm -i jdk-XXX\_linux-x64\_bin.rpm  
ubnutu体系:  
dpkg -i jdk-XXX\_linux-x64\_bin.deb

**服务相关命令（以启动服务为例）**  
centos体系：  
systemctl start mariadb  
ubnutu体系:  
systemctl start mysql

#### 2.3 思路如下

1. 安装jdk，mysql
2. 配置jdbc驱动配置文件
3. 通过jdbc在java app里连接msql并执行相应的数据库操作

### 3 几个常用的系统调用

#### 3.1 进程管理

##### 3.1.1 fork

linux里进程的创建是通过fork父进程完成的，关于fork的详细用法可以参考[这里](https://linux.die.net/man/2/fork)  
关于fork可以引申出孤儿进程和僵尸进程

- 孤儿进程：一个父进程退出，而它的一个或多个子进程还在运行，那么那些子进程将成为孤儿进程。孤儿进程将被init进程(进程号为1)所收养，并由init进程对它们完成状态收集工作。
- 僵尸进程：一个进程使用fork创建子进程，如果子进程退出，而父进程并没有调用wait或waitpid获取子进程的状态信息，那么子进程的进程描述符仍然保存在系统中。这种进程称之为僵死进程。
  ##### 3.1.2 execve
  execve用来执行一个二进制可执行文件或者以#! interpreter \[optional-arg\]为开头的脚本，关于execve的详细用法可以参考[这里](https://linux.die.net/man/2/execve)
  ##### 3.1.3 waitpid
  waitpid用来等待进程改变状态，常用于父进程等待子进程结束，关于waitpid的详细用法可以参考[这里](https://linux.die.net/man/2/waitpid)
  #### 3.2 内存管理
  *从操作系统角度来看，进程分配内存有两种方式，分别由两个系统调用完成：brk和mmap（不考虑共享内存）。*
  ##### 3.2.1 brk
  brk是将数据段(.data)的最高地址指针\_edata往高地址推，关于execve的详细用法可以参考[这里](https://linux.die.net/man/2/brk)
  ##### 3.2.2 mmap
  mmap是在进程的虚拟地址空间中（堆和栈中间，称为文件映射区域的地方）找一块空闲的虚拟内存，关于mmap更详细的用法可以参考[这里](https://linux.die.net/man/3/mmap)
  #### 3.3 文件管理
  *Linux里一切皆文件*
  ##### 3.3.1 open
  open用于打开一个文件，关于open更详细的用法可以参考[这里](https://linux.die.net/man/3/open)
  ##### 3.3.2 close
  close用于关闭一个文件，关于close更详细的用法可以参考[这里](https://linux.die.net/man/3/close)
  ##### 3.3.3 creat
  creat用于创建一个文件，关于creat更详细的用法可以参考[这里](https://linux.die.net/man/3/creat)
  ##### 3.3.4 lseek
  lseek用于跳到文件的某个位置，关于lseek更详细的用法可以参考[这里](https://linux.die.net/man/3/lseek)
  ##### 3.3.5 read
  read用于读取某个文件，关于read更详细的用法可以参考[这里](https://linux.die.net/man/3/read)
  ##### 3.3.6 write
  write用于读取某个文件，关于write更详细的用法可以参考[这里](https://linux.die.net/man/3/write)
  #### 3.4 信号处理
  ##### 3.4.1 kill
  用户进程通过kill函数，将一个用户信号发送给另一个进程,**注意这里的kill是指代发送信号而不是杀死进程之类的…**，关于sigaction更详细的用法可以参考[这里](https://linux.die.net/man/3/kill)
  ##### 3.4.2 sigaction
  sigaction用于注册信号处理函数，用kill发送的信号可以在sigaction中注册相应的信号处理函数用以处理，关于sigaction更详细的用法可以参考[这里](https://linux.die.net/man/3/sigaction)
  #### 3.5 进程间通信
  *内核可以通过消息队列来实现进程间通信*
  ##### 3.5.1 msgget
  创建一个新的消息队列，关于msgget更详细的用法可以参考[这里](https://linux.die.net/man/3/msgget)
  ##### 3.5.2 msgget
  将消息发送到消息队列，关于msgget更详细的用法可以参考[这里](https://linux.die.net/man/3/msgget)
  ##### 3.5.3 msgrcv
  从消息队列中取出消息，关于msgget更详细的用法可以参考[这里](https://linux.die.net/man/3/msgget)
  ##### 3.5.4 shmget
  创建一个共享内存块，关于shmget更详细的用法可以参考[这里](https://linux.die.net/man/3/shmget)
  ##### 3.5.5 shmmat
  将共享内存块映射到自己的内存空间（比如说自己的进程地址空间，关于shmmat更详细的用法可以参考[这里](https://linux.die.net/man/3/shmmat)
  ##### 3.5.6 sem\_wait
  持有信号量，信号量-1，关于sem\_wait更详细的用法可以参考[这里](https://linux.die.net/man/3/sem_wait)
  ##### 3.5.7 sem\_post
  释放信号量，信号量+1，关于sem\_post更详细的用法可以参考[这里](https://linux.die.net/man/3/sem_post)
  #### 3.6 网络通信
  ##### 3.6.1 socket
  从tcp/ip 的解度看 socket ，它更多地体现了用户 API 与协议栈的一个中间层接口层。用户通过调用socket API 将报文递交给协议栈，或者从协议栈中接收报文件。关于socket更详细的用法可以参考[这里](https://linux.die.net/man/3/socket)

#### 3.7 小结

![](/images/biji_os_01/WX20190407-101258@2x.png)

#### 3.8 课堂练习

以执行strace cat /dev/null 为例  
```
execve("/usr/bin/cat", ["cat", "/dev/null", "-o", "/root/straceout.txt"], [/* 23 vars */]) = 0
brk(NULL)                               = 0x1cda000
mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7fe3f1515000
access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
open("/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=36309, ...}) = 0
mmap(NULL, 36309, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7fe3f150c000
close(3)                                = 0
open("/lib64/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\2\1\1\3\0\0\0\0\0\0\0\0\3\0>\0\1\0\0\0P%\2\0\0\0\0\0"..., 832) = 832
fstat(3, {st_mode=S_IFREG|0755, st_size=2173512, ...}) = 0
mmap(NULL, 3981792, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7fe3f0f28000
mprotect(0x7fe3f10eb000, 2093056, PROT_NONE) = 0
mmap(0x7fe3f12ea000, 24576, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1c2000) = 0x7fe3f12ea000
mmap(0x7fe3f12f0000, 16864, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7fe3f12f0000
close(3)                                = 0
mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7fe3f150b000
mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7fe3f1509000
arch_prctl(ARCH_SET_FS, 0x7fe3f1509740) = 0
mprotect(0x7fe3f12ea000, 16384, PROT_READ) = 0
mprotect(0x60b000, 4096, PROT_READ)     = 0
mprotect(0x7fe3f1516000, 4096, PROT_READ) = 0
munmap(0x7fe3f150c000, 36309)           = 0
brk(NULL)                               = 0x1cda000
brk(0x1cfb000)                          = 0x1cfb000
brk(NULL)                               = 0x1cfb000
open("/usr/lib/locale/locale-archive", O_RDONLY|O_CLOEXEC) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=106070960, ...}) = 0
mmap(NULL, 106070960, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7fe3ea9ff000
close(3)                                = 0
open("/usr/share/locale/locale.alias", O_RDONLY|O_CLOEXEC) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=2502, ...}) = 0
mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7fe3f1514000
read(3, "# Locale name alias data base.\n#"..., 4096) = 2502
read(3, "", 4096)                       = 0
close(3)                                = 0
munmap(0x7fe3f1514000, 4096)            = 0
open("/usr/share/locale/zh_CN.UTF-8/LC_MESSAGES/libc.mo", O_RDONLY) = -1 ENOENT (No such file or directory)
open("/usr/share/locale/zh_CN.utf8/LC_MESSAGES/libc.mo", O_RDONLY) = -1 ENOENT (No such file or directory)
open("/usr/share/locale/zh_CN/LC_MESSAGES/libc.mo", O_RDONLY) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=81139, ...}) = 0
mmap(NULL, 81139, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7fe3f14f5000
close(3)                                = 0
open("/usr/lib64/gconv/gconv-modules.cache", O_RDONLY) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=26254, ...}) = 0
mmap(NULL, 26254, PROT_READ, MAP_SHARED, 3, 0) = 0x7fe3f150e000
close(3)                                = 0
write(2, "cat\357\274\232\346\227\240\346\225\210\351\200\211\351\241\271 -- o\n", 24cat：无效选项 -- o
) = 24
open("/usr/share/locale/zh_CN.UTF-8/LC_MESSAGES/coreutils.mo", O_RDONLY) = -1 ENOENT (No such file or directory)
open("/usr/share/locale/zh_CN.utf8/LC_MESSAGES/coreutils.mo", O_RDONLY) = -1 ENOENT (No such file or directory)
open("/usr/share/locale/zh_CN/LC_MESSAGES/coreutils.mo", O_RDONLY) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=190751, ...}) = 0
mmap(NULL, 190751, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7fe3f14c6000
close(3)                                = 0
open("/usr/share/locale/zh.UTF-8/LC_MESSAGES/coreutils.mo", O_RDONLY) = -1 ENOENT (No such file or directory)
open("/usr/share/locale/zh.utf8/LC_MESSAGES/coreutils.mo", O_RDONLY) = -1 ENOENT (No such file or directory)
open("/usr/share/locale/zh/LC_MESSAGES/coreutils.mo", O_RDONLY) = -1 ENOENT (No such file or directory)
write(2, "Try 'cat --help' for more inform"..., 39Try 'cat --help' for more information.
) = 39
close(1)                                = 0
close(2)                                = 0
exit_group(1)                           = ?
+++ exited with 1 +++
```

### 4 引用链接

[computer-run-without-operating-system](https://computer.howstuffworks.com/computer-run-without-operating-system1.htm)  
[极客时间](https://time.geekbang.org/column/article/88060)  
[kernel](https://www.kernel.org/)  
[overview-kernel-source](https://courses.linuxchix.org/kernel-hacking-2002/08-overview-kernel-source.html)  
[strace](https://linuxtools-rst.readthedocs.io/zh_CN/latest/tool/strace.html)  
[linux man](https://linux.die.net/man/2/fork)  
[Linux内存分配小结–malloc、brk、mmap](https://www.cnblogs.com/sky-heaven/p/10005642.html)
