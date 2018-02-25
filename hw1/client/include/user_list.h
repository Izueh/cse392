#ifndef USER_LIST_H
#define USER_LIST_H

struct user_list{
    int fd;
    int pid;
    char* user;
    char* initial_msg;
    struct user_list* next;
};

typedef struct user_list user_list;
void ul_add(user_list* node);
user_list* ul_find(char* name);
user_list* ul_remove(int fd);
user_list* ul_remove_by_user(char*user);
void ul_clean_child();
void ul_clean();
#endif

