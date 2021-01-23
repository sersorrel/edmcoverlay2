#pragma once
#include "layer_out.h"
#include "opaque_ptr.h"
#include <memory>

//have to use such a trick, so this H file does not have too many includes
class XPrivateAccess;

class XOverlayOutput : public OutputLayer
{
protected:
    XOverlayOutput(int window_xpos, int window_ypos, int window_width, int window_height);
    friend XOverlayOutput& getStaticObject<XOverlayOutput>(int, int, int, int);
public:
    static OutputLayer& get(int window_xpos, int window_ypos, int window_width, int window_height)
    {
        return getStaticObject<XOverlayOutput>(window_xpos, window_ypos, window_width, window_height);
    }
    ~XOverlayOutput() override;

    void cleanFrame() override;
    void flushFrame() override;

    void showVersionString(const std::string& version, const std::string& color) override;
    void draw(const draw_task::drawitem_t& drawitem) override;
private:
    std::shared_ptr<XPrivateAccess> xserv{nullptr};
};
