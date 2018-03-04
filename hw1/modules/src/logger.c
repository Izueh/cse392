#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "logger.h"

void log_it(const char* flag, const char* msg){
    char s[1000];
    time_t now= time(NULL);
    struct tm* p = localtime(&now);
    strftime(s,1000,"%c",p);
    if(verbose){
        printf("\e[1;34m[%s] %s%s\e[0m\n", s,flag, msg);

    }
}
