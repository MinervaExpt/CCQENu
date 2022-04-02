#ifndef CategoryHolder_h
#define CategoryHolder_h

#include <vector>;
#include "TH1D.h"
#include "MnvH1D.h"

namespace fits{
    class CategoryHolder{
        public:
        std::vector<TH1D*> cats;
    }
}
