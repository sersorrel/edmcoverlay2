#pragma once
#include "drawables.h"
#include "cm_ctors.h"

//virtual base class (interface) for doing output
class OutputLayer
{
protected:
    OutputLayer() = default;
public:
    NO_COPYMOVE(OutputLayer); //we don't want devices be copyable
    virtual ~OutputLayer() = default; //making sure we can proper delete children

    virtual void cleanFrame() = 0;
    virtual void flushFrame() = 0;
    virtual void showVersionString(const std::string& src, const std::string& color) = 0;
    virtual void draw(const draw_task::drawitem_t& drawitem) = 0;
};

template <typename T, typename... Args>
inline T& getStaticObject(Args... args)
{
    static T obj(args...);
    return obj;
}
