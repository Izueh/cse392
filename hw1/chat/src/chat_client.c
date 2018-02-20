#include "chat_client.h"

int main(int argc, char** argv){
    #define MAX_EVENTS 10
    if(argc <3){
        printf("invalid amount of arguments\n");
        exit(1);
    }

    int sockfd = atoi(argv[1]), e_fd, n, ndfs;
    char* name = argv[2];
    printf("Now chatting with %s\n", name);
    struct epoll_event ev, events[MAX_EVENTS];
    
    e_fd = epoll_create1(0xBAE);

    if(e_fd == -1){
        perror("epoll_create1");
        exit(EXIT_FAILURE);
    }

    //add Client Socket to the epoll
    ev.events = EPOLLIN;
    ev.data.fd = sockfd;
    if (epoll_ctl(e_fd, EPOLL_CTL_ADD, sockfd, &ev) == -1){
        perror("epoll_ctl: sockfd");
        exit(EXIT_FAILURE);
    }

    //add STDIN to epoll
    ev.events = EPOLLIN;
    ev.data.fd = STDIN_FILENO;
    if (epoll_ctl(e_fd, EPOLL_CTL_ADD, STDIN_FILENO, &ev) == -1){
        perror("epoll_ctl: stdin");
        exit(EXIT_FAILURE);
    }

    while(1){
            //wait for signal on either STDIN or Socket
        ndfs = epoll_wait(e_fd, events, sockfd, -1);
        if (ndfs == -1) {
            perror("epoll_wait");
            exit(EXIT_FAILURE);
        }

        for (n = 0; n < ndfs; ++n) {
            //info in socket needs to be read
        }
    }



}