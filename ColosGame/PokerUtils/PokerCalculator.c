#include <Python.h>
#include <assert.h>
#include <stdio.h>
#include"evalHandTables.h"
#define NUMCARDS 7

#define PRIVATE_CARD 2
#define MAX_SUITS 4
#define MAX_RANKS 13

#define rankOfCard( card ) ((card)/MAX_SUITS)
#define suitOfCard( card ) ((card)%MAX_SUITS)

static char suitChars[MAX_SUITS + 1] = "cdhs";
static char rankChars[MAX_RANKS + 1] = "23456789TJQKA";
int readCard(const char *string, uint8_t *card)
{
    char *spos;
    uint8_t rank,suit;

    if (string[0] == 0)
        return -1;
    spos = strchr(rankChars,toupper(string[0]));
    if (spos == NULL)
        return -1;
    rank = spos - rankChars;  // relative position

    if (string[1] == 0)
        return -1;   // one card must have two char to represent
    spos = strchr(suitChars, tolower(string[1]));
    if (spos == NULL)
        return -1;
    suit = spos - suitChars;
    *card = rank*MAX_SUITS + suit;

    return 2;  // read two card
}

int readCards(const char *string, const int maxCards,
              uint8_t *cards)
{
    int i, c, r;

    c = 0;
    for (i = 0; i < maxCards; ++i)
    {
        r = readCard(&string[c], &cards[i]);
        c += r;
    }
    if(c/2 != maxCards)   // 读的牌数与用户指定不一致，错误！
        return -1;
    else
        return i;   // 完成的牌的数量
}

int rankCardsetWithCardArray(const uint8_t *cardArray, const int numCards)
{
    int i;
    Cardset c = emptyCardset();

    for (i = 0; i < numCards; ++i)
    {
        addCardToCardset(&c, suitOfCard(cardArray[i]), rankOfCard(cardArray[i]));
    }
    return rankCardset(c);
}
double estimateWithNPublicArray(uint8_t* publicCardArray, uint8_t* privateCardArray, const int N){
    int i,j,k,myRank,possibleRank;
    int lose,win;
    uint8_t same_flag;
    win = 0;lose=0;same_flag = 0;
    myRank = rankCardsetWithCardArray(privateCardArray, N + PRIVATE_CARD);
    for (i = 0; i < MAX_RANKS*MAX_SUITS; i++)
    {
        for (k = 0; k < N; k++)
        {
            if (i == publicCardArray[k]){
                same_flag=1;
                break;
            }
        }
        if(same_flag){
            same_flag =0;
            continue;
        }
        for (j = i + 1; j < MAX_RANKS*MAX_SUITS; j++)
        {
            for (k = 0; k < N; k++)
            {
                if (j == publicCardArray[k]){
                    same_flag=1;
                    break;
                }
            }
            if(same_flag)
            {
                same_flag = 0;
                continue;
            }
            publicCardArray[N] = i;
            publicCardArray[N + 1] = j;
            possibleRank = rankCardsetWithCardArray(publicCardArray, N + PRIVATE_CARD);
            if (possibleRank > myRank)
                lose++;
            else
                win++;
        }
    }
    return (double)(win)/(win+lose);
        
} 

