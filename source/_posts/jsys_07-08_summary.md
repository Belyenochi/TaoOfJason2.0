---
title: "计算的要素第七-八章小结"
date: 2018-08-29 19:19:23
categories:
  - "计算机体系结构"
tags:
  - "Nand2tetris"
---

*Programmers are creators of universes for which they alone are responsiable. Universes of virtually unlimited complexity can be created in the form of computer programms. —-Joseph Weizenbaum, Computer Power and Human Reason, 1974*

因为书中第七章和第八章都在讲虚拟机的后端部分，故这里将其合并总结。

### 1 虚拟机

#### 1.1 虚拟机是什么

![](/images/jsys_07-08/VM.jpg)  
虚拟机（VM）是在本机操作系统之上的高级抽象，它模拟物理机器。在本书中，我们讨论的是中间编译目标，既不是进程虚拟机(process virtual machine)，比如JVM，CLR等运行时平台，也不是系统虚拟机(system virtual machine)，系统虚拟机提供了系统级的硬件抽象，比如VirtualBox。虚拟机使同一平台能够在多个操作系统和硬件体系结构上运行。可以将Java和Python的解释器作为示例，其中代码被编译为JVM特定的字节码。在Microsoft .Net体系结构中也可以看到相同的情况，其中代码被编译为CLR（公共语言运行时）的中间语言。这里有一篇讲解[Hack VM](http://nand2tetris-questions-and-answers-forum.32033.n3.nabble.com/What-does-quot-virtual-machine-quot-and-quot-real-platform-quot-mean-td4028959.html#a4028960)的例子供大家参考。  
虚拟机通常应该实现什么？它应该模拟物理CPU执行的操作，因此理想情况下应包含以下概念：

1. 将源语言编译为VM特定的字节码
2. 包含指令和操作数的数据结构（指令处理的数据）
3. 用于函数调用操作的调用堆栈
4. 指向下一条要执行的指令的“指令指针”（IP）
5. 一个虚拟的’CPU’ - 指令调度程序
6. 获取下一条指令（由指令指针寻址）
7. 解码操作数
8. 执行指令

#### 1.2 为什么需要虚拟机？

高级语言程序在运行在目标机器上之前，必须得翻译成对应的机器语言。这个编译过程是相当复杂的…通常，必须给任意给定的高级语言写对应到指定机器的编译器，但这种高级语言到机器语言的直接映射直接导致了强依赖，从软件工程的角度看减少依赖，没有什么是加一层抽象不能解决的，如果有，那就加两层。  
结果就是，为了减少依赖，将整个编译过程划分为几乎独立的两个阶段。

- 第一阶段，高级语言翻译到中间语言（IR）
- 第二阶段，中间语言翻译到对应的硬件机器语言

你看这样语言的编译器实现人员在大部分情况下就不用再写各种各样的编译到机器语言的编译器，瞧瞧Clojure，站在JVM的肩膀上：），事实上这种行为也是软件工程的良好体现，良好的模块化设计（高层模块和底层模块，模块件通过VMcode这种语言通信）和抽象屏障（VMCode就是高层和底层之间的万里长城）意味着编写高级语言的编译器的程序员（高层模块）和将VMcode编译到硬件的程序员（底层模块）可以分头行动，抽象屏障万岁！！！

#### 1.3 Stack based Virtual Machine

VM的实现主流有两种，一种是堆栈模型，一种是寄存器模型（下一节讲），选择模型要考虑的关键因素是：在VM操作中的操作数和操作结果应该放在哪里。而在堆栈模型中，是将其放在堆栈（stack）这个数据结构中。  
基于栈的虚拟机有以下几个特点

- 指令长度是固定的
- 执行多个操作数计算时，会先将操作数做压入栈，由运算指令取出并计算

下面以Add指令来说明stack machine的一般操作：  
![](/images/jsys_07-08/add.jpg)

1. PUSH 4 // 当前栈指针指向的地址赋值4，SP=SP+1
2. PUSH 5 // 当前栈指针指向的地址赋值5，SP=SP+1
3. ADD // 取出栈最上方的两个值相加，压入SP-2，SP=SP-1

可以看出基于堆栈的模型的优点在于操作数由堆栈指针(SP)隐式地寻址。这意味着虚拟机不需要显式地知道操作数地址，因为调用堆栈指针将给（Pop）下一个操作数。在基于堆栈的VM中，所有算术和逻辑运算都是通过push和pop操作数并在堆栈中生成来执行的。

#### 1.4 Register based Virtual Machine

在基于寄存器的虚拟机实现中，存储操作数的数据结构基于CPU的寄存器。这里没有PUSH或POP操作，但是指令需要包含操作数的地址（寄存器）。也就是说，指令的操作数在指令中明确地被寻址，不像基于堆栈的模型，其中我们有一个指向操作数的堆栈指针。例如，如果要在基于寄存器的虚拟机中执行ADD操作，则指令或多或少如下：  
![](/images/jsys_07-08/register.jpg)

正如前面提到的，没有POP或PUSH操作，因此添加指令只是一行。但是与堆栈不同，我们需要明确地将操作数的地址称为R1，R2和R3。这里的优点是**不存在入栈出栈开销**，并且基于寄存器的VM中的指令在指令调度循环内执行得更快。

基于寄存器的模型的另一个优点是它允许在基于堆栈的方法中无法完成的某些优化。一个这样的例子是当代码中有**共同的子表达式**时，寄存器模型可以计算一次并将结果存储在寄存器中以供将来使用时子表达式再次出现，这降低了重新计算表达式的成本。

基于寄存器的模型的**问题**是平均寄存器指令大于平均堆栈指令（指令长度也不是固定的），因为我们需要明确指定操作数地址。由于堆栈指针对堆栈机器的指令很短，相应的寄存器机器指令需要包含操作数位置，并且与堆栈代码相比产生更多的寄存器代码，并且如果利用寄存器做数据交换，就要经常保存和恢复寄存器的结果，这就导致基于寄存器的虚拟机在实现上要比基于栈的复杂，代码编译也要复杂得多

我遇到的一篇很棒的博客文章（在此链接中）包含基于寄存器的虚拟机的解释性和简单的C实现。如果实现虚拟机和解释器是您的主要兴趣，那么ANTLR创建者Terrence Parr的书名为“语言实现模式：创建您自己的特定领域和通用编程语言”，可能会非常方便。

### 2 堆栈运算

#### 2.1 算术和逻辑命令

![](/images/jsys_07-08/arithic.jpg)  
VM支持一元和二元操作命令。根据命令的操作数个数，从堆栈中弹出对应个元素，然后执行相应的运算，再将结果压入堆栈。这么做的好处很明显，每次操作不用管堆栈的其余部分（除了操作数）

#### 2.2 内存访问命令

![](/images/jsys_07-08/PushPop.jpg)  
所有的内存段都通过两个命令来存取，PUSH，POP，这使得对内存的操作只需关注栈顶的变化。

### 3 程序控制

#### 3.1 程序控制流命令

![](/images/jsys_07-08/goto.jpg)  
计算机程序默认的执行顺序是线性的，即一个命令接着一个命令执行 ，这个连续的控制流偶尔被分支命令打断（比如在循环中执行迭代）。在底层编程中，分支逻辑采用goto destination 命令实现，该命令让计算机跳转到目标参数指定的位置（Hack是goto到ROM的指定位置），而不是接着原指令的下一条指令线性执行。目的地址的指定方式可以有多种形式，最原始的一种就是指定即将执行的指令的物理地址。应用标签label来描述jump的目的地址可以建立稍微抽象一点的重定向命令（redirection command）。这种改进需要程序语言配有标签指令（labeling directive），它可将标签绑定到程序中的指定位置。

#### 3.2 函数调用命令

![](/images/jsys_07-08/funCall.jpg)  
高级语言所具有的这种能将表达式自由组合的能力使得我们可以编写抽象代码，让我们把主要精力放在算法的思想上面，而不是机器的执行上。当然高级语言抽象级别越高，在底层要做的工作就越多。特别是，必须在底层控制子程序（callee）和子程序调用者（caller）之间的相互影响。对于在运行期的每个子程序调用，底层必须处理下面的一些细节

- 将参数从调用者(caller)传递给被调用者(callee)
- 在跳转并执行被调用者之前，先保存调用者的状态
- 为被调用者使用的局部变量分配空间
- 跳转并执行被调用者
- 将被调用者的运行结果返回给调用者
- 在从被调用者返回之前，回收其使用的内存空间
- 恢复调用者的状态
- 返回到调用语句之后的下一条语句继续执行

有关上述命令的实现，书中都有详细介绍，这里就不再展开叙述。

### 4 Q&A

Q：有什么办法可以优化生成的asm代码吗？  
A：[hack vmtranslator优化](http://nand2tetris-questions-and-answers-forum.32033.n3.nabble.com/Generated-code-size-td1201814.html)

Q：How is the VM really made?  
A：VM Translator在您的计算机上运行，并将.vm文件转换为.asm文件。我用Python编写了我的VM Translator。编写本机VM是一项艰巨的任务，需要比Hack更复杂的计算机才能运行。Java VM是用C / C ++编写的。特定于平台的编译器允许它在各种不同的目标硬件上运行。已经用C / C ++编写了与目标操作系统连接的库。当您为32位Windows系统下载Java时，您将获得一个二进制文件，该二进制文件的目标是与适当的Windows支持库链接的32位Intel 处理器。在现实世界中，我们尽可能少地编写汇编代码。对于我（Mark）所做的嵌入式系统编程，工具（编译器等）在Windows上运行，只有二进制文件加载到实际的硬件上。所有代码都是用C语言编写的，带有一些小的汇编语言例程。512K ROM和64K RAM是一个很大的配置。现代C / C ++编译器是使用它们自己的早期版本编写的。第一个C编译器可能用B语言编写，B语言是C语言的前身。

Q：既然Hack VM只是个目标代码，那么如何用Jack来实现VM 模拟器呢（现在Jack的栈式虚拟机能跑都是多亏了Java编写的模拟器，实际上这个模拟器起了一个VM的作用，问题是现在要用Jack自我实现这个模拟器，通过JackOS的硬件）  
A：事实上这里Mark已经有了尝试[ Hack II: Escaping the Harvard straitjacket](http://nand2tetris-questions-and-answers-forum.32033.n3.nabble.com/Hack-II-Escaping-the-Harvard-straitjacket-td2877780.html)

### 5 Reference

[Virtual Machine](https://en.wikipedia.org/wiki/Virtual_machine)  
[Is the Java Virtual Machine really a virtual machine in the same sense as my VMWare or Parallels file?](https://stackoverflow.com/questions/861422/is-the-java-virtual-machine-really-a-virtual-machine-in-the-same-sense-as-my-vmw)  
[erlang虚拟机代码执行原理](https://blog.csdn.net/mycwq/article/details/45653897)  
[Stack based vs Register based Virtual Machine Architecture, and the Dalvik VM](https://markfaction.wordpress.com/2012/07/15/stack-based-vs-register-based-virtual-machine-architecture-and-the-dalvik-vm/)
