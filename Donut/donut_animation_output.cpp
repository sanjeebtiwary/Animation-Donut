void draw() {
    // ...
    std::ofstream outfile;
    outfile.open("donut_animation_output.txt");
    for (int i = 0; i < kScreenHeight; i++) {
        outfile << screen[i] << std::endl;
    }
    outfile.close();
}
