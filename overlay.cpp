/*
 * Copyright (c) 2020 ericek111 <erik.brocko@letemsvetemapplem.eu>.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, version 3.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */

// Modified for edmcoverlay2. Such modifications are copyright © 2020 Ash Holland.

#include <iostream>
#include <stdlib.h>
#include <csignal>

#include "socket.hh"
#include "json_message.hh"
#include "drawables.h"
#include "xoverlayoutput.h"

unsigned short port = 5020;


static void sighandler(int signum)
{
    std::cout << "edmcoverlay2: got signal " << signum << std::endl;
    if ((signum == SIGINT) || (signum == SIGTERM))
    {
        std::cout << "edmcoverlay2: SIGINT/SIGTERM, exiting" << std::endl;
        exit(0);
    }
}

int main(int argc, char* argv[])
{
    if (argc != 5)
    {
        std::cout << "Usage: overlay X Y W H" << std::endl;
        return 1;
    }
    auto& drawer = XOverlayOutput::get(atoi(argv[1]), atoi(argv[2]), atoi(argv[3]), atoi(argv[4]));

    std::cout << "edmcoverlay2: overlay starting up..." << std::endl;
    signal(SIGINT, sighandler);
    signal(SIGTERM, sighandler);

    std::shared_ptr<tcp_server_t> server(new tcp_server_t(port), [](tcp_server_t *p)
    {
        if (p)
        {
            //have no idea why it cannot be called from server destructor, but ok
            //let's do wrapper
            p->close();
            delete p;
        }
    });

    drawer.cleanFrame();
    drawer.showVersionString("edmcoverlay2 overlay process: running!", "green");
    drawer.flushFrame();
    std::cout << "edmcoverlay2: overlay ready." << std::endl;

    while (true)
    {
        auto socket = server->accept_autoclose();
        const std::string request = read_response(*socket);

        //std::cout << "edmcoverlay2: overlay got request: " << request << std::endl;

        drawer.cleanFrame();
        drawer.showVersionString("edmcoverlay2 running", "white");

        draw_task::drawitem_t drawitem;
        try
        {
            drawitem = draw_task::parseJsonString(request);
        }
        catch (std::exception& e)
        {
            std::cerr << "Json parse failed with message: " << e.what() << std::endl;
            drawitem.drawmode = draw_task::drawmode_t::idk;
        }
        catch (...)
        {
            std::cerr << "Json parse failed with uknnown reason." << std::endl;
            drawitem.drawmode = draw_task::drawmode_t::idk;
        }
        if (drawitem.drawmode != draw_task::drawmode_t::idk)
            drawer.draw(drawitem);

        drawer.flushFrame();
    }
    return 0;
}

