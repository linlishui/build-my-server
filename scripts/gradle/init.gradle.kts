@file:Suppress("UnstableApiUsage")

import org.gradle.util.GradleVersion

val urlMappingsTencent = mapOf(
    "https://repo.maven.apache.org/maven2" to "https://mirrors.tencent.com/nexus/repository/maven-public/",
    "https://dl.google.com/dl/android/maven2" to "https://mirrors.tencent.com/nexus/repository/maven-public/",
    "https://plugins.gradle.org/m2" to "https://mirrors.tencent.com/nexus/repository/gradle-plugins/"
)

val urlMappingsAliyun = mapOf(
    "https://repo.maven.apache.org/maven2" to "https://maven.aliyun.com/repository/central/",
    "https://dl.google.com/dl/android/maven2" to "https://maven.aliyun.com/repository/google/",
//    "https://plugins.gradle.org/m2" to "https://maven.aliyun.com/repository/gradle-plugin/",
    "https://plugins.gradle.org/m2" to "https://mirrors.tencent.com/nexus/repository/gradle-plugins/"
)

/**
 * 启用镜像地址映射
 */
fun RepositoryHandler.enableMirror() {
    all {
        if (this is MavenArtifactRepository) {
            val originalUrl = this.url.toString().removeSuffix("/")
            urlMappingsTencent[originalUrl]?.let {
                logger.lifecycle("Repository $name [$url] is mirrored to $it")
                setUrl(it)
            }
        }
    }
}

gradle.allprojects {
    buildscript {
        repositories.enableMirror()
    }
    repositories.enableMirror()
}

gradle.beforeSettings {
    pluginManagement.repositories.enableMirror()
    // 6.8 及更高版本执行 DependencyResolutionManagement 配置
    val versionR68 = GradleVersion.version("6.8")
    if (GradleVersion.current() >= versionR68) {
        val getDrm = settings.javaClass.getDeclaredMethod("getDependencyResolutionManagement")
        val drm = getDrm.invoke(settings)
        val getRepos = drm.javaClass.getDeclaredMethod("getRepositories")
        val repos = getRepos.invoke(drm) as RepositoryHandler
        repos.enableMirror()
        println("Gradle ${gradle.gradleVersion} DependencyResolutionManagement Configured $settings")
    } else {
        println("Gradle ${gradle.gradleVersion} DependencyResolutionManagement Ignored $settings")
    }
}