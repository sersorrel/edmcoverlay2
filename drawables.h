#pragma once
#include <string>
#include <iostream>
#include "json.hpp"

namespace draw_task
{
    using json = nlohmann::json;

    enum class drawmode_t
    {
        idk,
        text,
        shape,
    };

    struct drawitem_t
    {
        drawmode_t drawmode{drawmode_t::idk};
        // common
        int x{0};
        int y{0};
        std::string color;

        struct drawtext_t
        {
            // text
            std::string text;
            std::string size;
        } text;

        struct drawshape_t
        {
            // shape
            std::string shape;
            std::string fill;
            int w{0};
            int h{0};
            json vect;
        } shape;
    };

    /* text message: id, text, color, x, y, ttl, size
    * shape message: id, shape, color, fill, x, y, w, h, ttl
    * color: "red", "yellow", "green", "blue", "#rrggbb"
    * shape: "rect"
    * size: "normal", "large"
    */
    inline drawitem_t parseJsonString(const std::string& src)
    {
        //hate chained IFs, lets do it more readable....
#define FUNC_PARAMS const json& node, drawitem_t& drawitem
#define LHDR [](FUNC_PARAMS)->void
#define NINT node.get<int>()
#define NSTR node.get<std::string>()
        const static std::map<std::string, std::function<void(FUNC_PARAMS)>> processors =
        {
            {"x", LHDR{drawitem.x = NINT;}},
            {"y", LHDR{drawitem.y = NINT;}},
            {"color", LHDR{drawitem.color = NSTR;}},
            {"text", LHDR{drawitem.drawmode = drawmode_t::text; drawitem.text.text = NSTR;}},
            {"size", LHDR{drawitem.drawmode = drawmode_t::text; drawitem.text.size = NSTR;}},
            {"shape", LHDR{drawitem.drawmode = drawmode_t::shape; drawitem.shape.shape = NSTR;}},
            {"fill", LHDR{drawitem.drawmode = drawmode_t::shape; drawitem.shape.fill = NSTR;}},
            {"w", LHDR{drawitem.drawmode = drawmode_t::shape; drawitem.shape.w = NINT;}},
            {"h", LHDR{drawitem.drawmode = drawmode_t::shape; drawitem.shape.h = NINT;}},
            {"vector", LHDR{drawitem.drawmode = drawmode_t::shape; drawitem.shape.vect = node;}}
        };
#undef NINT
#undef NSTR
#undef LHDR
#undef FUNC_PARAMS

        drawitem_t drawitem;
        if (!src.empty())
        {
            const auto jsrc = json::parse(src)[0]; //fixme: python sends array of objects, where there is 1 object only, i.e. [{....}]
            for (const auto& kv : jsrc.items())
            {

                //std::cout << "Key: [" << kv.key() << "]" << std::endl;

                const auto it = processors.find(kv.key());
                if (it != processors.end())
                {
                    const auto prev_mode  = drawitem.drawmode;
                    it->second(kv.value(), drawitem);
                    if (prev_mode != drawmode_t::idk && drawitem.drawmode != prev_mode)
                    {
                        std::cout << "Mode was double switched text/shape in the same JSON. Ignoring."  << std::endl;
                        drawitem.drawmode = drawmode_t::idk;
                        break;
                    }
                }
                else
                    std::cout << "bad key: " << kv.key() << std::endl;
            }
        }
        return drawitem;
    }

    //generates lines (x1;y1)-(x2;y2) and calls user callback with it
    //to avoid copy-paste of code for different output devices
    template <class Callback>
    inline bool ForEachVectorPointsPair(const drawitem_t& src, const Callback& func)
    {
        if (src.drawmode == draw_task::drawmode_t::shape && src.shape.shape == "vect")
        {
            constexpr static int UNINIT_COORD = 1000000;
            int x1 = UNINIT_COORD, y1 = UNINIT_COORD, x2 = UNINIT_COORD, y2 = UNINIT_COORD;
            for (const auto& node_ : src.shape.vect.items())
            {
                // node_ is a point
                const auto& val = node_.value();
                int x = val["x"].get<int>();
                int y = val["y"].get<int>();

                if (x1 == UNINIT_COORD)
                {
                    x1 = x;
                    y1 = y;
                    continue;
                }
                if (x2 == UNINIT_COORD)
                {
                    x2 = x;
                    y2 = y;
                    func(x1, y1, x2, y2);
                    continue;
                }
                x1 = x2;
                y1 = y2;
                x2 = x;
                y2 = y;
                func(x1, y1, x2, y2);
            }
            return true;
        }
        return false;
    }
}
