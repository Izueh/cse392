#ifndef HELPERFUN_H
#define HELPERFUN_H
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include "user_list.h"

#define U2EM_LEN 8
#define MAXLINE 4096

void login(char* name, int sockfd);
void chat_handler(int sockfd, int wrtFD);
void open_chat(char* user, user_list* chat_info);
void logout(int sockfd);
void ot(char* user);
void socket_handler(int socketfd);
void std_handler(int socketfd);
void set_path(char* path);


#endif
