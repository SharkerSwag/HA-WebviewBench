plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.homeassistant.android.common)
}

android {
    namespace = "io.homeassistant.companion.android.microwakeword"
    // ndkVersion disabled - build environment lacks Ninja
    // ndkVersion = libs.versions.androidNdk.get()

    defaultConfig {
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        // externalNativeBuild disabled - build environment lacks Ninja
        // externalNativeBuild {
        //     cmake {
        //         arguments += "-DANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON"
        //     }
        // }
    }

    buildTypes {
        debug {
            // Required for HWASan wrap.sh to be included uncompressed in the APK
            // See https://developer.android.com/ndk/guides/hwasan
            packaging {
                jniLibs {
                    useLegacyPackaging = true
                }
            }
        }
    }

    // externalNativeBuild disabled - build environment lacks Ninja
    // externalNativeBuild {
    //     cmake {
    //         path = file("src/main/cpp/CMakeLists.txt")
    //         version = libs.versions.cmake.get()
    //     }
    // }
}

dependencies {
    androidTestImplementation(libs.bundles.androidx.test)
}

// If we ever add unit test to this module we could remove this block
tasks.withType<Test>().configureEach {
    failOnNoDiscoveredTests = false
}

// If we ever add unit test to this module we could remove this block
tasks.withType<Test>().configureEach {
    failOnNoDiscoveredTests = false
}
