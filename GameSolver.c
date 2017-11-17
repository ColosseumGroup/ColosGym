#include <Python.h>
#include <assert.h>
#include "game.h"
#include <stdio.h>
//////////////////////////////////////////////////////////////////////////////////这里开始
//初始化Game，原来的代码是去解析.game文档
//这里我为了简化，写手工输入

static Game* game = NULL;

//完成了一些初始化还有调用 别人在game.c写的valueOfState
double getReward(const char *msg, const char *lastMsg,
                 const int episode, const int playerNum, int fix_table)
{
    //这里有点乱。。。。不用这个了
    int playerSeat,seatToPlayer,len;
    MatchState state;
    readMatchState(lastMsg, game, &state);
    len = readMatchState(msg, game, &state);
    assert(len > 0);
    if (!fix_table)
    {
        playerSeat = ( playerNum+episode) % game->numPlayers;
    }
    seatToPlayer = state.viewingPlayer;
    
    double res = valueOfState(game, &state.state, seatToPlayer);
    return res;
}

//同样是调用别人在ExamplePlayer里面写的currentplayer
static double ifCurrentPlayer(const char *msg)
{
    MatchState state;
    int len = readMatchState(msg, game, &state);
    if (len < 0)
    {
        return -99.0;
    }
    if (stateFinished(&state.state))
    {
        return 3.0;
    }
    if (state.viewingPlayer != currentPlayer(game, &state.state))
    {
        return -2.0;
    }
    else
    {
        return 2.0;
    }
}
static void initGame(const char *path)
{
    if(game == NULL){
        FILE *file = fopen(path,"r");
        game = readGame(file);
    }
}
//下面是一些包装成python可调用的形式的套路
static PyObject *_getReward(PyObject *self, PyObject *args)
{
    char *_msg;
    char *_lastMsg;
    double res;
    int _fix = 0;
    int _epi,_pNum;

    if (!PyArg_ParseTuple(args, "ssii|i", &_msg, &_lastMsg, &_epi,&_pNum,&_fix))
    {
        return NULL;
    }
    res = getReward(_msg, _lastMsg,_epi,_pNum,_fix);
    return PyFloat_FromDouble(res);
}
static PyObject *_initGame(PyObject *self, PyObject *args)
{
    char *path;
    if (!PyArg_ParseTuple(args, "s", &path))
    {
        return NULL;
    }
    initGame(path);
    return PyFloat_FromDouble(1.0);
}
static PyObject *_currentPlayer(PyObject *self, PyObject *args)
{
    char *_msg;

    double res;
    if (!PyArg_ParseTuple(args, "s", &_msg))
    {
        return NULL;
    }
    res = ifCurrentPlayer(_msg);
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
     {"initGame",
     _initGame,
     METH_VARARGS,
     ""},
    {NULL, NULL, 0, NULL}};
struct PyModuleDef GameSolver = {

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

/*PyMODINIT_FUNC init_getReward_function(){
    Py_InitModule("getReward",_getReward_functionMethods);
}*/
