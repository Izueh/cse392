#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "logger.h"

void log_it(const char* msg){
        time_t now;
        time(&now);
        if(verbose){
                printf("%s %s\n", ctime(&now), msg);
        }
}
