#include <errno.h>
#include <sys/types.h>
#include <sys/wait.h>
#include "client.h"
#include "logger.h"
#include "helperfun.h"
#include "user_list.h"

int main(int argc, char** argv){
    #define MAX_EVENTS 10
    int sockfd, n, s, opt, ndfs;
    struct addrinfo hints;
    struct addrinfo *res, *rp;
    struct epoll_event events[MAX_EVENTS];
    sigset_t set;
        
    if(argc <  4){
        printf("%s", USAGE);
        exit(EXIT_FAILURE);
    }
    while((opt = getopt(argc,argv,"hv")) != -1){
        switch(opt){
            case 'h':
                    printf("%s", USAGE);
                    exit(EXIT_SUCCESS);
            case 'v':
                    verbose = 1;
                    break;
            case '?':
                    printf("%s", USAGE);
                    exit(EXIT_FAILURE);
            default:
                    printf("%s", USAGE);
                    exit(EXIT_FAILURE);
        }
    }

    // initialize getaddr struc
    memset(&hints, 0, sizeof(struct addrinfo));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;
    hints.ai_protocol = 0;
    hints.ai_canonname = NULL;
    hints.ai_addr = NULL;
    hints.ai_next = NULL;

    // try connections
    s = getaddrinfo(argv[argc-2], argv[argc-1], &hints, &res);
    if (s != 0){
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(s));
        exit(EXIT_FAILURE);
    }

    for(rp = res; rp != NULL; rp = rp->ai_next){
        struct timeval to = {50, 0};
        sockfd = socket(rp->ai_family, rp->ai_socktype, 
                        rp->ai_protocol);
        if (sockfd == -1){
            continue;
        }
        if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, (struct timeval*)&to, sizeof(struct timeval)) == -1) {
            printf("Error in setsockopt\n");
            continue;
        }
        if (connect(sockfd, rp->ai_addr, rp->ai_addrlen) != -1)
            break;
        close(sockfd);
    }
    free(res);

    if (rp == NULL){
        printf("Failed to connect to %s:%s\n",argv[argc-2],argv[argc-1]);
        exit(EXIT_FAILURE);
    }

    // path to chat bin
    char * cpy = strdup(argv[0]);
    char * last = strrchr(cpy,'/');
    *(last+1)='\0';
    char * path = calloc(1,strlen(cpy)+strlen("chat")+1);
    strcat(path,cpy);
    strcat(path,"chat");
    set_path(path);
    free(cpy);

    login(argv[argc-3], sockfd);

    // epoll stuff
    e_fd = epoll_create1(0);

    if(e_fd == -1){
        perror("epoll_create1");
        exit(EXIT_FAILURE);
    }

    //add Server Socket to the epoll
    ev.events = EPOLLIN;
    ev.data.fd = sockfd;
    if (epoll_ctl(e_fd, EPOLL_CTL_ADD, sockfd, &ev) == -1){
        perror("epoll_ctl: sockfd");
        exit(EXIT_FAILURE);
    }

    //add STDIN to epoll
    ev.events = EPOLLIN;
    ev.data.fd = STDIN_FILENO;
    if (epoll_ctl(e_fd, EPOLL_CTL_ADD, STDIN_FILENO, &ev) \
                    == -1){
        perror("epoll_ctl: stdin");
        exit(EXIT_FAILURE);
    }
    
    // signald stuff
    sigemptyset(&set);
    sigaddset(&set, SIGCHLD);
    sigaddset(&set, SIGINT);
    sigaddset(&set, SIGTERM);
    sigaddset(&set, SIGPIPE);
    if((sigprocmask(SIG_BLOCK, &set, NULL)) < 0){
        perror("sigprocmask");
        exit(EXIT_FAILURE);
    }
    while(0xCAFE){
        //wait for signal on either STDIN or Socket
        ndfs = epoll_wait(e_fd, events, sockfd, -1);
        if (ndfs == -1) {
            perror("epoll_wait");
            exit(EXIT_FAILURE);
        }
        if(errno == EINTR){
            continue;
        }

        for (n = 0; n < ndfs; ++n) {
            //info in socket needs to be read
            if(events[n].data.fd == STDIN_FILENO) {
                std_handler(sockfd);
            }
            //info coming from STDIN
            else if(events[n].data.fd == sockfd) {
                socket_handler(sockfd);
            }else{
                chat_handler(events[n].data.fd, sockfd);
            }
        }
    }
}

