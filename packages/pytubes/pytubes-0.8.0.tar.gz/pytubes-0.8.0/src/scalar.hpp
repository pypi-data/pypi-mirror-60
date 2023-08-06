#pragma once

#include "util/slice.hpp"
#include "util/pyobj.hpp"
#include "util/json/json.hpp"
#include "util/xsv.hpp"

namespace ss{

template<class X, typename... Ts> struct make_ignore { typedef X type;};
template<class X, typename... Ts> using ignore_t = typename make_ignore<X, Ts...>::type;
template<typename... Ts> using void_t = typename make_ignore<void, Ts...>::type;
template<typename... Ts> using bool_t = typename make_ignore<bool, Ts...>::type;
template<bool X, class Y> using enable_if_t = typename std::enable_if<X, Y>::type;


namespace iter{

    static const char null = 0;

    using NullType = std::tuple<>;

    struct Utf8 : ByteSlice {
        using el_t = uint8_t;
        Utf8() : ByteSlice() {}
        Utf8(const uint8_t *start, size_t len): ByteSlice(start, len) {}
        Utf8(const uint8_t *begin, const uint8_t *end, bool _): ByteSlice(begin, end, _) {}
        Utf8(const Slice<uint8_t> &src) : ByteSlice(src) {}
        Utf8(const Utf8 &src) : ByteSlice(src.start, src.len) {}
        Utf8(const std::basic_string<uint8_t> &src) : ByteSlice(src) {}
        Utf8(const std::vector<uint8_t> &src) : ByteSlice(src) {}
        inline bool operator==(const Utf8 &other) const {
            return len == other.len && std::equal(begin(), end(), other.begin());
        }
        inline bool operator!=(const Utf8 &other) const {
            return !(*this == other);
        }
    };
    using JsonUtf8 = json::Value<uint8_t>;

    enum class ScalarType{
        Null,
        Bool,
        Int64,
        Float,
        ByteSlice,
        Utf8,
        Object,
        JsonUtf8,
        Tsv,
        Csv
    };

    template<class T> struct ScalarType_t {  };
    template<> struct ScalarType_t<NullType> {
        constexpr static const ScalarType scalar_type = ScalarType::Null;
        using type = NullType;
        static const char * const type_name() { return "Null"; };
    };
    template<> struct ScalarType_t<bool> {
        constexpr static const ScalarType scalar_type = ScalarType::Bool;
        using type = bool;
        static const char * const type_name() { return "Bool"; };
    };
    template<> struct ScalarType_t<int64_t> {
        constexpr static const ScalarType scalar_type = ScalarType::Int64;
        using type = int64_t;
        static const char * const type_name() { return "Int64"; };
    };
    template<> struct ScalarType_t<double> {
        constexpr static const ScalarType scalar_type = ScalarType::Float;
        using type = double;
        static const char * const type_name() { return "Float"; };
    };
    template<> struct ScalarType_t<ByteSlice> {
        constexpr static const ScalarType scalar_type = ScalarType::ByteSlice;
        using type = ByteSlice;
        static const char * const type_name() { return "Bytes"; };
    };
    template<> struct ScalarType_t<Utf8> {
        constexpr static const ScalarType scalar_type = ScalarType::Utf8;
        using type = Utf8;
        static const char * const type_name() { return "Utf8"; };
    };
    template<> struct ScalarType_t<PyObj> {
        constexpr static const ScalarType scalar_type = ScalarType::Object;
        using type = PyObj;
        static const char * const type_name() { return "Object"; };
    };
    template<> struct ScalarType_t<JsonUtf8> {
        constexpr static const ScalarType scalar_type = ScalarType::JsonUtf8;
        using type = JsonUtf8;
        static const char * const type_name() { return "Json"; };
    };
    template<> struct ScalarType_t<TsvRow> {
        constexpr static const ScalarType scalar_type = ScalarType::Tsv;
        using type = TsvRow;
        static const char * const type_name() { return "Tsv"; };
    };
    template<> struct ScalarType_t<CsvRow> {
        constexpr static const ScalarType scalar_type = ScalarType::Csv;
        using type = CsvRow;
        static const char * const type_name() { return "Csv"; };
    };

    template<class T, class Enable>
    struct type_name_op{
        constexpr inline const char *operator()() const { return ScalarType_t<T>::type_name(); }
    };

    template<class T>
    constexpr ScalarType dtype_from_type() { return ScalarType_t<T>::scalar_type; }

    template<template <class U, class Enable=bool> class T, class... Args>
    /* constexpr(>c++14) */ inline
    decltype(T<NullType, bool>()(std::declval<Args &&>()...))
    dispatch_type(ScalarType type, Args &&... args) {
        switch (type) {
            case ScalarType::Null: return T<NullType, bool>()(args...);
            case ScalarType::Bool: return T<bool, bool>()(args...);
            case ScalarType::Int64: return T<int64_t, bool>()(args...);
            case ScalarType::Float: return T<double, bool>()(args...);
            case ScalarType::ByteSlice: return T<ByteSlice, bool>()(args...);
            case ScalarType::Utf8: return T<Utf8, bool>()(args...);
            case ScalarType::Object: return T<PyObj, bool>()(args...);
            case ScalarType::JsonUtf8: return T<JsonUtf8, bool>()(args...);
            case ScalarType::Tsv: return T<TsvRow, bool>()(args...);
            case ScalarType::Csv: return T<CsvRow, bool>()(args...);
            default:  throw_py<RuntimeError>("Got unexpected dtype value:  ", (size_t)type);
        }
        return T<NullType, bool>()(args...);
    }


    template<class T> struct field_type_t {using type = NullType;};
    template<> struct field_type_t<JsonUtf8> {using type = JsonUtf8;};
    template<> struct field_type_t<TsvRow> {using type = ByteSlice;};
    template<> struct field_type_t<CsvRow> {using type = ByteSlice;};
    template<> struct field_type_t<PyObj> {using type = PyObj;};

    template<class T>
    constexpr inline ScalarType field_dtype() {
        using field_type = typename field_type_t<T>::type;
        return ScalarType_t<field_type>::scalar_type;
    }

    template<class T, class Enable>
    struct field_dtype_op{
        constexpr inline ScalarType operator()() const { return field_dtype<T>(); }
    };

    inline ScalarType field_dtype_from_dtype(ScalarType dtype) {
        return dispatch_type<field_dtype_op>(dtype);
    }


    inline const char *type_name(ScalarType type) {
        return dispatch_type<type_name_op>(type);
    }


    inline std::ostream & operator<< (std::ostream &out, NullType const &t) {
        return out << "Null";
    }

    inline std::ostream & operator<< (std::ostream &out, PyObj const &t) {
        return out << "PyObj[" << t.obj << "]";
    }
    inline std::ostream & operator<< (std::ostream &out, std::basic_string<unsigned char> const &v) {
        return out << std::string((const char *)v.c_str(), v.length());
    }

}}


namespace std{
    template<> struct hash<ss::iter::NullType>{
        inline std::size_t operator()(const ss::iter::NullType& val) const {
            return 0;
        }
    };

    template<> struct hash<ss::iter::Utf8>{
        inline std::size_t operator()(const ss::iter::Utf8& val) const {
            return CityHash<sizeof(size_t)>((const char *)val.start, val.len);
        }
    };
}