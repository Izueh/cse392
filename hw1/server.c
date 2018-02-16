#include "server.h"

int main(int argc, char** argv){

    int sockfd, n, s;
    char recvline[MAXLINE + 1];
	struct addrinfo hints;
	struct addrinfo *res, *rp;
	
	if( argc !=  3 ){
		printf("USAGE: %s address port\n", argv[0]);
		exit(EXIT_FAILURE);
	}

	// initialize getaddr struc
	memset(&hints, 0, sizeof(struct addrinfo));
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_DGRAM;
	hints.ai_flags = AI_PASSIVE;
	hints.ai_protocol = 0;
	hints.ai_canonname = NULL;
	hints.ai_addr = NULL;
	hints.ai_next = NULL;
	
	// try connections
	s = getaddrinfo(argv[1],argv[2], &hints, &res);
	if (s != 0){
		fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(s));
		exit(EXIT_FAILURE);
	}

	for(rp = res; rp != NULL; rp = rp->ai_next){
		sockfd = socket(rp->ai_family, rp->ai_socktype, 
				rp->ai_protocol);
		if (sockfd == -1)
			continue;
		if (connect(sockfd, rp->ai_addr, rp->ai_addrlen) != -1)
			break;
		close(sockfd);
	}

	if (rp == NULL){
		printf("Failed to connect to %s:%s",argv[1],argv[2]);
		exit(EXIT_FAILURE);
	}

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

