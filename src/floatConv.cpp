#include <iostream>


extern "C" void toFloat(const uint8_t *arr)
{
   
    for (int i = 0; i < 4; i++){
    //  std::cout << arr[i] << std::endl;
    printf("%x - ", static_cast<uint8_t>(arr[i]));
    }
    
}

// int main(){
// const uint8_t test[4]= {'i', 0x2, 0x3, 0x4};
// toFloat(test);
// }