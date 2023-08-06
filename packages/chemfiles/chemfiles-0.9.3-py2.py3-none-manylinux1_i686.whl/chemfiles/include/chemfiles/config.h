// Chemfiles, a modern library for chemistry file reading and writing
// Copyright (C) Guillaume Fraux and contributors -- BSD license

// clang-format off
#ifndef CHEMFILES_CONFIG_HPP
#define CHEMFILES_CONFIG_HPP

/// An integer containing the major (x.0.0) version number
#define CHEMFILES_VERSION_MAJOR 0
/// An integer containing the minor (0.y.0) version number
#define CHEMFILES_VERSION_MINOR 9
/// An integer containing the patch (0.0.z) version number
#define CHEMFILES_VERSION_PATCH 3
/// The full version of chemfiles ("x.y.z"), as a string
#define CHEMFILES_VERSION "0.9.3"

/// thread_local implementation
#ifdef __cplusplus
    #if 1
        #define CHFL_THREAD_LOCAL thread_local
    #else
        #define CHFL_THREAD_LOCAL
    #endif
#endif

// clang-format on

#endif
