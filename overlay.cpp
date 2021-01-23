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
#include <climits>
#include <chrono>
#include <X11/Xos.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/Xatom.h>
#include <X11/extensions/shape.h>
#include <X11/extensions/Xcomposite.h>
#include <X11/extensions/Xfixes.h>
#include <math.h>
#include <memory>
#include <csignal>
#include <fstream>
#include <stdio.h>
#include <functional>

#include "socket.hh"
#include "json_message.hh"
#include "drawables.h"
#include "opaque_ptr.h"
#include "colors_mgr.h"
#include "cm_ctors.h"

unsigned short port = 5020;

// Events for normal windows
constexpr static long BASIC_EVENT_MASK = (StructureNotifyMask | ExposureMask | PropertyChangeMask |
        EnterWindowMask | LeaveWindowMask | KeyPressMask | KeyReleaseMask |
        KeymapStateMask);

constexpr static long NOT_PROPAGATE_MASK = (KeyPressMask | KeyReleaseMask | ButtonPressMask |
        ButtonReleaseMask | PointerMotionMask | ButtonMotionMask);


opaque_ptr<Display> g_display;

static int          g_screen;
static Window       g_win;

/* Pixmap   g_bitmap; */
static Colormap g_colormap;


std::chrono::high_resolution_clock::time_point t1 = std::chrono::high_resolution_clock::now();
std::chrono::high_resolution_clock::time_point t2 = std::chrono::high_resolution_clock::now();
int fpsmeterc = 0;
#define FPSMETERSAMPLE 100
auto duration = std::chrono::duration_cast<std::chrono::microseconds>( t2 - t1 ).count();
std::string fpsstring = "";

static int window_xpos;
static int window_ypos;
static int window_width;
static int window_height;

static inline int SCALE_W(int x)
{
    return x * window_width / 1280.0f;
}

static inline int SCALE_H(int y)
{
    return y * window_height / 1024.0f;
}

static inline int SCALE_X(int x)
{
    return SCALE_W(x) + 20;
}


static inline int SCALE_Y(int y)
{
    return SCALE_H(y) + 40;
}


constexpr static long event_mask = (StructureNotifyMask | ExposureMask | PropertyChangeMask | EnterWindowMask | LeaveWindowMask | KeyRelease | ButtonPress | ButtonRelease |
                                    KeymapStateMask);

/*
static void list_fonts()
{
    char **fontlist{nullptr};
    int num_fonts{0};
    if ((fontlist = XListFonts (g_display, "*", 1000, &num_fonts)))
    {
        for (int i = 0; i < num_fonts; ++i)
            fprintf(stderr, "> %s\n", fontlist[i]);
        XFreeFontNames(fontlist);
    }
}
*/

// Create a window
static void createShapedWindow()
{
    Window root    = DefaultRootWindow(g_display);

    auto vinfo = allocCType<XVisualInfo>();
    XMatchVisualInfo(g_display, DefaultScreen(g_display), 32, TrueColor, &vinfo);
    g_colormap = XCreateColormap(g_display, DefaultRootWindow(g_display), vinfo.visual, AllocNone);

    auto attr = allocCType<XSetWindowAttributes>();
    attr.background_pixmap = None;
    attr.background_pixel = 0;
    attr.border_pixel = 0;
    attr.win_gravity = NorthWestGravity;
    attr.bit_gravity = ForgetGravity;
    attr.save_under = 1;
    attr.event_mask = BASIC_EVENT_MASK;
    attr.do_not_propagate_mask = NOT_PROPAGATE_MASK;
    attr.override_redirect = 1; // OpenGL > 0
    attr.colormap = g_colormap;

    //unsigned long mask = CWBackPixel|CWBorderPixel|CWWinGravity|CWBitGravity|CWSaveUnder|CWEventMask|CWDontPropagate|CWOverrideRedirect;
    unsigned long mask = CWColormap | CWBorderPixel | CWBackPixel | CWEventMask | CWWinGravity | CWBitGravity | CWSaveUnder | CWDontPropagate | CWOverrideRedirect;

    g_win = XCreateWindow(g_display, root, window_xpos, window_ypos, window_width, window_height, 0, vinfo.depth, InputOutput, vinfo.visual, mask, &attr);

    /* g_bitmap = XCreateBitmapFromData (g_display, RootWindow(g_display, g_screen), (char *)myshape_bits, myshape_width, myshape_height); */

    //XShapeCombineMask(g_display, g_win, ShapeBounding, 900, 500, g_bitmap, ShapeSet);
    XShapeCombineMask(g_display, g_win, ShapeInput, 0, 0, None, ShapeSet );

    // We want shape-changed event too
    XShapeSelectInput (g_display, g_win, ShapeNotifyMask);

    // Tell the Window Manager not to draw window borders (frame) or title.
    auto wattr = allocCType<XSetWindowAttributes>();
    wattr.override_redirect = 1;
    XChangeWindowAttributes(g_display, g_win, CWOverrideRedirect, &wattr);


    //pass through input
    XserverRegion region = XFixesCreateRegion (g_display, NULL, 0);
    //XFixesSetWindowShapeRegion (g_display, w, ShapeBounding, 0, 0, 0);
    XFixesSetWindowShapeRegion (g_display, g_win, ShapeInput, 0, 0, region);
    XFixesDestroyRegion (g_display, region);

    // Show the window
    XMapWindow(g_display, g_win);
}


