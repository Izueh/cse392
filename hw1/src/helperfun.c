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
