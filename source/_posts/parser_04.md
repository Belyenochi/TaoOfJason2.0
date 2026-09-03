---
title: "从零开始的编译原理之旅----Parser篇(四)"
date: 2018-09-06 21:39:10
categories:
  - "编译原理"
tags:
  - "parser"
---

本篇主要阐述使用递归下降非回溯或回溯解析LL(1)文法，并比较两者优缺点

### 1 目录

本系列旨在学习各种parser思路及技巧，分为以下几个部分

1. [ 清晨入古寺—-论世间parser为何物](https://belyenochi.github.io/2018/08/28/parser_00/#more)
2. [ 初日照高林—-初探First集，Follow集 ](https://belyenochi.github.io/2018/09/03/parser_01/#more)
3. [ 曲径通幽处—-预测分析表的构建 ](https://belyenochi.github.io/2018/09/04/parser_02/#more)
4. [ 禅房花木深—-实现LL(1) parser ](https://belyenochi.github.io/2018/09/04/parser_06/#more)
5. [ 山光悦鸟性—-递归下降的两种实现 **\[本篇\]** ](https://belyenochi.github.io/2018/09/04/parser_06/#more)
6. 潭影空人心—-浅谈recursive ascent parser(SLR,LALR(1))
7. 万籁此俱寂—-parser combinator（从ohm.js源码说起）
8. 但余钟磬音—-反思与总结

### 2 什么是递归下降？

一个递归下降语法分析程序由一组过程组成，每个非终结符有一个对应的过程。程序的执行从开始符号对应的过程开始，如果这个过程扫描了整个输入串，它就停止执行并宣布语法分析成功完成。  
举一个直观的栗子：

```javascript
/*
	Grammar:
		S->cAd
		A->ab|a
*/

class compilerEngile {
	constructor(input) {
		// ...
	}
	
	compilerS() {
		// ...
	}

	compilerA() {
		// ...
	}

	run() {
		this.compilerS(); // Start !!!
	}
}
```

使用递归下降解析文法通俗的讲就是调用compilerS()根据函数调用是否成功（判断是否有非法字符串）且输入串是否完全匹配（是否有多余字符）来判断解析是否成功

\### 3 为什么使用递归下降解析LL（1）文法

上一章介绍了使用显式的维护一个stack来解析LL（1）文法，这种方法不如直接使用递归隐式的维护call stack来的直观，

本质上两者是等价的，唯一的区别是一个使用了系统的控制流一个自己构造控制流。

### 4 递归下降的预测分析（不带回溯）

这种递归下降属于递归下降中一种特殊的情况，不需要回溯的前提是LL（1）文法中每个非终结符的产生式不存在可以合并的左公因子,举个栗子：

```javascript
/*
	Grammar:
		S->sAd
		A->ab|c
*/

class compilerEngile {
	constructor(input) {
		// ...
	}
	
	compilerS() {
		eat('s');
		this.compilerA();
		eat('d');
	}

	compilerA() {
		if(this.input[cursor] === 'a') {
			eat('a');
			eat('b');
		} else if(this.input[cursor] === 'c') {
			eat('c');
		}
	}

	run() {
		this.compilerS(); // Start !!!
	}
}
```

代码如上，可以看出并不需要回溯，但是我们来分析一下之前定义的文法，

```
/*
	Grammar:
		S->sAd
		A->ab|a
*/
```

你会发现在解析A这个终结符的时候，hmmm，它第一个字母竟然是相同的也就是说没办法通过第一个字母来区分进入哪个分支，你可能会觉得这时候看第二个不就行了吗，是行了，不过因为这里的例子简单，看第二个字母的hack不会太丑，实际上编程语言的解析比这复杂很多，如果一直写，看第二个，看第三个的代码，那么代码会异常难看（我第一次不信邪的写出来过），还有同学可能会觉得这时候手动合并左公因子就行了嘛，嗯，这确实是一种方法，实际上一种更为优雅的方式就是**回溯**，通过回溯进入每一个分支看看是否正确。

### 5 递归下降的预测分析（带回溯）

```javascript
/*
	Grammar:
		S->sAd
		A->ab|a
*/

class compilerEngile {
	constructor(input) {
		// ...
	}
	
	compilerS() {
		eat('s');
		this.compilerA();
		eat('d');
	}

	compilerA() {
		if(firstOf(A) === 'a') {
			eat('a');
			eat('b');
		} else if(firstOf(A) === 'c') {
			eat('c');
		}
	}

	run() {
		this.compilerS(); // Start !!!
	}
}
```

这里又出现一个问题，假如进行回溯那么意味着要遍历所有分支，假如有n个非终结符，m个产生式，那么时间复杂度就是O（n\*m），这势必会降低效率，所以会采取一些优化，比如使用动态规划缓存结果，之后在讲解ohm.js源码的时候会详述 Incremental Packrat Parsing（递归下降回溯的优化），计算机科学嘛总是要在空间和时间之间做一个trade off。

到底使用表驱动的非递归预测分析算法还是采用递归下降就要看需求仁者见仁智者见智了。

### 6 递归下降的非回溯实现

```javascript
const assert = require('assert');

/*
	Grammar:
		S->sAd
		A->ab|c
*/
class compilerEngile {
    constructor(input) {
        this.input  = input;
        this.cursor = 0;
    }

    compilerS() {
        this.eat('s');
        this.compilerA();
        this.eat('d');
    }

    compilerA() {
        if(this.input[this.cursor] === 'a') {
            this.eat('a');
            this.eat('b');
        } else if(this.input[this.cursor] === 'c') {
            this.eat('c');
        }
    }

    run() {
        try {
            this.compilerS(); // Start !!!

            if (this.input.length !== this.cursor) { // deal with Extra unmatched characters
                throw Error(`unexpected Extra unmatched characters with ${this.input.slice(this.cursor)}` +
                 `at position ${this.cursor} in inputstring: ${this.input}`);
            }

            return true;
        } catch (e) {
            console.log(`Error: ${e.message}`);
            return false;
        }

    }

    eat(inputChar) {
        if (inputChar === this.input[this.cursor]) {
            this.cursor++;
        } else {
            throw Error(`unexpected match ${inputChar} with ${this.input} at position ${this.cursor}`);
        }
    }

}

// test
assert(new compilerEngile("sasbds").run() === false); // true
assert(new compilerEngile("sasbd").run()  === false); // true
assert(new compilerEngile("ssbds").run()  === false); // true
assert(new compilerEngile("sasds").run()  === false); // true
assert(new compilerEngile("sabds").run()  === false); // true
assert(new compilerEngile("sabd").run()   === true);  // true
```

### 7 递归下降的回溯实现

递归下降的DFS算法

```javascript
const assert = require('assert');

/*
	Grammar:
		S->sAd
		A->ab|c
*/
class compilerEngile {
    constructor(input) {
        this.input  = input;
        this.cursor = 0;
    }

    compilerS() {
        this.eat('s');
        this.compilerA();
        this.eat('d');
    }

    compilerA() {
        let save;

        return (save = this.saveCursor(this.cursor) , this.compilerA1()) ||
            (this.backtrack(save) , this.compilerA2());
    }

    compilerA1() {
        return this.eat('a') && this.eat('b');
    }

    compilerA2() {
        return this.eat('c');
    }

    run() {
        try {
            this.compilerS(); // Start !!!

            if (this.input.length !== this.cursor) { // deal with Extra unmatched characters
                throw Error(`unexpected Extra unmatched characters with ${this.input.slice(this.cursor)}` +
                    `at position ${this.cursor} in input string: ${this.input}`);
            }

            return true;
        } catch (e) {
            console.log(`Error: ${e.message}`);
            return false;
        }

    }

    // help function

    eat(inputChar) {
        if (inputChar === this.input[this.cursor]) {
            this.cursor++;

            return true;
        }

        return false;
    }

    backtrack(fn) {
        this.cursor = fn();
    }

    saveCursor(cursor) {
        return function() {
            return cursor;
        }
    }

}

// test
assert(new compilerEngile("sasbds").run() === false); // true
assert(new compilerEngile("sasbd").run()  === false); // true
assert(new compilerEngile("ssbds").run()  === false); // true
assert(new compilerEngile("sasds").run()  === false); // true
assert(new compilerEngile("sabds").run()  === false); // true
assert(new compilerEngile("sabd").run()   === true);  // true
```
