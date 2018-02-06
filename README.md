#  ColosGym

## 整体实现

* 游戏服务使用ACPC的代码，以及在此基础上改出来的其他游戏服务
* 在ColosGym增加支持的游戏，需要从BaseGame中继承，实现父类的所有虚函数即可使用
* Actor是对所有客户端和服务端的交互的抽象，已提供类似与OPENAI的Gym类似的API
* 对于有特别需求的用户，建议按照游戏传输字符串的形式自行继承BaseGame继承实现子类
* 当然，也可以研究服务端的交互方式来使用socket自行实现所有交互逻辑

## Poker Section

### 脚本使用：

这个东西是用来链接另一个PokerServer进行算法训练的。

### 实现说明：

#### 规则

使用规则参照游戏定义文件(.game), API用法参照alg4together.py

#### 三： 用法

在程序中的用法参照alg.py，应该注意的是

* 由于存在可能一开始，对手先决策，但是对手的决策是弃牌，导致刚reset的game马上就返回结束和reward，这一点和Gym有区别但是区别不大

使用的时候，需要在命令行中输入3个参数，从一个案例来说明,从测试的数据看

``` python
        port = 18374
        logpath = "/home/goodman/POKER/project_acpc_server_v1.0.41/project_acpc_server/match1.log"
        playerName = "Bob"

```
* 第一个是端口，Dealer会提供
* 第二个是在Dealer目录下，也就是project_acpc_server目录下会有一个dealer提供的log文件
* 第三个是player的名称，需要与端口的顺序向对应

另外说一下dealer的server的使用方法,命令行中输入一下
``` 
$ ./dealer matchName holdem.limit.2p.reverse_blinds.game 1000 0 Alice Bob
```

* 第一个是log文件的名称，对应的会在dealer的目录下，生成一个matchName.log的文件，其中记录对局信息
* 第二个参数是游戏的参数，在这个文件中有定义，具体可以打开这个文件看一下
* 对局次数
* 那个0，现在不需要设置，同样写0就好
* 后面两个就是名字了

输入上面的命令后，命令行会得到：
```
16177 48777
# name/game/hands/seed matchName holdem.limit.2p.reverse_blinds.game 1000 0
#--t_response 10000
#--t_hand 600000
#--t_per_hand 6000
```
要注意的是，这里的两个端口号是在后面的脚本需要的，16177对应Alice，48777对应Bob。

### 关于游戏的类型

默认是**holdem.limit.2p.reverse_blinds**，具体定义如下：
``` txt
GAMEDEF
limit
numPlayers = 2
numRounds = 4
blind = 10 5
raiseSize = 10 10 20 20
firstPlayer = 2 1 1 1
maxRaises = 3 4 4 4
numSuits = 4
numRanks = 13
numHoleCards = 2
numBoardCards = 0 3 1 1
END GAMEDEF
```

如果需要修改游戏类型，需要在GameSolver.c里面重新修改getGame()的参数。修改后重新使用setup.py重新打包。即可使用。


## Renju Section

### Rules

* 第一个玩家执黑先行，然后按照局次轮换先手。
* 越过棋盘的范围，在已有棋子上下子，都会导致失败
* 胜利reward为1，失败为0
* 其他使用方法，参照renju_examples.py

### Examples
* Oberserve
``` shell
[[ 1.  0.  1.  0.  0.  0.  0.  1.  0.  0.  0.  1.  0.  2.  1.]
 [ 0.  0.  0.  0.  0.  0.  1.  0.  0.  0.  0.  0.  0.  2.  2.]
 [ 2.  0.  0.  0.  0.  0.  2.  0.  2.  2.  1.  0.  1.  2.  1.]
 [ 0.  1.  0.  2.  0.  2.  2.  1.  0.  0.  2.  2.  0.  0.  2.]
 [ 1.  0.  1.  0.  0.  0.  0.  2.  1.  0.  1.  0.  1.  2.  0.]
 [ 0.  1.  1.  0.  0.  0.  0.  1.  0.  0.  1.  0.  1.  0.  1.]
 [ 0.  0.  0.  0.  1.  0.  0.  2.  1.  0.  0.  2.  0.  2.  1.]
 [ 2.  0.  2.  0.  0.  1.  0.  2.  0.  0.  0.  0.  0.  0.  0.]
 [ 1.  2.  0.  2.  1.  0.  0.  0.  0.  1.  1.  0.  0.  0.  1.]
 [ 0.  0.  1.  2.  0.  0.  2.  0.  0.  0.  0.  1.  2.  0.  0.]
 [ 0.  0.  1.  2.  2.  1.  0.  0.  2.  2.  1.  0.  2.  2.  2.]
 [ 0.  0.  0.  2.  2.  1.  0.  0.  1.  0.  1.  0.  0.  0.  0.]
 [ 0.  0.  0.  0.  0.  1.  0.  2.  0.  0.  0.  0.  0.  2.  0.]
 [ 0.  0.  0.  0.  2.  0.  0.  0.  1.  1.  2.  2.  0.  0.  0.]
 [ 0.  1.  1.  1.  2.  0.  0.  1.  2.  2.  2.  1.  0.  0.  2.]]
'''