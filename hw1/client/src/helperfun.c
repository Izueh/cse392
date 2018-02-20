#include "helperfun.h"
#include <errno.h>

char* read_socket_message(int sockfd){
    char buff[MAXLINE + 1]={0}, *msg = calloc(1, MAXLINE+1);
    int n = 0, size = 0, allocated=1;
    do {
        n = read(sockfd, buff , MAXLINE);
        if( n < 0){
            perror("read: ");
            exit(EXIT_FAILURE);
        }
        buff[n] = '\0';
        size += n;
        if(size > (allocated*MAXLINE)){
            allocated += 1;
            msg = realloc(msg, allocated*MAXLINE+1);
        }
        msg[size] = '\0';
        strcat(msg,buff);
    }while(!strstr(msg, "\r\n\r\n"));

    msg[size-4] = '\0';
    return msg;
}

char* split_first_word(char* msg){
    char* first_space = strchr(msg, ' ');
    if(first_space){
        *first_space = '\0';
        return (first_space+1);
    }
    return msg;
}

void command_action(char* msg, int sockfd){
    char* tail = split_first_word(msg);

    if( strcmp(msg, "/help\n") == 0){
        printf("/logout: logout\n/listu: list of online friends\n");
    } else if( strcmp(msg, "/logout\n") == 0){
        dprintf(sockfd, "BYE\r\n\r\n");
        char* msg = read_socket_message(sockfd);
        if( strcmp(msg, "EYB") == 0 ){
            printf("thank you\n");
            free(msg);
            exit(0);
        }
    } else if( strcmp(msg, "/listu\n")  == 0 ){
        dprintf(sockfd, "LISTU\r\n\r\n");
    } else if( strcmp(msg, "/chat") == 0 ){
        dprintf(sockfd, "TO %s", tail);

        char* msg = read_socket_message(sockfd);
        tail = split_first_word(msg);
        if( strcmp(msg, "OT") == 0){
            
        } else if( strcmp(msg, "EDNE") == 0){
            printf("User is not online");
        } else {
            printf("error in sending message");
            free(msg);
            exit(1);
        }

    } else {
        printf("invalid command");
        exit(1); 
    }
}

void login(char* name, int sockfd){
    dprintf(sockfd, "ME2U\r\n\r\n");
    char* msg = read_socket_message(sockfd);
    if( strcmp(msg, "U2EM") != 0){        
        printf("error in u2em");
        exit(1);
    }
    free(msg);
    dprintf(sockfd, "IAM %s\r\n\r\n", name);
    msg = read_socket_message(sockfd);
    if( strcmp(msg, "ETAKEN") == 0){        
        printf("User already in use\n");
        free(msg);
        exit(1);
    }else if( strcmp(msg, "MAI" ) == 0) {
        free(msg); 
        msg = read_socket_message(sockfd);
        char* tail = split_first_word(msg);
        if(strcmp(msg, "MOTD") == 0){
            printf("%s\n", tail);
        }
    }else {
        printf("Error adding user");
        free(msg);
        exit(1);
    }
}

void socket_handler(int sockfd){
    char* msg = read_socket_message(sockfd);
    printf("socket: %s", msg);
}

void std_handler(int sockfd){
    char* buff = calloc(1, MAXLINE+1);
    fgets(buff, MAXLINE+1, stdin);
    command_action(buff, sockfd);
}

