---
title: "计算的要素第五章小结"
date: 2018-08-04 15:22:46
categories:
  - "计算机体系结构"
tags:
  - "Nand2tetris"
---

*what I hear, I forget; What see, I remember; What I do, I understand.*

### 1 回顾

![](/images/jsys_05/00-04.jpg)  
经过了逻辑门，触发器，寄存器，RAM,PC，ALU，取址模式，I/O内存映像的学习，我们已经学习了实现CPU的前置条件，那么让我开始开始CPU以及进一步的Hack Machine的实现吧！

### 2 背景

#### 2.1 存储程序

一个由有限硬件组件构成的计算机却可以执行无限的任务队列，从交互式游戏到字处理到科学计算，这些其实都是“存储设备 （stored program）”概念的功劳。  
存储设备的概念想当简单：计算机基于固定的硬件平台，能够执行固定的指令集。同时，这些指令能够被当作构建模块，组成任意的模块。这种思想也体现在软件工程领域中的模块化设计，将机制（提供了什么能力）和策略（如何使用这些能力）分离。正是因为这种原因才使得Intel不用开发各种各样的游戏吧：-）

#### 2.2 冯诺依曼结构

冯诺依曼体系结构的基础是一个**中央处理单元**（CPU），它与**内存**进行交互，负责从**输入设备**接收数据，向**输出设备**发送数据。  
![](/images/jsys_05/stored%20program.jpg)  
这个体系结构的核心在于存储程序的概念：计算机内存不仅存储着要进行操作的数据，还存储着指示计算机运行的指令。

### 3 CPU的设计与实现

#### 3.1 CPU的构成

CPU是计算机体系的核心，负责执行已被加载到指令内存中的指令。这些指令告诉CPU去执行不同的计算，对内存进行读/写操作，以及根据条件跳转去执行程序中其他指令。CPU通过使用三个主要的硬件要素来执行任务：算术逻辑单元（ALU，Aritmetic-Logic Unit），一组寄存器（registers）和控制单元（control unit）。  
**算术逻辑单元（ALU）**：ALU负责执行计算机中所有底层的算术操作和逻辑操作。比如，典型的ALU可以执行的操作包括：将两个数相加；检查一个数是否为整数；在一个数据字（word）中进行位操作；等等。  
**寄存器（Registers）**：CPU的设计是为了能够快速地执行简单计算。为了提高它的性能，将这些和运算相关的数据暂存到某个局部存储器中是十分必要的，这远比从内存中搬进般出要好。因此，每个CPU都配有一个一组高速寄存器（Intelx86\_64中的各类寄存器），每个寄存器都能保存一个独立的字  
**控制单元（Contrl Unit）**：计算机指令用二进制代码来表示，通常具有16、32或64位宽。在指令能够被执行之前，须对其解码，指令里面包含的信息向不同的硬件设备（ALU，寄存器，内存）发送信号，指使它们如何执行指令。指令的解码过程是通过某些**控制单元**（Control Unit）。这些控制单元还负责决定下一步需要取出和执行哪一条指令。

#### 3.2 CPU的执行模型

CPU操作现在可以被描述成一个**重复的循环**：从内存中取 一条指令（字）：将其解码；执行该指令，取下一条指令：如此往复循环。指令的执行过程中可能包含下面的一些子任务：让ALU计算一些值，控制内部寄存器，从存储设备中读取一个字，或向存储设备中写入一个字。在执行这些任务的过程中，CPU也会计算出下一步该读取并执行哪一条指令。  
![](/images/jsys_05/Cycle.jpg)  
CPU的**取指-执行循环**（fetch-exec cycle）模型让人不禁联想到**元语言循环**上（eval-apply），不过后者是指称语义的实现（本质是递归求解子表达式）而前者则是一个迭代的物理模型（通过迭代求解子问题，在这里是每一条指令，两者区别从问题的规模看前者可以分解为n层，后者则是2层（在Hack Computer的CPU模型中））  
![](/images/jsys_05/exp%20and%20memory.jpg)

#### 3.3 eval-apply模型

![](/images/jsys_05/eval-apply.jpg)  
本质是通过将复合过程分解为原子（atom）过程来求解（当然途中可能会对求值环境产生作用）的过程。Evaluator就是另一个程序啦&#126;，之前写过一个简单的[Scheme Evaluator](https://github.com/Belyenochi/SchemeREPL/blob/master/js/Scheme.js),感兴趣的朋友可以参考实现

