#include "buf.h"
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdio.h>

char* read_socket_message(int sockfd, const char* const end_msg){
    char buff[2]={0}, *msg = calloc(1, MAXLINE+1);
    int n = 0, size = 0, allocated=1;
    do {
        retry:
        n = read(sockfd, buff , 1);
        if( n < 0){
            perror("read");
            exit(EXIT_FAILURE);
        }
        if (n == 0){
            free(msg);
            msg = malloc(1);
            msg[0] = '\0';
            return msg;

        }
        if (errno == EINTR)
           goto retry;
        buff[n] = '\0';
        size += n;
        if(size > (allocated*MAXLINE)){
            allocated += 1;
            msg = realloc(msg, (allocated*MAXLINE)+1);
        }
        msg[size] = '\0';
        strcat(msg,buff);
    }while(!strstr(msg, end_msg));
    msg[size-strlen(end_msg)] = '\0'; 
    return msg;
}

char* split_first_word(char* msg){
    char* first_space = strchr(msg, ' ');
    if(first_space){
        *first_space = '\0';
        return (first_space+1);
    }
    return NULL;
}

