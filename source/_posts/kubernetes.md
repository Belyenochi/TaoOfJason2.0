---
title: "围绕kubernetes的设计与源码探索之旅"
date: 2020-04-23 17:47:47
tags:
  - "kubernetes"
---

### 引言

在kubernetes相关基础设施领域工作将近一年时间了，期间对kubernetes以及相关组件乃至整个云计算的过去，当下与未来有了一定思考，趁此离职学习期间将这一年学到的东西整理一下，这次探索因为我在实际的工业界实践过程中已经有了自顶向下的实践，所以我决定这一次自底向上的去进行探索（当然隔壁的数据库实现也会慢慢更新的：），为了区别已经让我厌烦的XXX源码讲解我决定使用结合源码片段的自问自答形式（感谢little系列…感谢Friedman）。

### 适宜人群

- 了解kubernetes的使用以及基本概念（CRI,CNI,CSI）
- 有一定的kernel知识（进程，内存，IO子系统）
- 可以接受我有时候对具体细节实现浅尝辄止的习惯（但是一般我都会给一个更好的说明链接，因为有一些概念我自己也只是有所了解

### 目录

（初版）

1. kubernetes（v1.18.2）
   - kubelet
   - kube-proxy
   - kube-apiserver
   - kube-controllermanager
   - kube-scheduler
2. etcd（v3.4.3）
3. calico（v3.12）
4. runc（v1.0-rc10）
