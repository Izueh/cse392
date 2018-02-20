#include <stdlib.h>
#include <string.h>
#include "user_list.h"


user_list* head;
void ul_add(user_list* node){
    if(!head){
        head=node; 
    }else{
        node->next=head;
        head=node;
    }
}

user_list* ul_remove(int fd){
    if(!head)
        return NULL;
    user_list* prev=NULL, *walk=head;
    while(walk){
       if(walk->fd == fd){
           if(prev){
               prev->next = walk->next;
           }else{
               head = NULL;
           }
           return walk;
       } 
       prev = walk;
       walk = walk->next;
    }
    return NULL;
}

user_list* ul_find(char* name){
    user_list* walk= head;
    while(walk){
        if(!strcmp(walk->user, name)){
            return walk;
        }
        walk = walk->next;
    }
    return NULL;
}

void clean(){
    user_list* walk = head;
    while(walk){
        free(walk->user);
        walk = walk->next;
        free(walk);
    }
}


