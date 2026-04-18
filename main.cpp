#include <iostream>
#include "threadpool.h"

int main() {
    ThreadPool pool(3);

    for(int i = 0; i < 10; i++) {
        pool.enqueue([i] {
            std::cout << "Task " << i << " executed by thread\n";
        });
    }

    return 0;
}
