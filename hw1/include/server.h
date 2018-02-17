#ifndef serv_h
#define serv_h

#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/select.h>
#include <poll.h>
#include <stdlib.h>

#include <arpa/inet.h>


#define MAXLINE 4096

char USAGE[] = "USAGE: address port [[-v] [-h]]\n"; 

#endif

