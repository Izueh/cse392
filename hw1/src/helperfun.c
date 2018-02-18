#include "helperfun.h"
#include <errno.h>


void login(char* name, int sockfd){
    int n=0, total=0;
    char buff[30]={0}, *ptr=buff;

    dprintf(sockfd, "ME2U\r\n\r\n");
    do{
        ptr+=n;
        n = read(sockfd, ptr, sizeof(buff-total));
        total+=n;

    }while(total!=U2EM_LEN);
    buff[total] = '\0';
    printf(" %s %d\n", buff, strcmp(buff, "U2EM\r\n\r\n") );
    if( strcmp(buff, "U2EM\r\n\r\n") != 0){        
        printf("error in u2em");
    }

    dprintf(sockfd, "IAM %s\r\n\r\n", name);
    if( (n = read(sockfd, buff, sizeof(buff))) < 0 ){
        printf("receinved IAM error");     
    }
    if( strcmp(buff, "ETAKEN\r\n\r\n") == 0){        
        printf("User already in use");
    }else if( strcmp(buff, "MAI\r\n\r\n" ) == 0) {
        printf("Error in adding user");
    }

}


void socket_handler(int sockfd){
    char buff[MAXLINE + 1]={0}, *msg = malloc(MAXLINE+1);
    int n = 0, size = 0, allocated=1;
    do {
        n = read(sockfd, buff , MAXLINE);
        if( n < 0){
            perror("read: ");
            exit(EXIT_FAILURE);
        }
                
        printf("in the socket while");
        buff[n] = '\0';
        size += n;
        if(size > (allocated*MAXLINE)){
            allocated += 1;
            msg = realloc(msg, allocated*MAXLINE+1);
        }
        msg[size] = '\0';
        strcat(msg,buff);
    }while(!strstr(msg, "\r\n\r\n"));
}

void std_handler(){
    //char buff[MAXLINE + 1];
    
}
