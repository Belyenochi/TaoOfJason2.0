---
title: "从零开始的正则引擎之旅(零)"
date: 2018-08-27 17:06:11
categories:
  - "编译原理"
tags:
  - "RegexEngine"
---

### 1 序言

距离挖这个坑已经过去3个月了，嗯，我没记错的的话4个月前我还挖了一个brainfuck解释器的坑，就作为下周的作业吧&#126;  
废话不多说，本系列旨在

1. 理解掌握一个简单parser的所作所为。
2. 梳理正则引擎构建和优化过程中的各种该算法
3. 造出一个能用的正则引擎（C++）
4. 将该正则引擎作为Node.js的C++扩展

### 2 阶段构建图

![](/images/regex_engine_00/milestone.jpg)

1. 实现一个LL(1)的递归下降parser解析regex文法
2. 将part1生成的AST转化为NFA
3. 将NFA转化为DFA
4. 优化DFA，最小化等
5. <strong>【英雄难度副本】</strong>parser到VM code执行
6. <strong>【史诗难度副本】</strong>采用JIT优化引擎  
   后两个阶段我现在并没有很大的把握做好，但我会尽力而为的，也欢迎熟悉这一块的同学能够给予我一些建议与指正，感激不尽。

### 3 Reference

[Implementing Regular Expressions Russ Cox ](https://swtch.com/~rsc/regexp/)  
[ytljit](https://github.com/miura1729/ytljit/blob/master/sample/regexp.rb)  
[如何从零写一个正则表达式引擎？](https://www.zhihu.com/question/27434493)  
[Comparison of regular expression engines](https://en.wikipedia.org/wiki/Comparison_of_regular_expression_engines)  
[Regular Expression Matching Can Be Simple And Fast ](https://swtch.com/~rsc/regexp/regexp1.html)
