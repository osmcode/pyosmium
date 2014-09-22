TARGETS = osmium

# location of the Python header files
 
PYTHON_VERSION = 2.7
PYTHON_INCLUDE = /usr/include/python$(PYTHON_VERSION)
 
# location of the Boost Python include files and library
 
BOOST_INC = /usr/include
BOOST_LIB = /usr/lib/x86_64-linux-gnu/
OSMIUM_INC ?= ../libosmium/include/

CXXFLAGS += -Ilib/include -I$(PYTHON_INCLUDE) -I$(BOOST_INC) -I$(OSMIUM_INC)
CXXFLAGS += -fPIC -std=c++11
CXX = clang++-3.4

SRCDIR_CC = lib
SRCDIR_PY = osmium

LIB_EXPAT  := -lexpat
LIB_PBF    := -pthread -lz -lprotobuf-lite -losmpbf
LIB_GZIP   := -lz
LIB_BZIP2  := -lbz2


LIBS  = -L$(BOOST_LIB) -lboost_python-py27 
LIBS += -L/usr/lib/python$(PYTHON_VERSION)/config -lpython$(PYTHON_VERSION)
LIBS += $(LIB_EXPAT) $(LIB_PBF) $(LIB_GZIP) $(LIB_BZIP2)

LIB_TARGETS = $(addsuffix .so, $(addprefix $(SRCDIR_PY)/_, $(TARGETS)))

all: $(LIB_TARGETS)
 
$(LIB_TARGETS): $(SRCDIR_PY)/_%.so: $(patsubst %.cc,%.o,$(SRCDIR_CC)/%.cc)
	$(CXX) -shared -Wl,--export-dynamic $^ $(LIBS) -o $@

clean:
	rm -f $(SRCDIR_CC)/*.o $(SRCDIR_CC)/*/*.o $(SRCDIR_PY)/*.so
 
