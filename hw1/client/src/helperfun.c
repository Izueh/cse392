#include <errno.h>
#include "helperfun.h"
#include "user_list.h"
#include "buf.h"

user_list* open_chat(char* user){
    int socks[2], pid;
    char sockfd[10]; 
    user_list* new_chat = malloc(sizeof(user_list));
    if(socketpair(AF_UNIX,SOCK_STREAM,0,socks) < 0 ){
        perror("socketpair: ");
        return NULL;
        //free memory
    }
    if((pid=fork()) < 0){
        perror("fork: ");
        return NULL; 
    }else if(pid == 0){
        close(socks[0]);
        snprintf(sockfd, sizeof(sockfd), "%d", socks[1]);
        execl("xterm", "-e", "./chat", sockfd, user, (void *)NULL);
        perror("execl: ");
        exit(1);
    }
    new_chat->fd = socks[0];
    new_chat->pid = pid;
    new_chat->user = strdup(user);
    new_chat->next = NULL;
    return new_chat;

}

void command_action(char* msg, int sockfd){
    char* tail = split_first_word(msg), *user, *send_msg, *res;
    user_list* chat_info;
    ssize_t count;

    if( strcmp(msg, "/help\n") == 0){
        printf("/logout: logout\n/listu: list of online friends\n");
    } else if( strcmp(msg, "/logout\n") == 0){
        dprintf(sockfd, "BYE\r\n\r\n");
        char* msg = read_socket_message(sockfd, "\r\n\r\n");
        if( strcmp(msg, "EYB") == 0 ){
            printf("thank you\n");
            free(msg);
            exit(0);
        }
    } else if( strcmp(msg, "/listu\n")  == 0 ){
        dprintf(sockfd, "LISTU\r\n\r\n");
    } else if( strcmp(msg, "/chat") == 0 ){
        user = tail;
        send_msg = split_first_word(tail);
        dprintf(sockfd, "TO %s %s\r\n\r\n", user, send_msg);

        res = read_socket_message(sockfd, "\r\n\r\n");
        
        tail = split_first_word(res);
        if( strcmp(msg, "OT") == 0){
            chat_info = ul_find(user);
            if(chat_info){
                //this user has an open chat
            }else{
               chat_info = open_chat(user);
               if(!chat_info){
                   //free and handle error 
               }
               ul_add(chat_info);
               count = write(chat_info->fd,send_msg,strlen(send_msg));
               if(count < 0){
                   //something wrong
               }
            }
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
    char* msg = read_socket_message(sockfd, "\r\n\r\n");
    if( strcmp(msg, "U2EM") != 0){        
        printf("error in u2em");
        exit(1);
    }
    free(msg);
    dprintf(sockfd, "IAM %s\r\n\r\n", name);
    msg = read_socket_message(sockfd, "\r\n\r\n");
    if( strcmp(msg, "ETAKEN") == 0){        
        printf("User already in use\n");
        free(msg);
        exit(1);
    }else if( strcmp(msg, "MAI" ) == 0) {
        free(msg); 
        msg = read_socket_message(sockfd, "\r\n\r\n");
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
    char* msg = read_socket_message(sockfd, "\r\n\r\n");
    printf("socket: %s", msg);
}

void std_handler(int sockfd){
    char* buff = calloc(1, MAXLINE+1);
    fgets(buff, MAXLINE+1, stdin);
    command_action(buff, sockfd);
}
