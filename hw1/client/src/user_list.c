#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
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

user_list* ul_remove_by_user(char* user){
    if(!head)
        return NULL;
    user_list* prev=NULL, *walk=head;
    while(walk){
       if(!strcmp(walk->user, user)){
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
    user_list *walk= head;
    while(walk){
        if(!strcmp(walk->user, name)){
            return walk;
        }
        walk = walk->next;
    }
    return NULL;
}

void ul_clean_child(){
    user_list *walk=head, *prev=NULL;
    int status;
    while(walk){
        waitpid(walk->pid,&status,WNOHANG);
        if(WIFEXITED(status)){
            close(walk->fd);

            if(!prev){
                head = walk->next;
                free(walk);
                walk = head;
            }else{
                prev->next = walk->next;
                free(walk);
                walk = prev->next;
            }
        }
    }
}

void ul_clean(){
    user_list* walk = head;
    while(walk){
        free(walk->user);
        walk = walk->next;
        free(walk);
    }
}


