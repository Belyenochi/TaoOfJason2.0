---
title: "计算的要素-第一章小结"
date: 2018-07-30 13:35:12
categories:
  - "计算机体系结构"
tags:
  - "Nand2tetris"
---

*Such simple things,And we make of them something so complex it defeats us ,Almost. —-John Ashbery(1927)*

### 1 OverView

![](/images/jsys_01/ClassOverview.jpg)  
以上是课程的学习，内容，让我们bottum up搭建一个计算机吧!

### 2 什么是逻辑门（logic Gate）？

在谈论什么是逻辑门之前，我们得先谈谈布尔代数，因为计算机硬件基于二进制数据的表示和处理，所以布尔代数成了计算机中事实上不可或缺的理论根基。  
学过离散数学的朋友肯定对真值表不陌生，事实上逻辑门就是由布尔函数的物理具象化，输入和输出就是真值表的变量，如果布尔函数f有n个输入变量，返回m个二进制的结果，那么用来实现这个函数f的门将会有n个输入管脚（input pins）和m个输出管脚（ouput pins） 。当我们把一些值从输入管脚输入，它的内部结构即逻辑门  
会计算然后输出对应的结果值。  
![](/images/jsys_01/logicGate.jpg)

### 3 如何使用逻辑门

![](/images/jsys_01/implementOfGate.jpg)  
对于任何给定的逻辑门，我们都能够从外部和内部两个不同方面进行观察，图1.4中右边的图给出了门的内部结构（或称为内部实现），而左边部分仅仅显示了门的外部接口（interface），也就是输入和输出管脚。内部结构仅仅与门电路的设计者相关，而外部结构则是其他设计者所关心的（也就是外部结构也就是我们常常使用的黑盒抽象，只关心输入输出），他们仅仅使用门电路的抽象而不去关心其内部结构。  
下面总结两点关于逻辑设计的要素：

1. 虽然逻辑设计（门电路设计者）的基本功能可以通过不同的的方式实现其外部接口，但从效率的角度上来说，**基本原则**是用尽可能少的门来显示尽可能多的功能。
2. 给定门的描述（外部接口），通过应用已经实现的门，找到有效的方法来实现它。  
   **因为本课程后续部分采用了HDL语言，所以这里简单的解释HDL语言：**  
   chips(芯片)的HDL定义包括header部分和parts部分。  
   Header部分描述了芯片的接口(interface)，也就是芯片的名称、输入和输出管脚。  
   Pars部分描述了所有底层电路的名称和拓扑结构，这些电路是构成该芯片的基本部分，每个部分用一个statement(语句)来表示，它描述了该部分的名称与其他部分的连接方式。  
   为了简单明了的编写这些语句，HDL程序员必须有内在模块的接口文档，体现在project中就是注释了。  
   形如part’s pin name = chip’s pin name的含义是将芯片内部的管脚与外部管教相连，如此实现了芯片的输入输出。  
   更多关于HDL程序设计的内容可以参考《计算的要素》附录部分。

### 4 为什么使用逻辑门

之前曾谈到计算机的计算模型采用了布尔代数，从图灵机的纸带存储符号,到冯诺依曼体系结构的memory都采用了0,1作为数据的表示形式，其根本是高效和简单（当然lambda calculus不是这么做的，你可以自己定义数字如church numerals，函数等，因为是抽象模型所以理解和运算起来没有0，1在实际应用中直接，但事实上无论是TM,lambda calculus，冯诺依曼体系结构都是等价的，可以说前两者是等价的计算模型，后者是物理实现模型，本质都是对计算的建模且等价！）

### 5 各种逻辑门（project中的图示）

项目地址[https://github.com/Belyenochi/nand2tetris](https://github.com/Belyenochi/nand2tetris)

1. And  
   ![](/images/jsys_01/And.png)
2. And16  
   ![](/images/jsys_01/And16.png)
3. Dmux  
   ![](/images/jsys_01/DMux.png)
4. DMux4Way  
   ![](/images/jsys_01/DMux4Way.png)
5. DMux8Way  
   ![](/images/jsys_01/DMux8Way.png)
6. Mux  
   ![](/images/jsys_01/Mux.png)
7. Mux4Way16  
   ![](/images/jsys_01/Mux4Way16.png)
8. Not  
   ![](/images/jsys_01/Not.png)
9. Or  
   ![](/images/jsys_01/Or.png)
10. Xor  
    ![](/images/jsys_01/Xor.png)