static void openDisplay()
{
    g_display = std::shared_ptr<Display>(XOpenDisplay(0), [](Display * p)
    {
        if (p)
            XCloseDisplay(p);
    });

    if (!g_display)
    {
        std::cerr << "Failed to open X display" << std::endl;
        exit(-1);
    }

    Atom cmAtom = XInternAtom(g_display, "_NET_WM_CM_S0", 0);
    Window cmOwner = XGetSelectionOwner(g_display, cmAtom);
    if (!cmOwner)
    {
        std::cerr << "Composite manager is absent." << std::endl;
        std::cerr << "Please check instructions: https://wiki.archlinux.org/index.php/Xcompmgr" << std::endl;
        exit(-1);
    }
    g_screen    = DefaultScreen(g_display);

    // Has shape extions?
    int     shape_event_base;
    int     shape_error_base;

    if (!XShapeQueryExtension (g_display, &shape_event_base, &shape_error_base))
    {
        std::cerr << "NO shape extension in your system !" << std::endl;
        exit (-1);
    }
}





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
    window_xpos = atoi(argv[1]);
    window_ypos = atoi(argv[2]);
    window_width = atoi(argv[3]);
    window_height = atoi(argv[4]);
    std::cout << "edmcoverlay2: overlay starting up..." << std::endl;
    signal(SIGINT, sighandler);
    signal(SIGTERM, sighandler);

    openDisplay();

    MyColorMap colors(g_display, g_screen);
    const auto& white = colors.get("white");
    const auto& black = colors.get("black");
    const auto& green = colors.get("green");
    const auto& transparent = colors.get("transparent");

    createShapedWindow();

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

    const auto allocGlobGC = []()
    {
        return opaque_ptr<_XGC>(std::shared_ptr<_XGC>(XCreateGC(g_display, g_win, 0, nullptr), [](auto * p)
        {
            if (p)
                XFreeGC(g_display, p);
            XFlush(g_display);
        }));
    };

    const auto allocFont = [](const char* fontname)
    {
        XFontStruct* font = XLoadQueryFont(g_display, fontname);
        if (!font)
        {
            std::cerr << "Could not load font [" << fontname << "], using some fixed default." << std::endl;
            font = XLoadQueryFont(g_display, "fixed");
        }

        return opaque_ptr<XFontStruct>(std::shared_ptr<XFontStruct>(font, [](XFontStruct * p)
        {
            if (p)
                XFreeFont(g_display, p);
        }));
    };

    const auto cleanGC = [&white, &transparent](GC gc)
    {
        if (gc)
        {
            XSetBackground(g_display, gc, white.pixel);
            XSetForeground(g_display, gc, transparent.pixel);
            XFillRectangle(g_display, g_win, gc, 0, 0, window_width, window_height);
        }
    };

    const auto normalfont = allocFont("9x15bold");
    const auto largefont = allocFont("12x24");

    const auto print_version = [&normalfont, &cleanGC, &black](GC gc, const XColor & color, int& width, const char* version)
    {
        cleanGC(gc);
        XSetForeground(g_display, gc, black.pixel);
        const auto len = strlen(version);
        const auto scalex = SCALE_X(0);

        if (width < 0)
            width = XTextWidth(normalfont, version, len) + 5 + scalex;
        XFillRectangle(g_display, g_win, gc, 0, 0, width, 50);
        XSetForeground(g_display, gc, color.pixel);
        XDrawString(g_display, g_win, gc, scalex, SCALE_Y(0) - 10, version, len);
    };


    {
        const auto gc = allocGlobGC();
        int w = -1;
        print_version(gc, green, w, "edmcoverlay2 overlay process: running!");
        std::cout << "edmcoverlay2: overlay ready." << std::endl;
    }


    int version_w = -1;
    while (true)
    {
        auto socket = server->accept_autoclose();
        std::string request = read_response(*socket);

        //std::cout << "edmcoverlay2: overlay got request: " << request << std::endl;

        const auto gc = allocGlobGC();
        print_version(gc, white, version_w, "edmcoverlay2 running");

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
        if (drawitem.drawmode == draw_task::drawmode_t::idk)
            continue;


        if (drawitem.drawmode == draw_task::drawmode_t::text)
        {
            const auto& font = (drawitem.text.size == "large") ? largefont : normalfont;
            XSetFont(g_display, gc, font->fid);
            XSetForeground(g_display, gc, colors.get(drawitem.color).pixel);
            XDrawString(g_display, g_win, gc, SCALE_X(drawitem.x), SCALE_Y(drawitem.y),
                        drawitem.text.text.c_str(), strlen(drawitem.text.text.c_str()));
        }
        else
        {
            /* cout << "edmcoverlay2: drawing a shape" << endl; */
            XSetForeground(g_display, gc, colors.get(drawitem.color).pixel);

            const bool had_vec = draw_task::ForEachVectorPointsPair(drawitem, [&gc](int x1, int y1, int x2, int y2)
            {
                XDrawLine(g_display, g_win, gc, SCALE_X(x1), SCALE_Y(y1), SCALE_X(x2), SCALE_Y(y2));
            });

            if (!had_vec && drawitem.shape.shape == "rect")
            {
                /* cout << "edmcoverlay2: specifically, a rect" << endl; */
                // TODO distinct fill/edge colour
                XDrawRectangle(g_display, g_win, gc, SCALE_X(drawitem.x), SCALE_Y(drawitem.y), SCALE_W(drawitem.shape.w), SCALE_H(drawitem.shape.h));
            }
        }
    }
    return 0;
}

