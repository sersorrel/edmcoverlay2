overlay: Makefile X11/overlay.cpp X11/gason.cpp X11/gason.h X11/socket.cc X11/socket.hh X11/json_message.cc X11/json_message.hh
	g++ -g -O1 -std=c++11 -o overlay X11/overlay.cpp X11/gason.cpp X11/json_message.cc X11/socket.cc -lX11 -lXfixes -lXext -Wall
