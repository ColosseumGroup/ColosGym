#  ColosGym

## Poker Section

#### 脚本使用：

这个东西是用来链接另一个PokerServer进行算法训练的。

##### 一：引用说明

除了alg.py,player.py,testlog.py, setup.py和GameSolver.c是我自己写的，其他都是从Server上面复制的。这样做主要为了能够与Dealer的判断标准一致。其次将c包装成python，相对于直接使用python重写有速度快，避免重复代码工作的好处。就是比较难用。

##### 二：代码需求

* 1 完成动作操作
* 2 完成对Dealer传来的信息的接收
* 3 完成将信息解释为状态

### 实现说明：

#### 一： c封装成python函数的套路

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

### 四：关于游戏的类型

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


###temp
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