cmake_minimum_required(VERSION 3.12 FATAL_ERROR)

# Set project name and version
project(BasicGameUsage VERSION 0.6)

# Set C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

# Enable debug symbols by default
if(NOT CMAKE_BUILD_TYPE)
  #set(CMAKE_BUILD_TYPE Debug 
  set(CMAKE_BUILD_TYPE Release
    CACHE STRING 
      "Choose the type of build (Debug or Release)" 
      FORCE
    )
endif()

# Generate config.h
configure_file(config.h.in config.h)

# Find SFML shared libraries
find_package(SFML COMPONENTS system window graphics audio REQUIRED)

# Compile executable
add_executable(BasicGameUsage src/main.cpp)

# Set include directory search paths
target_include_directories(BasicGameUsage PRIVATE "${PROJECT_BINARY_DIR}")

# Link executable to required SFML libraries
target_link_libraries(BasicGameUsage sfml-system sfml-window sfml-graphics sfml-audio)

# Install target
install(TARGETS BasicGameUsage DESTINATION bin)