### 4 图灵机（Turing Machine）和冯诺依曼结构（von Neumann architecture）的大一统

TM和PL的初学者（比如在下）肯定会有疑问，这些抽象的东机器实非常美，但是是怎么映射到现实世界的呢，今天就以TM为例来谈一谈优雅的理论模型是如何转化到物理的取值-执行循环的（Fetch-Execute cycle）

#### 4.1 TM

![](/images/jsys_05/TM.png)  
![](/images/jsys_05/TM_increase.png)

> In his 1948 essay, “Intelligent Machinery”, Turing wrote that his machine consisted of:  
> …an unlimited memory capacity obtained in the form of **an infinite tape** marked out into squares, on each of which a symbol could be printed. At any moment there is one symbol in the machine; it is called the **scanned symbol**. The machine can alter the scanned symbol, and its behavior is in part determined by that symbol, but the symbols on the tape elsewhere do not affect the behavior of the machine. However, the tape can be **moved back and forth**through the machine, this being one of the elementary operations of the machine. Any symbol on the tape may therefore eventually have an innings.\[17\] (Turing 1948, p. 3\[18\])

形象的定义图灵机就是由一条无限长的纸带，字符集，状态集，当前所在位置，状态转移函数。（严格的图灵机定义是由[七元组](https://en.wikipedia.org/wiki/Turing_machine)组成，但和这里的5元组在计算能力上是等价的）  
图灵机相当于具有标准后进先出语义的双栈PDA ，通过使用一个堆栈来模拟右侧，另一个堆栈来模拟图灵机的左侧，从文法角度看TM的计算能力相当于**递归可枚举**文法。

Q：图灵机是当前计算机的极限了吗？  
A：从计算模型上来看是的，实际上到现在为止还没有超出图灵机计算能力范畴的计算机出现，无论是人工神经网络还是遗传算法，“机器学习”和“人工智能”领域的算法都是确定，有穷的，也没有超出图灵机的计算范畴，当然这么多年来人类还是有尝试的，比如[Oracle machine](https://zh.wikipedia.org/wiki/%E9%A0%90%E8%A8%80%E6%A9%9F)

更多关于TM的内容，可以参考Reference，和我之前的blog[ 理解图灵机及其边界](https://blog.csdn.net/qq_36936155/article/details/79347364)

#### 4.2 如何统一

![](/images/jsys_05/compare.jpg)  
介绍完了TM和冯诺依曼体系，是时候进行mapping了。  
状态集合state set -> state register  
纸带tape -> memory（通常意义上是RAM）  
状态转换函数delta -> 组合电路中的输出（输出至state register相当于进入了另一个状态）  
当前所在位置current position -> PC  
字符集character set -> memory中的instruction  
实际上，取值-执行模型中从内存中取出指令，交给CPU运算然后决定下一条指令的地址（模拟了纸带头读取当前位置，并根据当前位置进行state判断，左移右移或停机），然后改变PC（对应当前所在位置发生改变），然后循环直达到Final State（对应TM中的停机）

学过数据结构的朋友会发现图灵机实际上也代表了链式存储，call by position而冯诺依曼的RAM实际上就是Vector，嗯，通过多路选择器随机访问，call by rank，这也说明了图灵机作为理论模型在实际应用中还是需要进行trade off

### 5 Reference

[Evaluation and universal machines The Eval/Apply Cycle Examining](https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-001-structure-and-interpretation-of-computer-programs-spring-2005/lecture-notes/lecture23webhan.pdf)  
[Denotational\_semantics](https://en.wikipedia.org/wiki/Denotational_semantics)  
[Turing\_machine\_wiki](https://en.wikipedia.org/wiki/Turing_machine)  
[can-computers-do-things-turing-machines-cant](https://philosophy.stackexchange.com/questions/48865/can-computers-do-things-turing-machines-cant)  
[C++ Templates are Turing Complete](chrome-extension://cdonnmffkdaoajfknoeeecmchibpmkmg/static/pdf/web/viewer.html?file=http%3A%2F%2Fport70.net%2F~nsz%2Fc%2Fc%252B%252B%2Fturing.pdf)
