#include <iostream>
using namespace std;

struct package
{
    const char *name;
    int value;
};


void print_package(const package &p)
{
    std::cerr << p.name << "=" << p.value << std::endl;
}


int main(int, char **)
{

    print_package({"burl",10});


    return 0;
}

