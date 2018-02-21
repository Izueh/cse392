#ifndef BUF_H
#define BUF_H

#define MAXLINE 4096

char* read_socket_message(int sockfd, const char* const end_msg);
char* split_first_word(char* msg);

#endif
