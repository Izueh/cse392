CC := gcc
SRCD_CLIENT := client/src
SRCD_CHAT:= chat/src
BLDD_CLIENT := client/build
BLDD_CHAT := chat/build
MODD := modules/
BIND := bin
INCD_CLIENT := client/include
INCD_CHAT := chat/include
INCD_BUF := buf/

BUFO := buf/buf.o

ALL_CLIENT_SRCF := $(shell find $(SRCD_CLIENT) -type f -name *.c)
ALL_CHAT_SRCF := $(shell find $(SRCD_CHAT) -type f -name *.c)
ALL_CLIENT_OBJF := $(patsubst $(SRCD_CLIENT)/%,$(BLDD_CLIENT)/%,$(ALL_CLIENT_SRCF:.c=.o))
ALL_CHAT_OBJF := $(patsubst $(SRCD_CHAT)/%,$(BLDD_CHAT)/%,$(ALL_CHAT_SRCF:.c=.o))
CLIENT_FUNC_FILES := $(filter-out client/build/main.o, $(ALL_CLIENT_OBJF))
CHAT_FUNC_FILES := $(filter-out chat/build/main.o, $(ALL_CHAT_OBJF))

INC_CLIENT := -I $(INCD_CLIENT)
INC_CHAT := -I $(INCD_CHAT)
INC_BUF := -I $(INCD_BUF)

EXEC_CLIENT := client
EXEC_CHAT:= chat

CFLAGS := -Wall -Werror
DFLAGS := -g -DDEBUG -DCOLOR
STD := -std=gnu11

CFLAGS += $(STD)

.PHONY: clean all

debug: CFLAGS += $(DFLAGS)
debug: all

all: setup buf $(EXEC_CLIENT) $(EXEC_CHAT)

setup:
	mkdir -p bin client/build chat/build

buf:
	gcc -g -O -c buf/buf.c

$(EXEC_CLIENT): $(ALL_CLIENT_OBJF)
	$(CC) $^ $(BUFO) -o $(BIND)/$@ $(READLINE)

$(BLDD_CLIENT)/%.o: $(SRCD_CLIENT)/%.c
	$(CC) $(CFLAGS) $(INC_CLIENT) $(INC_BUF) -c -o $@ $<

$(EXEC_CHAT): $(ALL_CHAT_OBJF)
	$(CC) $^ $(BUFO) -o $(BIND)/$@ $(READLINE)

$(BLDD_CHAT)/%.o: $(SRCD_CHAT)/%.c
	$(CC) $(CFLAGS) $(INC_CHAT) $(INC_BUF) -c -o $@ $<

clean:
	$(RM) -r $(BLDD_CLIENT) $(BLDD_CHAT) $(BIND)
