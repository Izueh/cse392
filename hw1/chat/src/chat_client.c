#include "chat_client.h"
#include "buf.h"

int main(int argc, char** argv){
    #define MAX_EVENTS 10
    if(argc < 2){
        printf("invalid amount of arguments\n");
        exit(1);
    }

    int sockfd = atoi(argv[1]), e_fd, n, ndfs;
    char* name = argv[2],*initial_msg,*message,*sender;
    printf("\e[32mNow chatting with \e[1m%s\e[0m\n", name);
    struct epoll_event ev, events[MAX_EVENTS];
    printf("socket1 %d\n", sockfd);
    initial_msg = read_socket_message(sockfd, "\r\n\r\n");
    sender = split_first_word(initial_msg);
    message = split_first_word(sender);
    
    if(!strcmp(initial_msg, "TO"))
        printf("\e[34m< %s\e[0m\n", message);

    if(!strcmp(initial_msg, "FROM"))
        printf("\e[36m> %s\e[0m\n", message);
    
    printf("\e[34m< ");
    fflush(stdout);
    e_fd = epoll_create1(0);

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

    while(0xDEAD){
            //wait for signal on either STDIN or Socket
    reset:
        ndfs = epoll_wait(e_fd, events, sockfd, -1);
        if (ndfs == -1) {
            perror("epoll_wait");
            exit(EXIT_FAILURE);
        }
        for (n = 0; n < ndfs; ++n) {
            //info in socket needs to be read
            if(events[n].data.fd == sockfd) {
                char* msg = read_socket_message(sockfd, "\r\n\r\n");
                if(!strcmp(msg, "/offline")){
                    printf("\e[31mUser is offline\e[0m\n");
                    goto reset;
                }
                sender = split_first_word(msg);
                message = split_first_word(sender);
                printf("\n\e[36m> %s\e[0m\n", message);
                printf("\e[34m< ");
                fflush(stdout);

            }else{
                char* msg = read_socket_message(STDIN_FILENO, "\n");
                if(!strcmp(msg,"/close")){
                    close(sockfd);
                    exit(EXIT_SUCCESS);

                }
                dprintf(sockfd, "TO %s %s\n", name, msg);
                printf("\e[34m< ");
                fflush(stdout);
            }
        }
    }
}

