#include "xoverlayoutput.h"
#include "colors_mgr.h"
#include <X11/Xos.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/Xatom.h>
#include <X11/extensions/shape.h>
#include <X11/extensions/Xcomposite.h>
#include <X11/extensions/Xfixes.h>

// Events for normal windows
constexpr static long BASIC_EVENT_MASK = StructureNotifyMask | ExposureMask | PropertyChangeMask |
        EnterWindowMask | LeaveWindowMask | KeyPressMask | KeyReleaseMask | KeymapStateMask;

constexpr static long NOT_PROPAGATE_MASK = KeyPressMask | KeyReleaseMask | ButtonPressMask |
        ButtonReleaseMask | PointerMotionMask | ButtonMotionMask;

constexpr static long event_mask = StructureNotifyMask | ExposureMask | PropertyChangeMask | EnterWindowMask |
                                   LeaveWindowMask | KeyRelease | ButtonPress | ButtonRelease | KeymapStateMask;

class XPrivateAccess
{
public:
    XPrivateAccess() = delete;
    XPrivateAccess(int window_xpos, int window_ypos, int window_width, int window_height):
        window_xpos(window_xpos), window_ypos(window_ypos),
        window_width(window_width), window_height(window_height)
    {
        openDisplay();
        createShapedWindow();
        single_gc = allocGlobGC();
        colors.reset(new MyXOverlayColorMap(g_display, g_screen));
        normalfont = allocFont("9x15bold");
        largefont = allocFont("12x24");
    }

    ~XPrivateAccess()
    {
        normalfont.reset();
        largefont.reset();
        colors.reset();
        single_gc.reset();
        g_display.reset();
    }

    int SCALE_W(int x) const
    {
        return x * window_width / 1280.0f;
    }

    int SCALE_H(int y) const
    {
        return y * window_height / 1024.0f;
    }

    int SCALE_X(int x) const
    {
        return SCALE_W(x) + 20;
    }

    int SCALE_Y(int y) const
    {
        return SCALE_H(y) + 40;
    }

    opaque_ptr<_XGC> allocGlobGC() const
    {
        return opaque_ptr<_XGC>(std::shared_ptr<_XGC>(XCreateGC(g_display, g_win, 0, nullptr), [this](auto * p)
        {
            if (p)
                XFreeGC(g_display, p);
            XFlush(g_display);
        }));
    }

    opaque_ptr<XFontStruct> allocFont(const char* fontname) const
    {
        XFontStruct* font = XLoadQueryFont(g_display, fontname);
        if (!font)
        {
            std::cerr << "Could not load font [" << fontname << "], using some fixed default." << std::endl;
            font = XLoadQueryFont(g_display, "fixed");
        }

        return opaque_ptr<XFontStruct>(std::shared_ptr<XFontStruct>(font, [this](XFontStruct * p)
        {
            if (p)
                XFreeFont(g_display, p);
        }));
    }

    void cleanGC(GC gc) const
    {
        if (gc)
        {
            const auto& white = colors->get("white");
            const auto& transparent = colors->get("transparent");
            XSetBackground(g_display, gc, white.pixel);
            XSetForeground(g_display, gc, transparent.pixel);
            XFillRectangle(g_display, g_win, gc, 0, 0, window_width, window_height);
        }
    }

    void cleanGC() const
    {
        cleanGC(single_gc);
    }

    void flush() const
    {
        XFlush(g_display);
    }
private:
    void openDisplay()
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
    // Create a window
    void createShapedWindow()
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
public:
    const int window_xpos;
    const int window_ypos;
    const int window_width;
    const int window_height;

    opaque_ptr<Display> g_display{nullptr};
    opaque_ptr<_XGC> single_gc{nullptr};
    std::shared_ptr<MyXOverlayColorMap> colors{nullptr};
    opaque_ptr<XFontStruct> normalfont{nullptr};
    opaque_ptr<XFontStruct> largefont{nullptr};

    int          g_screen{0};
    Window       g_win{0};
    Colormap g_colormap{0};

};

//**********************************************************************************************************************
//*****************************XOverlayOutput***************************************************************************
//**********************************************************************************************************************

XOverlayOutput::XOverlayOutput(int window_xpos, int window_ypos, int window_width, int window_height):
    xserv(new XPrivateAccess(window_xpos, window_ypos, window_width, window_height))
{
    cleanFrame();
}

XOverlayOutput::~XOverlayOutput()
{
    xserv.reset();
}

void XOverlayOutput::cleanFrame()
{
    xserv->cleanGC();
}

void XOverlayOutput::flushFrame()
{
    xserv->flush();
}

void XOverlayOutput::showVersionString(const std::string &version, const std::string &color)
{
    const auto& gc = xserv->single_gc;
    const auto& g_display = xserv->g_display;
    const auto& g_win = xserv->g_win;
    const auto& black = xserv->colors->get("black");

    XSetForeground(g_display, gc, black.pixel);
    const auto len = version.length();
    const auto scalex = xserv->SCALE_X(0);


    const int width = XTextWidth(xserv->normalfont, version.c_str(), len) + 5 + scalex;
    XFillRectangle(g_display, g_win, gc, 0, 0, width, 50);
    XSetForeground(g_display, gc, xserv->colors->get(color).pixel);
    XDrawString(g_display, g_win, gc, scalex, xserv->SCALE_Y(0) - 10, version.c_str(), len);
}

void XOverlayOutput::draw(const draw_task::drawitem_t &drawitem)
{
    const auto& gc = xserv->single_gc;
    const auto& g_display = xserv->g_display;
    const auto& g_win = xserv->g_win;

    if (drawitem.drawmode == draw_task::drawmode_t::text)
    {
        const auto& font = (drawitem.text.size == "large") ? xserv->largefont : xserv->normalfont;
        XSetFont(g_display, gc, font->fid);
        XSetForeground(g_display, gc, xserv->colors->get(drawitem.color).pixel);
        XDrawString(g_display, g_win, gc, xserv->SCALE_X(drawitem.x), xserv->SCALE_Y(drawitem.y),
                    drawitem.text.text.c_str(), strlen(drawitem.text.text.c_str()));
    }
    else
    {
        /* cout << "edmcoverlay2: drawing a shape" << endl; */
        XSetForeground(g_display, gc, xserv->colors->get(drawitem.color).pixel);

        const bool had_vec = draw_task::ForEachVectorPointsPair(drawitem, [&](int x1, int y1, int x2, int y2)
        {
            XDrawLine(g_display, g_win, gc, xserv->SCALE_X(x1),
                      xserv->SCALE_Y(y1), xserv->SCALE_X(x2), xserv->SCALE_Y(y2));
        });

        if (!had_vec && drawitem.shape.shape == "rect")
        {
            /* cout << "edmcoverlay2: specifically, a rect" << endl; */
            // TODO distinct fill/edge colour
            XDrawRectangle(g_display, g_win, gc, xserv->SCALE_X(drawitem.x),
                           xserv->SCALE_Y(drawitem.y), xserv->SCALE_W(drawitem.shape.w), xserv->SCALE_H(drawitem.shape.h));
        }
    }
}
