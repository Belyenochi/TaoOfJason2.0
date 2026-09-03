---
title: "计算的要素第十二章总结"
date: 2018-09-01 23:05:16
categories:
  - "计算机体系结构"
tags:
  - "Nand2tetris"
---

本章是针对Hack OS各个模块的概述及其实现，其中某几个模块实现的算法很有意思，让我们马上开始吧&#126;

### 1 什么是OS（以Hack OS为例）

1. 以一种对软件友好的方式封装了不同的硬件服务
2. 用不同的函数和抽象数据类型扩展了高级语言。在这个意义上的操作系统与语言的标准程序库的分界线就不那么明显。事实上，某些现代语言（例如Java）就趋向于将很多经典的操作系统服务（比如GUI管理，内存管理，和多任务处理等）连同很多语言拓展一起打包到其标准程序库中，这么做的目的以我的理解是为了屏蔽系统层面的差异（比如C的fopen等）以及减少系统调用（比如Java的内存管理，向内存申请一大片空间，Java NIO等）

### 2 为什么我们需要OS

计算机是用来解决实际问题的，所以我们构建计算机硬件用来计算，基于硬件我们造了编译器用来写更可读的汇编程序，然后有了用汇编程序写的应用，随着应用程序越来越到，我们需要抽象出能够将控制（硬件和外围设备以及软件）和分配资源的常用功能集一体的概念，它就是Operating System，感兴趣的同学可以看看操作系统的演化。（有时间去研究研究发出来）  
计算机系统的基本目标是执行用户程序并以更容易的方式解决用户的问题。

### 3 数学操作

首先，这里明确的告诉了我下意识想到的通过累加和累减来实现乘除法来操作系统层面是不可行的，原因很简单，效率太低了高达O（n）的输入敏感复杂度会让计算一个100000000000000\*10000000000000的人在凳子上坐上几天（只是举个例子，数据不具备代表性），那么就让我们来看一看Hack OS的做法

注：以下所有运算都假定操作数为16位（Hacl硬件规范字长16位）

#### 3.1 乘法

![](/images/jsys_12/乘法.jpg)

```javascript
function multiply(x, y) {
    let sum = 0,index = 15;

    while(index > 0) {
        if (y.toString(2).padStart(16,"0").charAt(index) !== "0") {
        	console.log(y, index,y.toString(2).padStart(16,"0"));
             sum = sum + x;
        }
        x = x + x;
       index = index - 1;
    }

    return sum;
}
```

可以看到实际上乘法就是在模拟我们日常生活中的乘法，通过逐位相乘，并且再每一次乘完以后将被乘数左移一位，迭代这个过程直到遍历完所有位数，在日常生活中我们看到某个算术53\*20，当我们处理完5这一位不会再用0去乘20，但是在计算机中你需要一套规则去运算，这套规则在这里就是遍历完操作数的所有位，即便它全是0。

#### 3.2 除法

![](/images/jsys_12/除法.jpg)

```javascript
function divide(x, y) {
    let q,result,flag;

    flag = !((x < 0) ^ (y < 0));

    x = Math.abs(x);
    y = Math.abs(y);
    if(y > x) {
        return 0;
    }
    q = divide(x,y + y);

    if (x - (2 * q * y) < y) {
        result = q + q;
    } else {
        result = q + q + 1;
    }

    return flag ? result : -result;
}
```

思路也是模仿人除法的过程，选择一个尽可能从x上减去y的最大倍数（假定算式x/y），直到y比x大，这个过程的递归形式如上。

#### 3.3 平方根

![](/images/jsys_12/二叉树.jpg)

```javascript
function sqrt(x) {
    let y,j,temp,tempQ;

    y = 0;
    j = 7;

    while(j >= 0){
      temp = y + Math.pow(2,j);
      tempQ = temp * temp;
      //avoid overflow
      if((tempQ <= x) & (tempQ > 0)){
        y = temp;
      }
      j = j - 1;
    }
    
    return y;
}
```

这个算法就是根据y²<= x <(y+1)²，使得y从0开始逐步逼近x使得y满足上述区间

### 4 内存管理

内存管理很有趣，首先说一说内存管理的背景

#### 4.1 背景

计算机的程序会声明并使用各种类型的变量，包括整数、布尔数等简单的数据类型以及如数组、对象等复杂的数据类型。高级语言的最大优点之一是程序员不必关心内存管理细节：比如为变量分配内存空间；以及当该变量不再使用时，回收为其分配的内存空间。所有关于内存管理的琐碎工作都由编译器、操作系统和虚拟机在后端完成。  
不同的变量的内存在程序生命周期中的不同时刻被分配。例如，**静态变量**在编译期间由编译器为其分配内存，而**局部变量**则在每个子程序开始运行时被分配在堆栈内。其他变量的内存则是在程序的执行过程中被动态分配，这时候OS就要上了。注意操作系统本身并不自带垃圾回收功能，这是高级语言提供的内存管理手段，比如Java，JVM先向OS请求一大块内存用于程序运行，然后在这块内存中可以“自动内存管理”，本质是在OS层面之上进行内存管理，这样就不用频繁的调用系统的malloc，free了

