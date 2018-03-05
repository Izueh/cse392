#include <errno.h>
#include <sys/epoll.h>
#include <sys/types.h>
#include <sys/wait.h>
#include "helperfun.h"
#include "user_list.h"
#include "buf.h"
#include "logger.h"


extern int e_fd;
extern struct epoll_event ev;
char* chat_bin;

void open_chat(char* user, user_list* chat_info){
    int socks[2], pid;
    char sockfd[10]; 
    if(socketpair(AF_UNIX,SOCK_STREAM,0,socks) < 0 ){
        perror("socketpair: ");
        exit(EXIT_FAILURE);
        //free memory
    }
    if((pid=fork()) < 0){
        perror("fork: ");
        exit(EXIT_FAILURE);
    }else if(pid == 0){
        close(socks[0]);

        snprintf(sockfd, sizeof(sockfd), "%d", socks[1]);
        execlp("xterm","xterm", "-e", chat_bin, sockfd, user, (void *)NULL);
        perror("execl: ");
        exit(1);
    }
    close(socks[1]);
    chat_info->fd = socks[0];
    chat_info->pid = pid;

}

void logout(int sockfd){
    log_it("sending: ","BYE");
    dprintf(sockfd, "BYE\r\n\r\n");
    char* msg = read_socket_message(sockfd, "\r\n\r\n");
    if( strcmp(msg, "EYB") == 0 ){
        printf("thank you\n");
        free(msg);
        free(chat_bin);
        close(sockfd);
        kill(0, SIGKILL);
    }
}

//we should split this up into multiple function calls
void command_action(char* msg, int sockfd){
    char* tail = split_first_word(msg), *user, *send_msg;
    user_list* user_info;
    if( strcmp(msg, "/help") == 0){
        printf("/logout: logout\n/listu: list of online friends\n");
    } else if( strcmp(msg, "/logout") == 0){
        logout(sockfd);
        exit(EXIT_SUCCESS);
    } else if( strcmp(msg, "/listu")  == 0 ){
        log_it("sending: ","LISTU");
        dprintf(sockfd, "LISTU\r\n\r\n");
    } else if( strcmp(msg, "/chat") == 0 ){
        user = tail;
        send_msg = split_first_word(tail);
        if(send_msg == NULL){
            printf("\e[31m\e[1minvalid command\e[0m\n");
            return;
        }
        user_info = ul_find(user);
        if(user_info){
            printf("\e[31mChat is already open for user\e[0m");
            return;
        }
        user_info = malloc(sizeof(user_list));
        memset(user_info,0, sizeof(user_list));
        dprintf(sockfd, "TO %s %s\r\n\r\n", user, send_msg);

        int size =strlen("TO ")+strlen(user)+strlen(send_msg)+2;
        char* tmp = calloc(1,size);
        snprintf(tmp,size,"TO %s %s",user,send_msg);
        log_it("sending: ",tmp);
        free(tmp);

        user_info->user = strdup(user);
        user_info->initial_msg = strdup(send_msg);
        ul_add(user_info);
    }else if(!strcmp(msg, "/close")){
        printf("Good Bye\n");
        exit(EXIT_SUCCESS);
    } else {
        printf("\e[31m\e[1minvalid command\e[0m\n");
    }
}

void login(char* name, int sockfd){
    dprintf(sockfd, "ME2U\r\n\r\n");
    log_it("sending: ","ME2U");
    char* msg = read_socket_message(sockfd, "\r\n\r\n");
    if( strcmp(msg, "U2EM") != 0){        
        printf("error in u2em\n");
        exit(1);
    }
    free(msg);
    dprintf(sockfd, "IAM %s\r\n\r\n", name);

    int size = strlen("IAM ")+strlen(name)+1;
    char* tmp = calloc(1,size);
    snprintf(tmp,size,"IAM %s",name);
    log_it("sending: ", tmp);
    free(tmp);

    msg = read_socket_message(sockfd, "\r\n\r\n");
    if( strcmp(msg, "ETAKEN") == 0){        
        printf("\e[1;31mUser already in use\e[0m\n");
        free(msg);
        exit(1);
    }else if( strcmp(msg, "MAI" ) == 0) {
        free(msg); 
        msg = read_socket_message(sockfd, "\r\n\r\n");
        char* tail = split_first_word(msg);
        if(strcmp(msg, "MOTD") == 0){
            printf("\e[32mMessage of the Day: \e[1m%s\e[0m\n", tail);
        }
    }else {
        printf("Error adding user\n");
        free(msg);
        exit(1);
    }
}

