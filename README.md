#  Poker脚本说明

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

基本的思路是在实现一个c到python的类型的转换器，将python object转换为c对应的类型，就是在c函数再wrap一层便于调用，然后将其包装成一个module，module的method需要提前定义好。基本套路如下，以后可能还要用到，这里记录一下，另外PyArg_ParseTuple()的变量下次使用的时候查一下官方文档就好。

``` c

static PyObject *_currentPlayer(PyObject *self, PyObject *args)
{
    char *_msg;
    char *_lastMsg;

    double res;
    if (!PyArg_ParseTuple(args, "ss", &_msg, &_lastMsg))
    {
        return NULL;
    }
    res = ifCurrentPlayer(_msg, _lastMsg);
    return PyFloat_FromDouble(res);
}

static PyMethodDef GameSolverMethods[] = {
    {"getReward",
     _getReward,
     METH_VARARGS,
     ""},
    {"ifCurrentPlayer",
     _currentPlayer,
     METH_VARARGS,
     ""},
    {NULL, NULL, 0, NULL}};
static struct PyModuleDef GameSolver = {

    PyModuleDef_HEAD_INIT,
    "GameSolver",
    NULL,
    -1,
    GameSolverMethods};
PyMODINIT_FUNC PyInit_GameSolver(void)
{
    PyObject *m;
    m = PyModule_Create(&GameSolver);
    if (m == NULL)
    {
        return NULL;
    }
    return m;
}

```

#### 二： 关于之前的“神奇”bug
其实现在想清楚了也不觉得奇怪了。。。错误的原因是socket可能一次性接收多个MATCHSTATE，然后dealer先发送的MATCHSTATE就会被读取，如果读取的结果刚好不是自己的动作时机，就会等待dealer发送新的MATCHSTATE，但是dealer不会再发送，所以就陷入互相等待的过程。

知道了这一点解决方法就是改变解析接收的MATCHSTATE的方式，让它可以处理一个string包含多个MATCHSTATE的情况，然后一条条执行即可。

### TODO LIST

现在的状态是程序是可用的，能用于训练，局限性在必须要使用Dealer的log文档。其次，局限的地方还有就是程序的健壮性不足，退出脚本的方法不正确。

* 更改退出方式
* 增加soket的异常处理
* 清空无效代码
* 试图更改使用dealer的log文件的必要
* 适应算法代码加入消息到state的方法

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
