---
title: "从零开始的编译原理之旅----Parser篇(一)"
date: 2018-09-03 23:32:19
categories:
  - "编译原理"
tags:
  - "parser"
---

### 1 目录

本系列旨在学习各种parser思路及技巧，分为以下几个部分

1. [ 清晨入古寺—-论世间parser为何物](https://belyenochi.github.io/2018/08/28/parser_00/#more)
2. [ 初日照高林—-初探First集，Follow集 **\[本篇\]**](https://belyenochi.github.io/2018/09/03/parser_01/#more)
3. [ 曲径通幽处—-预测分析表的构建 ](https://belyenochi.github.io/2018/09/04/parser_02/#more)
4. [ 禅房花木深—-实现LL(1) parser ](https://belyenochi.github.io/2018/09/04/parser_06/#more)
5. [ 山光悦鸟性—-递归下降的两种实现 ](https://belyenochi.github.io/2018/09/04/parser_06/#more)
6. 潭影空人心—-浅谈recursive ascent parser(SLR,LALR(1))
7. 万籁此俱寂—-parser combinator（从ohm.js源码说起）
8. 但余钟磬音—-反思与总结

### 1 何谓First集，何谓Follow集合

所谓First集就是你在根据非终结符推导产生式的依据，比如：

```
S -> aAb
A -> a | <epsilon>
```

在分析S这个非终结符的时候，判断进入S产生式就需要查看S产生式的第一个字符是否与输入字符串匹配，像上面例子中每个产生式可以从左往右推导，并且只需要一个前看字符就可以判断进入哪个产生式，我们就说它是LL（1）文法,实际上first集是递归下降分析过程中使用的一种技术，通过对前看字符的预测分析（predicitive parsing）可以消除对非终结符解析的二义性，那么为啥还需要follow集呢，答案是可能存在相同的First集，比如：

```
S -> aEb
E -> 'a' | ε
```

加入我们要解析字符串”ab”，从S（Start）开始，a（匹配），E（匹配中），咦，E的First集没有产生式为终结符’b’啊，难道我就要抛出一个解析失败的异常吗？兄弟别急，如果非终结符的产生式包含了ε，那么这时候就要查看Follow(E),此处的Follow(E) = {b},这时文法解析器看到b match follow(E)就安心的在E这个终结符处选择了ε这个产生式，接着S的产生式匹配b，整个字符串匹配成功：）。

这里有同学可能会好奇为啥平白无故的我定义一个非终结符E生成产生式ε呢？  
我们来看看上面的文法没有使用ε（表示空）定义的情况：

```
S -> Sb
```

总结一下First集和Follow集的使用：  
First集用来做分支预测，follow集用来出来非终结符中含有ε（空）的情况。  
对与LL（1）文法一种简单有效的解析手法是使用递归下降，所谓的递归下降就是将每一个非终结符对应一个解析函数。举个栗子

```javascript
function S() {
	eat('a')
	E()
	eat('b')
}

function E() {
	if(First('a').indexOf(input) !== -1) {
		eat('a');
	} else if (Follow(E).indexOf(input) !== -1) {
		eat('ε');
	}
}
```

是不是很简单粗暴，如果你没有ε代码就会写成这样

```javascript
function S() {
	S()
	eat('b')
}
```

这就是左递归，调用栈很快就满了不是，所以我们要消除左递归就引入了ε

### 2 如何构造First集，Follow集合

#### 2.1 first集的构造

- If X is a terminal then First(X) is just X!
- If there is a Production X → ε then add ε to first(X)
- If there is a Production X → Y1Y2..Yk then add first(Y1Y2..Yk) to first(X)
- First(Y1Y2..Yk) is either
  - First(Y1) (if First(Y1) doesn’t contain ε)
  - OR (if First(Y1) does contain ε) then First (Y1Y2..Yk) is everything in First(Y1) as well as everything in First(Y2..Yk)
  - If First(Y1) First(Y2)..First(Yk) all contain ε then add ε  
    to First(Y1Y2..Yk) as well.

#### 2.2 follow集的构造

- First put $ (the end of input marker) in Follow(S) (S is the start symbol)
- If there is a production A → aBb, (where a can be a whole string) then everything in FIRST(b) except for ε is placed in FOLLOW(B).
- If there is a production A → aB, then everything in FOLLOW(A) is in FOLLOW(B)
- If there is a production A → aBb, where FIRST(b) contains ε, then everything in FOLLOW(A) is in FOLLOW(B)

#### 2.3实例讲解

首先定义一组Grammar

```
The Grammar

E → TE'

E' → +TE'

E' → ε

T → FT'

T' → *FT'

T' → ε

F → (E)

F → id
```

![](/images/parser_01/1.png)  
![](/images/parser_01/2.png)  
![](/images/parser_01/3.png)

以下为对first集合和follow集求解的代码实现

```javascript
// Special "empty" symbol.
let EPSILON = "ε";
/**
 * Rules for First Sets
 *
 * - If X is a terminal then First(X) is just X!
 * - If there is a Production X → ε then add ε to first(X)
 * - If there is a Production X → Y1Y2..Yk then add first(Y1Y2..Yk) to first(X)
 * - First(Y1Y2..Yk) is either
 *     - First(Y1) (if First(Y1) doesn't contain ε)
 *     - OR (if First(Y1) does contain ε) then First (Y1Y2..Yk) is everything
 *       in First(Y1) <except for ε > as well as everything in First(Y2..Yk)
 *     - If First(Y1) First(Y2)..First(Yk) all contain ε then add ε
 *       to First(Y1Y2..Yk) as well.
 */

function buildFirstSets(grammar, Sets) {
  return buildSet(firstOf, grammar, Sets, 0);
}

function firstOf(symbol, firstSets) {

  // A set may already be built from some previous analysis
  // of a RHS, so check whether it's already there and don't rebuild.
  if (firstSets[symbol]) {
    return firstSets[symbol];
  }

  // Else init and calculate.
  let first = firstSets[symbol] = {};

  // If it's a terminal, its first set is just itself.
  if (isTerminal(symbol)) {
    first[symbol] = true;
    return firstSets[symbol];
  }

  let productionsForSymbol = getProductionsForSymbol(symbol,grammar);
  for (let k in productionsForSymbol) {
    let production = getRHS(productionsForSymbol[k]);

    for (let i = 0; i < production.length; i++) {
      let productionSymbol = production[i];

      // Epsilon goes to the first set.
      if (productionSymbol === EPSILON) {
        first[EPSILON] = true;
        break;
      }

      // Else, the first is a non-terminal,
      // then first of it goes to first of our symbol
      // (unless it's an epsilon).
      let firstOfNonTerminal = firstOf(productionSymbol, firstSets);

      // If first non-terminal of the RHS production doesn't
      // contain epsilon, then just merge its set with ours.
      if (!firstOfNonTerminal[EPSILON]) {
        merge(first, firstOfNonTerminal);
        break;
      }

      // Else (we got epsilon in the first non-terminal),
      //
      //   - merge all except for epsilon
      //   - eliminate this non-terminal and advance to the next symbol
      //     (i.e. don't break this loop)
      merge(first, firstOfNonTerminal, [EPSILON]);
      // don't break, go to the next `productionSymbol`.
    }
  }

  return first;
}

/**
 * We have the following data structure for our grammars:
 *
 * let grammar = {
 *   1: 'S -> F',
 *   2: 'S -> (S + F)',
 *   3: 'F -> a',
 * };
 *
 * Given symbol `S`, the function returns `S -> F`,
 * and `S -> (S + F)` productions.
 */
function getProductionsForSymbol(symbol,grammar) {
  let productionsForSymbol = {};
  for (let k in grammar) {
    if (grammar[k][0] === symbol) {
      productionsForSymbol[k] = grammar[k];
    }
  }
  return productionsForSymbol;
}

/**
 * Given production `S -> F`, returns `S`.
 */
function getLHS(production) {
 */
function getLHS(production) {
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
 * Rules for Follow Sets
 *
 * - First put $ (the end of input marker) in Follow(S) (S is the start symbol)
 * - If there is a production A → aBb, (where a can be a whole string)
 *   then everything in FIRST(b) except for ε is placed in FOLLOW(B).
 * - If there is a production A → aB, then everything in
 *   FOLLOW(A) is in FOLLOW(B)
 * - If there is a production A → aBb, where FIRST(b) contains ε,
 *   then everything in FOLLOW(A) is in FOLLOW(B)
 */

function buildFollowSets(grammar, Sets) {
  return buildSet(followOf,grammar, Sets, 1);
}

function followOf(symbol, firstSets, followSets) {

  // If was already calculated from some previous run.
  if (followSets[symbol]) {
    return followSets[symbol];
  }

  // Else init and calculate.
  let follow = followSets[symbol] = {};

  // Start symbol always contain `$` in its follow set.
  if (symbol === START_SYMBOL) {
    follow['$'] = true;
  }

  // We need to analyze all productions where our
  // symbol is used (i.e. where it appears on RHS).
  let productionsWithSymbol = getProductionsWithSymbol(symbol);
  for (let k in productionsWithSymbol) {
    let production = productionsWithSymbol[k];
    let RHS = getRHS(production);

    // Get the follow symbol of our symbol.
    let symbolIndex = RHS.indexOf(symbol);
    let followIndex = symbolIndex + 1;

    // We need to get the following symbol, which can be `$` or
    // may contain epsilon in its first set. If it contains epsilon, then
    // we should take the next following symbol: `A -> aBCD`: if `C` (the
    // follow of `B`) can be epsilon, we should consider first of `D` as well
    // as the follow of `B`.

    while (true) {

      if (followIndex === RHS.length) { // "$"
        let LHS = getLHS(production);
        if (LHS !== symbol) { // To avoid cases like: B -> aB
          merge(follow, followOf(LHS, followSets, firstSets));
        }
        break;
      }

      let followSymbol = RHS[followIndex];

      // Follow of our symbol is anything in the first of the following symbol:
      // followOf(symbol) is firstOf(followSymbol), except for epsilon.
      let firstOfFollow = firstOf(followSymbol, firstSets);

      // If there is no epsilon, just merge.
      if (!firstOfFollow[EPSILON]) {
        merge(follow, firstOfFollow);
        break;
      }

      merge(follow, firstOfFollow, [EPSILON]);
      followIndex++;
    }
  }

  return follow;
}

function buildSet(builder, grammar, Sets, index) {
  for (let k in grammar) {
    builder(grammar[k][0], ...Sets);
  }

  // 0 stand for first Set 1 stands for follow Set
  return Sets[index];
}

/**
 * Finds productions where a non-terminal is used. E.g., for the
 * symbol `S` it finds production `(S + F)`, and for the symbol `F`
 * it finds productions `F` and `(S + F)`.
 */
function getProductionsWithSymbol(symbol) {
  let productionsWithSymbol = {};
  for (let k in grammar) {
    let production = grammar[k];
    let RHS = getRHS(production);
    if (RHS.indexOf(symbol) !== -1) {
      productionsWithSymbol[k] = production;
    }
  }
  return productionsWithSymbol;
}

function isTerminal(symbol) {
  return !/[A-Z]/.test(symbol);
}

function merge(to, from, exclude) {
  exclude || (exclude = []);
  for (let k in from) {
    if (exclude.indexOf(k) === -1) {
      to[k] = from[k];
    }
  }
}

function printGrammar(grammar) {
  console.log('Grammar:\n');
  for (let k in grammar) {
    console.log('  ', grammar[k]);
  }
  console.log('');
}

function printSet(name, set) {
  console.log(name + ': \n');
  for (let k in set) {
    console.log('  ', k, ':', Object.keys(set[k]));
  }
  console.log('');
}

// Testing

// --------------------------------------------------------------------------
// Example 1 of a simple grammar, generates: a, or (a + a), etc.
// --------------------------------------------------------------------------

let grammar = {
  1: 'S -> F',
  2: 'S -> (S + F)',
  3: 'F -> a',
};

let START_SYMBOL = 'S';

printGrammar(grammar);

printSet('First sets', buildFirstSets(grammar, [{}]));

printSet('Follow sets', buildFollowSets(grammar, [buildFirstSets(grammar, [{}]),{}]));

// Results:

// Grammar:
//
//    S -> F
//    S -> (S + F)
//    F -> a
//
// First sets:
//
//    S : [ 'a', '(' ]
//    F : [ 'a' ]
//    a : [ 'a' ]
//    ( : [ '(' ]
//
// Follow sets:
//
//    S : [ '$', '+' ]
//    F : [ '$', '+', ')' ]

// --------------------------------------------------------------------------
// Example 2 of a "calculator" grammar (with removed left recursion, which
// is replaced with a right recursion and epsilons), it generates language
// for e.g. (a + a) * a.
// --------------------------------------------------------------------------

let grammar = {
  1: 'E -> TX',
  2: 'X -> +TX',
  3: 'X -> ε',
  4: 'T -> FY',
  5: 'Y -> *FY',
  6: 'Y -> ε',
  7: 'F -> a',
  8: 'F -> (E)',
};

let START_SYMBOL = 'E';

printGrammar(grammar);

printSet('First sets', buildFirstSets(grammar, [{}]));

printSet('Follow sets', buildFollowSets(grammar, [buildFirstSets(grammar, [{}]),{}]));

// Results:

// Grammar:
//
//    E -> TX
//    X -> +TX
//    X -> ε
//    T -> FY
//    Y -> *FY
//    Y -> ε
//    F -> a
//    F -> (E)
//
// First sets:
//
//    E : [ 'a', '(' ]
//    T : [ 'a', '(' ]
//    F : [ 'a', '(' ]
//    a : [ 'a' ]
//    ( : [ '(' ]
//    X : [ '+', 'ε' ]
//    + : [ '+' ]
//    Y : [ '*', 'ε' ]
//    * : [ '*' ]
//
// Follow sets:
//
//    E : [ '$', ')' ]
//    X : [ '$', ')' ]
//    T : [ '+', '$', ')' ]
//    Y : [ '+', '$', ')' ]
//    F : [ '*', '+', '$', ')' ]
```

代码部分参考了[DmitrySoshnikov](https://github.com/DmitrySoshnikov)的parser

### 3 Reference

[compiler-design-first-in-syntax-analysis](compiler-design-first-in-syntax-analysis)  
[compiler-design-why-first-and-follow](compiler-design-why-first-and-follow)