double estimate1UnshowedArray(uint8_t* publicCardArray, uint8_t* privateCardArray, const int pbcN){
    int i,k,publicCaseCounter;
    double winningRate;
    const int unPbcN = 1;
    uint8_t same_flag;
    winningRate = 0.0;
    publicCaseCounter = 0;
    same_flag = 0;
    for (i = 0; i < MAX_RANKS*MAX_SUITS; i++)
    {   
        if(i == privateCardArray[pbcN+unPbcN]||i == privateCardArray[pbcN+unPbcN+1])
        {
            same_flag = 1;
        }
        else
        {
            for (k = 0; k < pbcN; k++)
                {
                    if (i == publicCardArray[k])
                    {
                        same_flag=1;
                        break;
                    }
                }
        }
        
        if(same_flag)
        {
            same_flag =0;
            continue;
        }
        publicCardArray[pbcN] = i;
        privateCardArray[pbcN] = i;
        winningRate += estimateWithNPublicArray(publicCardArray, privateCardArray,pbcN+unPbcN);
        publicCaseCounter ++;
    }
    return winningRate / publicCaseCounter;
}
double estimateKUnshowedArray(uint8_t* publicCardArray, uint8_t* privateCardArray, const int pbcN, const int k){
    int i,j;
    int publicCaseCounter;
    uint8_t same_flag;
    double winningRate;

    publicCaseCounter = 0;
    same_flag=0;
    winningRate = 0.0;
    for (i = 0; i < MAX_RANKS*MAX_SUITS; i++)
    {   
        if(i == privateCardArray[pbcN+k]||i == privateCardArray[pbcN+k+1]){
            same_flag = 1;
        }else{
            for (j = 0; j < pbcN; j++)
                {
                    if (i == publicCardArray[j]){
                        same_flag=1;
                        break;
                    }
                }
        }
        
        if(same_flag){
            same_flag =0;
            continue;
        }
        
        publicCardArray[pbcN] = i;
        privateCardArray[pbcN] = i;
        if(k==2)
        {
            winningRate += estimate1UnshowedArray(publicCardArray, privateCardArray,pbcN+1);
        }
        else if(k>2)
        {
            winningRate += estimateKUnshowedArray(publicCardArray,privateCardArray,pbcN+1, k-1);
        }
        else
        {
            winningRate = -100;
        }
        publicCaseCounter++;
    }
    return winningRate / publicCaseCounter;
}
/* 这里胜率是在当前公共牌下，对对手所有可能的手牌作出的估计，不考虑未出现的公共牌 */
double estimateWithNPublic(const char *msg, const char *privateC, const int N)
{
    int i;
    double winningRate;
    const int publicCardSize = N;
    const int privateCardSize = PRIVATE_CARD;


    uint8_t *publicCardArray = (uint8_t *)malloc((N + PRIVATE_CARD) * sizeof(uint8_t));
    readCards(msg, publicCardSize, publicCardArray);
    uint8_t *privateCardArray = (uint8_t *)malloc((N + PRIVATE_CARD) * sizeof(uint8_t));
    for (i = 0; i < publicCardSize; i++)
        privateCardArray[i] = publicCardArray[i];
    readCards(privateC, privateCardSize, privateCardArray + publicCardSize);

    winningRate = estimateWithNPublicArray(publicCardArray,privateCardArray,N);

    free(publicCardArray);
    free(privateCardArray);
    return winningRate;
}
double estimate1Unshowed(const char *msg, const char*privateC, const int pbcN){
    double winningRate;
    int i;
    const int unPbcN = 1;
    winningRate = 0.0;
    uint8_t *publicCardArray = (uint8_t *)malloc(( pbcN + unPbcN + PRIVATE_CARD) * sizeof(uint8_t));
    readCards(msg, pbcN, publicCardArray);
    uint8_t *privateCardArray = (uint8_t *)malloc(( pbcN + unPbcN + PRIVATE_CARD) * sizeof(uint8_t));
    for (i = 0; i < pbcN; i++)
        privateCardArray[i] = publicCardArray[i];
    readCards(privateC, PRIVATE_CARD, privateCardArray + pbcN + unPbcN);
    winningRate = estimate1UnshowedArray(publicCardArray, privateCardArray,pbcN);
    free(publicCardArray);
    free(privateCardArray);
    return winningRate;
}
/* 这里的胜率是考虑了未出现的公共牌以及对手的手牌计算的胜率 */
double estimate2Unshowed(const char *msg, const char *privateC, const int pbcN)
{
    double winningRate;
    int i;
    const int unPbcN = 2;
    winningRate = 0.0;
    uint8_t *publicCardArray = (uint8_t *)malloc(( pbcN + unPbcN + PRIVATE_CARD) * sizeof(uint8_t));
    readCards(msg, pbcN, publicCardArray);
    uint8_t *privateCardArray = (uint8_t *)malloc(( pbcN + unPbcN + PRIVATE_CARD) * sizeof(uint8_t));
    for (i = 0; i < pbcN; i++)
        privateCardArray[i] = publicCardArray[i];
    readCards(privateC, PRIVATE_CARD, privateCardArray + pbcN + unPbcN);
    winningRate =  estimateKUnshowedArray(publicCardArray, privateCardArray, pbcN, 2);
    free(publicCardArray);
    free(privateCardArray);
    return winningRate;
}
double estimatePrivateCard(const char *msg)
{
    double winningRate;
    const int unPbcN = 3;
    winningRate = 0.0;
    uint8_t *publicCardArray = (uint8_t *)malloc(( unPbcN + PRIVATE_CARD ) * sizeof(uint8_t));
    uint8_t *privateCardArray = (uint8_t *)malloc(( unPbcN + PRIVATE_CARD ) * sizeof(uint8_t));
    readCards(msg, PRIVATE_CARD, privateCardArray+unPbcN);
    winningRate =  estimateKUnshowedArray(publicCardArray, privateCardArray, 0, 3);
    free(publicCardArray);
    free(privateCardArray);
    return winningRate;    
}
double rankCards(const char *msg, const int numCards)
{
    int rank;
    uint8_t *cardArray = (uint8_t *)malloc(numCards * sizeof(uint8_t));
    readCards(msg, numCards, cardArray);
    rank = rankCardsetWithCardArray(cardArray, numCards);
    free(cardArray);
    return (double)rank;
}

