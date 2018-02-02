#include <Python.h>
#include <assert.h>
#include "game.h"
#include <stdio.h>


static Game* game = NULL;  /*游戏定义，module初始化的时候被初始化*/


/*
暂时不用的GetReward
*/
static uint8_t playerToSeat(const Game *game, const uint8_t player0Seat,
                            const uint8_t player)
{
  return (player + player0Seat) % game->numPlayers;
}
double getReward(const char *msg, const int episode, const int playerNum, int fix_table)
{
    int player0Seat=0,len=0,result=0;
    MatchState state;
    len = readMatchState(msg, game, &state);
    assert(len > 0);
    if(!fix_table){
        player0Seat = (player0Seat+episode)%game->numPlayers;
    }
    for(int i = 0;i<game->numPlayers;++i)
    {
        if(playerToSeat(game,player0Seat,i)==playerNum){
            return valueOfState(game,&state.state,i);
        }
    }
    return 3.1415926;  // werid number for error。。。。
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
/*
模块初始化时，必须初始化，否则运算结果错误或异常
*/
static void initGame(const char *path)
{
    if(game == NULL){
        FILE *file = fopen(path,"r");
        game = readGame(file);
    }
}


//********下面是一些包装成python可调用的形式的套路**************


static PyObject *_getReward(PyObject *self, PyObject *args)
{
    char *_msg;
    char *_lastMsg;
    double res;
    int _fix = 0;
    int _epi,_pNum;

    if (!PyArg_ParseTuple(args, "sii|i", &_msg, &_epi,&_pNum,&_fix))
    {
        return NULL;
    }
    res = getReward(_msg, _epi, _pNum, _fix);
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
