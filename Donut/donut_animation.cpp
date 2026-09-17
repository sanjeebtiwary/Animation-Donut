#include <SDL2/SDL.h>
#include <SDL2/SDL_opengl.h>
#include <GL/glu.h>

#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <string>
#include <thread>
#include <vector>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

struct Controls {
    std::string mode = "auto";
    double rotate_x = 0.9;
    double rotate_y = 0.0;
    double rotate_z = 0.0;
    double zoom = 1.0;
    double speed = 1.2;
};

std::string trim(const std::string& text) {
    const std::string whitespace = " \t\r\n";
    const auto start = text.find_first_not_of(whitespace);
    if (start == std::string::npos) {
        return "";
    }
    const auto end = text.find_last_not_of(whitespace);
    return text.substr(start, end - start + 1);
}

void loadControls(const std::string& path, Controls& controls) {
    std::ifstream input(path.c_str());
    if (!input.is_open()) {
        return;
    }

    std::string line;
    while (std::getline(input, line)) {
        line = trim(line);
        if (line.empty() || line[0] == '#') {
            continue;
        }

        const auto equal = line.find('=');
        if (equal == std::string::npos) {
            continue;
        }

        const std::string key = trim(line.substr(0, equal));
        const std::string value = trim(line.substr(equal + 1));

        if (key == "mode") {
            controls.mode = value;
        } else if (key == "rotate_x") {
            controls.rotate_x = std::stod(value);
        } else if (key == "rotate_y") {
            controls.rotate_y = std::stod(value);
        } else if (key == "rotate_z") {
            controls.rotate_z = std::stod(value);
        } else if (key == "zoom") {
            controls.zoom = std::stod(value);
        } else if (key == "speed") {
            controls.speed = std::stod(value);
        }
    }
}

void drawTorus(double rotation_x, double rotation_y, double rotation_z, double zoom, double time) {
    const int major_segments = 60;
    const int minor_segments = 24;
    const double major_radius = 1.2;
    const double minor_radius = 0.45;

    glClearColor(0.03f, 0.07f, 0.11f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    const double aspect = 1.0;
    gluPerspective(45.0, aspect, 0.1, 20.0);

    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    glTranslatef(0.0f, 0.0f, -4.5f);
    glScalef(static_cast<float>(zoom), static_cast<float>(zoom), static_cast<float>(zoom));
    glRotatef(static_cast<float>(rotation_x * 57.2958), 1.0f, 0.0f, 0.0f);
    glRotatef(static_cast<float>(rotation_y * 57.2958 + time * 45.0), 0.0f, 1.0f, 0.0f);
    glRotatef(static_cast<float>(rotation_z * 57.2958), 0.0f, 0.0f, 1.0f);

    const GLfloat light_pos[] = {2.0f, 3.0f, 4.0f, 1.0f};
    const GLfloat light_color[] = {1.0f, 0.9f, 0.8f, 1.0f};
    const GLfloat ambient[] = {0.2f, 0.2f, 0.25f, 1.0f};

    glEnable(GL_DEPTH_TEST);
    glEnable(GL_LIGHTING);
    glEnable(GL_LIGHT0);
    glEnable(GL_COLOR_MATERIAL);
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos);
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_color);
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient);

    for (int i = 0; i < major_segments; ++i) {
        double u1 = (static_cast<double>(i) / major_segments) * 2.0 * M_PI;
        double u2 = (static_cast<double>(i + 1) / major_segments) * 2.0 * M_PI;

        glBegin(GL_TRIANGLE_STRIP);
        for (int j = 0; j <= minor_segments; ++j) {
            double v = (static_cast<double>(j) / minor_segments) * 2.0 * M_PI;

            auto point = [&](double uu, double vv) {
                const double x = (major_radius + minor_radius * std::cos(vv)) * std::cos(uu);
                const double y = (major_radius + minor_radius * std::cos(vv)) * std::sin(uu);
                const double z = minor_radius * std::sin(vv);
                const double nx = std::cos(uu) * std::cos(vv);
                const double ny = std::sin(uu) * std::cos(vv);
                const double nz = std::sin(vv);
                glNormal3d(nx, ny, nz);
                const float shade = 0.45f + 0.55f * static_cast<float>((std::sin(uu + time * 2.0) + 1.0) * 0.5);
                glColor3f(0.3f + shade * 0.4f, 0.8f * shade, 1.0f);
                glVertex3d(x, y, z);
            };

            point(u1, v);
            point(u2, v);
        }
        glEnd();
    }
}

int main(int argc, char* argv[]) {
    const std::string project_root = ".";
    const std::string control_file = project_root + "/Donut/donut_controls.txt";

    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        std::cerr << "SDL init failed: " << SDL_GetError() << std::endl;
        return 1;
    }

    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 2);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 1);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_COMPATIBILITY);
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);

    SDL_GL_SetSwapInterval(1);

    SDL_Window* window = SDL_CreateWindow(
        "3D Donut Studio",
        SDL_WINDOWPOS_CENTERED,
        SDL_WINDOWPOS_CENTERED,
        1280,
        900,
        SDL_WINDOW_OPENGL | SDL_WINDOW_SHOWN
    );

    if (!window) {
        std::cerr << "Window creation failed: " << SDL_GetError() << std::endl;
        SDL_Quit();
        return 1;
    }

    SDL_GLContext context = SDL_GL_CreateContext(window);
    if (!context) {
        std::cerr << "OpenGL context failed: " << SDL_GetError() << std::endl;
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }

    glEnable(GL_DEPTH_TEST);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    Controls controls;
    const auto start = std::chrono::steady_clock::now();
    bool running = true;

    while (running) {
        loadControls(control_file, controls);

        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = false;
            }
        }

        const auto now = std::chrono::steady_clock::now();
        const double elapsed = std::chrono::duration<double>(now - start).count();

        const double rotation_x = controls.rotate_x + (controls.mode == "auto" ? 0.7 : 0.0);
        const double rotation_y = controls.rotate_y + (controls.mode == "auto" ? elapsed * controls.speed : 0.0);
        const double rotation_z = controls.rotate_z + (controls.mode == "auto" ? elapsed * controls.speed * 0.8 : 0.0);

        drawTorus(rotation_x, rotation_y, rotation_z, controls.zoom, elapsed);
        SDL_GL_SwapWindow(window);
        std::this_thread::sleep_for(std::chrono::milliseconds(16));
    }

    SDL_GL_DeleteContext(context);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
