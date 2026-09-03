---
title: "计算的要素-第四章小结"
date: 2018-08-02 19:52:00
categories:
  - "计算机体系结构"
tags:
  - "Nand2tetris"
---

*Make everything as simple as possible, but bot simpler.—- 阿尔伯特 · 爱因斯坦（1879&#126;1955）*

本章关于Hack机器语言的细节都在书里写的很清楚，所以这里不再赘述

### 1 register

![](/images/jsys_04/register.jpg)  
![](/images/jsys_04/register_detail.jpg)  
Hack Computer的register总共只有三种，除了上一章中构建的Memory register以外，分别加了CPU内的Data register和Address/data register，值得一提的是正如上图中所见，M寄存器是特指定RAM\[A\]所指定的Memory特定位置的存储单元，A寄存器和D寄存器的分工也很明确，A可以用来访存和存储数据，这个数据在书本和项目中的体现就是一个地址，就像指针，我在某个内存单元a中存了内存单元b的地址,如下

    @a
    A=M

那么此时A寄存器的作用就是存储数据，只不过这个数据是一个地址，那么何时算存储地址呢？  
Answer：@a的时候会a的值放入A寄存器此时就是一个地址啦&#126;，因为在汇编器的层面像a这种variable都会对应这一个地址，比如从RAM的第16个地址开始每个存储单元（n位register）对应一个变量，那么这个第xx个地址a对应的地址值

### 2 memory mapping

本节一个很重要的亮点就是讲清楚了内存映像（memory mapping），下面就键盘和屏幕两个外设来说明内存映像。

#### 2.1 Keyboard

![](/images/jsys_04/keyboard.jpg)  
从图中可以看出，当你按下键盘的那一刻，键盘中的电路选择出你现在按下的键并通过外设的数据线（无线键盘不算），将数据送入计算机对应的端口，实际上这里还触发了一个中断，CPU会根据中断类型对应有处理中断的例程（一般写在BIOS里），然后例程和读取对应端口的输入然后写到相应的内存中去，在本课程中这个阶段忽略了中断以及相应的处理。

#### 2.2 Screen

![](/images/jsys_04/screen_ex.jpg)  
![](/images/jsys_04/screen.jpg)  
聊完了键盘再聊聊屏幕，Hack Computer把屏幕分成了512\*256个像素点，每个像素点对应存储单元中的一个比特位，这里关于Screen根据选取内存位置选取对应行列书中有详尽的描述，本质是通过修改内存中Screen设备对应的内存映像然后写入Screen设备对应的颜色存储区形成了屏幕上不断变化的效果。更多的细节可以参考下面给出的Reference，**本质上外设的处理都可以基于memory mapping**，包括这里没谈到的鼠标，感兴趣的同学可以玩玩MS的Spy++，利用Hook可以看到对应的鼠标事件消息实际上是基于像素的位置的移动，那么显而易见鼠标外设的内存映像就是对应处于的位置（current position）；-）。

### 3 mmap

mmap是一个符合POSIX标准的Unix 系统调用，它将文件或设备映射到内存中。它是一种内存映射文件 I / O的方法。它实现了请求分页，因为文件内容最初不是从磁盘读取的，根本不使用物理RAM。在访问特定位置之后，以“ lazy ”方式执行来自磁盘的实际读取

联想到Linux下的mmap，我觉得有必要深入研究一下它，所以下次专门开一篇文章谈一谈这个话题

### 4 Reference

[memory map from Wikipedia](https://en.wikipedia.org/wiki/Memory-mapped_I/O)  
[mmap from Wikipedia](https://en.wikipedia.org/wiki/Mmap)
