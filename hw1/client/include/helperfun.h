#ifndef HELPERFUN_H
#define HELPERFUN_H
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

#define U2EM_LEN 8
#define MAXLINE 4096

void login(char* name, int sockfd);
void socket_handler(int socketfd);
void std_handler(int socketfd);


#endif
