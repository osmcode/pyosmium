#ifndef PYOSMIUM_WIN_BOOST_FIX_HPP
#define PYOSMIUM_WIN_BOOST_FIX_HPP

// workarodund for Visual Studio 2015 Update 3
// https://connect.microsoft.com/VisualStudio/Feedback/Details/2852624
#if (_MSC_VER > 1800 && _MSC_FULL_VER > 190023918)
namespace boost {

    template <>
    const volatile osmium::index::map::Map<unsigned __int64,class osmium::Location>*
    get_pointer(const volatile osmium::index::map::Map<unsigned __int64,
                class osmium::Location> *c)
    {
       return c;
    }
}
#endif


#endif
