#include <Python.h>
#include <assert.h>
#include "game.h"
//////////////////////////////////////////////////////////////////////////////////这里开始
//初始化Game，原来的代码是去解析.game文档
//这里我为了简化，写手工输入
short getGame(Game *game)
{
    int ROUNDS = 2;
    int STACK = 1200;
    for (int c = 0; c < ROUNDS; ++c)
    {
        game->stack[c] = STACK;
    }

    game->bettingType = noLimitBetting;
    game->numPlayers = 2;
    game->numRounds = 2;
    ///////////////////////////////////
    game->firstPlayer[0] = 1;
    game->firstPlayer[1] = 1;
    // ///////////////////////////////////Ludec是无限注的
    // game->maxRaises[0] = 3;
    // game->maxRaises[1] = 4;
    // game->maxRaises[2] = 4;
    // game->maxRaises[3] = 4;
    ////////////////////////////////////
    game->numSuits = 2;
    game->numRanks = 3;
    game->numHoleCards = 1;
    /////////////////////////////
    game->blind[0] = 100;
    game->blind[1] = 100;
    /////////////////////
    game->raiseSize[0] = 10;
    game->raiseSize[1] = 10;
    game->raiseSize[2] = 20;
    game->raiseSize[3] = 20;
    ///////////////////////////
    game->numBoardCards[0] = 0;
    game->numBoardCards[1] = 1;
    //////////////////
    game->numHoleCards = 1;
    return 1;
}
//完成了一些初始化还有调用 别人在game.c写的valueOfState
double getReward(const char *msg, const char *lastMsg,
                 const int episode, const int playerNum, int fix_table)
{
    //这里有点乱。。。。不用这个了
    int playerSeat,seatToPlayer,len;
    MatchState state;
    Game *game;
    game = (Game *)malloc(sizeof(*game));
    getGame(game);
    readMatchState(lastMsg, game, &state);
    len = readMatchState(msg, game, &state);
    assert(len > 0);
    if (!fix_table)
    {
        playerSeat = ( playerNum+episode) % game->numPlayers;
    }
    seatToPlayer = state.viewingPlayer;
    
    double res = valueOfState(game, &state.state, seatToPlayer);
    free(game);
    return res;
}

//同样是调用别人在ExamplePlayer里面写的currentplayer
double ifCurrentPlayer(const char *msg, const char *lastMsg)
{

    Game *game;
    MatchState state;
    game = (Game *)malloc(sizeof(*game));
    getGame(game);
    readMatchState(lastMsg, game, &state);
    int len = readMatchState(msg, game, &state);
    if (len < 0)
    {
        return 3.0;
    }
    uint8_t currentP = currentPlayer(game, &state.state);
    free(game);
    if (stateFinished(&state.state))
    {
        return 3.0;
    }
    if (state.viewingPlayer != currentP)
    {
        return 2.0;
    }
    else
    {
        return -2.0;
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

/*PyMODINIT_FUNC init_getReward_function(){
    Py_InitModule("getReward",_getReward_functionMethods);
}*/