void chat_handler(int sockfd, int wrtFD){
    char* msg;
    user_list* user;
    msg = read_socket_message(sockfd, "\n");
    if(!*msg){
        user = ul_remove(sockfd);
        close(user->fd);
        waitpid(user->pid,NULL,0);
        free(msg);
        free(user);
        return;
    }
    dprintf(wrtFD, "%s\r\n\r\n", msg);
    free(msg);
    ev.events = EPOLLIN;
    ev.data.fd = sockfd;
    if(epoll_ctl(e_fd, EPOLL_CTL_DEL, sockfd, &ev) < 0){
        perror("epoll_ctl: ot");
        exit(EXIT_FAILURE);
    }
}

void ot(char* user){
    user_list* chat_info = ul_find(user);
    if(chat_info && chat_info->fd){
        //this user has an open chat
        if(chat_info->initial_msg){
            dprintf(chat_info->fd,"TO %s %s\r\n\r\n", chat_info->user,\
                    chat_info->initial_msg);
            free(chat_info->initial_msg);
            chat_info->initial_msg = NULL;
        }
    }else{
       open_chat(user, chat_info);
       if(!chat_info){
           
           //free and handle error 
       }
       dprintf(chat_info->fd,"TO %s %s\r\n\r\n",chat_info->user,\
               chat_info->initial_msg);
       free(chat_info->initial_msg);
       chat_info->initial_msg = NULL;
       
    }
    ev.events = EPOLLIN;
    ev.data.fd = chat_info->fd;
    if(epoll_ctl(e_fd, EPOLL_CTL_ADD, chat_info->fd, &ev) == -1){
        perror("epoll_ctl: sockfd");
        exit(EXIT_FAILURE);
    }
}

void socket_handler(int sockfd){
    char* msg,*tail,*user;
    user_list* chat_info;
    msg = read_socket_message(sockfd, "\r\n\r\n");
    if(!*msg){
        printf("\e[1;31mserver closed connection\e[0m");
        free(msg);
        exit(EXIT_FAILURE);
    }
    tail = split_first_word(msg);
    if(!strcmp(msg, "UTSIL")){
        printf("Online Users: \n"); 
        while((user=tail)){
            tail = split_first_word(tail);
            printf("%s\n",user);
        }
    }else if(!strcmp(msg, "FROM")){
        user = tail;
        tail = split_first_word(tail);
        if(tail == NULL){
            exit(1);
            return;
        }
        chat_info = ul_find(user);
        if(chat_info){
        //chat is open relay message
            dprintf(chat_info->fd,"FROM %s %s\r\n\r\n",chat_info->user,tail);
            dprintf(sockfd, "MORF %s\r\n\r\n", chat_info->user);
        }else{
        //open chat with new message
            chat_info = malloc(sizeof(user_list));
            memset(chat_info,0,sizeof(user_list));
            chat_info->user = strdup(user);
            open_chat(user, chat_info);
            ul_add(chat_info);
            dprintf(chat_info->fd,"FROM %s %s\r\n\r\n",chat_info->user,tail);
            dprintf(sockfd, "MORF %s\r\n\r\n", chat_info->user);

            int size = strlen("MORF ") + strlen(chat_info->user)+1;
            char* tmp = calloc(1,size);
            snprintf(tmp,size,"MORF %s", chat_info->user);
            log_it("sending: ",tmp);
            free(tmp);

            ev.events = EPOLLIN;
            ev.data.fd = chat_info->fd;
            if(epoll_ctl(e_fd, EPOLL_CTL_ADD, chat_info->fd, &ev) == -1){
                perror("epoll_ctl: sockfd");
                exit(EXIT_FAILURE);
            }
        }    
    }else if(!strcmp(msg, "OT")){
        user = tail;
        ot(user);
    } else if( !strcmp(msg, "EDNE")){
        user = tail;
        chat_info = ul_remove_by_user(user);
        if(chat_info->pid){
            dprintf(chat_info->fd, "/offline\r\n\r\n");
            ev.events = EPOLLIN;
            ev.data.fd = chat_info->fd;
            if(epoll_ctl(e_fd, EPOLL_CTL_ADD, chat_info->fd, &ev) == -1){
                perror("epoll_ctl: sockfd");
                exit(EXIT_FAILURE);
            }
        }else{
            free(chat_info->initial_msg);
            free(chat_info->user);
            free(chat_info);
            printf("User \e[1m%s\e[0m is not online\n", user);
        }
    } else if (!strcmp(msg, "UOFF")){
        user = tail;
        chat_info = ul_find(user);
        if(chat_info){
            dprintf(chat_info->fd, "/offline\r\n\r\n");
        }
    }
    free(msg);
}

void std_handler(int sockfd){
    char* pos;
    char* buff = read_socket_message(STDIN_FILENO, "\n");
    if ((pos=strchr(buff, '\n')) != NULL)
        *pos = '\0';
    command_action(buff, sockfd);
}

void set_path(char* chat_path){
    chat_bin = chat_path;
}
