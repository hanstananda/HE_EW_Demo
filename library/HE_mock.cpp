
#include <stdio.h>      /* printf, scanf, puts, NULL */
#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */
#include <map>
#include <string>
#include <iostream>
#include <vector>

#define Q 0x10000 //2**16
#define DIM_N 768
#define SEED_LEN 32
#define KEY_LEN 12288 //N*16
#define CIPHER_LEN 1568//(N+16)*2
#define C2_LEN 16


int main(int argc, char* argv[]){
    srand (time(NULL));
    // Check the number of parameters
    if (argc < 2) {
        // Tell the user how to run the program
        std::cerr << "Usage: " << argv[0] << " (decrypt | encrypt ) or (add | sub | addition | subtraction ) numParties" << std::endl;
        /* "Usage messages" are a conventional way of telling the user
         * how to run a program if they enter the command incorrectly.
         */
        return 1;
    }
    std::string param1(argv[1]);
    std::map<std::string,char> argMapper= {
            {"addition",'+'},
            {"add", '+'},
            {"subtraction",'-'},
            {"sub", '-'},
//            {"multiplication",'*'},
//            {"multi", '*'},
    };

    std::string seed;
    bool isSeedProvided;
    std::cin >> isSeedProvided;
    if(isSeedProvided) {
        std::cin>>seed;
    }
    if(param1 == "decrypt") {
        int sk_seed = rand() % 10 + 1;
        if(isSeedProvided) {
            // sk_seed.setData(seed);
        }
        seed = std::to_string(sk_seed);
        std::cout<<"1 "<<seed<<"\n";
        int n;
        std::cin>>n;
        std::cout<<n<<"\n";
        for(int i=1;i<=n;i++) {
            int m;
            std::cin>>m;
            std::cout<<m<<" ";
            for(int j=1;j<=m;j++) {
                std::array<int, DIM_N> a_input{};
                std::array<int, C2_LEN> c_input{};
                for(int k=0;k<DIM_N;k++) {
                    std::cin>>a_input[k];
                }
                for(int k=0;k<C2_LEN;k++) {
                    std::cin>>c_input[k];
                }
                // Build the AHE from encrypted value
                std::cout<<a_input[0]<<" ";
            }
            std::cout<<"\n";
        }
    }
    else if(param1 == "encrypt") {
        int sk_seed = rand() % 10 + 1;
        if(isSeedProvided) {
            // sk_seed.setData(seed);
        }
        seed = std::to_string(sk_seed);
        std::cout<<"1 "<<seed<<"\n";

        int n;
        std::cin>>n;
        std::cout<<n<<"\n";
        for(int i=1;i<=n;i++) {
            int m;
            std::cin>>m;
            std::cout<<m<<"\n";
            for(int j=1;j<=m;j++) {
                int val;
                std::cin>>val;
                std::pair<std::array<int, DIM_N>, std::array<int, C2_LEN> > res;
                res.first.fill(val);
                res.second.fill(val);
                for(auto el:res.first) {
                    std::cout<<el<<" ";
                }
                std::cout<<"\n";
                for(auto el:res.second) {
                    std::cout<<el<<" ";
                }
                std::cout<<"\n";
            }
        }
    }
    else {
        std::cerr << "Wrong arguments given! Usage: " << argv[0] << " (decrypt | encrypt ) or (add | sub | addition | subtraction ) numParties"  << std::endl;
    }
    return 0;
}