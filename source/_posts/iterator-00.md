---
title: "迭代器实现（零）"
date: 2018-08-31 11:24:07
tags:
  - "Jason Tomas的造轮子之旅"
---

### 1 迭代器是什么

在计算机编程中，迭代器是一个对象，它使程序员能够遍历容器，特别是列表。通常通过容器的接口提供各种类型的迭代器。虽然给定迭代器的接口和语义是固定的，但迭代器通常是根据容器实现的底层结构实现的，并且通常紧密耦合到容器以启用迭代器的操作语义。迭代器执行遍历并且还允许访问容器中的数据元素，但本身不执行迭代（即，并非没有采用该概念或使用术语的轻微自由）。迭代器在行为上类似于数据库游标。迭代器可以追溯到1974年的CLU编程语言。

### 2 为什么会需要迭代器？

1. 便于数据流的控制，假定有一个数据流，这时如果有迭代器就可以很方便的操作这个数据流，当然也可以把迭代器理解为延时求值（lazy eval）啦
2. 解耦算法和数据结构，比如你想找到树中符合条件的节点，传统的做法是使用一个查找算法，传入一个树对象和查找条件，遍历树进行匹配，而拥有迭代器之后，你只需不停的next直到迭代器末尾，大大增加了代码的可读性（毕竟是线性的）

```javascript
// 使用迭代器前
select(node, condition,result) {
	if (node) {
		if(node.left !== '') {
			select(node.left);
		}
		if (condition(node.value)) {
			result.push(node.value);
		}
		if(node.right !== '') {
			select(node.right);
		}
	}
}
```

```javascript
// 使用迭代器后,可读性增强了
select(treeIterator, condition， result) {
	for(treeNode of treeIterator) { // 假定这里for of调用迭代器，事实上在JS中也确实如此
		if(condition(treeNode)) {
			result.push(treeNode);
		}
	}
}
```

虽然线性的代码更可读，但我个人觉得递归的代码真的很美…我个人在可以递归的条件下是不会去写迭代的（除了效率限制），不过现在部分编译器支持Tail call optimization，虽然JavaScript没有，但是你可以将任何递归用黑魔法 Trampoline转化为形式上的尾递归&#126;

### 3 实现迭代器

迭代器的本质是延迟求值或者说部分求值（令我想到了SICP的流模型），那么由于传统的程序执行比如递归，你是无法控制程序的控制流的，拿之前的递归遍历树的例子来看，你无法在它遍历到某个子树（这时这个子树的左右节点还存在）的情况下马上回到根节点的，这是因为受限于函数的调用栈，当然你可以通过cps变换来手动控制你的代码，这是另外一回事，这里暂不予展开。既然我们不能控制函数调用栈，那我们就一不做二不休的自己创建栈来模拟之前的遍历函数运行，这样代码就在我们的掌控下了（基于栈的程序控制其实体现着栈式虚拟机的思想，通过push和pop来控制”计算”，而CPS变换更多的体现的是续算（continuation）的传递，PL的魔法啦）

接下来我们可以看看，基于栈的非递归遍历实现  
```javascript
// 基于栈的非递归查询算法的实现
function inorder_tarverse_nonrecursive(node,condition,result) {
	let stack = [];

	while (true) {
		// 压入所有左子节点
		while (node) {
			stack.push(node);
			node = node.left;
		}
		// Pop出左子节点，进入右子节点或者返回父节点
		while (true) {
			let top = stack.pop();
			if (condition(top)) {
				result.push(top.value);
			}
			if (top.right) {
				node = top.right;
				break;
			}
			// 此时根节点和根中所有左子节点已经遍历完毕
			if (stack.length === 0) {
				break;
			}
		}
		// 遍历完毕所有节点
		if (stack.length === 0) {
			break;
		}
	}
}
```

这里给出递归实现以做对比  
```javascript
function inorder_traverse(node,condition,result) {
	if (node) {
		inorder_traverse(node.left);
		if (condition(node.value)) {
			result.push(result);
		};
		inorder_traverse(node.right);
	}
}
```

递归的调用栈和非递归模拟的程序栈对比  
树：  
![](/images/tools/iterator/树.jpg)

非递归：  
![](/images/tools/iterator/栈1.jpg)  
![](/images/tools/iterator/栈2.jpg)

递归  
![](/images/tools/iterator/callStack.jpg)

可以看出非递归模拟递归的本质就在于程序控制流的模拟，这里的控制流并不是调用栈的模拟，而是计算顺序的模拟（体现在上面的例子中就是对节点值的访问顺序），非递归模拟代码就是用栈中的节点来模拟访问的次序

既然现在我们已经能够用栈来模拟控制流，这也意味着对程序的遍历的控制已经完全受制于我们（这里的完全受制是逻辑上的，屏蔽底层编译的细节），我们终于摆脱了了call stack :)

现在我们可以肆意的操控我们的遍历程序,接下来用闭包保存栈，每次next调用pop一次来实现迭代  
```javascript
function makeTreeIterator(node){
	let controlStack = [];

	((function InorderIterator(currNode) {
		// 将当前节点的所有左子节点入栈
		while (currNode) {
			controlStack.push(currNode);
			currNode = currNode.left;
		}
	})(node))

	return {
		next: function(){
			if (controlStack.length) {
				// 取出当前节点
				let top = controlStack.pop();

				if (top.right) {
					let currNode = top.right;

					// 将当前节点的右子节点的所有左子节点压栈
					while (currNode) {
						controlStack.push(currNode);
						currNode = currNode.left;
					}
				}

				return {value: top.value, done: false};
			} else {
				return {done: true};
			}
		}
	}
}
```

拉出迭代器遛遛  
```javascript
let tree = {
	value: 5,
	left: {
		value: 4,
		left: '',
		right: ''
	},
	right: {
		value: 8,
		left: {
			value: 6,
			left: '',
			right: ''
		},
		right: ''
	}
}

let test = makeTreeIterator(tree),result = [];

for(let i = test.next(); i.done !== true; i=test.next()) {
	if (i.value < 5) {
		result.push(i.value);
	}
}
console.log(result); // [4]
```

还有一种实现迭代器的方法就是使用continuation来实现控制反转啦&#126;  
下一篇博客会去讲解如何用continuation来实现迭代器，这里先用ES6的generator来预热  
```javascript
function* inOrder(node) {
	let x;

	if (node) {
		for (x of inOrder(node.left)) {
			yield x;
		}
		yield node.value;
		for (x of inOrder(node.right)) {
			yield x;
		}
	}
}

let test = inOrder(tree),result = [];
for(i of test) {
	if (i < 5) {
		result.push(i);
	}
}
console.log(result); // [4]
```

### 4 小结

基于栈可以模拟控制流，这也是栈式虚拟机的思想，堆栈处理不愧是计算机领域强劲的技术，从迭代引申到控制流，看来“取指-执行”模型不仅仅用在CPU啊。

### 5 Reference

[二叉树迭代器算法](https://coolshell.cn/articles/9886.html/comment-page-1#comments)  
[What is an iterator?](http://effbot.org/pyfaq/what-is-an-iterator.htm)  
[Folder Iterator Continuation Token Recursive Loop](https://stackoverflow.com/questions/49052473/folder-iterator-continuation-token-recursive-loop)  
[generators-iterators-control-and-continuations/](http://gallium.inria.fr/blog/generators-iterators-control-and-continuations/)
