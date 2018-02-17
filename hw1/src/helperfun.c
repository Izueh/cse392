#include "helperfun.h"

void login(char* name, int sockfd){
    int n;
    char buff[30];
    char* intialMess = "ME2U\r\n\r\n";
    write(sockfd, intialMess, sizeof(intialMess));
    if( (n = read(sockfd, buff, sizeof(buff))) < 0 ){
        printf("Error in initial server message");     
    }
    printf("%s", buff);
    if( strcmp(buff, "U2EM\r\n\r\n") ){        
        printf("Error in initial server message");     
    }
}