在OS看来内存其实就是一块大数组（big buffer），当然真实的内存实现我们已经在之前看到过了(多个Register->多个RAM->Memory)。

#### 4.2 内存管理算法

##### 4.2.1 alloc

![](/images/jsys_12/malloc.jpg)  
上图的freeList的节点乍看可能有点疑惑，其实这里的freeList是经历过deAlloc的，一开是freeList只有一个节点就是整块内存区，然后随着alloc-deAlloc，链表节点逐渐增多，碎片化也越来越严重…

##### 4.2.2 deAlloc

![](/images/jsys_12/delloc.jpg)  
deAlloc的算法其实可以总结如下：  
假设待释放节点值为o

1. 找到freeList中节点的地址值比待释放节点值大的节点（A）
2. 将待释放的节点的next域设为A的地址  
   3.将A的上一个节点的next域设为o

然而我刚开始的做法是：

1. 将o的next域设为freeList指向的节点
2. 修改freeList指向o的地址（这和上图Mark的做法有点出路，个人觉得这样头插效率比根据Address来的高且简单）  
   当然我所谓的优于，是建立在没有合并的基础上的…

##### 4.2.3 defragmentation（碎片合并）

细心的读者已经发现了，上图中还包含这碎片合并的动作，这个碎片合并的动作如果链表不是根据address有序的话复杂度是O（n²）级别的，这带来的直接后果就是，咦，为什么我的程序关的这么慢。。。所以我们在deAlloc的时候要用第一个算法的原因就是如此。

defragmentation算法如下：  
1.遍历链表  
2.如果当前节点的地址值+size+1（存储size的存储单元） = 下一个节点的地址，merge

### 5 输入输出管理

这部分我就说两个比较有意思的地方

#### 5.1 输出

##### 5.1.1 绘制三角形

![](/images/jsys_12/sanjiao.jpg)  
这里说绘制三角形，不如说如何模拟三角形，实际上我们画出的三角形是以堆砌一个个像素形成的，可以把像素看出3\*1的正方形，而绘制三角形的过程，就是如何堆砌正方形让它更像三角形，下面是过程图示  
![](/images/jsys_12/sanjiaoxing.png)

**图中最关键的一点在于 当前的坐标斜率<=(y2-y1)/(x2-x1),a++，否则b++**

##### 5.1.2 绘制圆

![](/images/jsys_12/circle.jpg)  
绘制圆的本质就是绘制一系列的矩形，算法如上

#### 5.2 输入

这一部分主要描述操作系统如何在三个递增的抽象层级上来管理面向文本的输入：

1. 捕获单字符输入
2. 捕获多字符输入
3. 捕获多字符输入（也就是字符串）

##### 5.2.1 侦测键盘输入

![](/images/jsys_12/keyboard.jpg)  
在底层捕获键盘输入时，程序直接从硬件获取数据，并确定用户当前按下哪个键。对该原始数据的访问依赖于键盘接口的具体特性。比如，若接口是被键盘持续更新的内存映像（比如Hack），就可以通过检测对应的内存映像来确定按下了哪个键

##### 5.2.2 读取单一字符

![](/images/jsys_12/readchar.jpg)

##### 5.2.3 读取字符串

![](/images/jsys_12/readLine.jpg)

**其他模块String，Array，Output，Sys是在以上模块上的封装，具体的实现细节就参考书吧。**

### 6 Q&A

Q：关于平方根算法有更高效的算法吗？  
A：除了书中提到的牛顿法求平方根（不动点算法），泰勒展开，[这里](http://nand2tetris-questions-and-answers-forum.32033.n3.nabble.com/A-more-efficient-square-root-algorithm-td4028140.htmla)实现了一个长除法的实现，除了平方根算法，书中对于圆的绘制也有[更高效的算法](http://nand2tetris-questions-and-answers-forum.32033.n3.nabble.com/Fast-circle-algorithm-td4030808.html)

### 7 Reference

[用于绘制圆的快速Bresenham型算法，John Kennedy](http://sites.google.com/site/johnkennedyshome/home/downloadable-papers/bcircle.pdf)  
[用于绘制椭圆的快速Bresenham型算法，John Kennedy](https://sites.google.com/site/johnkennedyshome/home/downloadable-papers/bcircle.pdf?attredirects=0)
