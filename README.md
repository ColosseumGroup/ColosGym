#  Poker脚本说明

#### 脚本使用：

这个东西是用来链接另一个PokerServer进行算法训练的。

##### 一：引用说明

除了alg.py,player.py,testlog.py, setup.py和GameSolver.c是我自己写的，其他都是从Server上面复制的。这样做主要为了能够与Dealer的判断标准一致。其次将c包装成python，相对于直接使用python重写有速度快，避免重复代码工作的好处。就是比较难用。

#### 二：代码需求

* 1 完成动作操作
* 2 完成对Dealer传来的信息的接收
* 3 完成将信息解释为状态


