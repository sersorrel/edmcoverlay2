#pragma once

//test must be used OUTSIDE class definition like
/*
 * class A{};
 * TEST_MOVE_NOEX(A);
*/
#define TEST_MOVE_NOEX(TYPE) static_assert(std::is_nothrow_move_constructible<TYPE>::value && std::is_nothrow_move_assignable<TYPE>::value, " Should be noexcept Moves.")

//helper macros to declare/delete copy-moves
#define DEFAULT_COPYMOVE(TYPE) TYPE(const TYPE&) = default;TYPE(TYPE&&) = default;TYPE& operator=(const TYPE&) = default;TYPE& operator=(TYPE&&) = default
#define NO_COPYMOVE(TYPE) TYPE(const TYPE&) = delete;TYPE(TYPE&&) = delete;TYPE& operator=(const TYPE&) = delete;TYPE& operator=(TYPE&&) = delete
#define MOVEONLY_ALLOWED(TYPE) TYPE(const TYPE&) = delete;TYPE(TYPE&&) = default;TYPE& operator=(const TYPE&) = delete;TYPE& operator=(TYPE&&) = default



//only stack allocation allowed
#define STACK_ONLY static void *operator new     (size_t) = delete; \
                   static void *operator new[]   (size_t) = delete
