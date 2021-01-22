CC=gcc
CXX=g++
CXXFLAGS=-pedantic-errors -Wall -Werror -fstack-protector-all -O3 -march=native -std=c++14
LDFLAGS=-lX11 -lXfixes -lXext
all: overlay

overlay: overlay.o socket.o json_message.o
	$(CXX) $(LDFLAGS) $^ -o $@

#this rules describes ANY .c file to be compiled into .o file
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

%.o: %.cc
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f *.o overlay