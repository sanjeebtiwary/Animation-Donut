#include <iostream>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <chrono>
#include <thread>

const int kScreenWidth = 120;
const int kScreenHeight = 40;

char screen[kScreenHeight][kScreenWidth + 1]; // +1 for null character

// Precompute sin/cos tables for performance
float cos_table[kScreenWidth];
float sin_table[kScreenWidth];

void initialize() {
    for (int i = 0; i < kScreenWidth; i++) {
        cos_table[i] = std::cos(i * M_PI / 60.0);
        sin_table[i] = std::sin(i * M_PI / 60.0);
    }
}

void draw() {
    // Clear the screen
    for (int i = 0; i < kScreenHeight; i++) {
        for (int j = 0; j < kScreenWidth; j++) {
            screen[i][j] = ' ';
        }
        screen[i][kScreenWidth] = '\0'; // null terminate each line
    }

    // Draw the donut
    float theta = 0;
    float phi = 0;
    char c = '.';
    for (int i = 0; i < 8000; i++) {
        float sin_theta = std::sin(theta);
        float cos_theta = std::cos(theta);
        float sin_phi = std::sin(phi);
        float cos_phi = std::cos(phi);

        float x = cos_theta;
        float y = sin_phi * sin_theta;
        float z = cos_phi * sin_theta;

        // Project 3D point to 2D screen space
        float x2d = x * sin_table[i % kScreenWidth] - z * cos_table[i % kScreenWidth];
        float y2d = x * cos_table[i % kScreenWidth] + z * sin_table[i % kScreenWidth];
        int xp = kScreenWidth / 2 + 30 * x2d / (y2d + 5);
        int yp = kScreenHeight / 2 + 15 * y2d / (y2d + 5);

        // Draw the character at the projected screen coordinates
        if (yp >= 0 && yp < kScreenHeight && xp >= 0 && xp < kScreenWidth) {
            screen[yp][xp] = c;
        }

        // Update the rotation angles and character
        theta += 0.04;
        phi += 0.02;
        c = (c == '.' ? ':' : '.');
    }
}

int main() {
    initialize();

    // Write the animation output to a text file
    std::ofstream outfile;
    outfile.open("donut_animation_output.txt");

    auto start_time = std::chrono::steady_clock::now();
    while (true) {
        auto current_time = std::chrono::steady_clock::now();
        float elapsed_time = std::chrono::duration_cast<std::chrono::milliseconds>(current_time - start_time).count();

        // Draw the donut and write it to the output file
        draw();
        for (int i = 0; i < kScreenHeight; i++) {
            outfile << screen[i];
        }
    }
}
