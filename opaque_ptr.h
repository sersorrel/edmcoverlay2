#pragma once
#include <memory>
#include <type_traits>
#include "cm_ctors.h"

//Warning! This is unsafe pattern, do not repeat it!
//This is here just to convinient update existing C-code.
//Know the limits!

template <typename T>
class opaque_ptr
{
public:
    using value_t = T; //just handy, maybe
    using shared_t = std::shared_ptr<value_t>;
private:
    shared_t ptr{nullptr};
public:
    DEFAULT_COPYMOVE(opaque_ptr);
    opaque_ptr() = default;
    ~opaque_ptr() = default;

    opaque_ptr(const shared_t& s): ptr(s)
    {
    }

    opaque_ptr& operator = (const shared_t& s)
    {
        ptr = s;
        return *this;
    }

    operator value_t*() const
    {
        return ptr.get();
    }

    value_t* get() const
    {
        return ptr.get();
    }

    value_t* operator ->()
    {
        return ptr.get();
    }

    value_t* operator ->() const
    {
        return ptr.get();
    }

    operator bool() const
    {
        return static_cast<bool>(ptr);
    }

    void reset()
    {
        ptr.reset();
    }

    //this allows to cast to anything, darn unsafe. But macroses use it.
    template <typename Type>
    explicit operator Type() const
    {
        static_assert(std::is_pointer<Type>::value, "Expecting cast to pointer.");
        return reinterpret_cast<Type>(ptr.get());
    }
};

