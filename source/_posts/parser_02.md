---
title: "从零开始的编译原理之旅----Parser篇(二)"
date: 2018-09-04 20:53:18
categories:
  - "编译原理"
tags:
  - "parser"
---

### 1 目录

本系列旨在学习各种parser思路及技巧，分为以下几个部分

1. [ 清晨入古寺—-论世间parser为何物](https://belyenochi.github.io/2018/08/28/parser_00/#more)
2. [ 初日照高林—-初探First集，Follow集 ](https://belyenochi.github.io/2018/09/03/parser_01/#more)
3. [ 曲径通幽处—-预测分析表的构建 **\[本篇\]**](https://belyenochi.github.io/2018/09/04/parser_02/#more)
4. [ 禅房花木深—-实现LL(1) parser ](https://belyenochi.github.io/2018/09/04/parser_06/#more)
5. [ 山光悦鸟性—-递归下降的两种实现 ](https://belyenochi.github.io/2018/09/04/parser_06/#more)
6. 潭影空人心—-浅谈recursive ascent parser(SLR,LALR(1))
7. 万籁此俱寂—-parser combinator（从ohm.js源码说起）
8. 但余钟磬音—-反思与总结

### 2 什么是预测分析表

预测分析表是在语法分析中用于进行预测分析的数据结构，龙书上有比较详细的定义，在这里就举一个栗子来说明：

假定有如下文法：

    S -> F
    S -> (S + F)
    F -> a

它的预测分析表长这个样：

| 非终结符/终结符 | ( | ) | a | + | $ |
|---|---|---|---|---|---|
| S | S -> (S + F) | - | S -> F | - | - |
| F | - | - | F -> a | - | - |

假如这时我们要解析一个字符串”(a + a)”

1. 读入”(“
2. 查询预测分析表
3. 根据预测分析表结果，进入相应的产生式（也可称展开产生式）
4. 这里有两种等价的方式实现匹配 4.1 使用程序的调用栈递归进行预测分析，当程序正常结束且输入完全匹配时，语法分析成功 4.2 使用栈数据结构来非递归的预测分析，当栈为空且完全匹配时，语法分析成功

Tip:这里有同学可能会问，为啥总是能用非递归来模拟递归？  
其实在Forthan的年代，人们还木有意识到递归对于程序的用处，第一个倡导编程语言应该实现递归的就是大名鼎鼎的Dijkstra ，随着[Dijkstra的论文](https://dijkstrascry.com/node/4)发表，在 那之后的语言比如ALGOL 60便使用了call stack这个概念来实现递归，不过据说在forthan的年代（也就是50年代早期）IBM的机器还没有堆栈实现，并且机器很小，估计用了递归效率也够呛，不过递归的威力早在Church提出lambda calculus以及 Church encoding就已经显现出来了。

### 3 为什么需要预测分析表

其实你也可以不用实现预测分析表，预测分析表的本质就是对当前字符进行分支判断吗，只不过这分支比较多，然后你懂的代码写出来都是if-else，嵌套if-else，这一点都不优雅：（，所以我们需要预测分析表来驱动预测语义分析（这部分龙书语法分析部分讲的挺细）

### 4 实现预测分析表

```javascript
/**
 * Building LL(1) parsing table from First and Follow sets.
 *
 * by Dmitry Soshnikov <dmitry.soshnikov@gmail.com>
 * MIT Style License
 *
 * This diff is a continuation of what we started in the previous two diffs:
 *
 * Dependencies:
 *
 *   1. Actual LL Parser, that uses parsing table:
 *      https://gist.github.com/DmitrySoshnikov/29f7a9425cdab69ea68f
 *
 *   2. First and Follow sets construction:
 *      https://gist.github.com/DmitrySoshnikov/924ceefb1784b30c5ca6
 *
 * As we implemented in diff (1), LL Parser uses a parsing table. This
 * table is built based on First and Follow sets which we built in
 * the diff (2). In this diff we finishing constructing the parsing table
 * based on the data from previous analysis.
 *
 * The purpose of the parsing table is to tell which next production to use
 * based on the symbol on the stack, and the current symbol in the buffer.
 * As we said in (1), rows of the table are non-terminals, and columns are
 * terminals.
 *
 * Grammar:
 *
 *   1. S -> F
 *   2. S -> (S + F)
 *   3. F -> a
 *
 * Parsing table:
 *
 *   +------------------+
 *   |    (  )  a  +  $ |
 *   +------------------+
 *   | S  2  -  1  -  - |
 *   | F  -  -  3  -  - |
 *   +------------------+
 *
 * The rules for constructing the table are the following:
 *
 *   1. Scan all non-terminals in the grammar, and put their derivations under
 *      the columns which are in the First set of the RHS for this non-terminal.
 *
 *   2. If this non-terminal has `ε` (epsilon, "empty" symbol) as one of its
 *      derivations, then put the corresponding ε-derivation into the columns
 *      which are in the Follow set of this non-terminal.
 *
 * Let's see it on the implementation.
 */

// Special "empty" symbol.
let EPSILON = 'ε';

/**
 * Given a grammar builds a LL(1) parsing table based on the
 * First and Follow sets of this grammar.
 */
function buildParsingTable(grammar, firstSets, followSets) {
    let parsingTable = {};

    for (let k in grammar) {
        let production = grammar[k];
        let LHS = getLHS(production);
        let RHS = getRHS(production);
        let productionNumber = Number(k);

        // Init columns for this non-terminal.
        if (!parsingTable[LHS]) {
            parsingTable[LHS] = {};
        }

        // All productions goes under the terminal column, if
        // this terminal is not epsilon.
        if (RHS !== EPSILON) {
            getFirstSetOfRHS(RHS, firstSets).forEach(function(terminal) {
                parsingTable[LHS][terminal] = productionNumber;
            });
        } else {
            // Otherwise, this ε-production goes under the columns from
            // the Follow set.
            followSets[LHS].forEach(function(terminal) {
                parsingTable[LHS][terminal] = productionNumber;
            });
        }
    }

    return parsingTable;
}

/**
 * Given production `S -> F`, returns `S`.
 */
function getLHS(production) {
    return production.split('->')[0].replace(/\s+/g, '');
}

/**
 * Given production `S -> F`, returns `F`.
 */
function getRHS(production) {
    return production.split('->')[1].replace(/\s+/g, '');
}

/**
 * Returns First set of RHS.
 */
function getFirstSetOfRHS(RHS, firstSets) {

    // For simplicity, in this educational parser, we assume that
    // the first symbol (if it's a non-terminal) cannot produces `ε`.
    // Since in real parser, we need to get the First set of the whole RHS.
    // This means, that if `B` in the production `X -> BC` can be `ε`, then
    // the First set should of course include First(C) as well, i.e. RHS[1], etc.
    //
    // That is, in a real parser, one usually combines steps of building a
    // parsing table, First and Follow sets in one step: when a parsing table
    // needs the First set of a RHS, it's calculated in place.
    //
    // But here we just return First of RHS[0].
    //

    return firstSets[RHS[0]];
}

// Testing

// ----------------------------------------------------------------------
// Example 1 of a simple grammar, generates: a, or (a + a), etc.
// ----------------------------------------------------------------------

// We just manually define our First and Follow sets for a given grammar,
// see again diff (2) where we automatically generated these sets.

let grammar_1 = {
    1: 'S -> F',
    2: 'S -> (S + F)',
    3: 'F -> a',
};

// See https://gist.github.com/DmitrySoshnikov/924ceefb1784b30c5ca6
// for the sets construction.

let firstSets_1 = {
    'S': ['a', '('],
    'F': ['a'],
    'a': ['a'],
    '(': ['('],
};

let followSets_1 = {
    'S': ['$', '+'],
    'F': ['$', '+', ')'],
};

console.log(buildParsingTable(grammar_1, firstSets_1, followSets_1));

// Results:

// S: { a: 1, '(': 2 }
// F: { a: 3 }

// That corresponds to the following table:

// +------------------+
// |    (  )  a  +  $ |
// +------------------+
// | S  2  -  1  -  - |
// | F  -  -  3  -  - |
// +------------------+

// ----------------------------------------------------------------------
// Example 2, for the "calculator" grammar, e.g. (a + a) * a.
// ----------------------------------------------------------------------

let grammar_2 = {
    1: 'E -> TX',
    2: 'X -> +TX',
    3: 'X -> ε',
    4: 'T -> FY',
    5: 'Y -> *FY',
    6: 'Y -> ε',
    7: 'F -> a',
    8: 'F -> (E)',
};

// See https://gist.github.com/DmitrySoshnikov/924ceefb1784b30c5ca6
// for the sets construction.

let firstSets_2 = {
    'E': ['a', '('],
    'T': ['a', '('],
    'F': ['a', '('],
    'a': ['a'],
    '(': ['('],
    'X': ['+', 'ε'],
    '+': ['+'],
    'Y': ['*', 'ε'],
    '*': ['*'],
};

let followSets_2 = {
    'E': ['$', ')'],
    'X': ['$', ')'],
    'T': ['+', '$', ')'],
    'Y': ['+', '$', ')'],
    'F': ['*', '+', '$', ')'],
};

console.log(buildParsingTable(grammar_2,firstSets_2,followSets_2));

// Results:

// E: { a: 1, '(': 1 },
// X: { '+': 2, '$': 3, ')': 3 },
// T: { a: 4, '(': 4 },
// Y: { '*': 5, '+': 6, '$': 6, ')': 6 },
// F: { a: 7, '(': 8 }

// That corresponds to the following table:

// +---------------------+
// |    a  +  *  (  )  $ |
// +---------------------+
// | E  1  -  -  1  -  - |
// | X  -  2  -  -  3  3 |
// | T  4  -  -  4  -  - |
// | Y  -  6  5  -  6  6 |
// | F  7  -  -  8  -  - |
// +---------------------+
```

### 4 Reference

[parsing table](https://en.wikipedia.org/wiki/Parse_table)  
[Dijikstra’s Algorithm](chrome-extension://cdonnmffkdaoajfknoeeecmchibpmkmg/static/pdf/web/viewer.html?file=http%3A%2F%2Fwww.yorku.ca%2Fwalker%2Fmath2320%2FDijkstra.pdf)  
[DmitrySoshnikov gitst](https://gist.github.com/DmitrySoshnikov/644383a86b045a3a8ad3)
