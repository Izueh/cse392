CC := gcc
SRCD := src
BLDD := build
BIND := bin
INCD := include

ALL_SRCF := $(shell find $(SRCD) -type f -name *.c)
ALL_OBJF := $(patsubst $(SRCD)/%,$(BLDD)/%,$(ALL_SRCF:.c=.o))
FUNC_FILES := $(filter-out build/main.o, $(ALL_OBJF))
TEST_SRC := $(shell find $(TSTD) -type f -name *.c)

INC := -I $(INCD)

EXEC := client 

CFLAGS := -Wall -Werror
DFLAGS := -g -DDEBUG -DCOLOR
STD := -std=gnu11

CFLAGS += $(STD)

.PHONY: clean all

debug: CFLAGS += $(DFLAGS)
debug: all

all: setup $(EXEC) $(TEST_EXEC)

setup:
	mkdir -p bin build

$(EXEC): $(ALL_OBJF)
	$(CC) $^ -o $(BIND)/$@ $(READLINE)

$(BLDD)/%.o: $(SRCD)/%.c
	$(CC) $(CFLAGS) $(INC) -c -o $@ $<

clean:
	$(RM) -r $(BLDD) $(BIND)