static PyObject *_estimatePrivateCard(PyObject *self, PyObject *args)
{
    char *message;
    double res;

    if (!PyArg_ParseTuple(args, "s", &message))
    {
        return NULL;
    }
    res = estimatePrivateCard(message);
    return PyFloat_FromDouble(res);
}
static PyObject *_rankCards(PyObject *self, PyObject *args)
{
    char *message;
    int N;
    double res;

    if (!PyArg_ParseTuple(args, "si", &message, &N))
    {
        return NULL;
    }
    res = rankCards(message,N);
    return PyFloat_FromDouble(res);
}
static PyObject *_estimateWithNPublic(PyObject *self, PyObject *args)
{
    char* publicMessage;
    char* privateMessage;
    int N;
    double res;
    if (!PyArg_ParseTuple(args, "ssi", &publicMessage,&privateMessage,&N))
    {
        return NULL;
    }
    res = estimateWithNPublic(publicMessage,privateMessage,N);
    return PyFloat_FromDouble(res);
}
static PyObject *_estimate1UnShowed(PyObject *self, PyObject *args)
{
    char* publicMessage;
    char* privateMessage;
    int pbcN;
    double res;
    if (!PyArg_ParseTuple(args, "ssi", &publicMessage,&privateMessage,&pbcN))
    {
        return NULL;
    }
    res = estimate1Unshowed(publicMessage,privateMessage,pbcN);
    return PyFloat_FromDouble(res);
}
static PyObject *_estimate2UnShowed(PyObject *self, PyObject *args)
{
    char* publicMessage;
    char* privateMessage;
    int pbcN;
    double res;
    if (!PyArg_ParseTuple(args, "ssi", &publicMessage,&privateMessage,&pbcN))
    {
        return NULL;
    }
    res = estimate2Unshowed(publicMessage,privateMessage,pbcN);
    return PyFloat_FromDouble(res);
}
static PyMethodDef PokerCalculatorMethods[] = {
    {"hand_strength",
     _estimatePrivateCard,
     METH_VARARGS,
     ""},
    {"estimate_river",
     _estimateWithNPublic,
     METH_VARARGS,
     ""},
    {"estimate_turn",
     _estimate1UnShowed,
     METH_VARARGS,
     ""},
    {"estimate_flop",
     _estimate2UnShowed,
     METH_VARARGS,
     ""},
    {"rank_cards",
     _rankCards,
     METH_VARARGS,
     ""},
    {NULL, NULL, 0, NULL}};
struct PyModuleDef PokerCalculator = {

    PyModuleDef_HEAD_INIT,
    "PokerCalculator",
    NULL,
    -1,
    PokerCalculatorMethods};
PyMODINIT_FUNC PyInit_PokerCalculator(void)
{
    PyObject *m;
    m = PyModule_Create(&PokerCalculator);
    if (m == NULL)
    {
        return NULL;
    }
    return m;
}
