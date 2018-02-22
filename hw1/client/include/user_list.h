#ifndef USER_LIST_H
#define USER_LIST_H

struct user_list{
    int fd;
    char* user;
    int pid;
    struct user_list* next;
};

typedef struct user_list user_list;
void ul_add(user_list* node);
user_list* ul_find(char* name);
void ul_clean_child();
void ul_clean();
#endif

