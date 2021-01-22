#pragma once
#include <map>
#include <string>
#include <X11/Xlib.h>
#include <stdint.h>
#include <exception>
#include <algorithm>

#include "opaque_ptr.h"
#include "cm_ctors.h"

class MyColorMap
{
private:
    const opaque_ptr<Display>& g_display;
    const int g_screen;
    struct rgba
    {
        uint8_t red{0xFF};
        uint8_t green{0xFF};
        uint8_t blue{0xFF};
        uint8_t alpha{0xFF};
    };
    std::map<std::string, XColor> known_colors;

public:
    NO_COPYMOVE(MyColorMap);
    ~MyColorMap() = default;
    MyColorMap() = delete;

    //we take reference here to object, so this map must be destroyed prior object destroyed
    MyColorMap(const opaque_ptr<Display>& g_display, int g_screen):
        g_display(g_display),
        g_screen(g_screen)
    {
    }

    const XColor& get(std::string name)
    {
        //making string lowercased as we use names in lowercase everywhere here
        std::transform(name.begin(), name.end(), name.begin(),
                       [](auto c)
        {
            return std::tolower(c);
        });

        //if we know that color just return it
        const auto it = known_colors.find(name);
        if (it != known_colors.end())
            return it->second;

        //otherwise request creation and return
        known_colors[name] = color_from_name(name);
        return known_colors[name];
    }

private:
    XColor color_from_name(const std::string& name) const
    {
        const static std::map<std::string, rgba> named_colors =
        {
            {"transparent", {0, 0, 0, 0}},
            {"white", {255, 255, 255, 255}},
            {"black", {0, 0, 0, 100}},
            {"blue", {0, 0, 255, 255}},
            {"yellow", {255, 255, 0, 255}},
            {"green", {0, 255, 0, 255}},
            {"red", {255, 0, 0, 255}},
        };

        rgba curr;

        if (name.rfind("#", 0) == 0)
        {
            //direct hex color code
            if (name.length() == 7)
            {
                unsigned int r, g, b;
                sscanf(name.c_str(), "#%02x%02x%02x", &r, &g, &b);
                curr = rgba{static_cast<uint8_t>(r), static_cast<uint8_t>(g),
                            static_cast<uint8_t>(b), static_cast<uint8_t>(0xFF)};
            }
        }
        else
        {
            const auto it = named_colors.find(name);
            if (it != named_colors.end())
                curr = it->second;
        }

        return createXColorFromRGBA(curr);
    }

    XColor createXColorFromRGBA(const rgba& c) const
    {
        auto color = allocCType<XColor>();

        // m_color.red = red * 65535 / 255;
        color.red = (static_cast<uint32_t>(c.red) * 0xFFFFu) / 0xFFu;
        color.green = (static_cast<uint32_t>(c.green) * 0xFFFFu) / 0xFFu;
        color.blue = (static_cast<uint32_t>(c.blue) * 0xFFFFu) / 0xFFu;
        color.flags = DoRed | DoGreen | DoBlue;

        if (!XAllocColor(g_display, DefaultColormap(g_display, g_screen), &color))
            throw std::runtime_error("createXColorFromRGB: Cannot create color");


        *(&color.pixel) = ((*(&color.pixel)) & 0x00ffffffu) | (c.alpha << 24);
        return color;
    }
};
