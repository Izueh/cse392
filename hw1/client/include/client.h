#ifndef SERVER_H 
#define SERVER_H

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
#include <sys/epoll.h>
#include <stdlib.h>

#include <arpa/inet.h>
#include "user_list.h"

#define MAXLINE 4096

char USAGE[] = "USAGE:[[-v] [-h]] username address port\n"; 
struct epoll_event ev;
int e_fd;


#endif

