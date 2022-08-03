#ifndef CutFromConfig_H
#define CutFromConfig_H
#include "utils/NuConfig.h"
#include "PlotUtils/Cut.h"
#include "include/CVUniverse.h"
#include "include/CVFunctions.h"

namespace PlotUtils{

///// this gets a result out of the config and takes care of the type.
//
//template <class var_t>
//var_t getValue(const NuConfig config, const std::string key){
//  return typeid(var_t) == typeid(double) ? config.GetDouble(key):config.GetInt(key);
//}

template <class UNIVERSE, class EVENT = detail::empty>
class MaximumFromConfigFunc: public Cut<UNIVERSE, EVENT>
{
public:
    typedef std::function<double(const UNIVERSE&)> PointerToCVUniverseFunction;
    MaximumFromConfigFunc(const NuConfig& config, CVFunctions<UNIVERSE>& functions): Cut<UNIVERSE, EVENT>(config.GetString("name")+"<="+(config.GetString("max"))), m_Max(config.GetDouble("max")), m_func(functions.GetRecoFunction(config.GetString("variable")))
    {
    }
#ifndef __GCCXML__
    virtual ~MaximumFromConfigFunc() = default;
#endif
private:
    bool checkCut(const UNIVERSE& univ, EVENT& /*evt*/) const override
    {
        return m_func(univ) <= m_Max;
    }
    const PointerToCVUniverseFunction m_func;
    const double m_Max; //Maximum value of UNIVERSE::var that passes this Cut
};



template <class UNIVERSE, class EVENT = detail::empty>
class MinimumFromConfigFunc: public Cut<UNIVERSE, EVENT>
{
public:
    typedef std::function<double(const UNIVERSE&)> PointerToCVUniverseFunction;
    MinimumFromConfigFunc(const NuConfig& config, CVFunctions<UNIVERSE>& functions): Cut<UNIVERSE, EVENT>(config.GetString("name")+">="+std::to_string( config.GetDouble("min"))), m_Min(config.GetDouble("min")), m_func(functions.GetRecoFunction(config.GetString("variable")))
    {
    }
#ifndef __GCCXML__
    virtual ~MinimumFromConfigFunc() = default;
#endif
private:
    bool checkCut(const UNIVERSE& univ, EVENT& /*evt*/) const override
    {
        return m_func(univ) >= m_Min;
    }
    const PointerToCVUniverseFunction m_func;
    const double m_Min; //Minimum value of UNIVERSE::var that passes this Cut
};


template <class UNIVERSE, class EVENT = detail::empty>
class IsSameFromConfigFunc: public Cut<UNIVERSE, EVENT>
{
public:
    typedef std::function<double(const UNIVERSE&)> PointerToCVUniverseIntFunction;
    IsSameFromConfigFunc(const NuConfig& config, CVFunctions<UNIVERSE>& functions): Cut<UNIVERSE, EVENT>(config.GetString("name")+ "==" + std::to_string( config.GetInt("equals"))), m_Matches(config.GetInt("equals")), m_func(functions.GetRecoIntFunction(config.GetString("variable")))
    {
        
    }
#ifndef __GCCXML__
    virtual ~IsSameFromConfigFunc() = default;
#endif
private:
    bool checkCut(const UNIVERSE& univ, EVENT& /*evt*/) const override
    {
        //std::cout << Cut<UNIVERSE, EVENT>::getName() << " " << m_func(univ) << " "  << m_Matches << std::endl;
        return m_func(univ) == m_Matches;
    }
    const PointerToCVUniverseIntFunction m_func;
    const int  m_Matches; //Maximum value of UNIVERSE::var that passes this Cut
};

// takes a vector with 2 entried, min and max.
template <class UNIVERSE, class EVENT = detail::empty>
class RangeFromConfigFunc: public Cut<UNIVERSE>
{
public:
    typedef std::function<double(const UNIVERSE&)> PointerToCVUniverseFunction;
    RangeFromConfigFunc(const NuConfig& config, CVFunctions<UNIVERSE>& functions): Cut<UNIVERSE,EVENT>((config.GetString("min")) + "<=" +  config.GetString("name")+ "<=" + (config.GetString("max"))), m_min(config.GetDouble("min")), m_max(config.GetDouble("max")),m_func(functions.GetRecoFunction(config.GetString("variable")))
    {
    }
#ifndef __GCCXML__
    virtual ~RangeFromConfigFunc() = default;
#endif
private:
    bool checkCut(const UNIVERSE& univ , EVENT& /*evt*/) const// override
    {
        return m_func(univ) >= m_min && m_func(univ) <= m_max;
    }
    const PointerToCVUniverseFunction m_func;
    const double m_min; //Minimum value of UNIVERSE::var that passes this Cut
    const double m_max; //Maximum value of UNIVERSE::var that passes this Cut
};


// make version for constraints?

template <class UNIVERSE>
class MaximumConstraintFromConfigFunc: public SignalConstraint<UNIVERSE>
{
public:
    typedef std::function<double(const UNIVERSE&)> PointerToCVUniverseFunction;
    MaximumConstraintFromConfigFunc(const NuConfig& config, CVFunctions<UNIVERSE>& functions): SignalConstraint<UNIVERSE>(config.GetString("name")+"<="+(config.GetString("max"))), m_Max(config.GetDouble("max")),m_func(functions.GetTrueFunction(config.GetString("variable")))
    {
    }
#ifndef __GCCXML__
    virtual ~MaximumConstraintFromConfigFunc() = default;
#endif
private:
    bool checkConstraint(const UNIVERSE& univ/*evt*/) const //override
    {
        return m_func(univ) <= m_Max;
    }
    const PointerToCVUniverseFunction m_func;
    const double m_Max; //Maximum value of UNIVERSE::var that passes this Cut
};

template <class UNIVERSE>
class MinimumConstraintFromConfigFunc: public SignalConstraint<UNIVERSE>
{
public:
    typedef std::function<double(const UNIVERSE&)> PointerToCVUniverseFunction;
    MinimumConstraintFromConfigFunc(const NuConfig& config, CVFunctions<UNIVERSE>& functions): SignalConstraint<UNIVERSE>(config.GetString("name")+">="+(config.GetString("min"))), m_Min(config.GetDouble("min")), m_func(functions.GetTrueFunction(config.GetString("variable")))
    {
    }
#ifndef __GCCXML__
    virtual ~MinimumConstraintFromConfigFunc() = default;
#endif
private:
    bool checkConstraint(const UNIVERSE& univ /*evt*/) const //override
    {
        return m_func(univ) >= m_Min;
    }
    const PointerToCVUniverseFunction m_func;
    const double  m_Min; //Minimum value of UNIVERSE::var that passes this Cut
};

template <class UNIVERSE>
class IsSameConstraintFromConfigFunc: public SignalConstraint<UNIVERSE>
{
public:
    typedef std::function<double(const UNIVERSE&)> PointerToCVUniverseFunction;
    IsSameConstraintFromConfigFunc(const NuConfig& config, CVFunctions<UNIVERSE>& functions): SignalConstraint<UNIVERSE>(config.GetString("name")+ "==" + (config.GetString("equals"))), m_Matches(config.GetInt("equals")),m_func(functions.GetTrueIntFunction(config.GetString("variable")))
    {
    }
#ifndef __GCCXML__
    virtual ~IsSameConstraintFromConfigFunc() = default;
#endif
private:
    bool checkConstraint(const UNIVERSE& univ /*evt*/) const// override
    {
        return m_func(univ) == m_Matches;
    }
    const PointerToCVUniverseFunction m_func;
    const int m_Matches; //Maximum value of UNIVERSE::var that passes this Cut
};


// takes a vector with 2 entried, min and max.
template <class UNIVERSE>
class RangeConstraintFromConfigFunc: public SignalConstraint<UNIVERSE>
{
public:
    typedef std::function<double(const UNIVERSE&)> PointerToCVUniverseFunction;
    RangeConstraintFromConfigFunc(const NuConfig& config, CVFunctions<UNIVERSE>& functions): SignalConstraint<UNIVERSE>((config.GetString("min")) + "<=" + config.GetString("name")+ "<=" + (config.GetString("max"))), m_min(config.GetDouble("min")), m_max(config.GetDouble("max")), m_func(functions.GetTrueFunction(config.GetString("variable")))
    {
    }
#ifndef __GCCXML__
    virtual ~RangeConstraintFromConfigFunc() = default;
#endif
private:
    bool checkConstraint(const UNIVERSE& univ /*evt*/) const// override
    {
        return m_func(univ) >= m_min && m_func(univ) <= m_max;
    }
    const PointerToCVUniverseFunction m_func;
    const double m_min; //Minimum value of UNIVERSE::var that passes this Cut
    const double m_max; //Maximum value of UNIVERSE::var that passes this Cut
};

template <class UNIVERSE, class EVENT = detail::empty>
class OrContraintFromConfig: public Cut<UNIVERSE, EVENT>
{
public:
    typedef std::function<double(const UNIVERSE&)> PointerToCVUniverseIntFunction;
    Or(const NuConfig& config, CVFunctions<UNIVERSE>& functions)
    {
        
    }
#ifndef __GCCXML__
    virtual ~IsSameFromConfigFunc() = default;
#endif
private:
    std::string fname = "OR[";
    std::vector<NuConfig> fcuts;
    std::vector<std::string> fcuts = config.GetStringVector("Constraints");
    for (auto f:fcuts){
        
    }
    SignalConstraint<UNIVERSE> ftheCut = SignalConstraint<UNIVERSE>("O")
    bool checkCut(const UNIVERSE& univ, EVENT& /*evt*/) const override
    {
        //std::cout << Cut<UNIVERSE, EVENT>::getName() << " " << m_func(univ) << " "  << m_Matches << std::endl;
        return m_func(univ) == m_Matches;
    }
    const PointerToCVUniverseIntFunction m_func;
    const int  m_Matches; //Maximum value of UNIVERSE::var that passes this Cut
};

/////---
//  
//template <class UNIVERSE, class EVENT = detail::empty>
//class MaximumFromConfigFunc: public Cut<UNIVERSE, EVENT>
//  {
//  typedef std::function<double(const UNIVERSE&)> PointerToCVUniverseFunction;
//    public:
//      MaximumFromConfigFunc(const NuConfig& config,  CVFunctions<UNIVERSE>& functions): Cut<UNIVERSE, EVENT>(config.GetString("name")+" <= "+config.GetString("max")), m_Max(config.GetDouble("max")), m_func(functions.GetRecoFunction(config.GetString("variable")))
//  {
//    
//      }
//#ifndef __GCCXML__
//      virtual ~MaximumFromConfigFunc() = default;
//#endif
//    private:
//      bool checkCut(const UNIVERSE& univ, EVENT& /*evt*/) const override
//      {
//        return m_func(univ) <= m_Max;
//      }
//
//      const double m_Max; //Maximum value of UNIVERSE::var that passes this Cut
//      const PointerToCVUniverseFunction m_fun;
//  };
//

}
#endif

