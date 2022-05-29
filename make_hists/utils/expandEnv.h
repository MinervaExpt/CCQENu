#ifndef EXPANDENV_H
#define EXPANDENV_H

//https://codereview.stackexchange.com/questions/172644/c-environment-variable-expansion
//https://codereview.stackexchange.com/users/75307/toby-speight

#include <string>
#include <regex>
#include <cstdlib>

inline std::string expandEnv(std::string text)
{
    static const std::regex env_re{R"--(\$\{([^}]+)\})--"};
    std::smatch match;
    while (std::regex_search(text, match, env_re)) {
        auto const from = match[0];
        auto const next = match[1].str();
        auto const var_name = next.c_str();
        text.replace(from.first, from.second, std::getenv(var_name));
    }
    return text;
}
#endif
