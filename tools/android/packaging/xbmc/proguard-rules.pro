# ProGuard rules for DanmakuFlameMaster and overlay integration
-keep class master.flame.danmaku.** { *; }
-dontwarn master.flame.danmaku.**

# Keep JSON models and JNI-bound classes if any appear under our packages
-keep class org.xbmc.** { *; }
-keep class tv.danmaku.** { *; }
