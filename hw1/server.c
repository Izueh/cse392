#include "server.h"

int main(){
    int sockfd, n;
    char recvline[MAXLINE + 1];
    struct sockaddr_in servaddr;

    if((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
        printf("socket error");

    bzero(&servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(5020);
    char ip_address[] = "127.0.0.1";
    if(inet_pton(AF_INET, ip_address, &servaddr.sin_addr) <= 0)
        printf("error");

    if (connect(sockfd, (struct sockaddr *) &servaddr, sizeof(servaddr)) < 0)
        printf("connect error");

    char buff[] = "ayyyy";
    write(sockfd, buff, sizeof(buff));

    while ( (n = read(sockfd, recvline, MAXLINE)) > 0) {
        recvline[n] = 0;
        /* null terminate */
        if (fputs(recvline, stdout) == EOF)
            printf("fputs error");
    }
    if (n < 0)
        printf("read error");

}

