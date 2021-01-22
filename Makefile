overlay: Makefile overlay.cpp gason.cpp gason.h socket.cc socket.hh json_message.cc json_message.hh
	g++ -g -O3 -march=native -std=c++14 -o overlay overlay.cpp gason.cpp json_message.cc socket.cc -lX11 -lXfixes -lXext -Wall
